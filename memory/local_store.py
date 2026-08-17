"""
本地文件存储
"""
import json,os
from memory.paths import FACTS_JSON
def local_facts(path=FACTS_JSON):
    if os.path.exists(path):
        with open(path,encoding="utf-8") as f:
            return json.load(f)

    return {}

def save_fact(k,v,path=FACTS_JSON):
    d=local_facts(path)
    d[k]=v
    with open(path,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
    return d

if __name__=="__main__":
    save_fact("them","浅色模式")
    print("读回",local_facts())