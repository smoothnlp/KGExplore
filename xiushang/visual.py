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

    
def rel2graph(rels:list):
    """
    依据多条知识图谱N元组构建Networkx类型的有向图
    :param rels:
    :return: nx.DiGraph
    """
    g = nx.DiGraph()
    rels.sort(key=lambda x:x['edge_type'],reverse=True)  

    for rel in rels:
        rel['source'] = norm(rel['source'])
        rel['target'] = norm(rel['target'])
        g.add_node(rel['source'],type=rel['source_type'])
        g.add_node(rel['target'],type=rel['target_type'])
        if (rel['source'],rel['target']) in g.edges():  ## 相同scource,target，保留一条边，attr叠加
            if rel['edge_type'] in g.edges[(rel['source'],rel['target'])]['label'] and rel['edge'] not in g.edges[(rel['source'],rel['target'])]['label']:
                g.edges[(rel['source'],rel['target'])]['label']+=(','+rel['edge'])
            elif rel['edge_type'] not in g.edges[(rel['source'],rel['target'])]['label']and rel['edge'] not in g.edges[(rel['source'],rel['target'])]['label']:
                g.edges[(rel['source'],rel['target'])]['label']+=('\n'+rel['edge'])
        elif (rel['target'],rel['source']) in g.edges():
            if rel['edge_type'] in g.edges[(rel['target'],rel['source'])]['label'] and rel['edge'] not in g.edges[(rel['target'],rel['source'])]['label']:
                g.edges[(rel['target'],rel['source'])]['label']+=(','+rel['edge'])
            elif rel['edge_type'] not in g.edges[(rel['target'],rel['source'])]['label']and rel['edge'] not in g.edges[(rel['target'],rel['source'])]['label']:
                g.edges[(rel['target'],rel['source'])]['label']+=('\n'+rel['edge'])        
        else:
            g.add_edge(rel['source'],rel['target'], label=rel['edge'], type=rel['edge_type'])
    return g


def graph_visual(gram,x:int=12,y:int=12):
    """
    用matplotlib对有向图进行可视化
    :param g: nx.DiGraph
    :param x: 像素
    :param y: 像素
    :return:
    """
    g = rel2graph(gram)
    if len(g)<=0: ## 处理空的Graph
        return
    if len(g)>40:
        raise Exception('The input digraph is too large')
    
    g_edges = list(g.edges())
    if len(set([x[0] for x in g_edges]))==1 or len(set([x[1] for x in g_edges]))==1:  ## centre node发出的边单向
        pos = nx.drawing.layout.kamada_kawai_layout(g)
    else:                                                                             ## centre_node同时有入边和出边
        source_nodes,target_nodes = zip(*g_edges)
        centre_node = Counter(source_nodes).most_common(1)[0][0]
        centre_node = norm(centre_node)
        source_nodes = list(set(source_nodes)-set([centre_node]))
        target_nodes = list(set(target_nodes)-set(source_nodes)-set([centre_node]))
        alpha, beta = (math.pi*0.9)/len(source_nodes), (math.pi*0.9)/len(target_nodes)
        r = 1.0
        pos_arrs = [np.array([r*math.cos(math.pi*0.55+alpha*i),-r*math.sin(math.pi*0.55+alpha*i)]) for i in range(len(source_nodes))]
        pos_arrs += [np.array([r*math.cos(math.pi*1.55+beta*i),-r*math.sin(math.pi*1.55+beta*i)]) for i in range(len(target_nodes))]
        pos={**dict(zip(source_nodes+target_nodes,pos_arrs)), **{centre_node:np.array([0,0])}}
    
    ## 控制fig大小
    if len(g_edges)>24:
        x,y = len(g_edges)*0.5,len(g_edges)*0.5
    fig = plt.figure(figsize = (x,y),dpi=100)
    plt.title('股权业务关系图', fontdict={"fontsize": 14})

    node_labels = {k: label_modification(k) for k in g.nodes}
    nx.draw(g, pos, labels=node_labels,
            with_labels=True,
            node_color=[pattern_dic[t] for t in nx.get_node_attributes(g, "type").values()],
            edge_color=[pattern_dic[t] for t in nx.get_edge_attributes(g, "type").values()],
            node_size=[min(len(n), 5) * 1300 for n in g.nodes],
            alpha=1.0,
            font_color="darkslategrey",
            font_size=12,
            width=3.0,
            font_family="SimHei")
    nx.draw_networkx_edge_labels(g,
                                 pos,
                                 edge_labels=nx.get_edge_attributes(g, "label"),
                                 font_color='black',
                                 font_size=12,
                                 width=0.6,
                                 font_family="SimHei")
    return fig