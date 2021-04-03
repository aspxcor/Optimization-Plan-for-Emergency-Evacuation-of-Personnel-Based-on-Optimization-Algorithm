# -*- coding: utf-8 -*-
# 本程序主要思想：
#   通过染色体编码格式控制交换以后的前两条染色体编码一定合法
#   不引入CV矩阵进行合法性检查
#   不引入先验知识，插板位置纯依靠进化进行搜索
#   从实验结果看，本方法不甚理想，推测将插板位置与遗传算法剥离开来效果可能更好
#   引入了结果的作图，关于作图的美观性与直观性，还有一定改进空间
import geatpy as ea
import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

m = loadmat("xingguo.mat")
B=m['BusBlank'][0][0]       # 自行设定 可控制变量
# B=5       # 自行设定 可控制变量
Y=m['depot'][0][0]
S=m['ND'][0][0]
T=m['NS'][0][0]
N=m['N'][0][0]
Dij=m['path']       # 编号规则 从0开始编号，编号顺序 S~T~Y
L=m['DSeparate'].reshape(S)
U=m['SSeparate'].reshape(T)
numOfGenetic=L.sum()
STrans=[]
TTrans=[]
for i in range(S):
    STrans+=L[i]*[i]
for i in range(T):
    TTrans+=U[i]*[i+S]
Nind=400
SizeOfMap=10
# Chrom3Probability=0.7

class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数） 也即优化目标的数目
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 2*numOfGenetic+B-1  # 初始化Dim（决策变量维数）  #注意 插板时两两一组
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [0] * numOfGenetic + [0] * numOfGenetic + [0] * (B-1)# 决策变量下界
        ub = [numOfGenetic-1] * numOfGenetic + [U.sum()-1] * numOfGenetic + [numOfGenetic-2] * (B-1)# 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)        # 调用父类构造方法完成实例化

    def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
        referenceObjV  = np.array([[600]])
        return referenceObjV

    def aimFunc(self, pop):  # 目标函数
        SInTurns = pop.Phen[:, :numOfGenetic].astype(int)
        TInTurns = pop.Phen[:, numOfGenetic:2 * numOfGenetic].astype(int)
        Turns = pop.Phen[:, 2 * numOfGenetic:].astype(int)

        for t in range(Nind):
            for i in range(numOfGenetic):
                SInTurns[t][i]=STrans[SInTurns[t][i]]
                TInTurns[t][i] = TTrans[TInTurns[t][i]]

        TmaxMin=np.zeros((SInTurns.shape[0], 1), dtype=np.int)
        for i in range(SInTurns.shape[0]):
            SInTurn=SInTurns[i]
            TInTurn=TInTurns[i]
            Turn=Turns[i]

            Turn.sort()

            #按B辆车辆进行切片
            SInTurnOfCar = [SInTurn[:Turn[0] + 1]] + [SInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [SInTurn[Turn[B-2] + 1:]]
            TInTurnOfCar = [TInTurn[:Turn[0] + 1]] + [TInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [TInTurn[Turn[B-2] + 1:]]

            time=np.zeros(B,dtype=int)
            for carCurrent in range(B):
                tmpTime=Dij[N-1][SInTurnOfCar[carCurrent][0]]
                tmpTime += Dij[SInTurnOfCar[carCurrent][0]][TInTurnOfCar[carCurrent][0]]
                for j in range(1,len(SInTurnOfCar[carCurrent])):
                    tmpTime += Dij[TInTurnOfCar[carCurrent][j-1]][SInTurnOfCar[carCurrent][j]]
                    tmpTime += Dij[SInTurnOfCar[carCurrent][j]][TInTurnOfCar[carCurrent][j]]
                time[carCurrent]=tmpTime

            TmaxMin[i]=time.max()

        pop.ObjV = TmaxMin  # 计算目标函数值，赋值给pop种群对象的ObjV属性

def DrawPointMap(Chromosome,Block):
    SPlotInOrder = [STrans[_] for _ in Chromosome[0, :numOfGenetic]]
    TPlotInOrder = [TTrans[_] - S for _ in Chromosome[0, numOfGenetic:2 * numOfGenetic]]

    plt.figure()
    x0 = SizeOfMap//2
    y0 = SizeOfMap//2
    SPointX = np.random.rand(S) * SizeOfMap
    SPointY = np.random.rand(S) * SizeOfMap
    TPointX = np.random.rand(T) * SizeOfMap
    TPointY = np.random.rand(T) * SizeOfMap

    plt.scatter(SPointX, SPointY, color = 'r', marker = 'o',label = '受灾点')     # 要标记的点的坐标、大小及颜色
    plt.scatter(TPointX, TPointY, color='b', marker='o', label='避难所')          # 要标记的点的坐标、大小及颜色
    plt.scatter(x0, y0, s = 200, color = 'r',marker='*',label = '车库')          # annotate an important value 要标记的点的坐标、大小及颜色

    for i in range(B):
        RoutePlot(x0, y0, SPointX, SPointY, TPointX, TPointY, i, SPlotInOrder, TPlotInOrder, Block)

    plt.legend()                                      # 图例
    plt.savefig('roadmap.svg', dpi=600, bbox_inches='tight')
    plt.show()

# 配送路线绘制
def RoutePlot(x0, y0, SPointX, SPointY, TPointX, TPointY, index, SPlotInOrder, TPlotInOrder, Block):
    color=list(mcolors.CSS4_COLORS.keys())[index*2]         #colors[index]
    if index == 0:
        plt_arrow(x0, y0, SPointX[SPlotInOrder[0]], SPointY[SPlotInOrder[0]], color)
        for j in range(Block[index]):
            plt_arrow(SPointX[SPlotInOrder[j]], SPointY[SPlotInOrder[j]], TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], color)
            plt_arrow(TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], SPointX[SPlotInOrder[j+1]], SPointY[SPlotInOrder[j+1]], color)
        plt_arrow(SPointX[SPlotInOrder[Block[index]]], SPointY[SPlotInOrder[Block[index]]], TPointX[TPlotInOrder[Block[index]]],TPointY[TPlotInOrder[Block[index]]], color)
    elif index == B - 1:
        plt_arrow(x0, y0, SPointX[SPlotInOrder[Block[index-1]+1]], SPointY[SPlotInOrder[Block[index-1]+1]], color)
        for j in range(Block[index - 1] + 1, numOfGenetic-1):
            plt_arrow(SPointX[SPlotInOrder[j]], SPointY[SPlotInOrder[j]], TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], color)
            plt_arrow(TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], SPointX[SPlotInOrder[j+1]], SPointY[SPlotInOrder[j+1]], color)
        plt_arrow(SPointX[SPlotInOrder[numOfGenetic-1]], SPointY[SPlotInOrder[numOfGenetic-1]], TPointX[TPlotInOrder[numOfGenetic-1]],TPointY[TPlotInOrder[numOfGenetic-1]], color)
    else:
        plt_arrow(x0, y0, SPointX[SPlotInOrder[Block[index-1]+1]], SPointY[SPlotInOrder[Block[index-1]+1]], color)
        for j in range(Block[index - 1] + 1, Block[index]):
            plt_arrow(SPointX[SPlotInOrder[j]], SPointY[SPlotInOrder[j]], TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], color)
            plt_arrow(TPointX[TPlotInOrder[j]], TPointY[TPlotInOrder[j]], SPointX[SPlotInOrder[j+1]], SPointY[SPlotInOrder[j+1]], color)
        plt_arrow(SPointX[SPlotInOrder[Block[index]]], SPointY[SPlotInOrder[Block[index]]], TPointX[TPlotInOrder[Block[index]]],TPointY[TPlotInOrder[Block[index]]], color)

