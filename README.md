# xiushang
>嗅商 - 商业知识图谱


## 安装
```shell
git clone https://github.com/smoothnlp/xiushang.git
cd xiushang
python setup.py develop  ## 安装开发模式
```

## 使用文档

### 调用示例

```python
from xiushang import client,config
config.setApiKey(api_key)
gram = client.get_ngram(target="董明珠",limit=30)
gram = client.get_ngram_related(node="行吟信息科技（上海）有限公司")
gram = client.search_bigram(text="董明珠",limit=10)
```

### 可视化

```python
from xiushang import visual
fig = visual.graph_visual(gram)
```
* 股权关系
![xiushang_demo.png](https://github.com/smoothnlp/xiushang/blob/master/demo/comp_comp.png)

* 任职关系
![xiushang_demo.png](https://github.com/smoothnlp/xiushang/blob/master/demo/comp_person.png)

* 商标所有权
![xiushang_demo.png](https://github.com/smoothnlp/xiushang/blob/master/demo/comp_brand.png)

* 全领域的知识图谱
![](https://github.com/smoothnlp/xiushang/blob/master/demo/kg.png)



### 功能文档
```python
client.get_ngram(target="董明珠",limit=30)
    """
    :param
        source: 出发节点
        target: 到达节点
        limit: 单次最多返回多少条
    :return 固定source或target的知识图谱2元组        
    """
>> [{'edge': '作为自然人股东', 'edge_id': '7d22b561d37aa2d1565688240a4b5e47', 'edge_type': '股东', 'source': '珠海喜马明珠新媒体有限公司', 'source_id': '05c5d0ccfc3224bba8fa326a8831a269', 'source_type': '企业', 'target': '董明珠', 'target_id': '23e71caf8f4072f8aa429504b86fc80d', 'target_type': '人物'},...]

client.get_ngram_related(node="行吟信息科技（上海）有限公司")
    """
    :param
        node: 相关节点
        total_limit: 单次最多返回多少条
    :return 与node相关的知识图谱2元组        
    """
>> [{'edge': '获得D轮融资','edge_id': '884ad7fa95be508085ff5c80dcae90c7','edge_type': '融资','source': '行吟信息科技（上海）有限公司','source_id': '3fb8a3eb84e3ea2089c41d34cbbaf3a9','source_type': '企业','target': 'K11郑志刚','target_id': '04bcbd10f97de300e960db3f2ccfe3b3','target_type': '投资方'},  {'edge': '作为其他投资者','edge_id': 'e067f1a2a7e6f4e26365b10d6d215512','edge_type': '股东','source': '河南省景禾文化传播有限公司','source_id': 'eca53823ab181b6e5ad7ac88683b32cd','source_type': '企业','target': '行吟信息科技（上海）有限公司','target_id': '3fb8a3eb84e3ea2089c41d34cbbaf3a9','target_type': '企业'},...]

client.search_bigram(text="董明珠")
    """
    :param
        text: 出发节点
        limit: 单次最多返回多少条
    :return 从text出发的知识图谱2元组        
    """
>> {'response': [{'source': '董明珠', 'source_id': '529d0a7654ae77433bcd8321ffa3f9d9', 'edge': '状态描述', 'target': '实际控制人', 'target_id': '393bfaedcab20995462dc720ec5958ba', 'edge_type': '状态描述', 'evident_sentence': '董明珠是实际控制人，但不是第一大股东，股权与经营权的不对应肯定会影响企业未来上市。', 'evident_url': 'https://www.huxiu.com/article/274716.html', 'ngram_id': '18e66f9f57fbbc374387b2b96e7c2a6b', 'source_flag': 'entity', 'target_flag': 'entity'},..., {'source': '董明珠', 'source_id': '126924dd44f071f48f937f5d2e558bb8', 'edge': '还加强', 'target': '对银隆业务运营的管控', 'target_id': '7eeb21114830f2feb79a53fbdaa4eefa', 'edge_type': '事件触发', 'evident_sentence': '除了增持股份，董明珠还加强对银隆业务运营的管控。', 'evident_url': 'https://36kr.com/p/5148260', 'ngram_id': '442e01bd3af23b6a8a0738e6d88c2111', 'source_flag': 'entity', 'target_flag': 'phrase'}], 'request_id': 'e283d124-4b6a-4f14-b0e4-be53ba4aad5e'}

visual.graph_visual(gram,x,y)
    """
    :param 
        gram: 知识图谱2元组
        x: 像素
        y: 像素
    :return figure
    """
```