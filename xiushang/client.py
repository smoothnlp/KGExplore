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

def get_ngram(path = "/service/api/xiushang/ngram",**kargs):
    """
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

def get_node(path = "/service/api/xiushang/node",**kargs):
    return _request_single(path=path, params=kargs)

def get_edge(path = "/service/api/xiushang/edge",**kargs):
    return _request_single(path=path, params=kargs)

def get_ngram_related(node, total_limit:int = 200):
    limit = 50
    offset = 0
    ngrams = []
    output = get_ngram(source = node,offset = offset, limit = limit)
    while output is not None and (len(output)!=0) and offset+limit <= total_limit:
        ngrams += output
        offset += limit
        output =  get_ngram(source = node,offset = offset,limit = limit)
    offset = 0
    output = get_ngram(target=node, offset=offset, limit=limit)
    while output is not None and (len(output)!=0) and offset+limit <= total_limit:
        ngrams += output
        offset += limit
        output = get_ngram(source=node, offset=offset, limit=limit)
    return ngrams