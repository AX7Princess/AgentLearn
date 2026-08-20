import json
from Agent.agent  import RealLLM
from memory.memory_manager import MemoryManager

__mm: MemoryManager=None

def set_memory_manager(mm:MemoryManager):
    global __mm
    __mm=mm

def save_preference(fact:str)->str:
    """保存用户偏好的长期记忆模型自主判断"""
    __mm.add({"role":"user","content":fact},persist=True)
    return "已保存到长期记忆"

def reacll_memory(query:str,k=3)->str:
    """从长期记忆力召回相关事实"""
    facts=__mm.recall(query,k=k)
    return ";".join(facts) if facts else "(没找到相关记忆)"


MEMORY_TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "save_preference",
        "description": "当用户说出自己的偏好、个人信息、长期需求时调用，保存到长期记忆",
        "parameters": {"type": "object",
                       "properties": {"fact": {"type": "string", "description": "要记住的用户事实"}},
                       "required": ["fact"]}}},
    {"type": "function", "function": {
        "name": "recall_memory",
        "description": "当用户问起以前说过的事、偏好、个人信息时调用，从长期记忆检索",
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string", "description": "检索关键词"}},
                       "required": ["query"]}}},
]

MEMORY_TOOLS_FUNC = {"save_preference": save_preference,
                     "recall_memory": reacll_memory}