def plt_arrow(x_begin,y_begin,x_end,y_end,color):
    plt.arrow(x_begin, y_begin, x_end - x_begin, y_end - y_begin, length_includes_head=True,     # 增加的长度包含箭头部分
             head_width = 0.15, head_length =0.2, fc=color, ec=color)

if __name__ == '__main__':
    """===============================实例化问题对象==========================="""
    problem = MyProblem()  # 生成问题对象
    """=================================种群设置=============================="""
    Encodings = ['P', 'P', 'P']  # 编码方式
    NIND = Nind  # 种群规模
    Field1 = ea.crtfld(Encodings[0], problem.varTypes[:numOfGenetic], problem.ranges[:, :numOfGenetic], problem.borders[:, :numOfGenetic])
    Field2 = ea.crtfld(Encodings[1], problem.varTypes[numOfGenetic:2*numOfGenetic], problem.ranges[:, numOfGenetic:2*numOfGenetic], problem.borders[:, numOfGenetic:2*numOfGenetic])
    Field3 = ea.crtfld(Encodings[2], problem.varTypes[2*numOfGenetic:], problem.ranges[:, 2*numOfGenetic:], problem.borders[:, 2*numOfGenetic:])
    Fields = [Field1, Field2, Field3]  # 创建区域描述器
    population = ea.PsyPopulation(Encodings, Fields, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    myAlgorithm = ea.soea_psy_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    myAlgorithm.recOper = ea.Xovdp(XOVR=0.9, Parallel=True)  # 设置交叉算子
    myAlgorithm.mutOper = ea.Mutinv(Pm=0.6, Parallel=True)  # 设置变异算子
    # myAlgorithm = ea.soea_psy_GGAP_SGA_templet(problem, population)
    myAlgorithm.MAXGEN = 500  # 最大进化代数
    myAlgorithm.trappedValue = 1  # “进化停滞”判断阈值
    myAlgorithm.maxTrappedCount = myAlgorithm.MAXGEN//2  # 进化停滞计数器最大上限值，如果连续maxTrappedCount代被判定进化陷入停滞，则终止进化
    myAlgorithm.logTras = 1  # 设置每隔多少代记录日志，若设置成0则表示不记录日志
    myAlgorithm.verbose = True  # 设置是否打印输出日志信息
    myAlgorithm.drawing = 1  # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）
    """===========================根据先验知识创建先知种群========================"""
    # tmpChrom1 = np.concatenate([np.ones(L[_], dtype=int) * _ for _ in range(S)])
    # tmpChrom2 = np.concatenate([np.ones(U[_], dtype=int) * (_ + S) for _ in range(T)])
    # tmpChrom3 = np.array([_ * numOfGenetic // B for _ in range(1, B)]).reshape(1, B - 1)
    # # for j in range(B - 1):
    # #     tmpChrom3[0][j] = tmpChrom3[0][j] + 1 if random.random() > 0.5 else tmpChrom3[0][j]
    #
    # np.random.shuffle(tmpChrom1)
    # np.random.shuffle(tmpChrom2)
    # prophetChrom = [tmpChrom1.reshape(1, numOfGenetic), tmpChrom2[: numOfGenetic].reshape(1, numOfGenetic), tmpChrom3]
    # prophetPop = ea.PsyPopulation(Encodings, Fields, 1, prophetChrom)
    #
    # for i in range(1, Nind):
    #     np.random.shuffle(tmpChrom1)
    #     np.random.shuffle(tmpChrom2)
    #     # tmpChrom3=np.array(random.sample(range(0,numOfGenetic-2),B - 1)).reshape(1, B - 1)
    #     tmpChrom3 = np.array([_ * numOfGenetic // B for _ in range(1, B)]).reshape(1, B - 1)
    #     for j in range(B - 1):
    #         tmpChrom3[0][j] = tmpChrom3[0][j] + 1 if random.random() < Chrom3Probability else tmpChrom3[0][j]
    #     prophetChrom = [tmpChrom1.reshape(1, numOfGenetic), tmpChrom2[: numOfGenetic].reshape(1, numOfGenetic),tmpChrom3]
    #     prophetPop += ea.PsyPopulation(Encodings, Fields, 1, prophetChrom)
    """==========================调用算法模板进行种群进化========================"""
    # [BestIndi, population] = myAlgorithm.run(prophetPop)  # 执行算法模板，得到最优个体以及最后一代种群 # 先验知识版本
    [BestIndi, population] = myAlgorithm.run()  # 执行算法模板，得到最优个体以及最后一代种群
    BestIndi.save()  # 把最优个体的信息保存到文件中
    """=================================输出结果=============================="""
    print('评价次数：%s' % myAlgorithm.evalsNum)
    print('时间已过 %s 秒' % myAlgorithm.passTime)
    if BestIndi.sizes != 0:
        print('最小的救援时间为：%s' % BestIndi.ObjV[0][0])
        Block = BestIndi.Phen[0, 2 * numOfGenetic:].astype(int)
        Block.sort()
        print('最优的救援方案为：')
        for i in range(B):
            print("第"+str(i+1)+"辆车的救援路线：",end="")
            if i==0:
                print("车库→",end="")
                for j in range(Block[i]+1):
                    print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→",end="")
                    print("避难所" + str(TTrans[BestIndi.Phen[0, j+numOfGenetic].astype(int)]+1) + "→",end="")
                print("救援结束")
            elif i==B-1:
                print("车库→", end="")
                for j in range(Block[i-1] + 1,numOfGenetic):
                    print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→", end="")
                    print("避难所" + str(TTrans[BestIndi.Phen[0, j + numOfGenetic].astype(int)]+1) + "→", end="")
                print("救援结束")
            else:
                print("车库→", end="")
                for j in range(Block[i-1] + 1,Block[i] + 1):
                    print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→", end="")
                    print("避难所" + str(TTrans[BestIndi.Phen[0, j + numOfGenetic].astype(int)]+1) + "→", end="")
                print("救援结束")
        DrawPointMap(BestIndi.Phen.astype(int),Block)
    else:
        print('没找到可行解。')