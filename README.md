# Knowledge Explore
> - KGExplore: 通用领域知识图谱
> - XiuShang 嗅商: 商业知识图谱

## Vision
> WE ARE DOING IT! FOR REAL! 我们是真的在做! 这是我们眼中的知识图谱现状: 
>  - every body talks about it: 欢迎了解一下各家科技公司的技术宣传稿 :)
>  - nobody really knows how to do it: 别说do it, 什么是知识图谱, 每行每业的定义都不尽相同. 至于怎么做?做什么?, 以后再说; PPT先画, 牛X先吹. 
>  - everyone thinks everyone else is doing it, so everyone claims they are doing it: 这年头, ppt上没提到"知识图谱"概念的, 都不好意思说自己是AI公司.

我们团队一直相信, 人类积累的很多知识其实一直就在文字中(为啥有文化的人都写书呢, 文字传播知识呗!). 而作为一个专业的NLP团队, 
我们一直将我们的核心研发集中在了"无监督学习"和"NLP技术的大规模工程化"上. 在经过一年多的研发&开发后, 我们做出了一套可在大规模文本上抽取的"文字对象间关系"的技术框架,
虽然结果还有不断完善的空间, 但是既然是**知识,就值得被分享**

## 安装


```shell
https://github.com/smoothnlp/KGExplore.git
cd KGExplore
python setup.py install
```

## 使用介绍

> 知识图谱N元组的搜索与可视化

#### 身份验证
> 请将您的身份/就职公司/业务场景/联系方式等电邮到business@smoothnlp.com; 我们对科研工作者提供**免费**的服务调用!

```python
import kgexplore as kge
kge.config.setApiKey(YOUR_API_KEY)
```

### 通用领域知识图谱
```python
rels = []
rels += kge.search_bigram("瑞幸咖啡",limit=10)
kge.visualize(rels)
```
![](https://github.com/smoothnlp/kgexplore/blob/master/demo/瑞幸咖啡.png)


### 嗅商 - 商业知识图谱

```python
rels = []
rels += kge.get_xiushang_ngram(target="董明珠",source_type='企业')
rels += kge.get_xiushang_ngram(source="珠海格力电器股份有限公司",target_type="人物")
kge.visualize(rels)
```
![](https://github.com/smoothnlp/kgexplore/blob/master/demo/嗅商-格力-董明珠.png)

### 请我们喝咖啡
 - 如果你是科研人员: **Free** 
 - 请算法工程师喝咖啡(28元): 5K次调用
 - 请整个团队喝咖啡(128元): 5万次调用
 - 有意包养我们(我们在找融资): 心诚即可,请电邮business@smoothnlp.com

> 请使用下方的二维码进行付款, 然后将支付凭证截图电邮到business@smoothnlp.com ; 我们会在24小时内回复apikey. 谢谢大家支持

![](https://github.com/smoothnlp/kgexplore/blob/master/demo/wechat_payment_qr.jpeg)