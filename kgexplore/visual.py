import networkx as nx
import math
import numpy as np
import pkg_resources
import unicodedata
from heapq import heappush, heappop
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.font_manager as font_manager


## 设置字体
font_files = [pkg_resources.resource_filename('kgexplore', 'resources/simhei/simhei.ttf')]
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)
plt.rcParams['font.family'] = "SimHei"

## 设置颜色
## 设置颜色
pattern_dic = {'企业':'powderblue','投资方':'powderblue','机构':'#cadcf2', ## node-机构
               '人物':'bisque',                                            ## node-人物
               '品牌':'#d1f6d9','商标':'#d1f6d9',                          ## node-产品
               '产品':'#ffffad','货品':'#e5e59b','地区':'#c9c9cb','公司与品牌':'#d6f0fa',
               '修饰短语':'#dff7f2',
                '修饰性名词短语':'#dff7f2',
               '其他':'#faebe3',                      ## search_bigram-node
               '融资':'steelblue','投资':'steelblue','股东':'steelblue',      ## edge-投融资
               '任职':'darksalmon',                                           ## edge-任职
               '企业品牌':'mediumseagreen','企业商标':'mediumseagreen',       ## edge-产品
               '事件触发':'#bc8f8f', '状态描述':'#7ba7cc',
               "数值描述":"#3291a8",
               '属性描述':'#62c28d'}## search_bigram-edge

default_color = '#faebe3'

def determine_color(node_type):
    if node_type in pattern_dic:
        return pattern_dic[node_type]
    else:
        return default_color

normalize = lambda x: unicodedata.normalize('NFKC', x)  ## 中文标点转英文标点，全角字符转半角字符

