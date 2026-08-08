from openai import OpenAI
client =OpenAI(api_key="sk-fd111bbe5e6c44bdbb833c444ee171c3",base_url="https://api.deepseek.com")
message=[{"role":"user","content":"你是哪个大模型"}]
response=client.chat.completions.create(model="deepseek-v4-flash",messages=message,stream=True,reasoning_effort="low",extra_body={"thinking":{"type":"enabled"}},max_tokens=200,)
reasoning_content=""
content=""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content+=chunk.choices[0].delta.reasoning_content
    if chunk.choices[0].delta.content: 
        content +=chunk.choices[0].delta.content

message.append({"role":"assistant","reasoning_content":reasoning_content,"content":content})
message.append({"role":"user","content":"0.9+0.3是多少"})
response=client.chat.completions.create(model="deepseek-v4-flash",messages=message,stream=True,reasoning_effort="low",extra_body={"thinking":{"type":"enabled"}},max_tokens=200,)
for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content+=chunk.choices[0].delta.reasoning_content
    if chunk.choices[0].delta.content: 
        content +=chunk.choices[0].delta.content
print("reasoning_content:",reasoning_content)
print("content:",content)