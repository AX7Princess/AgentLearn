from openai import OpenAI
import os
client=OpenAI(api_key="",base_url="https://api.deepseek.com")
def getcontent(messages,**kwards):
    reasoning_content,content='',''
    response=client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=True,
        reasoning_effort="low",
        extra_body={"thinking":{"type":"enabled"}},
        max_tokens=kwards.get("max_tokens",50)
    )
    for chunk in response:
        delta= chunk.choices[0].delta
        if delta.reasoning_content:
            reasoning_content+=delta.reasoning_content
        if  delta.content:
            content+=delta.content
        if content:
            messages.append({"role": "assistant", "content": content})
        else:
            content=reasoning_content
    return content
messages=[{"role":"system","content":"你是以为思维缜密的小助手"}]

def react_prompt(question,system_prompt="你是位智能小助手",tools="today"):
    u=(
        f"可用工具{tools}\n"
        f"Thought:先根据用户问题想清楚要干什么\n"
        f"Action:调用哪个工具更适合该问题\n"
        f"Action Input:参数\n"
        f"Observation:工具返回结果\n"
        f"Answer:最终回答\n\n问题:{question}"
    )
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":u}
        ]
    return messages

def today():
    return "今天是2026年8月20日"

TOOLS={"today":today}

tools = [{
    "type": "function",
    "function": {
        "name": "today",
        "description": "获取今天的日期",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}]


class FakeLLm:
    def create(self,**kwargs):
            message=kwargs["message"]
            last=message[-1]
            if last["role"]=="tool":
                return {"choices":[{"message":{"content":"答案是："+last["content"]}}]}
            return{"choices": [{"message": {"tool_calls": [
                {"id": "call_1", "function": {"name": "today", "arguments": "{}"}}
            ]}}]}

def agent(question):
    messages=[{"role":"user","content":question}]
    for i in range(2):
        resp=client.chat.completions.create( model="deepseek-v4-flash",
            messages=messages,
            tools=tools,                      # ← 关键:把工具列表传进去
        )
        msg = resp.choices[0].message
        print(f"第{i+1}轮 模型说：{msg}")
    if "tool_calls" not in msg:
        return msg.content

    name=msg["tool_calls"][0]["function"]["name"]
    result =TOOLS[name]()
    print(f"     → 执行工具 {name},得到: {result}")
    messages.append({"role": "assistant", "content": None,"tool_calls": msg["tool_calls"]})
    messages.append({"role": "tool", "tool_call_id": "call_1", "content": result})
    return "达到最大轮数"


def main():
    while True:
        q = input("User: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        print("Agent:", agent(q))

if __name__ == "__main__":
    main()