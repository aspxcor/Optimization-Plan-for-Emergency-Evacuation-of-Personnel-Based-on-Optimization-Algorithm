# -*- coding: utf-8 -*-
import geatpy as ea
import numpy as np
from scipy.io import loadmat
m = loadmat("xingguo.mat")
B=3     # 自行设定 可控制变量
Y=m['depot'][0][0]
S=m['ND'][0][0]
T=m['NS'][0][0]
N=m['N'][0][0]
Dij=m['path']       # 编号规则 从0开始编号，编号顺序 S~T~Y
L=m['DSeparate'].reshape(S)
U=m['SSeparate'].reshape(T)
numOfGenetic=L.sum()
Nind=100

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

    # def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
    #     referenceObjV  = np.array([[23]])
    #     return referenceObjV

    def aimFunc(self, pop):  # 目标函数
        SInTurns = pop.Phen[:, :numOfGenetic].astype(int)
        TInTurns = pop.Phen[:, numOfGenetic:2 * numOfGenetic].astype(int)
        Turns = pop.Phen[:, 2 * numOfGenetic:].astype(int)
        # TInTurns = pop.Phen[:, numOfGenetic:2*numOfGenetic].reshape([Nind, numOfGenetic]).astype(int)
        # SInTurns = pop.Phen[:, :numOfGenetic].reshape([Nind, numOfGenetic]).astype(int)
        # Turns=pop.Phen[:, 2*numOfGenetic:].reshape([Nind, B-1]).astype(int)      #使用X[:,i]切片第i个节点

        TmaxMin=np.zeros((Nind, 1), dtype=np.int)
        for i in range(Nind):
            SInTurn=SInTurns[i]
            TInTurn=TInTurns[i]
            Turn=Turns[i]

            if Turn[0]>Turn[1]:
                Turn[0],Turn[1]=Turn[1],Turn[0]

            #按三辆车切片
            SInTurnOfCar = [SInTurn[:Turn[0]+1],SInTurn[Turn[0]+1:Turn[1]+1],SInTurn[Turn[1]+1:]]
            TInTurnOfCar = [TInTurn[:Turn[0]+1],TInTurn[Turn[0]+1:Turn[1]+1],TInTurn[Turn[1]+1:]]

            # SInTurnOfCar1 = SInTurn[:Turn[0]]
            # TInTurnOfCar1 = TInTurn[:Turn[0]]
            # SInTurnOfCar2 = SInTurn[Turn[0]:Turn[1]]
            # TInTurnOfCar2 = TInTurn[Turn[0]:Turn[1]]
            # SInTurnOfCar3 = SInTurn[Turn[1]:]
            # TInTurnOfCar3 = TInTurn[Turn[1]:]

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
            # pop.CV=np.hstack([CV1,CV2,CV3,CV4,CV5,CV7,CV8,CV9,CV10,CV11,CV12,CV13])



        # Yijb = pop.Phen[:,:N*N*B].reshape([Nind, N, N, B]).astype(int)  # 得到决策变量矩阵Xijb
        # Xijr = pop.Phen[:,N*N*B:].reshape([Nind, N, N, R]).astype(int)  # 得到决策变量矩阵Xijr
        # l = list(range(Y)) + list(range(Y + S, N))
        #
        # # 目标函数
        # TmaxMin = np.zeros((Nind, B), dtype=np.int)  # b      # 40*b(40*3)
        # for b in range(B):
        #     for i in range(Y):
        #         for j in range(Y,Y+S):
        #             TmaxMin[:, [b]] += Dij[i][j] * Yijb[:, [i], [j], [b]]
        #     for i in range(S):
        #         for j in l:
        #             TmaxMin[:, [b]] += Dij[i][j] * Yijb[:, [i], [j], [b]]
        #     for i in range(N):
        #         for j in range(Y,Y+S):
        #             TmaxMin[:, [b]] += Dij[i][j] * Yijb[:, [i], [j], [b]]
        #
        # #PPT式1
        # CV1=abs(Xijr.sum(axis=3)-Yijb.sum(axis=3)).sum(axis=(1,2)).reshape(Nind,1)
        #
        # # PPT式2
        # preCV2 =np.stack([np.array(L) for _ in range(Nind)], axis=0)
        # preCV2[:, :] -= Yijb.sum(axis=(2,3)).reshape(Nind,N)[:,Y:Y+S]
        # CV2 = np.zeros((Nind, 1), dtype=np.int)
        # for q in range(Nind):
        #     for i in range(S):
        #         CV2[q] += abs(preCV2[q][i])
        #
        #
        # # PPT式3
        # preCV3 =np.stack([np.array(U) for _ in range(Nind)], axis=0)
        # preCV3[:, :] -= Yijb.sum(axis=(1,3)).reshape(Nind,N)[:,Y+S:N]
        # CV3 = np.zeros((Nind, 1), dtype=np.int)
        # for q in range(Nind):
        #     for j in range(T):
        #         if preCV3[q][j] < 0:
        #             CV3[q] -= preCV3[q][j]
        #
        # # PPT式4
        # preCV4 =np.stack([np.array(L) for _ in range(Nind)], axis=0)
        # preCV4[:, :] -= Xijr.sum(axis=(2,3)).reshape(Nind,N)[:,Y:Y+S]
        # CV4 = np.zeros((Nind, 1), dtype=np.int)
        # for q in range(Nind):
        #     for i in range(S):
        #         CV4[q] += abs(preCV4[q][i])
        #
        # # PPT式5
        # preCV5 =np.stack([np.array(U) for _ in range(Nind)], axis=0)
        # preCV5[:, :] -= Xijr.sum(axis=(1,3)).reshape(Nind,N)[:,Y+S:N]
        # CV5 = np.zeros((Nind, 1), dtype=np.int)
        # for q in range(Nind):
        #     for j in range(T):
        #         if preCV5[q][j] < 0:
        #             CV5[q] -= preCV5[q][j]
        #
        # # PPT式6 有问题 待修改
        # # CV6 = np.zeros((Nind, 1), dtype=np.int)
        # # for n in range(Nind):
        # #     for r in range(R-1):
        # #         tmpSum=0
        # #         for i in range(S):
        # #             for j in range(T):
        # #                 tmpSum+=Xijr[n][i+Y][j+Y+S][r]-Xijr[n][i+Y][j+Y+S][r+1]
        # #         if tmpSum<0:
        # #             CV6[n]-=tmpSum
        #
        # #纸式1
        # CV7 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for j in range(S):
        #         for r in range(R-1):
        #             tmpSum=0
        #             for i in l:
        #                 tmpSum += Xijr[n][i][j + Y][r] - Xijr[n][j + Y][i][r + 1]
        #             # if tmpSum!=0:
        #             CV7[n]+=abs(tmpSum)
        #
        # #纸式2
        # CV8 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for j in range(T):
        #         for r in range(R-1):
        #             tmpSum=0
        #             for i in range(S):
        #                 tmpSum += Xijr[n][i+Y][j + Y+S][r] - Xijr[n][j + Y+S][i+Y][r + 1]
        #             if tmpSum<0:
        #                 CV8[n]-=tmpSum
        #
        # #纸式3
        # CV9 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for r in range(R):
        #         tmpSum=0
        #         for i in range(S):
        #             for j in range(T):
        #                 tmpSum+=Xijr[n][i+Y][j+Y+S][r]
        #         if tmpSum>B:
        #             CV9[n]+=tmpSum-B
        #
        # # 纸式4
        # CV10 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for b in range(B):
        #         tmpSum = 0
        #         for i in range(S):
        #             for j in range(T):
        #                 tmpSum += Yijb[n][i + Y][j + Y + S][b]
        #         if tmpSum > R:
        #             CV10[n] += tmpSum - R
        #
        # # 纸式5
        # CV11 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for j in range(S):
        #         for i in l:
        #             CV11[n]+=abs(Xijr[n][i][j+Y][R-1])
        #
        # # 纸式6
        # CV12 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for j in range(S):
        #         for b in range(B):
        #             tmpSum=0
        #             for i in l:
        #                 tmpSum+=Yijb[n][i][j+Y][b]-Yijb[n][j+Y][i][b]
        #             # if tmpSum!=0:
        #             CV12+=abs(tmpSum)
        #
        # # 纸式7
        # CV13 = np.zeros((Nind, 1), dtype=np.int)
        # for n in range(Nind):
        #     for j in range(T):
        #         for b in range(B):
        #             tmpSum=0
        #             for i in range(S):
        #                 tmpSum += Yijb[n][i+Y][j + Y+S][b] - Yijb[n][j + Y+S][i+Y][b]
        #             if tmpSum<0 or tmpSum>1:
        #                 CV13[n]+=abs(tmpSum)
        #
        # pop.ObjV = np.max(TmaxMin, axis=1).reshape(Nind, 1)  # 计算目标函数值，赋值给pop种群对象的ObjV属性
        # pop.CV=np.hstack([CV1,CV2,CV3,CV4,CV5,CV7,CV8,CV9,CV10,CV11,CV12,CV13])

        # print(pop.CV.sum()//NIND)

