'''
长期记忆学习文档
长期记忆 = 关电脑也不丢
长期记忆 = 单文档 RAG + 落盘
    嵌入/相似度召回  → 只是把"文档"换成"用户事实"且持久化
pip install chromadb
'''
import chromadb
from pathlib import Path
import chromadb, time
from memory.paths import MEM_STORE 
#BASE=Path(__file__).parent

class LongTermMemory:
    def __init__(self, path=MEM_STORE, collection_name="long_term"):
        self.client = chromadb.PersistentClient(path=path)  # 绝对路径
        self.col = self.client.get_or_create_collection(collection_name)

    def add_fact(self, text: str, fid: str, private: bool = False):
        """存一条长期事实。private=True 表示敏感, 召回时默认不出网。"""
        self.col.add(ids=[fid], documents=[text],
                     metadatas=[{"private": private, "ts": time.time()}])

        #Chroma 的 add 要求每个参数都是列表（ids=[...]、documents=[...]）——因为 Chroma 的 add 支持批量加。就算你只存一条，也要写成 [fid]、[text]

    def recall(self,query:str,k:int=3,include_private=False)->list[str]:
        """召回相关事实。默认跳过 private=True 的敏感事实(不进 prompt)。"""
        res=self.col.query(query_texts=[query],n_results=k)
        facts=[]
        for doc,meta in zip(res["documents"][0],res["metadatas"][0]):
            if  meta and meta.get("private") and not include_private:
                continue
            facts.append(doc)
        return facts
    def delete(self,fid:str):
        self.col.delete(ids=[fid])