from xiushang import config
import networkx as nx
import math
import numpy as np
import unicodedata
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


## 设置字体
font_dirs = ['simhei/']
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)
plt.rcParams['font.family'] = "SimHei"

## 设置颜色
pattern_dic = {'企业':'powderblue','机构':'powderblue','投资方':'powderblue',  ## node-机构
               '人物':'bisque',                                               ## node-人物
               '品牌':'#9ffeb0','商标':'#9ffeb0',                             ## node-产品
               '融资':'steelblue','投资':'steelblue','股东':'steelblue',      ## edge-投融资
               '任职':'darksalmon',                                           ## edge-任职
               '企业品牌':'mediumseagreen','企业商标':'mediumseagreen'}       ## edge-产品

norm = lambda x: unicodedata.normalize('NFKC', x)  ## 中文标点转英文标点，全角字符转半角字符


def label_modification(label):
    length = len(label)
    if 0 < length <= 6:
        return label
    elif length <= 12:
        return label[:length // 2] + "\n" + label[length // 2:]
    else:
        return label[:length // 3] + "\n" + label[length // 3:2 * length // 3] + "\n" + label[2 * length // 3:]

    
def to_marker_edge(marker_size, marker):
    """
    get edge shrink_target
    :param marker_size: int 
    :param marker: default 'o'
    :return: float
    """
    if marker in "s^>v<d":  # `large` markers need extra space
        return pow(2*marker_size,0.49)/2
    else:
        return pow(marker_size,0.49)/2
    
    
def rel2graph(rels:list):
    """
    依据多条知识图谱N元组构建Networkx类型的有向图
    :param rels:
    :return: nx.MultiGraph
    """
    G = nx.MultiGraph()
    rels.sort(key=lambda x:x['edge_type'],reverse=True)  
    for rel in rels:
        rel['source'] = norm(rel['source'])
        rel['target'] = norm(rel['target'])
        G.add_node(rel['source'],type=rel['source_type'])
        G.add_node(rel['target'],type=rel['target_type'])
        G.add_edges_from([(rel['source'],rel['target'],{'label':rel['edge'], 'type':rel['edge_type']})])
    return G


def graph_visual(gram,x:int=16,y:int=16):
    """
    用matplotlib对有向图进行可视化
    :param g: nx.DiGraph
    :param x: 像素
    :param y: 像素
    :return:
    """
    G = rel2graph(gram)
    if len(G)<=0: ## 处理空的Graph
        return
    if len(G)>40:
        raise Exception('The input digraph is too large')
    
    pos = nx.drawing.kamada_kawai_layout(G)

    nodelist = list(G.nodes())
    node_labels = {k: label_modification(k) for k in G.nodes}
    node_size = [min(len(n), 5) * 1500 for n in G.nodes]

    edgelist = list(G.edges)
    target_count = Counter([x[1] for x in G.edges()])
    edge_labels = nx.get_edge_attributes(G, "label")
    edge_types = nx.get_edge_attributes(G,'type')
    
    ## 控制fig大小
    if len(nodelist)>32:
        x,y = len(edgelist)*0.5,len(edgelist)*0.5
    fig = plt.figure(figsize = (x,y),dpi=80)
    nx.draw_networkx_nodes(G, pos, 
                       node_color = [pattern_dic[t] for t in nx.get_node_attributes(G, "type").values()], 
                       node_size =[min(len(n), 5) * 1300 for n in G.nodes],
                       alpha = 1)
    nx.draw_networkx_labels(G,pos,
                            labels=node_labels,
                            font_color="darkslategrey",font_size=12,font_family="SimHei")



    ax = plt.gca()
    for (n1, n2, n3), label in edge_labels.items():
        # middle control point of quadratic Bezier curve is located at the same distance
        # from the start point C0(x1, y1) and end point C2(x2, y2) and the distance of
        # the C1 to the line connecting C0-C2 is *rad* times the distance of C0-C2.
        (x1, y1) = pos[n1]  # C0
        (x2, y2) = pos[n2]  # C2
        rad = 0.4/target_count[n2]*math.ceil(n3/2)*(-1)**(n3%2) 
        x12, y12 = (x1+x2)/2., (y1+y2)/2.
        dx, dy = x2-x1, y2-y1
        x, y = x12+rad*dy/2, y12-rad*dx/2  # pos of edge label

        # space from edge head to target
        target_node_size = node_size[nodelist.index(n1)]
        shrink_target = to_marker_edge(target_node_size, 'o') 

        # edge
        arrow = ax.annotate("",
                    xy=(x1, y1), xycoords='data',
                    xytext=(x2, y2), textcoords='data',
                    arrowprops=dict(arrowstyle="->", 
                                color=pattern_dic[edge_types[(n1,n2,n3)]],
                                shrinkB=shrink_target, 
                                linewidth=2.5,
                                connectionstyle="arc3,rad={}".format(str(-rad)) 
                                    )
                    )
        arrow.set_zorder(0)  ##先画edge，再画node

        # make label orientation "right-side-up"
        angle = np.arctan2(y2-y1, x2-x1)/(2.0*np.pi)*360
        if angle > 90:
            angle -= 180
        if angle < - 90:
            angle += 180
        xy = np.array((x, y))
        trans_angle = ax.transData.transform_angles(np.array((angle,)),xy.reshape((1, 2)))[0]
        bbox = dict(boxstyle="round", fc="w", ec='0.9', alpha=0.9)  # text box
        if not isinstance(label, str):
            label = str(label)  # this makes "1" and 1 labeled the same

        # edge label
        t = ax.text(x, y,
                    label,
                    size=14,
                    color='black',
                    family='SimHei',
                    weight='normal',
                    horizontalalignment='center',
                    verticalalignment='center',
                    rotation=trans_angle,
                    transform=ax.transData,
                    bbox=bbox)
    plt.show()
    return 


################################################################################################
#TODO:
#1.同edge去重，如“商标”重复太多，展示效果不好；
#2.部分情况下， G.add_edges_from()第一次调用时，将source、target倒转，未发现明显的错误规律，
#   展示图暂时用G.remove_node(list(G.edges())[0][0])处理过
################################################################################################