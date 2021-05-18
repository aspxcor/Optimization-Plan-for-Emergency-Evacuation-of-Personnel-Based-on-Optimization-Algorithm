#coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
plt.rcParams['font.sans-serif']=['SimHei'] #显示中文标签
plt.rcParams['axes.unicode_minus']=False   #这两行需要手动设置

# # 兴国图1：救援时间~救援车队数目
# x=np.array([10,20,30,40,50,60,70,80,90,100,110,120,130,140])
# y =np.array([38,19,15,12,10,9,7,6.5,6.1,5.9,5.8,5.7,5.5,5.2])
# plt.plot(x, y, '.-')
# plt.xlabel('救援车队数目')
# plt.ylabel('救援时间/小时')
# plt.show()

# # 兴国图2：求解时间~救援车队数目
# x=np.array([10,20,30,40,50,60,70,80,90,100,110,120,130,140])
# y =np.array([1.8,1.4,1.8,2.0,2.1,2.2,2.5,2.3,2.6,3.2,2.9,3,2.7,2.7])
# plt.plot(x, y, '.-')
# plt.xlabel('救援车队数目')
# plt.ylabel('求解时间/分钟')
# plt.show()

# # 4.2节对比图：柱状图：三个不同模型
# np.set_printoptions(suppress=True)
# mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei为黑体
# mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负
# r = [[726, 1064, 651],  # Oracle
#      [762, 884, 676],  # GDB
#      [752,      951,		644]#,    #SQLITE
#      ]
# w = [[400, 400, 400],  # Oracle
#      [212, 244, 223],  # GDB
#      [211, 255, 229]#,  # SQLITE
#      ]
# # 这是柱图x轴标签
# ysr = ['第1组实验', '第2组实验', '第3组实验']
# def DrawGeoDtaabse(rcount, wcount, y):
#     # 第一行 第一列图形   2,1 代表2行1列
#     ax1 = plt.subplot(2, 1, 1)
#     # 第二行 第一列图形
#     ax3 = plt.subplot(2, 1, 2)
#     # 默认时间格式
#     plt.sca(ax1)
#     plt.xlabel("", color='r')  # X轴标签
#     plt.ylabel("平均救援时间/分钟", color='r')  # Y轴标签
#     # plt.grid(True)   显示格网
#     # plt.gcf().autofmt_xdate() 显示时间
#     plt.legend()  # 显示图例
#     plt.title("平均救援时间")  # 标题
#     # x1 = [1, 5, 9, 13, 17, 21, 25, 29]  # x轴点效率位置
#     x1 = [1, 5, 9]  # x轴点效率位置
#     x2 = [i + 1 for i in x1]  # x轴线效率位置
#     x3 = [i + 2 for i in x1]  # x轴面效率位置
#     y1 = [i[0] for i in rcount]  # y轴点效率位置
#     y2 = [i[1] for i in rcount]  # y轴线效率位置
#     y3 = [i[2] for i in rcount]  # y轴面效率位置
#     # 占位以免 数据源标签丢失
#     # y0 = ["", "", "", "", "", "", "", ""]
#     y0 = ["", "", ""]
#     plt.bar(x1, y1, alpha=0.7, width=0.9, color='r', label="遗传算法1", tick_label=y0)
#     plt.bar(x3, y3, alpha=0.7, width=0.9, color='b', label="遗传算法2", tick_label=y0)
#     plt.bar(x2, y2, alpha=0.7, width=0.9, color='g', label="遗传算法3", tick_label=y)
#     plt.legend()
#     # 至此第一行的读取效率绘制完毕,再重复一下第二行的写效率
#     plt.sca(ax3)
#     plt.xlabel("实验组别序号", color='r')  # X轴标签
#     plt.ylabel("遗传子代代数", color='r')  # Y轴标签
#     # plt.grid(True)
#     plt.legend()  # 显示图例
#     plt.title("终止计算时遗传子代代数")  # 图标题
#     y1 = [i[0] for i in wcount]
#     y2 = [i[1] for i in wcount]
#     y3 = [i[2] for i in wcount]
#     # y0 = ["", "", "", "", "", "", "", ""]
#     y0 = ["", "", ""]
#     plt.bar(x1, y1, alpha=0.7, width=0.9, color='r', label="遗传算法1", tick_label=y0)
#     plt.bar(x3, y3, alpha=0.7, width=0.9, color='b', label="遗传算法2", tick_label=y0)
#     plt.bar(x2, y2, alpha=0.7, width=0.9, color='g', label="遗传算法3", tick_label=y)
#     plt.legend()
#     plt.show()
# DrawGeoDtaabse(r, w, ysr)

