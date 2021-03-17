## graphshortestpath

[DIST，PATH，PRED] = graphshortestpath（G，S）确定从节点S到图G中所有其他节点的单个源最短路径。边的权重是n-by-n邻接矩阵中表示的所有非零条目通过稀疏矩阵G.
[DIST，PATH，PRED] = graphshortestpath（G，S，D）确定单个源 - 从节点S到节点D的单个目的地最短路径。DIST是从源到每个节点的n个距离（对于不可到达的节点使用Inf而对于源节点使用零）。 PATH包含到每个节点的获胜路径，PRED包含获胜路径的前任节点。

```matlab
%创建一个包含6个节点和11个边的有向图 求解节点1到6的最短路径
W = [.41 .99 .51 .32 .15 .45 .38 .32 .36 .29 .21];
DG = sparse([6 1 2 2 3 4 4 5 5 6 1],[2 6 3 5 4 1 6 3 4 3 5],W)
h = view(biograph(DG,[],'ShowWeights','on'))
%找到从1到6的最短路径
[dist,path,pred] = graphshortestpath(DG,1,6) %dist 最短路径值   path最短路径
%标记最短路径的节点和边缘
set(h.Nodes(path),'Color',[1 0.4 0.4])
edges = getedgesbynodeid(h,get(h.Nodes(path),'ID'));
set(edges,'LineColor',[1 0 0])
set(edges,'LineWidth',1.5)
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190716092019471.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzNjk3MTY3,size_16,color_FFFFFF,t_70)