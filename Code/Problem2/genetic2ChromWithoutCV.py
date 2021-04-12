# -*- coding: utf-8 -*-
# 本程序主要思想：
#   通过染色体编码格式控制交换以后的前两条染色体编码一定合法
#   不引入CV矩阵进行合法性检查
#   不引入先验知识
#   插板位置依靠遗传阶段的决策算法
#   遗传过程中控制的最优变量为所有车辆总救援时间之和
"""
soea_psy_SEGA_templet : class - Polysomy Strengthen Elitist GA templet(增强精英保留的多染色体遗传算法模板)
算法描述:
本模板实现的是增强精英保留的遗传算法。算法流程如下：
1) 根据编码规则初始化N个个体的种群。
2) 若满足停止条件则停止，否则继续执行。
3) 对当前种群进行统计分析，比如记录其最优个体、平均适应度等等。
4) 独立地从当前种群中选取N个母体。
5) 独立地对这N个母体进行交叉操作。
6) 独立地对这N个交叉后的个体进行变异。
7) 将父代种群和交叉变异得到的种群进行合并，得到规模为2N的种群。
8) 从合并的种群中根据选择算法选择出N个个体，得到新一代种群。
9) 回到第2步。
该算法宜设置较大的交叉和变异概率，否则生成的新一代种群中会有越来越多的重复个体。

"""
import geatpy as ea
import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import Counter

