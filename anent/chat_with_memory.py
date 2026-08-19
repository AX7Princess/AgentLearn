# chat_with_memory.py —— 带记忆的 ChatSession（Day5 步骤C）
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.memory_manager import MemoryManager
from agent import RealLLM


class SummarizeLLM:
    """给 RealLLM 包一层 summarize 接口（compress 需要）"""
    def __init__(self, llm):
        self._llm = llm

    def summarize(self, text: str) -> str:
        sys_prompt = ("你是对话摘要助手。把下面的对话浓缩成200字以内的摘要，"
                      "保留关键事实、决策和用户偏好，省略寒暄。只输出摘要本身。")
        resp = self._llm.chat([                                # ← ② self._llm
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": text},
        ])
        return resp.choices[0].message.content                 # ← ③④ 点号 + message单数


class ChatSession:                                             # ← ① 顶格！不在任何类里面
    def __init__(self, system_prompt="你是客服小助手M。"):
        self.llm = RealLLM()
        self.summer = SummarizeLLM(self.llm)
        self.mm = MemoryManager(window=8, max_tokens=1500, keep=4,
                                llm=self.summer)
        self.mm.add({"role": "system", "content": system_prompt})  # ← ⑤ 加system，不是假user

    def chat(self, user_msg: str, persist: bool = False) -> str:
        self.mm.add({"role": "user", "content": user_msg}, persist=persist)
        ctx = self.mm.get_context(query=user_msg)              # 长期召回 + 窗口
        resp = self.llm.chat(ctx)
        reply = resp.choices[0].message.content                # ← ④ message单数
        self.mm.add({"role": "assistant", "content": reply})
        self.mm.maybe_compress()                               # ← ⑥ 不传参！内部用self.mm.llm
        return reply


if __name__ == "__main__":
    bot = ChatSession()
    while True:
        u = input("你: ")
        if u.lower() in ("exit", "quit"):
            break
        print("Agent:", bot.chat(u))