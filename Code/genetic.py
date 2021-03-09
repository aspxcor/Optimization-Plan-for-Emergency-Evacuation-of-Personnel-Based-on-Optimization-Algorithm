# -*- coding: utf-8 -*-
import geatpy as ea  # import geatpy
import numpy as np
import random
B=3
R=3
Y=1
S=3
T=3
N=Y+S+T
# 编号规则 A表示边 稍后补充A和Dij的自动生成算法
# 从0开始编号，编号顺序 Y~S~T
Dij=np.array([[0,7,4,9,0,0,0],
              [7,0,0,0,6,7,8],
              [4,0,0,0,10,9,2],
              [9,0,0,0,6,3,7],
              [0,6,10,6,0,0,0],
              [0,7,9,3,0,0,0],
              [0,8,2,7,0,0,0]])
# d=np.array([[6,7,8],
#    [10,9,2],
#    [6,3,7]])
# dStart=np.array([7,4,9])
L=np.array([1,3,3])
U=np.array([4,4,1])
Nind=2000

class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        # Dim = B*R*S*T  # 初始化Dim（决策变量维数）
        Dim = N * N * (S + T)  # 初始化Dim（决策变量维数）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [0] * Dim # 决策变量下界
        ub = [3]  * Dim# 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)
    def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
        referenceObjV  = np.array([[23]])
        return referenceObjV

    def aimFunc(self, pop):  # 目标函数
        Yijb = pop.Phen[:,:N*N*B].reshape([Nind, N, N, B]).astype(int)  # 得到决策变量矩阵Xijb
        Xijr = pop.Phen[:,N*N*B:].reshape([Nind, N, N, R]).astype(int)  # 得到决策变量矩阵Xijr

        # 目标函数
        TmaxMin = np.zeros((Nind, B), dtype=np.int)  # b      # 40*b(40*3)
        for b in range(B):
            for i in range(N):
                for j in range(N):
                    TmaxMin[:, [b]] += Dij[i][j] * Yijb[:, [i], [j], [b]]

        #PPT式1
        preCV1=Xijr.sum(axis=3)-Yijb.sum(axis=3)   #i*j
        CV1=np.zeros((Nind,1),dtype=np.int)
        for q in range(Nind):
            for s in range(S):
                for t in range(T):
                    if preCV1[q][s+Y][t+Y+T]!=0:
                        CV1[q]+=preCV1[q][s+Y][t+Y+T]

        # PPT式2
        CV2 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for i in range(S):
                tmpSum=0
                for j in range(T):
                    for b in range(B):
                        tmpSum+=Yijb[[n],[i+Y],[j+Y+S],[b]]
                if tmpSum<L[i]:
                    CV2[n]+=L[i]-tmpSum

        # PPT式3
        CV3 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(T):
                tmpSum=0
                for i in range(S):
                    for b in range(B):
                        tmpSum+=Yijb[[n],[i+Y],[j+Y+S],[b]]
                if tmpSum>U[j]:
                    CV3[n]+=tmpSum-U[j]

        # PPT式4
        CV4 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for i in range(S):
                tmpSum=0
                for j in range(T):
                    for r in range(R):
                        tmpSum+=Xijr[[n],[i+Y],[j+Y+S],[r]]
                if tmpSum<L[i]:
                    CV4[n]+=L[i]-tmpSum

        # PPT式5
        CV5 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(T):
                tmpSum=0
                for i in range(S):
                    for r in range(R):
                        tmpSum+=Xijr[[n],[i+Y],[j+Y+S],[r]]
                if tmpSum>U[j]:
                    CV5[n]+=tmpSum-U[j]

        # PPT式6
        CV6 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for r in range(R-1):
                tmpSum=0
                for i in range(S):
                    for j in range(T):
                        tmpSum+=Xijr[n][i+Y][j+Y+S][r]-Xijr[n][i+Y][j+Y+S][r+1]
                if tmpSum<0:
                    CV6[n]-=tmpSum

        #纸式1
        CV7 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(S):
                for r in range(R-1):
                    tmpSum=0
                    for i in range(N):
                        if Dij[i][j+Y]>0:
                            tmpSum+=Xijr[n][i][j+Y][r]
                    for k in range(N):
                        if Dij[j+Y][k]>0:
                            tmpSum-=Xijr[n][j+Y][k][r+1]
                    if tmpSum!=0:
                        CV7[n]+=abs(tmpSum)

        #纸式2
        CV8 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(T):
                for r in range(R-1):
                    tmpSum=0
                    for i in range(N):
                        if Dij[i][j+Y+S]>0:
                            tmpSum+=Xijr[n][i][j+Y+S][r]
                    for k in range(N):
                        if Dij[j+Y+S][k]>0:
                            tmpSum-=Xijr[n][j+Y+S][k][r+1]
                    if tmpSum<0:
                        CV8[n]-=tmpSum

        #纸式3
        CV9 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for r in range(R):
                tmpSum=0
                for i in range(S):
                    for j in range(T):
                        tmpSum+=Xijr[n][i+Y][j+Y+S][r]
                if tmpSum>B:
                    CV9[n]+=tmpSum-B

        # 纸式4
        CV10 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for b in range(B):
                tmpSum = 0
                for i in range(S):
                    for j in range(T):
                        tmpSum += Yijb[n][i + Y][j + Y + S][b]
                if tmpSum > R:
                    CV10[n] += tmpSum - R

        # 纸式5
        CV11 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(S):
                l=list(range(Y))+list(range(Y+S,N))
                for i in l:
                    if Xijr[n][i][j+Y][R-1]!=0:
                        CV11[n]+=abs(Xijr[n][i][j+Y][R-1])

        # 纸式6
        CV12 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(S):
                for b in range(B):
                    tmpSum=0
                    for i in range(N):
                        if Dij[i][j+Y]>0:
                            tmpSum+=Yijb[n][i][j+Y][b]
                    for k in range(N):
                        if Dij[j+Y][k] > 0:
                            tmpSum-=Yijb[n][j+Y][k][b]
                    if tmpSum!=0:
                        CV12+=abs(tmpSum)

        # 纸式7
        CV13 = np.zeros((Nind, 1), dtype=np.int)
        for n in range(Nind):
            for j in range(T):
                for b in range(B):
                    for i in range(Y,Y+S):
                        for k in range(Y,Y+S):
                            if Yijb[n][i][j][b]-Yijb[n][j][k][b]<0 or Yijb[n][i][j][b]-Yijb[n][j][k][b]>1:
                                CV13[n]+=abs(Yijb[n][i][j][b]-Yijb[n][j][k][b])

        pop.ObjV = np.max(TmaxMin, axis=1).reshape(Nind, 1)  # 计算目标函数值，赋值给pop种群对象的ObjV属性
        pop.CV=np.hstack([CV1,CV2,CV3,CV4,CV5,CV6,CV7,CV8,CV9,CV10,CV11,CV12,CV13])