class genetic2ChromWithoutCVProblem(ea.Problem):  # 继承Problem父类
    def __init__(self,B, Y, S, T, N, Dij, L, U, numOfGenetic, Nind, SizeOfMap, KRefAns,averageDistanceYS,totalAverageDistanceST,totalAverageDistanceTS):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数） 也即优化目标的数目
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 2*numOfGenetic  # 初始化Dim（决策变量维数）  #注意 插板时两两一组
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [0] * numOfGenetic + [0] * numOfGenetic# 决策变量下界
        ub = [numOfGenetic-1] * numOfGenetic + [U.sum()-1] * numOfGenetic        # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）

        self.B = B
        self.Y = Y
        self.S = S
        self.T = T
        self.N = N
        self.Dij = Dij
        self.L = L
        self.U = U
        self.averageDistanceYS = averageDistanceYS
        self.totalAverageDistanceST = totalAverageDistanceST
        self.totalAverageDistanceTS = totalAverageDistanceTS
        self.numOfGenetic = numOfGenetic
        self.Nind = Nind
        self.SizeOfMap = SizeOfMap
        self.KRefAns = KRefAns

        self.STrans = []
        self.TTrans = []
        for i in range(S):
            self.STrans += L[i] * [i]
        for i in range(T):
            self.TTrans += U[i] * [i + S]

        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)        # 调用父类构造方法完成实例化

    def calReferObjV(self):  # 设定目标数参考值（本问题目标函数参考值设定为理论最优值）
        refAns=self.averageDistanceYS+int(round(self.numOfGenetic/self.B))*self.totalAverageDistanceST+(int(round(self.numOfGenetic/self.B))-1)*self.totalAverageDistanceTS
        referenceObjV  = np.array([[int(refAns*self.KRefAns)]])
        return referenceObjV

    # def aimFunc(self,pop):
    #     Vars = pop.Phen  # 得到决策变量矩阵
    #     args = [Vars,self.B,self.Y,self.S,self.T,self.N,self.Dij,self.L,self.U,self.averageDistanceYS,self.totalAverageDistanceST,self.totalAverageDistanceTS,self.numOfGenetic,self.Nind,self.SizeOfMap,self.KRefAns,self.STrans,self.TTrans]
    #     pop.ObjV = np.array(list(futures.map(subAimFunc, args)))  # 调用SCOOP的map函数进行分布式计算，并构造种群所有个体的目标函数值矩阵ObjV

    def aimFunc(self, pop):  # 目标函数
        # 将染色体解码为两部分S T
        SInTurns = pop.Phen[:, :self.numOfGenetic].astype(int)
        TInTurns = pop.Phen[:, self.numOfGenetic:2 * self.numOfGenetic].astype(int)

        # 将解码后的染色体翻译为不同编号的地理位置信息（从逻辑编号到物理编号）
        for t in range(self.Nind):
            for i in range(self.numOfGenetic):
                SInTurns[t][i] = self.STrans[SInTurns[t][i]]
                TInTurns[t][i] = self.TTrans[TInTurns[t][i]]

        # 目标函数数组
        TmaxMin=np.zeros((SInTurns.shape[0], 1), dtype=np.int)
        DijFirst=self.Dij[S+T][:S].sum()

        # 按Nind进行轮询
        for i in range(SInTurns.shape[0]):
            SInTurn=SInTurns[i]
            TInTurn=TInTurns[i]

            #按B辆车辆进行切片 尽可能平均即可
            # SInTurnOfCar = [SInTurn[:Turn[0] + 1]] + [SInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [SInTurn[Turn[B-2] + 1:]]
            # TInTurnOfCar = [TInTurn[:Turn[0] + 1]] + [TInTurn[Turn[_] + 1:Turn[_ + 1] + 1] for _ in range(0,B-2)] + [TInTurn[Turn[B-2] + 1:]]

            # averageDistanceST = (sum([Dij[SInTurn[_]][TInTurn[_]] for _ in range(numOfGenetic)])) // numOfGenetic
            # averageDistanceTS = (sum([Dij[TInTurn[_]][SInTurn[_+1]] for _ in range(numOfGenetic-1)])) // numOfGenetic
            # refObjV=int(round(numOfGenetic/B))*averageDistanceST+(int(round(numOfGenetic/B))-1)*averageDistanceTS+averageDistanceYS

            sumFromSToT = 0
            sumFromTToS = 0
            for j in range(self.numOfGenetic):
                sumFromSToT += Dij[SInTurn[j]][TInTurn[j]]
            for j in range(self.numOfGenetic - 1):
                sumFromTToS += Dij[TInTurn[j]][SInTurn[j + 1]]
            avgFromTToS = sumFromTToS / (self.numOfGenetic - 1)
            avgTime = round((DijFirst + sumFromSToT + avgFromTToS * (self.numOfGenetic - B)) / B)

            blockCount=0
            blockList=[]
            while blockCount<self.B-1:
                blockStartPosition=0 if blockCount==0 else blockList[blockCount-1]+1
                #防止blockStartPosition=numOfGenetic的特别处理
                if blockStartPosition==self.numOfGenetic:
                    if blockList[-2]!=self.numOfGenetic-3:
                        blockList[-1]=self.numOfGenetic-3
                    else:
                        blockList[-2]=blockList[-3]+1
                        blockList[-1] = self.numOfGenetic - 3
                    blockList.append(self.numOfGenetic-2)
                    blockCount+=1
                    continue
                # print("blockCount=", blockCount,"blockStartPosition=",blockStartPosition)
                tmpTurnTime=Dij[S+T][SInTurn[blockStartPosition]]
                tmpTurnTime+=Dij[SInTurn[blockStartPosition]][TInTurn[blockStartPosition]]
                if tmpTurnTime>avgTime:
                    blockCount+=1
                    blockList.append(blockStartPosition)
                    # continue
                else:
                    isFindFlag=False
                    for t in range(blockStartPosition+1,self.numOfGenetic):
                        tmpTurnTime+=Dij[TInTurn[t-1]][SInTurn[t]]
                        tmpTurnTime+=Dij[SInTurn[t]][TInTurn[t]]
                        if tmpTurnTime>avgTime:
                            blockCount += 1
                            isFindFlag=True
                            # blockList.append(t - 1)
                            if tmpTurnTime-avgTime>avgTime-tmpTurnTime+Dij[SInTurn[t]][TInTurn[t]]+Dij[TInTurn[t-1]][SInTurn[t]]:
                                blockList.append(t-1)
                            else:
                                blockList.append(t)
                            break
                    if isFindFlag is False:
                        blockCount+=1
                        if blockStartPosition!=self.numOfGenetic-1:
                            blockList.append(blockStartPosition)
                        else:
                            blockList[-1]-=1
                            blockList.append(self.numOfGenetic-2)
                            # print("Error,blockStartPosition==self.numOfGenetic-1")

            #blockList查重 防止出现重复元素
            while len(blockList)-len(set(blockList)):
                reSee=[key for key,value in dict(Counter(blockList)).items() if value > 1]
                for pRe in reSee:
                    blockList[blockList.index(pRe)]-=1

            if blockList[self.B - 2] > self.numOfGenetic - 2 and blockList[self.B - 3] < self.numOfGenetic - 2:
                blockList[self.B - 2] = self.numOfGenetic - 2
            elif blockList[self.B - 2] > self.numOfGenetic - 2 and blockList[self.B - 3] > self.numOfGenetic - 2:
                print("Error,Both two of the end in the blockList is upper than self.numOfGenetic-2")
            # try:
            #     if blockList[self.B-2]>self.numOfGenetic-2 and blockList[self.B-3]<self.numOfGenetic-2:
            #         blockList[self.B - 2] = self.numOfGenetic - 2
            #     elif blockList[self.B-2]>self.numOfGenetic-2 and blockList[self.B-3]>self.numOfGenetic-2:
            #         print("Error,Both two of the end in the blockList is upper than self.numOfGenetic-2")
            # except IndexError:
            #     print("IndexError,blockList=",blockList)
            #     print("blockCount=",blockCount)


            # tmpBlock1 = [_ * self.numOfGenetic // self.B for _ in range(1, self.B)]
            SInTurnOfCar1 = [SInTurn[:blockList[0] + 1]] + [SInTurn[blockList[_] + 1:blockList[_ + 1] + 1] for _ in range(0,self.B-2)] + [SInTurn[blockList[self.B-2] + 1:]]
            TInTurnOfCar1 = [TInTurn[:blockList[0] + 1]] + [TInTurn[blockList[_] + 1:blockList[_ + 1] + 1] for _ in range(0,self.B-2)] + [TInTurn[blockList[self.B-2] + 1:]]

            # tmpBlock2 = [_ * self.numOfGenetic // self.B + 1 for _ in range(1, self.B)]
            # SInTurnOfCar2 = [SInTurn[:tmpBlock2[0] + 1]] + [SInTurn[tmpBlock2[_] + 1:tmpBlock2[_ + 1] + 1] for _ in range(0, self.B - 2)] + [SInTurn[tmpBlock2[self.B - 2] + 1:]]
            # TInTurnOfCar2 = [TInTurn[:tmpBlock2[0] + 1]] + [TInTurn[tmpBlock2[_] + 1:tmpBlock2[_ + 1] + 1] for _ in range(0, self.B - 2)] + [TInTurn[tmpBlock2[self.B - 2] + 1:]]
            #
            # tmpBlock3 = [_ * self.numOfGenetic // self.B - 1 for _ in range(1, self.B)]
            # SInTurnOfCar3 = [SInTurn[:tmpBlock3[0] + 1]] + [SInTurn[tmpBlock3[_] + 1:tmpBlock3[_ + 1] + 1] for _ in range(0, self.B - 2)] + [SInTurn[tmpBlock3[self.B - 2] + 1:]]
            # TInTurnOfCar3 = [TInTurn[:tmpBlock3[0] + 1]] + [TInTurn[tmpBlock3[_] + 1:tmpBlock3[_ + 1] + 1] for _ in range(0, self.B - 2)] + [TInTurn[tmpBlock3[self.B - 2] + 1:]]

            time1=np.zeros(self.B,dtype=int)
            for carCurrent in range(self.B):
                try:
                    tmpTime=self.Dij[self.N-1][SInTurnOfCar1[carCurrent][0]]
                except IndexError:
                    print("IndexError,carCurrent=",carCurrent,"SInTurnOfCar1=",SInTurnOfCar1)
                    print(blockList)
                tmpTime += self.Dij[SInTurnOfCar1[carCurrent][0]][TInTurnOfCar1[carCurrent][0]]
                for j in range(1,len(SInTurnOfCar1[carCurrent])):
                    tmpTime += self.Dij[TInTurnOfCar1[carCurrent][j-1]][SInTurnOfCar1[carCurrent][j]]
                    tmpTime += self.Dij[SInTurnOfCar1[carCurrent][j]][TInTurnOfCar1[carCurrent][j]]
                time1[carCurrent]=tmpTime

            TmaxMin[i] = time1.max()

            # time2 = np.zeros(self.B, dtype=int)
            # for carCurrent in range(self.B):
            #     tmpTime = self.Dij[self.N - 1][SInTurnOfCar2[carCurrent][0]]
            #     tmpTime += self.Dij[SInTurnOfCar2[carCurrent][0]][TInTurnOfCar2[carCurrent][0]]
            #     for j in range(1, len(SInTurnOfCar2[carCurrent])):
            #         tmpTime += self.Dij[TInTurnOfCar2[carCurrent][j - 1]][SInTurnOfCar2[carCurrent][j]]
            #         tmpTime += self.Dij[SInTurnOfCar2[carCurrent][j]][TInTurnOfCar2[carCurrent][j]]
            #     time2[carCurrent] = tmpTime
            #
            # time3 = np.zeros(self.B, dtype=int)
            # for carCurrent in range(self.B):
            #     tmpTime = self.Dij[self.N - 1][SInTurnOfCar3[carCurrent][0]]
            #     tmpTime += self.Dij[SInTurnOfCar3[carCurrent][0]][TInTurnOfCar3[carCurrent][0]]
            #     for j in range(1, len(SInTurnOfCar3[carCurrent])):
            #         tmpTime += self.Dij[TInTurnOfCar3[carCurrent][j - 1]][SInTurnOfCar3[carCurrent][j]]
            #         tmpTime += self.Dij[SInTurnOfCar3[carCurrent][j]][TInTurnOfCar3[carCurrent][j]]
            #     time3[carCurrent] = tmpTime
            #
            # TmaxMin[i]=min(time1.max(),time2.max(),time3.max())

        pop.ObjV = TmaxMin  # 计算目标函数值，赋值给pop种群对象的ObjV属性