def label_modification(label):
    """
    为node上的label做换行处理, 保证一定宽度
    :param label:
    :return:
    """
    length = len(label)
    if 0 < length <= 6:
        return label
    elif length <= 12:
        return label[:length // 2] + "\n" + label[length // 2:]
    else:
        return label[:length // 3] + "\n" + label[length // 3:2 * length // 3] + "\n" + label[2 * length // 3:]
     

def _get_trans_angle(x1,x2,y1,y2,rad,ax):
    """
    计算 edge_label的坐标(x,y) 和 旋转角度trans_angle 
    :param (x1,x2): source
    :param (y1,y2): target
    :param rad: edge的弯曲弧度,使用quadratic Bezier curve计算
    :param ax
    :return: edge_label的坐标(x,y) , 旋转角度trans_angle
    """
    x12, y12 = (x1+x2)/2., (y1+y2)/2.
    dx, dy = x2-x1, y2-y1
    x, y = x12+rad*dy/2, y12-rad*dx/2
    angle = np.arctan2(y2-y1, x2-x1)/(2.0*np.pi)*360
    if angle > 90:
        angle -= 180
    if angle < - 90:
        angle += 180
    trans_angle = ax.transData.transform_angles(np.array((angle,)),np.array((x, y)).reshape((1, 2)))[0]
    return x, y, trans_angle

    
def to_marker_edge(marker_size, marker):
    """
    get edge shrink_target
    :param marker_size: int 
    :param marker: default 'o'
    :return: float
    """
    if marker in "s^>v<d":  # `large` markers need extra space
        return pow(2*marker_size,0.5)/2
    else:
        return pow(marker_size,0.5)/2

   
def shortest_path_length(G):
    def _dijkstra(G, node):
        """使用dijkstra算法计算 node 与 图中其它节点 之间的最短路径"""
        G_succ = {k: list(G._adj[k].keys()) for k in G._adj.keys()}
        for u,v in G.edges():
            G_succ[v] += [u]  # 保存全部邻接关系
        push = heappush
        pop = heappop
        dist = {}  # dictionary of final distances
        seen = {}
        fringe = []
        if node not in G:
            raise nx.NodeNotFound(f"Node {node} not in G")
        seen[node] = 0
        push(fringe, (0, node))
        while fringe:
            (d, v) = pop(fringe)
            if v in dist:
                continue  # already searched this node.
            dist[v] = d
            for u in G_succ[v]:
                vu_dist = dist[v] + 1
                if u in dist:
                    if vu_dist < dist[u]:
                        raise ValueError('Contradictory paths found:','negative weights?')
                elif u not in seen or vu_dist < seen[u]:
                    seen[u] = vu_dist
                    push(fringe, (vu_dist, u))
        return dist
    return {n:_dijkstra(G, n) for n in G}
    
    
def rel2graph(rels:list):
    """
    依据多条知识图谱N元组构建Networkx类型的有向图
    :param rels:
    :return: nx.MultiDiGraph
    """
    G = nx.MultiDiGraph()
    rels.sort(key=lambda x:x['edge_type'],reverse=True)  
    for rel in rels:
        rel['source'] = normalize(rel['source'])
        rel['target'] = normalize(rel['target'])
        G.add_node(rel['source'],type=rel['source_type'])
        G.add_node(rel['target'],type=rel['target_type'])
        G.add_edges_from([(rel['source'],rel['target'],
                           {'edge_attr':{'label':rel['edge'], 'type':rel['edge_type']}})])
    return G

      
def draw_graph(G,
               width:int = 14,
               height:int = 14,
               node_label_size: int = 12,
               edge_label_size: int = 14,
               save_path=None):
    """
    用matplotlib对多重边有向图进行可视化
    :param G: nx.MultiDiGraph
    :param width, height: 窗口尺寸
    :return:
    """    
    if len(G)==2:
        pos = nx.drawing.planar_layout(G)
    else:
        dists = shortest_path_length(G)
        pos = nx.drawing.kamada_kawai_layout(G,dist=dists)
    node_labels = {k: label_modification(k) for k in G.nodes}
    nodesize = {k:min(len(k), 5) * 1500 for k in G.nodes}
    edges = nx.get_edge_attributes(G,'edge_attr')
    
    ## 控制fig大小
    # if len(node_labels)>28:
    #     width, height = len(node_labels)*0.5,len(node_labels)*0.5

    fig = plt.figure(figsize = (width, height),dpi=60)
    ## 添加水印
    #wm_img = plt.imread(pkg_resources.resource_filename('kgexplore', 'resources/')+'watermark.png')
    wm_img = plt.imread(pkg_resources.resource_filename('kgexplore', 'resources/watermark.png'))
    fig.figimage(wm_img,alpha=0.15)
    ## 获得绘制的句柄
    ax = fig.add_axes([0.1, 0.1, 0.9, 0.9]) ## axes的左下角在fig的图像坐标上的位置 + axes在fig的图像坐标上x、y方向的长度
    ## draw nodes
    nx.draw_networkx_nodes(G, pos, 
                       node_color=[determine_color(t) for t in nx.get_node_attributes(G, "type").values()],
                       node_size=list(nodesize.values()),
                       alpha = 1)
    nx.draw_networkx_labels(G,pos,
                            labels=node_labels,
                            font_color="darkslategrey",
                            font_size=node_label_size,
                            font_family="SimHei")

    ax = plt.gca() ## get current axes
    for (source,target,num_degree),attr in edges.items():
        num_edge = len(G[source][target])
        # middle control point of quadratic Bezier curve is located at the same distance
        # from the start point C0(x1, y1) and end point C2(x2, y2) and the distance of
        # the C1 to the line connecting C0-C2 is *rad* times the distance of C0-C2.
        (x1, y1) = pos[source]  # C0
        (x2, y2) = pos[target]  # C2
        rad = 0.4/num_edge*math.ceil(num_degree/2)*(-1)**(num_degree%2) 
        x, y, trans_angle = _get_trans_angle(x1,x2,y1,y2,rad,ax)  # 计算 edge_label的坐标(x,y) 和 旋转角度trans_angle
        shrink_target = to_marker_edge(nodesize[target], 'o')   # space from edge head to target

        # edge
        arrow = ax.annotate("",
                    xy=(x2, y2), xycoords='data',        ##箭头指向
                    xytext=(x1, y1), textcoords='data',  ##箭头尾部
                    arrowprops=dict(arrowstyle="->", 
                                color=determine_color(attr['type']), linewidth=2.5,
                                shrinkB=shrink_target, 
                                connectionstyle="arc3,rad={}".format(str(rad))))
        arrow.set_zorder(0)  ##先画edge，再画node

        # edge label
        t = ax.text(x, y,str(attr['label']),
                    size=edge_label_size,color='black',family='SimHei',weight='normal',
                    horizontalalignment='center',verticalalignment='center',
                    rotation=trans_angle,transform=ax.transData,
                    bbox=dict(boxstyle="round", fc="w", ec='0.9', alpha=0.9))
    ## legend
    handles_node = [mpatches.Patch(color=determine_color(t), label=t)
                      for t in set(nx.get_node_attributes(G, "type").values())]
    handles_edge = [mlines.Line2D([],[],color=determine_color(t),label=t,linewidth=2.5)
                      for t in set([d['type'] for d in edges.values()])]
    legend1 = plt.legend(handles=handles_node, fontsize=12, framealpha=0.2,title='node',
                         bbox_to_anchor=(0.95, 1.05),bbox_transform=plt.gcf().transFigure)
    legend1.get_title().set_fontsize(fontsize = 14)  # 设置legend title字号
    ax.add_artist(legend1)  ## 使用双legend
    legend2 = plt.legend(handles=handles_edge, fontsize=12, framealpha=0.2,title='edge',
                         bbox_to_anchor=(1.05, 1.05),bbox_transform=plt.gcf().transFigure)
    legend2.get_title().set_fontsize(fontsize = 14)  # 设置legend title字号
    
    for key, spine in ax.spines.items():  ## 删除边框
        spine.set_visible(False)
    if save_path:
        plt.savefig(save_path,dpi=fig.dpi,bbox_inches='tight')
    plt.show()
    return 

   
def visualize(rels,
                 width:int=14,
                 height:int=14,
                 **kargs):
    """
    :param rels: list or dict
    :param width, height: 窗口尺寸
    :return:
    """
    if not isinstance(rels,list):
        raise ValueError("Invalid input type of "+str(type(rels)))

    ## 过滤 source 与 target 相同的情况
    rels = [rel for rel in rels if rel['target']!=rel['source']]

    G = rel2graph(rels)
    if len(G)<=0:             ## 处理空的Graph
        return
    if len(G)>100:
        raise Exception("The input digraph is too large")
    draw_graph(G,width,height,**kargs)

#TODO:
#1.同edge去重，如“商标”重复太多，展示效果不好；
#2.使用nx.MultiGraph()得到的graph，无法正确记录edge的指向，
#   nx.MultiDiGraph()可以正确记录edge的指向，但nx.drawing.kamada_kawai_layout(G)计算的pocision不对。
#   (已解决，nx.MultiDiGraph()+shortest_path_length()计算最短路径)
################################################################################################
