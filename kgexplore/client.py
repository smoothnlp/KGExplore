import time
import requests
from .configurations import config
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError

def _request_single(path, counter=0, params:dict = {}):
    if counter > 99:
        raise Exception(
            " exceed maximal attemps for parsing. ")
    if config.apikey is not None and isinstance(config.apikey,str):   ## pro 版本支持 apikey 调用
        params['apikey'] = config.apikey
    content = {**params}
    try:
        r = requests.get(config.HOST + path, params=content,timeout=120)
    except (Timeout) as e:
        config.logger.critical(str(e))
        return None
    except (ConnectionError) as e:
        config.logger.warn(str(e))
        time.sleep(0.5)  ## 延迟50毫秒再调用
        counter += 10
        return
    result = r.json()
    if r.status_code==429:  ## qps超限制
        counter += 1
        time.sleep(0.05)  ## 延迟50毫秒再调用
        return _request_single( path=path, counter=counter)
    elif isinstance(result, dict) and "payload" in result:
        response = result['payload']
        return response
    else:
        raise Exception(r.text)

def get_xiushang_ngram(path = "/service/api/xiushang/ngram",**kargs):
    """
    嗅商接口; 返回商业知识图谱N元组.
    :param path:
    :param kargs:
        source: 出发节点
        target: 到达节点
        source_type: (目前支持)
        target_type:
        offset: 默认为0
        limitL: 单次最多返回多少条
    :return:
    """
    return _request_single(path=path,params=kargs)

def get_xiushang_node(path = "/service/api/xiushang/node",**kargs):
    return _request_single(path=path, params=kargs)

def get_xiushang_edge(path = "/service/api/xiushang/edge",**kargs):
    return _request_single(path=path, params=kargs)

def get_xiushang_ngram_related(node, total_limit:int = 10):
    limit = 50
    offset = 0
    ngrams = []
    output = get_xiushang_ngram(source = node,offset = offset, limit = limit)
    while output is not None and (len(output)!=0) and offset+limit <= total_limit:
        ngrams += output
        offset += limit
        output =  get_xiushang_ngram(source = node,offset = offset,limit = limit)
    offset = 0
    output = get_xiushang_ngram(target=node, offset=offset, limit=limit)
    while output is not None and (len(output)!=0) and offset+limit <= total_limit:
        ngrams += output
        offset += limit
        output = get_xiushang_ngram(source=node, offset=offset, limit=limit)
    return ngrams

def search_bigram(text,  ## 长度不超过80
                  limit:int = 6,
                  path:str = "/pro/ngram/searchNgram"):
    response =  _request_single(path = path,
                           params = {"text":text,
                                     "limit":limit})
    if isinstance(response,dict) and "response" in response:
        return response["response"]
    else:
        raise ValueError("Search for Bigram Failed")

