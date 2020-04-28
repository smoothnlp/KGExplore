from kgexplore import client
from kgexplore import config

config.setApiKey("Lr997iJRYYKSEFnN9pDTKdsgQMsIH9AJ")

print(client.get_ngram(target = "刘强东"))

print(client.get_ngram_related(node = "刘强东"))

print(client.search_bigram(text = "红旗H9"))