# def subAimFunc(args):  # 目标函数
#     # 将染色体解码为两部分S T
#     B = args[1]
#     Y = args[2]
#     S = args[3]
#     T = args[4]
#     N = args[5]
#     Dij = args[6]
#     L = args[7]
#     U = args[8]
#     averageDistanceYS = args[9]
#     totalAverageDistanceST = args[10]
#     totalAverageDistanceTS = args[11]
#     numOfGenetic = args[12]
#     Nind = args[13]
#     SizeOfMap = args[14]
#     KRefAns = args[15]
#     STrans = args[16]
#     TTrans = args[17]
#     # print(args[0])
#     print(args.shape)
#     SInTurns = args[0][:, :numOfGenetic].astype(int)
#     TInTurns = args[0][:, numOfGenetic:2 * numOfGenetic].astype(int)
#
#     # 将解码后的染色体翻译为不同编号的地理位置信息（从逻辑编号到物理编号）
#     for t in range(Nind):
#         for i in range(numOfGenetic):
#             SInTurns[t][i] = STrans[SInTurns[t][i]]
#             TInTurns[t][i] = TTrans[TInTurns[t][i]]
#
#     # 目标函数数组
#     TmaxMin=np.zeros((SInTurns.shape[0], 1), dtype=np.int)
#     DijFirst=Dij[S+T][:S].sum()
#
#     # 按Nind进行轮询
#     for i in range(SInTurns.shape[0]):
#         SInTurn=SInTurns[i]
#         TInTurn=TInTurns[i]
#
#         #按B辆车辆进行切片 尽可能平均即可
#         sumFromSToT = 0
#         sumFromTToS = 0
#         for j in range(numOfGenetic):
#             sumFromSToT += Dij[SInTurn[j]][TInTurn[j]]
#         for j in range(numOfGenetic - 1):
#             sumFromTToS += Dij[TInTurn[j]][SInTurn[j + 1]]
#         avgFromTToS = sumFromTToS / (numOfGenetic - 1)
#         avgTime = round((DijFirst + sumFromSToT + avgFromTToS * (numOfGenetic - B)) / B)
#
#         blockCount=0
#         blockList=[]
#         while blockCount<B-1:
#             blockStartPosition=0 if blockCount==0 else blockList[blockCount-1]+1
#             #防止blockStartPosition=numOfGenetic的特别处理
#             if blockStartPosition==numOfGenetic:
#                 if blockList[-2]!=numOfGenetic-3:
#                     blockList[-1]=numOfGenetic-3
#                 else:
#                     blockList[-2]=blockList[-3]+1
#                     blockList[-1] = numOfGenetic - 3
#                 blockList.append(numOfGenetic-2)
#                 blockCount+=1
#                 continue
#             # print("blockCount=", blockCount,"blockStartPosition=",blockStartPosition)
#             tmpTurnTime=Dij[S+T][SInTurn[blockStartPosition]]
#             tmpTurnTime+=Dij[SInTurn[blockStartPosition]][TInTurn[blockStartPosition]]
#             if tmpTurnTime>avgTime:
#                 blockCount+=1
#                 blockList.append(blockStartPosition)
#                 # continue
#             else:
#                 isFindFlag=False
#                 for t in range(blockStartPosition+1,numOfGenetic):
#                     tmpTurnTime+=Dij[TInTurn[t-1]][SInTurn[t]]
#                     tmpTurnTime+=Dij[SInTurn[t]][TInTurn[t]]
#                     if tmpTurnTime>avgTime:
#                         blockCount += 1
#                         isFindFlag=True
#                         # blockList.append(t - 1)
#                         if tmpTurnTime-avgTime>avgTime-tmpTurnTime+Dij[SInTurn[t]][TInTurn[t]]+Dij[TInTurn[t-1]][SInTurn[t]]:
#                             blockList.append(t-1)
#                         else:
#                             blockList.append(t)
#                         break
#                 if isFindFlag is False:
#                     blockCount+=1
#                     if blockStartPosition!=numOfGenetic-1:
#                         blockList.append(blockStartPosition)
#                     else:
#                         blockList[-1]-=1
#                         blockList.append(numOfGenetic-2)
#                         # print("Error,blockStartPosition==self.numOfGenetic-1")
#         if blockList[B - 2] > numOfGenetic - 2 and blockList[B - 3] < numOfGenetic - 2:
#             blockList[B - 2] = numOfGenetic - 2
#         elif blockList[B - 2] > numOfGenetic - 2 and blockList[B - 3] > numOfGenetic - 2:
#             print("Error,Both two of the end in the blockList is upper than self.numOfGenetic-2")
#         # try:
#         #     if blockList[self.B-2]>self.numOfGenetic-2 and blockList[self.B-3]<self.numOfGenetic-2:
#         #         blockList[self.B - 2] = self.numOfGenetic - 2
#         #     elif blockList[self.B-2]>self.numOfGenetic-2 and blockList[self.B-3]>self.numOfGenetic-2:
#         #         print("Error,Both two of the end in the blockList is upper than self.numOfGenetic-2")
#         # except IndexError:
#         #     print("IndexError,blockList=",blockList)
#         #     print("blockCount=",blockCount)
#
#
#         # tmpBlock1 = [_ * self.numOfGenetic // self.B for _ in range(1, self.B)]
#         SInTurnOfCar1 = [SInTurn[:blockList[0] + 1]] + [SInTurn[blockList[_] + 1:blockList[_ + 1] + 1] for _ in range(0,B-2)] + [SInTurn[blockList[B-2] + 1:]]
#         TInTurnOfCar1 = [TInTurn[:blockList[0] + 1]] + [TInTurn[blockList[_] + 1:blockList[_ + 1] + 1] for _ in range(0,B-2)] + [TInTurn[blockList[B-2] + 1:]]
#
#         time1=np.zeros(B,dtype=int)
#         for carCurrent in range(B):
#             try:
#                 tmpTime=Dij[N-1][SInTurnOfCar1[carCurrent][0]]
#             except IndexError:
#                 print("IndexError,carCurrent=",carCurrent,"SInTurnOfCar1=",SInTurnOfCar1)
#                 print(blockList)
#             tmpTime += Dij[SInTurnOfCar1[carCurrent][0]][TInTurnOfCar1[carCurrent][0]]
#             for j in range(1,len(SInTurnOfCar1[carCurrent])):
#                 tmpTime += Dij[TInTurnOfCar1[carCurrent][j-1]][SInTurnOfCar1[carCurrent][j]]
#                 tmpTime += Dij[SInTurnOfCar1[carCurrent][j]][TInTurnOfCar1[carCurrent][j]]
#             time1[carCurrent]=tmpTime
#
#         TmaxMin[i] = time1.max()
#
#     return TmaxMin  # 计算目标函数值，赋值给pop种群对象的ObjV属性

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

