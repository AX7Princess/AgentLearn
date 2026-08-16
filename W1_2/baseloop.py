import json
from openai import OpenAI
import os
def get_weather(city:str)->str: 
    #天气实际查询函数
    return f"{city}"+"今天台风，注意安全"

# 注册工具
tools=[ 
    {
        "type":"function","function":{
            "name":"get_weather","description":"获取指定城市天气","parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string"
                    }
                },
                 "required":["city"]
                    }
            }
        }  
]
messages=[{"role":"user","content":"今天北京天气怎么样"}]
client=OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")
res=client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    tools=tools,
    max_tokens=100,
)
msg=res.choices[0].message
try:
    print("msg:type",type(msg),"\n\n",msg)
except:
    print("无法打印")
if msg.tool_calls:
    messages.append(msg)
    for tc in msg.tool_calls:
        result=get_weather(**json.loads(tc.function.arguments))
        try:
            print("result:"+result+"\n")
        except Exception as e:
            print("result无法打印",e)
        messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
    final=client.chat.completions.create(model="deepseek-v4-flash", messages=messages, tools=tools)
    print(final.choices[0].message.content)