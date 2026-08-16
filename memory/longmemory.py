'''
长期记忆学习文档
长期记忆 = 关电脑也不丢
长期记忆 = 单文档 RAG + 落盘
    嵌入/相似度召回  → 只是把"文档"换成"用户事实"且持久化
pip install chromadb
'''
import chromadb
from pathlib import Path

BASE=Path(__file__).parent

class LongTermMemory:
    def __init__(self,path=str(BASE/"mem_store"),collection="long_term"):
        self.client=chromadb.PersistentClient(path=path) #建客户端(连上本地存储)
        self.col=self.client.get_or_create_collection(collection)# 拿货架(没有就建)

    def add_fact(self,text:str,fid:str): #Chroma 的 add 要求每个参数都是列表（ids=[...]、documents=[...]）——因为 Chroma 的 add 支持批量加。就算你只存一条，也要写成 [fid]、[text]
        self.col.add(ids=[fid],documents=[text])

    def recall(self,query:str,k:int=3)->list[str]:
        res=self.col.query(query_texts=[query],n_results=k)
        return res["documents"][0] if res["documents"] else []

    def delete(self,fid:str):
        self.col.delete(ids=[fid])