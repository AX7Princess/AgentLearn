import re,json
class MockMsg:
    def __init__(self,content=None,too_calls=None):
        self.content=content
        self.tool_calls=too_calls

class MockResp:
    def __init__(self,msg):
        self.choices=[type("C",(),{"message":msg})()] #self.choices = [...]：将上面这个实例对象放进一个列表里，赋值给 choices

class MockFC:
    def __init__(self,name,arguments):
        self.name=name
        self.arguments=json.dumps(arguments,ensure_ascii=False) #ensure_ascii=False将中文。表情符号等非ascll不转义未\uxxxx形式

class MockTC:
    def __init__(self,i,name,arguments):
        self.id=f"call_{i}"
        self.function=MockFC(name,arguments)

class MockLLM:
    def create(self,**kwargs):
        msgs=kwargs["messages"]
        user_text=next(m["content"] for m in reversed(msgs) if m["role"]=="user")
        has_result=any(m["role"]=="tool" for m in msgs)
        if has_result:
            results=[m["content"] for m in msgs if m["role"]=="tool"]
            return MockResp(MockMsg(content="根据工具返回，最终答案："+"|".join(results)))
        calls=[]
        if "天气" in user_text:
            calls.append(MockTC(len(calls),"get_weather",{"city":"北京"}))
        m=re.search(r"算[一下出]?\s*[0-9+\-*/().\s]+)",user_text)
        if m:
            calls.append(MockTC(len(calls), "calc", {"expr": m.group(1).strip()}))        
        if "死循环" in user_text:      
             calls.append(MockTC(len(calls), "calc", {"expr": "1+1"}))
        if calls:
            return MockResp(MockMsg(content=None, tool_calls=calls))
        return MockResp(MockMsg(content="这是不需要工具的普通回答。"))

def get_weather(city):return f"{city} 台风巴威今天登陆。"  #有实际aip后调用api

def calc(exper):
    if "/0" in exper :raise ValueError("除数为0")
    return str(eval(exper))

def run_tool(name,args):
    try:
        if name=="get_weather":return get_weather(**args)
        if name == "calc":        return calc(**args)
        return f"未知工具:{name}"
    except Exception as e:
        return f"工具执行失败:{e}"  
def run_agent(user_input, llm, tools=None, max_rounds=5):
    messages = [{"role": "user", "content": user_input}]
    for _ in range(max_rounds):
        resp = llm.create(model="any", messages=messages, tools=tools or [])
        msg = resp.choices[0].message
        if not msg.tool_calls:                     
            return msg.content
        # 把 assistant 的 tool_calls 原样加回历史
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": tc.id, "type": "function",
                                         "function": {"name": tc.function.name,
                                                      "arguments": tc.function.arguments}}
                                        for tc in msg.tool_calls]})
        for tc in msg.tool_calls:                   # 同一轮多个工具全部执行
            args = json.loads(tc.function.arguments)
            result = run_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return "达到最大轮数,停止(防死循环)"

# ========== 4. 四个场景一次验证 ==========
mock = MockLLM()
print("场景1 单工具   :", run_agent("北京天气怎么样?", mock))
print("场景2 并行双工具:", run_agent("北京天气怎么样?顺便算一下 23*7+5", mock))
print("场景3 报错自愈  :", run_agent("帮我算一下 10/0", mock))
print("场景4 防死循环  :", run_agent("死循环测试", mock))