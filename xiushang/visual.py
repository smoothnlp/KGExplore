import networkx as nx
import math
import numpy as np
import pkg_resources
import unicodedata
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
               '企业品牌':'mediumseagreen','企业商标':'mediumseagreen',       ## edge-产品
               'entity':'powderblue', 'phrase':'powderblue',                               ## search_bigram-node
               '事件触发':'steelblue', '状态描述':'darksalmon', '属性描述':'mediumseagreen'} ## search_bigram-edge

norm = lambda x: unicodedata.normalize('NFKC', x)  ## 中文标点转英文标点，全角字符转半角字符


def label_modification(label):
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
    
    
def rel2graph(rels:list):
    """
    依据多条知识图谱N元组构建Networkx类型的有向图
    :param rels:
    :return: nx.MultiGraph, dict
    """
    G = nx.MultiGraph()
    edges_dic = {}
    rels.sort(key=lambda x:x['edge_type'],reverse=True)  
    for rel in rels:
        rel['source'] = norm(rel['source'])
        rel['target'] = norm(rel['target'])
        G.add_node(rel['source'],type=rel['source_type'])
        G.add_node(rel['target'],type=rel['target_type'])
        G.add_edges_from([(rel['source'],rel['target'],{'label':rel['edge'], 'type':rel['edge_type']})])
        if (rel['source'],rel['target']) in edges_dic.keys():
            edges_dic[(rel['source'],rel['target'])] += [(rel['source'],rel['target'],len(edges_dic[(rel['source'],rel['target'])]),rel['edge'], rel['edge_type'])]
        elif (rel['target'],rel['source']) in edges_dic.keys():
            edges_dic[(rel['target'],rel['source'])] += [(rel['source'],rel['target'],len(edges_dic[(rel['target'],rel['source'])]),rel['edge'], rel['edge_type'])]
        else:
            edges_dic[(rel['source'],rel['target'])] = [(rel['source'],rel['target'],0,rel['edge'], rel['edge_type'])]
            
    return G, edges_dic

      
def draw_graph(G,edges_dic,width,height,save_path=None):
    """
    用matplotlib对多重边有向图进行可视化
    :param G: nx.MultiGraph
    :param edges_dic: dict
    :param width, height: 窗口尺寸
    :return:
    """    
    pos = nx.drawing.kamada_kawai_layout(G)
    node_labels = {k: label_modification(k) for k in G.nodes}
    nodesize = {k:min(len(k), 5) * 1500 for k in G.nodes}
    
    ## 控制fig大小
    if len(node_labels)>28:
        width, height = len(node_labels)*0.5,len(node_labels)*0.5
    fig = plt.figure(figsize = (width, height),dpi=60)
    ## 添加水印
    wm_img = plt.imread(pkg_resources.resource_filename('xiushang', 'resources/')+'watermark.png')
    fig.figimage(wm_img,alpha=0.15)
    ## 获得绘制的句柄
    ax = fig.add_axes([0.03, 0.03, 0.94, 0.94]) ## axes的左下角在fig的图像坐标上的位置 + axes在fig的图像坐标上x、y方向的长度
    ## draw nodes
    nx.draw_networkx_nodes(G, pos, 
                       node_color=[pattern_dic[t] for t in nx.get_node_attributes(G, "type").values()], 
                       node_size=list(nodesize.values()),
                       alpha = 1)
    nx.draw_networkx_labels(G,pos,
                            labels=node_labels,
                            font_color="darkslategrey",font_size=12,font_family="SimHei")

    ax = plt.gca() ## get current axes
    for k,v_lst in edges_dic.items():
#         if set([v[3] for v in v_lst])==set(['注册商标']):  ## edge内容为“注册商标”时去重
#             v_lst = v_lst[:1]
        num_edge = len(v_lst)
        for v in v_lst:
            # middle control point of quadratic Bezier curve is located at the same distance
            # from the start point C0(x1, y1) and end point C2(x2, y2) and the distance of
            # the C1 to the line connecting C0-C2 is *rad* times the distance of C0-C2.
            source, target, count, label, edge_type = v
            (x1, y1) = pos[source]  # C0
            (x2, y2) = pos[target]  # C2
            rad = 0.4/num_edge*math.ceil(count/2)*(-1)**(count%2) 
            x, y, trans_angle = _get_trans_angle(x1,x2,y1,y2,rad,ax)  # 计算 edge_label的坐标(x,y) 和 旋转角度trans_angle
            shrink_target = to_marker_edge(nodesize[target], 'o')   # space from edge head to target

            # edge
            arrow = ax.annotate("",
                        xy=(x2, y2), xycoords='data',        ##箭头指向
                        xytext=(x1, y1), textcoords='data',  ##箭头尾部
                        arrowprops=dict(arrowstyle="->", 
                                    color=pattern_dic[edge_type], linewidth=2.5,
                                    shrinkB=shrink_target, 
                                    connectionstyle="arc3,rad={}".format(str(rad))))
            arrow.set_zorder(0)  ##先画edge，再画node

            # edge label
            t = ax.text(x, y,str(label),
                        size=14,color='black',family='SimHei',weight='normal',
                        horizontalalignment='center',verticalalignment='center',
                        rotation=trans_angle,transform=ax.transData,
                        bbox=dict(boxstyle="round", fc="w", ec='0.9', alpha=0.9))
    for key, spine in ax.spines.items():  ## 删除边框
        spine.set_visible(False)
    if save_path:
        plt.savefig(save_path,dpi=fig.dpi)
    plt.show()
    return 

   
def graph_visual(rels,width:int=14,height:int=14,save_path=None):
    """
    :param rels: list or dict
    :param width, height: 窗口尺寸
    :return:
    """
    if type(rels)==dict:      ## rels=client.search_bigram()
        rels = rels['response']
        for dic in rels:
            dic["source_type"] = dic.pop("source_flag")
            dic["target_type"] = dic.pop("target_flag")
    elif type(rels)!=list:
        raise ValueError("Invalid input type of "+str(type(rels)))
    G, edges_dic = rel2graph(rels)
    if len(G)<=0:             ## 处理空的Graph
        return
    if len(G)>40:
        raise Exception("The input digraph is too large")
    draw_graph(G,edges_dic,width,height,save_path)
    return 
   
   
def composedgraph_visual(rels,width:int=14,height:int=14,save_path=None):
    """
    :param rels: list of list/ list of dict
    :param width, height: 窗口尺寸
    :return:
    """
    graphs, edges_dic = [], {}
    for rel in rels:
        if type(rel)==dict:
            rel = rel['response']
            for dic in rel:
                dic["source_type"] = dic.pop("source_flag")
                dic["target_type"] = dic.pop("target_flag")
        elif type(rel)!=list:
            raise ValueError("Invalid input type of "+str(type(rels)))
        g, edges_dic1 = rel2graph(rel)
        graphs.append(g)
        edges_dic.update(edges_dic1)
    G = nx.compose_all(graphs)  
    if len(G)<=0:             ## 处理空的Graph
        return
    if len(G)>40:
        raise Exception("The input digraph is too large")
    draw_graph(G,edges_dic,width,height,save_path)
    return 


################################################################################################
#TODO:
#1.同edge去重，如“商标”重复太多，展示效果不好；
#2.使用nx.MultiGraph()得到的graph，无法正确记录edge的指向，
#   nx.MultiDiGraph()可以正确记录edge的指向，但nx.drawing.kamada_kawai_layout(G)计算的pocision不对。
#   (已解决，用edges_dic记录箭头指向)
################################################################################################