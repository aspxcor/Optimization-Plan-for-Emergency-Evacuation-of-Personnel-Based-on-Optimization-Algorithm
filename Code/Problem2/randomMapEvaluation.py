# -*- coding: utf-8 -*-
# 本程序主要思想：
#   随机生成数据集，调用三种算法进行评估并绘图
import numpy as np
import random
import genetic2ChromWithoutCV as g2WithoutCV
import genetic3ChromWithoutCV as g3WithoutCV
import genetic3ChromWithCV as g3WithCV

# 初始化数据
B=random.randint(1,60)                  # 公交车数目
Y=1                                     # 车库数目 后期放开
numOfGenetic=1
numofShelter=0
while numOfGenetic>numofShelter:
    S=random.randint(1,30)              # 受灾点数目
    T=random.randint(1,40)              # 避难所人数
    L=np.array(random.sample(range(1,30), S))     # 每个受灾点受灾人数
    U=np.array(random.sample(range(1,200), T))    # 每个避难所人数上限
    numOfGenetic=L.sum()                # 总待转移人数
    numofShelter=U.sum()                # 避难所人数上限
N=Y+S+T
Dij=np.zeros((N,N),dtype=int)           # 编号规则 从0开始编号，编号顺序 S~T~Y
for i in range(S):                      # Y~S
    Dij[N-1][i]=random.randint(30,200)
for i in range(S):                      # S~T
    for j in range(S,S+T):
        Dij[i][j]=random.randint(30,200)
for i in range(S):                      # T~S
    for j in range(S,S+T):
        Dij[j][i]=int(Dij[i][j]*random.uniform(0.8,1.2))
Nind=150
SizeOfMap=10
KRefAns=0.9
Chrom3Probability=0.7

# STrans=[]
# TTrans=[]
# for i in range(S):
#     STrans+=L[i]*[i]
# for i in range(T):
#     TTrans+=U[i]*[i+S]

print("================ 基本信息 ================")
print("B =",B,", S =",S,", T=",T,", Y =",Y,", N =",N)
print("L =",L)
print("U =",U)
print("Dij =")
print(Dij)
print("Shape of Dij :",Dij.shape)

print("================ genetic3ChromWithCV ================")
g3WithCV.genetic3ChromWithCV(B, Y, S, T, N, Dij, L, U, numOfGenetic, Nind, SizeOfMap, KRefAns,Chrom3Probability)
print("================ genetic3ChromWithoutCV ================")
g3WithoutCV.genetic3ChromWithoutCV(B, Y, S, T, N, Dij, L, U, numOfGenetic, Nind, SizeOfMap, KRefAns)
print("================ genetic2ChromWithoutCV ================")
g2WithoutCV.genetic2ChromWithoutCV(B, Y, S, T, N, Dij, L, U,numOfGenetic,Nind,SizeOfMap,KRefAns)