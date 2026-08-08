from openai import OpenAI
import os
client =OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY")  ,base_url="https://api.deepseek.com")
def get_response(messages,**kwargs):
    response=client.chat.completions.create(model="deepseek-v4-flash",messages=messages,stream=True,reasoning_effort="low",extra_body={"thinking":{"type":"disabled"}},max_tokens=kwargs.get("max_tokens", 500),)
    reasoning_content=""
    content=""
    for chunk in response:
        delta=chunk.choices[0].delta
        if delta.reasoning_content:
            reasoning_content+=delta.reasoning_content
        if delta.content:
            content+=delta.content
    if content:
        messages.append({"role":"assistant","content":content})
    if not content:
        content = reasoning_content 
    return content
messages = [{"role": "system", "content": "你是一个耐心Agent老师，擅长用通俗的语言解释学生提到的问题。请根据问题一步步分析学生当前的学习阶段，给出最适合当前阶段的回答。"}]
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    messages.append({"role":"user","content":user_input})
    response = get_response(messages)
    print("Agent导师:", response)
if __name__ == "__main__": 
    pass