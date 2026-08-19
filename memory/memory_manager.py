"""
记忆调度，把所有记忆模块拼接寄来，对外暴露对外只暴露 add / get_context / maybe_compress / recall
get_context 里召回结果是临时拼接、不写回 buffer → 避免清单避坑"每次召回都追加 system 导致堆积"
maybe_compress 用 msgs is not self.stm.buffer 判断"真的压了才写回" → 没超阈值不碰 buffer
add_fact 的 fid 用内容哈希 → 稳定、不重复
"""
#memory_manager.py 整合调度，不重写逻辑
from memory.compress import compress, maybe_compress as _auto_compress #导入上下文以压缩
from memory.shortmemory import ShortTermMemory #导入短期记忆
from memory.long_term import LongTermMemory #导入长期记忆
import hashlib

def _fid(text: str) -> str:
    """内容哈希生成稳定ID：不重复、可跨进程（比 hash() 稳，hash有随机盐）"""
    return "f" + hashlib.md5(text.encode("utf-8")).hexdigest()[:12]

class MemoryManager():
    def __init__(self,window=8,max_tokens:int=2000,keep=4,llm=None):
        self.stm=ShortTermMemory(window=window,maxtokens=max_tokens)
        self.ltm=LongTermMemory()   #长期chroma
        self.keep,self.max_tokens,self.llm=keep,max_tokens,llm
    def add(self,msg:dict,persist:bool=False): 
        self.stm.add(msg)
        # 只有明确是用户事实才落长期，persist默认false
        if persist and msg.get("role")=="user":
            self.ltm.add_fact(msg["content"],fid=_fid(msg["content"]))
    #取得上下文，有query才召回，召回将结果临时拼接，不污染buffer
    def get_context(self,query:str=None)->list[dict]:
        base=self.stm.context()#取system和滑动窗口消息
        if not query:
            return base
        facts=self.ltm.recall(query,k=3)
        if not facts:
            return base
        facts_msg={"role":"system","content":"已知用户长期事实："+"|".join(facts)}
        sys_msgs=[m for m in base if m.get("role") in self.stm.system_roles]#取短期里的系统prompt
        others=[m for m in base if m.get("role") not in self.stm.system_roles]
        return sys_msgs+[facts_msg]+others #系统提示+长期事实+窗口
    #超阈值自动压缩 压完写回buffer，下次context取压缩后结果
    def maybe_compress(self,llm=None):
        llm=llm or self.llm
        if llm is None:
            return self.stm.buffer
        msgs=_auto_compress(self.stm.buffer,llm,max_tokens=self.max_tokens,keep=self.keep)
        if msgs is not self.stm.buffer:#真压缩了才写回
            self.stm.buffer=msgs
        return self.stm.buffer
    #给外部用,直接暴露recall
    def recall(self,query:str,k:int=3)->list[str]:
        return self.ltm.recall(query,k=k)