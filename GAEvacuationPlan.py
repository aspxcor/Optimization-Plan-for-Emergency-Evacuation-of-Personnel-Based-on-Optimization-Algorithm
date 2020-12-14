# -*- coding: utf-8 -*-
import geatpy as ea  # import geatpy
import numpy as np
B=3
R=3
S=3
T=3
d=[[6,7,8],
   [10,9,2],
   [6,3,7]]
dStart=[7,4,9]
L=[1,3,3]
U=[4,4,1]
Nind=40
# t=[0,0,0]
# Xijbr=np.zeros((3,3,3,3), dtype=np.int)
# tMax=0

class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 81  # 初始化Dim（决策变量维数）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [0] * Dim # 决策变量下界
        ub = [1]  * Dim# 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)
    def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
        referenceObjV  = np.array([[23]])
        return referenceObjV

    def aimFunc(self, pop):  # 目标函数
        Xijbr = pop.Phen.reshape([40,B,R,S,T])  # 得到决策变量矩阵

        # 式5
        preCV6 = Xijbr.sum(axis=(1, 2)) - np.ones((40,3, 3), dtype=np.int)  # b*r
        CV6=np.zeros((40,1), dtype=np.int)
        for q in range(40):
            for b in range(B):
                for r in range(R):
                    if preCV6[q][b][r]>0:
                        # cnt+=1
                        CV6[q] += preCV6[q][b][r]

        # #式3
        Ttobr=np.zeros((40,3,3), dtype=np.int)          # b*r
        for b in range(B):
            for r in range(R):
                for i in range(S):
                    for j in range(T):
                        Ttobr[:,[b],[r]]+=d[i][j]*Xijbr[:,[i],[j],[b],[r]]

        #式4
        TbackbrMin=np.zeros((Nind, B, R-1), dtype=np.int)       # b*(r-1)
        for b in range(B):
            for r in range(R-1):
                TempTable = np.zeros((40, S, T), dtype=np.int)
                for i in range(S):
                    for j in range(T):
                        TempTable[:,[i],[j]]=d[i][j]*(Xijbr[:,:,[j],[b],[r]].sum(axis=1)+Xijbr[:,[i],:,[b],[r+1]].reshape(40,3).sum(axis=1).reshape(40,1)-np.ones((40,1), dtype=np.int))
                for q in range(Nind):
                    TbackbrMin[q][b][r]=TempTable[q].max()




        #式2
        TmaxMin=Ttobr.sum(axis=(2))+TbackbrMin.sum(axis=(2))        #40*b(40*3)
        for i in range(S):
            for j in range(T):
                TmaxMin+=dStart[i]*Xijbr[:,[i],[j],:,[0]].reshape(40,3)

        #式6

        preCV3 = np.zeros((40, 3, 3), dtype=np.int)  # b*(r-1)
        for b in range(B):
            for r in range(R - 1):
                for i in range(S):
                    for j in range(T):
                        preCV3[:, [b], [r]] += Xijbr[:, [i], [j], [b], [r + 1]] - Xijbr[:, [i], [j], [b], [r]]
        CV3 = np.zeros((40, 1), dtype=np.int)
        for q in range(40):
            # cnt=0
            for b in range(B):
                for r in range(R):
                    if preCV3[q][b][r]>0:
                        CV3[q]+=preCV3[q][b][r]

        #式7
        preCV4 =np.stack([np.array(L) for _ in range(40)], axis=0)
        preCV4[:, :] -= Xijbr.sum(axis=(2, 3, 4)).reshape(40, 3)
        CV4 = np.zeros((40, 1), dtype=np.int)
        for q in range(40):
            for i in range(S):
                if preCV4[q][i] > 0:
                    CV4[q] += preCV4[q][i]

        #式8
        preCV5 = np.stack([np.array(U) for _ in range(40)], axis=0)
        preCV5[:, :] -= Xijbr.sum(axis=(1, 3, 4)).reshape(40, 3)
        CV5 = np.zeros((40, 1), dtype=np.int)
        for q in range(40):
            for j in range(T):
                if preCV5[q][j] < 0:
                    CV5[q] -= preCV5[q][j]

        pop.ObjV = np.max(TmaxMin, axis=1).reshape(40, 1)  # 计算目标函数值，赋值给pop种群对象的ObjV属性
        pop.CV=np.hstack([CV3,
                          CV4,
                          CV5,
                          CV6])


if __name__ == '__main__':
    """===============================实例化问题对象==========================="""
    problem = MyProblem()  # 生成问题对象
    """=================================种群设置=============================="""
    Encoding = 'BG'  # 编码方式
    NIND = 40  # 种群规模
    Field = ea.crtfld(Encoding, problem.varTypes, problem.ranges, problem.borders)  # 创建区域描述器
    population = ea.Population(Encoding, Field, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    myAlgorithm = ea.soea_SEGA_templet(problem, population)  # 实例化一个算法模板对象
    myAlgorithm.MAXGEN = 5000  # 最大进化代数
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
        print('[验证各个约束条件]')
        print('验证式8：U=[4,4,1],Xijbr(sum)=',Xijbr.sum(axis=(0,2,3)))
        print('验证式7：L=[1,3,3],Xijbr(sum)=',Xijbr.sum(axis=(1,2,3)))
        print('验证式6：左侧=', Xijbr.sum(axis=(0,1))[:,[0,1]],'右侧=', Xijbr.sum(axis=(0,1))[:,[1,2]])
        print('验证式5：左侧=', Xijbr.sum(axis=(0,1)))
        Ttobr = np.ones((3, 3), dtype=np.int)
        for b in range(B):
            for r in range(R):
                Ttobr[b, r] = (d * Xijbr[:, :, b, r]).sum(axis=(0,1))
        print('Ttobr=',Ttobr)
    else:
        print('没找到可行解。')