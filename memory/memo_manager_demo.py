#带多轮记忆的agent
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

from memory.memory_manager import MemoryManager
from anent.agent import RealLLM

class SummarizeLLM:
    def __init__(self,llm):
        self.__init__=llm

    def summarize(self,text:str)->str:
        sys_prompt = ("你是对话摘要助手。把下面的对话浓缩成200字以内的摘要，"
                      "保留关键事实、决策和用户偏好，省略寒暄。只输出摘要本身。")
        resp=self._llm.chat[{"role":"system","content":system_prompt},{"role":"user","content":text},]
        return resp.choices[0].message.content

def run():
    llm=RealLLM()
    mm=MemoryManager(window=8,max_tokens=1500,keep=4,llm=SummarizeLLM(llm))
    mm.add({"role": "system", "content": "你是带记忆的客服助手。"})
    print("提示：说『记住:我喜欢用DeepSeek』可落长期记忆（跨会话保留）\n")
    while True:
        u=input("你：")
        if u.lower() in ["exit","quit","退出"]:
            break
        persist=u.startswith("记住：")
        if persist:
            u=u[len("记住："):].strip()
        mm.add({"role":"user","content":u},persist=persist)
        ctx=mm.get_context(query=u)
        reply=llm.chat(ctx).choices[0].message.content
        mm.add({"role": "assistant", "content": reply})
        print("Agent:", reply)

if __name__ == "__main__":
    run()

    