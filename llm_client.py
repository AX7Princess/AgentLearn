from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json,os,ast
import urllib.request
from pathlib import Path
load_dotenv(override=True, dotenv_path=find_dotenv())

class LLMClient():
    def chat(self,message,tools=None):
        raise NotImplemented("子类必须实现 chat()")

class RealLLM(LLMClient):
    def __init__(self,provide="deepseek"):
        cfg={
            "deepseek":{"base_url":"https://api.deepseek.com","key":"DEEPSEEK_API_KEY","model":"deepseek-v4-flash"},
            "openai": {"base_url": None, "key": "OPENAI_API_KEY", "model": "gpt-4o-mini"},
        }[provide]
        self.client = OpenAI(api_key=os.getenv(cfg["key"]), base_url=cfg["base_url"])
        print(f"实际使用的 provider={provide}, key 已加载={'是' if os.getenv(cfg['key']) else '否'}")
       # print(repr(os.getenv(cfg["key"])))
        self.model=cfg["model"]
    def chat(self,messages,tools=None):
        return self.client.chat.completions.create(model=self.model,messages=messages,tools=tools)

class FakeMessage:
    def __init__(self,content=None,tool_calls=None):
        self.content,self.tool_calls=content,tool_calls

class FakeChoice:
    def __init__(self,message):
        self.message=message

class FakeResponse:
    def __init__(self, message): self.choices = [FakeChoice(message)]

class FakeFunction:
    def __init__(self, name, arguments):
        self.name, self.arguments = name, arguments


class FakeToolCall:
    def __init__(self, name, arguments):
        self.id = "call_mock_001"
        self.function = FakeFunction(name, arguments)

class MockLLM(LLMClient):
    def chat(self,message,tools=None):
        if message[-1]["role"]=="tool":
            result=message[-1]["content"]
            return FakeResponse(FakeMessage(content=f"模型看到工具结果[{result}]后给出的最终回答"))
        q=message[-1]["content"]
        if "天气" in q:
            return FakeResponse(FakeMessage(tool_calls=[FakeToolCall("get_weather",'{"city":"天津"}')]))
        if "等于" in q or "计算" in q:
            return FakeResponse(FakeMessage(tool_calls=[FakeToolCall("calculator", '{"expr": "1+1"}')]))
        return FakeResponse(FakeMessage(content="Mock回答"))

def run_tool(name,arg):
    try:
        return TOOLS_FUNC[name](**arg)
    except Exception as e:
        return(f"参数出错了:{e}")

def fc_loop(question,llm,max_rounds=3):
   messages=[{"role":"user","content":question}]
   tool_records = []   
   for _ in range(max_rounds):
        rep=llm.chat(messages,tools=TOOLS_SCHEMA)
        msg=rep.choices[0].message
        if not msg.tool_calls:
            return {
                "answer": msg.content,     # 最终答案
                "tool_records": tool_records,   # [] = 没调工具(模型猜的!)
            }
            #return msg.content
        messages.append(msg)
        for tc in msg.tool_calls:
            try:
                arg=json.loads(tc.function.arguments)
            except Exception as e:
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"参数解析失败:{e}"})
                continue
            result=run_tool(tc.function.name,arg)
            tool_records.append({"tool": tc.function.name, "args": arg, "result": result})
            messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
            print(msg)
   return {"answer": "达到最大轮数", "tool_records": tool_records}


   


def get_weather(city:str)->str:#查询天气
    city_encoded = urllib.parse.quote(city)          # 深圳 → %E6%B7%B1%E5%9C%B3
    url = f"https://wttr.in/{city_encoded}?format=3"
      # 返回简短的天气文本
    print(url)
    return urllib.request.urlopen(url).read().decode()

def calculator(expr: str) -> str:#四则运算
    return str(ast.literal_eval(expr))

TOOLS_FUNC = {"get_weather": get_weather, "calculator": calculator}   
TOOLS_SCHEMA = [
    {"type": "function", "function": {"name": "get_weather", "description": "查天气",
     "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "calculator", "description": "四则运算",
     "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}, "required": ["expr"]}}},
]

if __name__=="__main__":
    
    llm = RealLLM("deepseek")
  # 真实 DeepSeek 下问一个同时触发两个工具的问题
    print(fc_loop("天津天气怎么样？顺手算一下 23+5", llm))