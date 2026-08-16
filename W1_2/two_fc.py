from openai import OpenAI
from dotenv import load_dotenv
import json,os,ast
import urllib.request
load_dotenv()  
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url="https://api.deepseek.com")
TOOLS_FUNC=[
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
                }, 
     {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "四则运算,传入表达式如 '23*7+5'",
            "parameters": {
                "type": "object",
                "properties": {"expr": {"type": "string"}},
                "required": ["expr"],
            }
        }
    },
]


def get_weather(city:str)->str:#查询天气
    city_encoded = urllib.parse.quote(city)          # 深圳 → %E6%B7%B1%E5%9C%B3
    url = f"https://wttr.in/{city_encoded}?format=3"
      # 返回简短的天气文本
    return urllib.request.urlopen(url).read().decode()

def calculator(expr: str) -> str:#四则运算
    return str(ast.literal_eval(expr))

def fc_loop(question,max_tokens=100,max_runds=3):
    messages=[{"role":"user","content":question}]
    for _ in range(max_runds):
        rep=client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                tools=TOOLS_FUNC,
                max_tokens=max_tokens,
            )
        msg=rep.choices[0].message
        '''
        如果llm返回了toolcalls就提取需要的字段，如果没返回，就将内容返回给大模型再次尝试取得函数信息
        '''
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for tc in msg.tool_calls:
            # 拿到大模型调用函数返回的参数
            try:
                arg=json.loads(tc.function.arguments)#json将工具调用返回的str转换为dir
                print(arg)
            except Exception as e:
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"参数解析失败:{e}"})
                print(e)
                continue
            result=run_status(tc.function.name,arg)
            messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
    return print("出错啦，已至最大请求轮数")
TOOLS_FC = {
    "get_weather": get_weather,
    "calculator": calculator,  }
def run_status(name:str,args:dict)->str:
    try:        
        if name not in TOOLS_FC:
            return  f"未知工具:{name}"
        return TOOLS_FC[name](**args)
    except Exception as e:
        return f"工具调用失败:{e}"
    
def run():
   while True:
        user_input=input("user:")
        print("输入exit或者quit退出\n")
        if user_input.strip().lower() in ["exit","quit"]:
           break
        print(fc_loop(user_input))
if __name__=="__main__":
    print(run())