# 4.3节对比图：柱状图：三个不同模型
np.set_printoptions(suppress=True)
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei为黑体
mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负
r = [[926],  # Oracle
     [762],  # GDB
     [752],#,    #SQLITE
     [722],
     [642]
     ]
w = [[400],  # Oracle
     [212],  # GDB
     [211],#,  # SQLITE
     [211],
     [642]
     ]
# 这是柱图x轴标签
ysr = ['遗传方案1', '遗传方案2', '遗传方案3', '遗传方案4', '遗传方案5']
def DrawGeoDtaabse(rcount, wcount, y):
    # 第一行 第一列图形   2,1 代表2行1列
    ax1 = plt.subplot(2, 1, 1)
    # 第二行 第一列图形
    ax3 = plt.subplot(2, 1, 2)
    # 默认时间格式
    plt.sca(ax1)
    plt.xlabel("遗传方案序号", color='r')  # X轴标签
    plt.ylabel("平均救援时间/分钟", color='r')  # Y轴标签
    # plt.grid(True)   显示格网
    # plt.gcf().autofmt_xdate() 显示时间
    # plt.legend()  # 显示图例
    plt.title("平均救援时间")  # 标题
    # x1 = [1, 5, 9, 13, 17, 21, 25, 29]  # x轴点效率位置
    x1 = [1, 2, 3,4,5]  # x轴点效率位置
    x2 = [i + 1 for i in x1]  # x轴线效率位置
    x3 = [i + 2 for i in x1]  # x轴面效率位置
    y1 = [i[0] for i in rcount]  # y轴点效率位置
    # y2 = [i[1] for i in rcount]  # y轴线效率位置
    # y3 = [i[2] for i in rcount]  # y轴面效率位置
    # 占位以免 数据源标签丢失
    # y0 = ["", "", "", "", "", "", "", ""]
    y0 = ["", "", "", "", ""]
    plt.bar(x1, y1, alpha=0.7, width=0.6, color='b', label="遗传算法1", tick_label=y)
    # plt.bar(x3, y3, alpha=0.7, width=0.9, color='b', label="遗传算法2", tick_label=y0)
    # plt.bar(x2, y2, alpha=0.7, width=0.9, color='g', label="遗传算法3", tick_label=y)
    # plt.legend()
    # # 至此第一行的读取效率绘制完毕,再重复一下第二行的写效率
    # plt.sca(ax3)
    # plt.xlabel("遗传方案序号", color='r')  # X轴标签
    # plt.ylabel("遗传子代代数", color='r')  # Y轴标签
    # # plt.grid(True)
    # # plt.legend()  # 显示图例
    # plt.title("终止计算时遗传子代代数")  # 图标题
    # y1 = [i[0] for i in wcount]
    # # y2 = [i[1] for i in wcount]
    # # y3 = [i[2] for i in wcount]
    # # y0 = ["", "", "", "", "", "", "", ""]
    # y0 = ["", "", "", ""]
    # plt.bar(x1, y1, alpha=0.7, width=0.6, color='b', label="遗传算法1", tick_label=y)
    # # plt.bar(x3, y3, alpha=0.7, width=0.9, color='b', label="遗传算法2", tick_label=y0)
    # # plt.bar(x2, y2, alpha=0.7, width=0.9, color='g', label="遗传算法3", tick_label=y)
    # # plt.legend()
    plt.show()
DrawGeoDtaabse(r, w, ysr)