if __name__ == '__main__':
    # """===============================加载原始数据============================"""
    # # global m
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
    # myAlgorithm = ea.soea_SEGA_templet(problem, population)  # 实例化一个算法模板对象

    # myAlgorithm = ea.soea_DE_rand_1_L_templet(problem, population)  # 实例化一个算法模板对象
    # myAlgorithm = ea.soea_DE_currentToBest_1_bin_templet(problem, population)  # 实例化一个算法模板对象
    # myAlgorithm.mutOper.F = 0.7  # 差分进化中的参数F
    # myAlgorithm.recOper.XOVR = 0.7  # 重组概率

    myAlgorithm = ea.soea_psy_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    myAlgorithm.recOper = ea.Xovdp(XOVR=0.9, Parallel=True)  # 设置交叉算子
    myAlgorithm.mutOper = ea.Mutinv(Pm=0.5, Parallel=True)  # 设置变异算子

    myAlgorithm.MAXGEN = 2000  # 最大进化代数
    myAlgorithm.logTras = 1  # 设置每隔多少代记录日志，若设置成0则表示不记录日志
    myAlgorithm.verbose = True  # 设置是否打印输出日志信息
    myAlgorithm.drawing = 1  # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）
    """===========================根据先验知识创建先知种群========================"""
    # prophetChrom = np.zeros([NIND,N * N * (B+R)],dtype=np.int)

    # tmpProp1=np.zeros([N ,N ,B],dtype=np.int)
    # tmpProp1[0][1][0]=tmpProp1[1][4][0]=tmpProp1[4][3][0]=tmpProp1[3][5][0]=tmpProp1[0][2][1]=tmpProp1[2][4][1]=tmpProp1[4][3][1]=tmpProp1[3][5][1]=tmpProp1[0][2][2]=tmpProp1[2][6][2]=tmpProp1[6][2][2]=tmpProp1[2][5][2]=tmpProp1[5][3][2]=tmpProp1[3][5][2]=1
    # tmpProp2 = np.zeros([N, N, R], dtype=np.int)
    # tmpProp2[0][1][0]=tmpProp2[1][4][1]=tmpProp2[2][4][1]=tmpProp2[2][6][1]=tmpProp2[6][2][2]=tmpProp2[2][5][3]=tmpProp2[5][3][4]=tmpProp2[3][5][5]=1
    # tmpProp2[0][2][0]=tmpProp2[4][3][2]=tmpProp2[3][5][3]=2
    # tmpProp=np.append(tmpProp1,tmpProp2)
    # prophetChrom = np.stack([np.array(tmpProp) for _ in range(Nind)], axis=0)
    #
    # prophetPop=ea.Population(Encoding, Field, NIND,prophetChrom)
    # myAlgorithm.call_aimFunc(prophetPop)  # 计算先知种群的目标函数值及约束（假如有约束）
    """==========================调用算法模板进行种群进化========================"""
    # [BestIndi, population] = myAlgorithm.run(prophetPop)  # 执行算法模板，得到最优个体以及最后一代种群 # 先验知识版本
    [BestIndi, population] = myAlgorithm.run()  # 执行算法模板，得到最优个体以及最后一代种群
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