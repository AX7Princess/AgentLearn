import re,json
class FakeLLm:
    def create(self,**kwargs):
        message=kwargs["message"]
        last=message[-1]
        if last["role"]=="tool":
            return {"choices":[{"message":{"content":"答案是："+last["content"]}}]}
        return{"choices": [{"message": {"tool_calls": [
            {"id": "call_1", "function": {"name": "today", "arguments": "{}"}}
        ]}}]}
def today():
    return "今天是2026年8月10日"
TOOLS = {"today": today}
def agent(question):
    messages=[{"role":"user","content":question}]
    for i in range(2):
        resp=FakeLLm().create(message=messages)
        msg=resp["choices"][0]["message"]
        print(f"第{i+1}轮 模型说：{msg}")
    if "tool_calls" not in msg:
        return msg["content"]

    name=msg["tool_calls"][0]["function"]["name"]
    result =TOOLS[name]()
    print(f"     → 执行工具 {name},得到: {result}")
    messages.append({"role": "assistant", "content": None,"tool_calls": msg["tool_calls"]})
    messages.append({"role": "tool", "tool_call_id": "call_1", "content": result})
    return "达到最大轮数"
print(agent("今天几号"))