# 记忆工具
from .base import BaseTool


class SavePreferenceTool(BaseTool):
    name = "save_preference"
    description = "当用户表达稳定偏好/事实时调用，跨会话记住"
    parameters = {
        "type": "object",
        "properties": {"fact": {"type": "string", "description": "要记住的用户事实"}},
        "required": ["fact"],
    }

    def __init__(self, mm=None):
        self.mm = mm          # 依赖注入：MemoryManager 由外面传入

    def execute(self, fact: str) -> str:
        if self.mm is None:
            return "错误：记忆管理器未注入"
        self.mm.add({"role": "user", "content": fact}, persist=True)  # [1]
        return f"已保存到长期记忆 ✓"