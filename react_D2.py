from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def get_response(messages, **kwargs):
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        stream=True,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "enabled"}},
        max_tokens=kwargs.get("max_tokens", 500),
    )
    reasoning_content, content = "", ""
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.reasoning_content:
            reasoning_content += delta.reasoning_content
        if delta.content:
            content += delta.content
    if content:
        messages.append({"role": "assistant", "content": content})
    else:
        content = reasoning_content
    return content

def few_shot_prompt(system_prompt, examples, question):
    """结构:system + 示例对(user/assistant) + 真实问题"""
    messages = [{"role": "system", "content": system_prompt}]
    for ex in examples:                          # ← 修 Bug1:遍历字典
        messages.append({"role": "user", "content": ex["question"]})
        messages.append({"role": "assistant", "content": ex["answer"]})
    messages.append({"role": "user", "content": question})   # ← 修 Bug3/4:真实问题
    return messages
system_prompt = "你是一个信息抽取助手,逐句分析用户输入,严格按格式输出:时间:xxx;人物:xxx;事项:xxx"
examples = [
    {"question": "2023年5月1日,张三在北京参加了一个科技大会。",
     "answer": "时间:2023年5月1日;人物:张三;事项:在北京参加了一个科技大会。"},
    {"question": "李四于2022年12月25日拜访了上海的朋友。",
     "answer": "时间:2022年12月25日;人物:李四;事项:拜访了上海的朋友。"},
]
def react_prompt(system_prompt,question,tools="搜索引擎、计算器"):
    u=(f"可用工具：{tools}。请严格按格式回答\n"
       f"Thought:我先想清楚要干什么\n"
       f"Action:调用哪个工具\n"
       f"Action Input:参数\n"
       f"Observation:工具返回的结果\n"
       f"Answer:最终回答\n\n问题:{question}"
    )
    return [{"role":"system","content":system_prompt},{"role":"user","content":u}]

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    #msgs = few_shot_prompt(system_prompt, examples, user_input)   # ← 传 question
    msgs = react_prompt("你现在是可以调用工具的助手了", user_input)
    response = get_response(msgs)
    print("Agent导师:", response)