def initData():
    L = np.ones(3)
    U = np.zeros(3)     #初始化
    while (L.sum() > U.sum()):      #防止生成的数据本身无法满足救援条件
        B = random.randint(2, 5)
        R = random.randint(2, 5)
        S = random.randint(2, 5)
        T = random.randint(2, 5)
        d = np.random.randint(1, 11, size=(S, T))
        dStart = np.random.randint(1, 11, size=S)
        L = np.random.randint(1, 6, size=S)
        U = np.random.randint(1, 6, size=T)
    print('本次基因长度为 %d ,随机生成的变量值为：'%(S*T*B*R))
    print(' |  S  |  T  |  B  |  R  | ')
    print('---------------------------')
    print(" | ", S, " | ", T, " | ", B, " | ", R, " | ")
    print('Source 与 Sink 间距离矩阵')
    print(d)
    print('Single Yard 与各个 Source 间距离矩阵')
    print(dStart)
    print('%d 个 Source 的待救援者人数分别为' % S)
    print(L)
    print('%d 个 Sink 的最大容量分别为' % T)
    print(U)

if __name__ == '__main__':
    """==============================随机生成原始数据=========================="""
    # initData()
    """===============================实例化问题对象==========================="""
    problem = MyProblem()  # 生成问题对象
    """=================================种群设置=============================="""
    Encoding = 'RI'  # 编码方式
    NIND = Nind  # 种群规模
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    myAlgorithm = ea.soea_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    myAlgorithm.MAXGEN = 300  # 最大进化代数
    myAlgorithm.recOper = ea.Xovdp(XOVR = 0.8,Parallel=True) # 设置交叉算子
    myAlgorithm.mutOper = ea.Mutinv(Pm =0.95,Parallel=True)  # 设置变异算子
    myAlgorithm.logTras = 1  # 设置每隔多少代记录日志，若设置成0则表示不记录日志
    myAlgorithm.verbose = True  # 设置是否打印输出日志信息
    myAlgorithm.drawing = 1  # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；3：绘制决策空间过程动画）
    """==========================调用算法模板进行种群进化========================"""
    # prophetChrom=np.array([[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0]])
    # prophetPop=ea.Population(Encoding, Field, 1,prophetChrom,)
    # [BestIndi, population] = myAlgorithm.run(prophetPop)  # 执行算法模板，得到最优个体以及最后一代种群
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
        print('最优的i,j,b,r值为：')
        print(' |  b  |  r  |  i  |  j  | ')
        print('---------------------------')
        Xijbr=BestIndi.Phen.reshape(3,3,3,3)
        for b in range(B):
            for r in range(R):
                for i in range(S):
                    for j in range(T):
                        if(Xijbr[i][j][b][r]==1):
                            print(" | ",b+1," | ",r+1," | ",i+1," | ",j+1," | ")
        # print('[验证各个约束条件]')
        # print('验证式8：U=[4,4,1],Xijbr(sum)=',Xijbr.sum(axis=(0,2,3)))
        # print('验证式7：L=[1,3,3],Xijbr(sum)=',Xijbr.sum(axis=(1,2,3)))
        # print('验证式6：左侧=', Xijbr.sum(axis=(0,1))[:,[0,1]],'右侧=', Xijbr.sum(axis=(0,1))[:,[1,2]])
        # print('验证式5：左侧=', Xijbr.sum(axis=(0,1)))
        # Ttobr = np.ones((B, R), dtype=np.int)
        # for b in range(B):
        #     for r in range(R):
        #         Ttobr[b, r] = (d * Xijbr[:, :, b, r]).sum(axis=(0,1))
        # print('Ttobr=',Ttobr)
    else:
        print('没找到可行解。')