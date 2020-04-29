# Knowledge Explore
> 知识探索


## 安装
```shell
git clone https://github.com/smoothnlp/xiushang.git
cd xiushang
python setup.py install
```

## 使用文档

> 知识图谱N元组的搜索与可视化

#### 身份验证
> 请电邮到 contact@smoothnlp.com 或 添加文档最下方的企业微信; 我们对科研工作者提供**免费**的服务调用!

```python
import kgexplore as kge
kge.config.setApiKey(YOUR_API_KEY)
```

### 通用领域知识图谱
```python
rels = []
rels += kge.search_bigram("瑞幸咖啡",limit=10)
rels += kge.search_bigram("互联网咖啡")
kge.visualize(rels)
```
![](https://github.com/smoothnlp/kgexplore/blob/master/demo/咖啡.png)


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
 - 请算法工程师喝咖啡(28元): 1万次调用
 - 请整个团队喝咖啡(128元): 10万次调用
 - 有意包养我们(我们在找融资): 心诚即可,请电邮contact@smoothnlp.com

> 请使用下方的二维码进行付款, 然后将支付凭证截图电邮到contact@smoothnlp.com; 我们会在24小时内回复apikey. 谢谢大家支持

![](https://github.com/smoothnlp/kgexplore/blob/master/demo/wechat_payment_qr.jpeg)