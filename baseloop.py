import json
from openai import OpenAI
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
messages=[{"role":"suer","content":"今天北京天气怎么样"}]
client=OpenAI(api_key=os.getenv(),base_url="https://api.deepseek.com")
res=client.chat.completions.create(
    model="deep-seek-v4-flash",
    messages=messages,
    max_tookens=100,
)
