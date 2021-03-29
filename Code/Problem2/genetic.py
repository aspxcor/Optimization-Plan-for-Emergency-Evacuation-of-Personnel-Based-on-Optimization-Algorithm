# -*- coding: utf-8 -*-
import geatpy as ea
import numpy as np
from scipy.io import loadmat
import random
m = loadmat("xingguo.mat")
B=m['BusBlank'][0][0]       # 自行设定 可控制变量
Y=m['depot'][0][0]
S=m['ND'][0][0]
T=m['NS'][0][0]
N=m['N'][0][0]
Dij=m['path']       # 编号规则 从0开始编号，编号顺序 S~T~Y
L=m['DSeparate'].reshape(S)
U=m['SSeparate'].reshape(T)
numOfGenetic=L.sum()
Nind=300
Chrom3Probability=0.7

class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数） 也即优化目标的数目
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 2*numOfGenetic+B-1  # 初始化Dim（决策变量维数）  #注意 插板时两两一组
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [0] * numOfGenetic + [S] * numOfGenetic + [0] * (B-1)# 决策变量下界
        ub = [S-1] * numOfGenetic + [N-Y-1] * numOfGenetic + [numOfGenetic-2] * (B-1)# 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
        referenceObjV  = np.array([[600]])
        return referenceObjV

    def aimFunc(self, pop):  # 目标函数
        SInTurns = pop.Phen[:, :numOfGenetic].astype(int)
        TInTurns = pop.Phen[:, numOfGenetic:2 * numOfGenetic].astype(int)
        Turns = pop.Phen[:, 2 * numOfGenetic:].astype(int)

        TmaxMin=np.zeros((SInTurns.shape[0], 1), dtype=np.int)
        CV1 = np.zeros((SInTurns.shape[0], 1), dtype=np.int)     #限制S所有人员完全疏散
        CV2 = np.zeros((SInTurns.shape[0], 1), dtype=np.int)     #限制T所有避难所不超过容量上限
        for i in range(SInTurns.shape[0]):
            SInTurn=SInTurns[i]
            TInTurn=TInTurns[i]
            Turn=Turns[i]

            Turn.sort()

            #按B辆车辆进行切片
            SInTurnOfCar = [SInTurn[:Turn[0] + 1]] + [SInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [SInTurn[Turn[B-2] + 1:]]
            TInTurnOfCar = [TInTurn[:Turn[0] + 1]] + [TInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [TInTurn[Turn[B-2] + 1:]]

            #计算CV矩阵
            for s in range(S):
                if np.count_nonzero(SInTurn==s)<L[s]:
                    CV1[i]+=L[s]-np.count_nonzero(SInTurn==s)
            for t in range(T):
                if np.count_nonzero(TInTurn == (t+S)) > U[t]:
                    CV2[i] += np.count_nonzero(TInTurn == (t+S))-U[t]

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
        pop.CV=np.hstack([CV1,CV2])


if __name__ == '__main__':
    """===============================实例化问题对象==========================="""
    problem = MyProblem()  # 生成问题对象
    """=================================种群设置=============================="""
    Encodings = ['RI', 'RI', 'P']  # 编码方式
    NIND = Nind  # 种群规模
    Field1 = ea.crtfld(Encodings[0], problem.varTypes[:numOfGenetic], problem.ranges[:, :numOfGenetic], problem.borders[:, :numOfGenetic])
    Field2 = ea.crtfld(Encodings[1], problem.varTypes[numOfGenetic:2*numOfGenetic], problem.ranges[:, numOfGenetic:2*numOfGenetic], problem.borders[:, numOfGenetic:2*numOfGenetic])
    Field3 = ea.crtfld(Encodings[2], problem.varTypes[2*numOfGenetic:], problem.ranges[:, 2*numOfGenetic:], problem.borders[:, 2*numOfGenetic:])
    Fields = [Field1, Field2, Field3]  # 创建区域描述器
    population = ea.PsyPopulation(Encodings, Fields, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    # myAlgorithm = ea.soea_psy_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    # myAlgorithm.recOper = ea.Xovdp(XOVR=0.9, Parallel=True)  # 设置交叉算子
    # myAlgorithm.mutOper = ea.Mutinv(Pm=0.5, Parallel=True)  # 设置变异算子
    myAlgorithm = ea.soea_psy_GGAP_SGA_templet(problem, population)
    myAlgorithm.MAXGEN = 600  # 最大进化代数
    # myAlgorithm.trappedValue = 1  # “进化停滞”判断阈值
    # myAlgorithm.maxTrappedCount = myAlgorithm.MAXGEN//2  # 进化停滞计数器最大上限值，如果连续maxTrappedCount代被判定进化陷入停滞，则终止进化
    myAlgorithm.logTras = 1  # 设置每隔多少代记录日志，若设置成0则表示不记录日志
    myAlgorithm.verbose = True  # 设置是否打印输出日志信息
    myAlgorithm.drawing = 1  # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）
    """===========================根据先验知识创建先知种群========================"""
    tmpChrom1 = np.concatenate([np.ones(L[_], dtype=int) * _ for _ in range(S)])
    tmpChrom2 = np.concatenate([np.ones(U[_], dtype=int) * (_ + S) for _ in range(T)])
    tmpChrom3 = np.array([_ * numOfGenetic // B for _ in range(1, B)]).reshape(1, B - 1)
    # for j in range(B - 1):
    #     tmpChrom3[0][j] = tmpChrom3[0][j] + 1 if random.random() > 0.5 else tmpChrom3[0][j]

    np.random.shuffle(tmpChrom1)
    np.random.shuffle(tmpChrom2)
    prophetChrom = [tmpChrom1.reshape(1, numOfGenetic), tmpChrom2[: numOfGenetic].reshape(1, numOfGenetic), tmpChrom3]
    prophetPop = ea.PsyPopulation(Encodings, Fields, 1, prophetChrom)

    for i in range(1,Nind):
        np.random.shuffle(tmpChrom1)
        np.random.shuffle(tmpChrom2)
        # tmpChrom3=np.array(random.sample(range(0,numOfGenetic-2),B - 1)).reshape(1, B - 1)
        tmpChrom3=np.array([_ * numOfGenetic // B for _ in range(1, B)]).reshape(1, B - 1)
        for j in range(B-1):
            tmpChrom3[0][j]=tmpChrom3[0][j]+1 if random.random()<Chrom3Probability else tmpChrom3[0][j]
        prophetChrom = [tmpChrom1.reshape(1, numOfGenetic), tmpChrom2[: numOfGenetic].reshape(1, numOfGenetic), tmpChrom3]
        prophetPop+=ea.PsyPopulation(Encodings, Fields, 1, prophetChrom)

    myAlgorithm.call_aimFunc(prophetPop)  # 计算先知种群的目标函数值及约束（假如有约束）
    """==========================调用算法模板进行种群进化========================"""
    [BestIndi, population] = myAlgorithm.run(prophetPop)  # 执行算法模板，得到最优个体以及最后一代种群 # 先验知识版本
    # [BestIndi, population] = myAlgorithm.run()  # 执行算法模板，得到最优个体以及最后一代种群
    BestIndi.save()  # 把最优个体的信息保存到文件中
    """=================================输出结果=============================="""
    print('评价次数：%s' % myAlgorithm.evalsNum)
    print('时间已过 %s 秒' % myAlgorithm.passTime)
    if BestIndi.sizes != 0:
        print('最优的目标函数值为：%s' % BestIndi.ObjV[0][0])
        print('最优的控制变量值为：')
        for i in range(BestIndi.Phen.shape[1]):
            print(BestIndi.Phen[0, i],end=" ")
        print("")
    else:
        print('没找到可行解。')