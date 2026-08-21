# tools/recall_memory.py
from .base import BaseTool


class RecallMemoryTool(BaseTool):
    name = "recall_memory"
    description = "需要回顾用户历史偏好/事实时调用"
    parameters = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "检索关键词"}},
        "required": ["query"],
    }

    def __init__(self, mm=None):
        self.mm = mm

    def execute(self, query: str) -> str:
        if self.mm is None:
            return "错误：记忆管理器未注入"
        facts = self.mm.recall(query, k=3)          # 召回结果拼回上下文 [1]
        return "；".join(facts) if facts else "（没有找到相关记忆）"