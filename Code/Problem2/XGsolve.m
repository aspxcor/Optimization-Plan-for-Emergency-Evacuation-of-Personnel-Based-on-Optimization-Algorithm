%% 预处理
VC=500;%单车车容量
BusBlank=50;%车辆在车库的分布
depot=length(BusBlank);%车库数目
DSeparate=ceil(dw(dw>0).'/VC);%受灾点容量
SSeparate=-floor(dw(dw<0).'/VC);%避难所容量
ND=length(DSeparate);%受灾点数目
NS=length(SSeparate);%避难所数目
N=length(dw);%总节点数目
CNPathClus(CNPathClus==inf)=0;
CN=sparse(CNPathClus);
CN=ceil(CN/1000*60);
path=inf*ones(N);
Rpath=cell(N);
%受灾点到避难所最短路径及具体路线
for i=1:ND
    for j=1:NS
        [path(i,ND+j),Rpath{i,ND+j}]=graphshortestpath(CN,i,ND+j);
    end
end
%避难所到受灾点最短路径及具体路线
for i=1:NS
    for j=1:ND
        [path(ND+i,j),Rpath{ND+i,j}]=graphshortestpath(CN,ND+i,j);
    end
end
%车库到受灾点最短路径及具体路线
for i=1:depot
    for j=1:ND
        [path(ND+NS+i,j),Rpath{ND+NS+i,j}]=graphshortestpath(CN,ND+NS+i,j);
    end
end
