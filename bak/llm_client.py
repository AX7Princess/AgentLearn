from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json,os,ast
import urllib.request
from pathlib import Path
import openmeteo_requests
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
            print(arg)
            tool_records.append({"tool": tc.function.name, "args": arg, "result": result})
            messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
          #  print(msg)
   return {"answer": "达到最大轮数", "tool_records": tool_records}


   


def get_weather(latitude:float,longitude:float)->str:#查询天气
    openmeteo = openmeteo_requests.Client()
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={latitude}"
           f"&longitude={longitude}"
           f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
           f"&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
           f"&timezone=Asia%2FShanghai")
    data = json.loads(urllib.request.urlopen(url).read())
    WEATHER_CODE_DESC = {
    0: "晴朗的天空",
    1: "主要晴朗",
    2: "局部多云",
    3: "阴天",
    45: "雾气",
    48: "霜雾沉积",
    51: "毛毛雨：轻度",
    53: "毛毛雨：中度",
    55: "毛毛雨：密集",
    56: "冻毛毛雨：轻微",
    57: "冻毛毛雨：强度高",
    61: "降雨：轻度",
    63: "降雨：中度",
    65: "降雨：强雨",
    66: "冻雨：轻度",
    67: "冻雨：强烈",
    71: "降雪量：轻度",
    73: "降雪量：中度",
    75: "降雪量：重度",
    77: "雪粒",
    80: "阵雨：轻度",
    81: "阵雨：中度",
    82: "阵雨：猛烈",
    85: "雪阵阵：轻微",
    86: "雪阵阵：猛烈",
    95: "雷暴：轻度或中度",
    96: "雷暴伴轻微冰雹",
    99: "雷暴伴强烈冰雹",
    }
    cur = data["current"]
    today = {k: v[0] for k, v in data["daily"].items()}
    return json.dumps({
        "天气": WEATHER_CODE_DESC.get(today["weather_code"], f"未知天气码{today['weather_code']}"),
        "当前温度_C": cur["temperature_2m"],
        "湿度_%": cur["relative_humidity_2m"],
        "今日最高_C": today["temperature_2m_max"],
        "今日最低_C": today["temperature_2m_min"],
        "日出": today["sunrise"][11:16],
        "日落": today["sunset"][11:16],
        "降雨概率_%": today["precipitation_probability_max"],
    }, ensure_ascii=False)
  #  print(result)
    return result
    #city_encoded = urllib.parse.quote(city)          # 深圳 → %E6%B7%B1%E5%9C%B3
    #url = f"https://wttr.in/{city_encoded}?format=3"
      # 返回简短的天气文本
   # print(url)
   #return urllib.request.urlopen(url).read().decode()


def calculator(expr: str) -> str:#四则运算“
    return str(ast.literal_eval(expr))

TOOLS_FUNC = {"get_weather": get_weather, "calculator": calculator}   
TOOLS_SCHEMA = [
    {"type": "function", "function": {"name": "get_weather", "description": "查天气",
     "parameters": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "required": ["latitude", "longitude"]}}},
    {"type": "function", "function": {"name": "calculator", "description": "四则运算",
     "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}, "required": ["expr"]}}},
]

if __name__=="__main__":
    
    llm = RealLLM("deepseek")
  # 真实 DeepSeek 下问一个同时触发两个工具的问题
    print(fc_loop("天津天气怎么样？", llm))
   # get_weather(39.08,117.20)