def genetic2ChromWithoutCV(B, Y, S, T, N, Dij, L, U,numOfGenetic,Nind,SizeOfMap,KRefAns):
    """===============================事前准备==========================="""
    averageDistanceYS = (sum([Dij[S + T][_] for _ in range(S)])) // S
    totalAverageDistanceST = (sum([Dij[xS][yT] for xS in range(S) for yT in range(S, S + T)])) // (int(S) * int(T))
    totalAverageDistanceTS = (sum([Dij[yT][xS] for xS in range(S) for yT in range(S, S + T)])) // (int(S) * int(T))
    """===============================实例化问题对象==========================="""
    problem = genetic2ChromWithoutCVProblem(B, Y, S, T, N, Dij, L, U, numOfGenetic, Nind, SizeOfMap, KRefAns,averageDistanceYS,totalAverageDistanceST,totalAverageDistanceTS)  # 生成问题对象
    """=================================种群设置=============================="""
    Encodings = ['P', 'P']  # 编码方式
    NIND = Nind  # 种群规模
    Field1 = ea.crtfld(Encodings[0], problem.varTypes[:numOfGenetic], problem.ranges[:, :numOfGenetic], problem.borders[:, :numOfGenetic])
    Field2 = ea.crtfld(Encodings[1], problem.varTypes[numOfGenetic:2*numOfGenetic], problem.ranges[:, numOfGenetic:2*numOfGenetic], problem.borders[:, numOfGenetic:2*numOfGenetic])
    Fields = [Field1, Field2]  # 创建区域描述器
    population = ea.PsyPopulation(Encodings, Fields, NIND)  # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
    """===============================算法参数设置============================="""
    # myAlgorithm = ea.soea_psy_SEGA_templet(problem, population)  # 增强精英保留的遗传算法
    # myAlgorithm.recOper = ea.Xovdp(XOVR=0.95, Parallel=True)  # 设置交叉算子
    # myAlgorithm.mutOper = ea.Mutinv(Pm=0.9, Parallel=True)  # 设置变异算子

    # myAlgorithm = ea.soea_psy_SGA_templet(problem, population)  # 原始版本单目标遗传算法
    myAlgorithm = ea.soea_psy_studGA_templet(problem, population)  # 种马遗传算法
    myAlgorithm.recOper = ea.Xovpmx(XOVR=0.95)  # 生成部分匹配交叉算子对象
    myAlgorithm.mutOper = ea.Mutinv(Pm=0.1)  # 生成逆转变异算子对象
    # myAlgorithm = ea.soea_psy_GGAP_SGA_templet(problem, population)   #带代沟的简单遗传算法
    myAlgorithm.MAXGEN = 1000  # 最大进化代数
    # myAlgorithm.trappedValue = 1  # “进化停滞”判断阈值
    # myAlgorithm.maxTrappedCount = myAlgorithm.MAXGEN//2  # 进化停滞计数器最大上限值，如果连续maxTrappedCount代被判定进化陷入停滞，则终止进化
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
        # Block = BestIndi.Phen[0, 2 * numOfGenetic:].astype(int)
        # Block.sort()
        print('最优的救援方案为：')
        for i in range(BestIndi.Phen.shape[1]):
            print(BestIndi.Phen[0, i],end=" ")
        print("")
        # for i in range(B):
        #     print("第"+str(i+1)+"辆车的救援路线：",end="")
        #     if i==0:
        #         print("车库→",end="")
        #         for j in range(Block[i]+1):
        #             print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→",end="")
        #             print("避难所" + str(TTrans[BestIndi.Phen[0, j+numOfGenetic].astype(int)]+1) + "→",end="")
        #         print("救援结束")
        #     elif i==B-1:
        #         print("车库→", end="")
        #         for j in range(Block[i-1] + 1,numOfGenetic):
        #             print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→", end="")
        #             print("避难所" + str(TTrans[BestIndi.Phen[0, j + numOfGenetic].astype(int)]+1) + "→", end="")
        #         print("救援结束")
        #     else:
        #         print("车库→", end="")
        #         for j in range(Block[i-1] + 1,Block[i] + 1):
        #             print("受灾点" + str(STrans[BestIndi.Phen[0, j].astype(int)]+1) + "→", end="")
        #             print("避难所" + str(TTrans[BestIndi.Phen[0, j + numOfGenetic].astype(int)]+1) + "→", end="")
        #         print("救援结束")
        # DrawPointMap(BestIndi.Phen.astype(int),Block)
    else:
        print('没找到可行解。')

if __name__ == '__main__':
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
    Nind=2000
    SizeOfMap=10
    KRefAns=0.5

    genetic2ChromWithoutCV(B, Y, S, T, N, Dij, L, U,numOfGenetic,Nind,SizeOfMap,KRefAns)