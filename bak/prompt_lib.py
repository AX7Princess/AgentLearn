from openai import OpenAI
from llm_client import fc_loop, RealLLM
import os

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def get_response(messages,**kwargs):
    response = client.chat.completions.create(
        model=kwargs.get("model","deepseek-v4-flash"),
        messages=messages,
        stream=True,
        reasoning_effort=kwargs.get("reasoning_effort","low"),
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

def ask(quextion,system_prompt="你是擅长多种角度对比方案的资深决策专家",max_tokens=500):
    msgs=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": quextion}
    ]
    response = get_response(msgs, max_tokens=max_tokens)
    return response

def tot_solve(question,n=3):
    schemes=ask(
        f"请针对以下问题给出{n}种不同解决思路，编号列出：\n{question}\n",
        system_prompt="你是擅长发散思维的规划专家",
        max_tokens=600,
    )
    scores = ask(
        f"请对以下 {n} 个方案根据实行难度，风险评估逐一打分(1-10分),并各用一句话说明理由:\n{schemes}",
        system_prompt="你是严格的评审专家,打分要客观",
        max_tokens=500,
    )
    best = ask(
        f"综合以下评分,选出最优方案,并给出具体实施步骤:\n{scores}",
        system_prompt="你是决策专家,直接给最终选择",
        max_tokens=600,
    )
    return schemes, scores, best

def cot_prompt(question,system_prompt="你是一个逻辑缜密，思维严谨的推理助手"):
    u=f"请一步步思考，再给出答案。\n问题:{question}"
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": u}]

DEFAULT_EXAMPLES = [
    {"question": "我明天下午3点约了张医生复诊",
     "answer": "时间:明天下午3点;人物:张医生;事项:复诊"},
    {"question": "周五晚上和李总在望江楼吃饭",
     "answer": "时间:周五晚上;人物:李总;事项:吃饭"},
]

def few_shot_prompt(question,examples=DEFAULT_EXAMPLES,system_prompt="你是擅长信息抽取的助手") :
    msgs=[{"role":"system","content":system_prompt}]
    for ex in examples:
        msgs.append({"role":"user","content":ex["question"]})
        msgs.append({"role":"assistant","content":ex["answer"]})
    msgs.append({"role":"user","content":question})
    return msgs

def react_prompt(question,system_prompt="你是以为多种能小助手",tools="搜索引擎、计算器"):
   # u=(f"可用工具:{tools}。严格按格式回答：\n"
    #   f"Thought:先根据用户问题想清楚要干什么\n"
   #    f"Action:调用哪个工具更适合该问题\n"
   #    f"Action Input:参数\n"
   #    f"Observation:工具返回结果\n"
   #    f"Answer:最终答案\n\n问题:{question}"     
   # )
    #return [{"role": "system", "content": system_prompt}, {"role": "user", "content": u}]
    return fc_loop(question, RealLLM("deepseek")) 

BUILDERS = {"cot": cot_prompt, "few_shot": few_shot_prompt, "react": react_prompt}


def auto_select(question):
    content=f"判断下面用户的问题适合哪种回答，输出格式：cot_prompt或few_shot_prompt或react_prompt或tot_solve)\n规则:注重结果中间思考过程的任务，逻辑推理，数学解题过程，公式推导输出cot_prompt,格式固定模板化输出的，文本提取特定词汇格式化输出的输出Few_shot_prompt,需要依赖其他工具的输出react_prompt,开放性问题，思维发散问题，思维风暴，多种选择多种路径实现，多选择对比找最优解决方案输出tot_solve\n问题:{question}"
    msgs = get_response([{"role": "user", "content": content}], max_tokens=50)
    print(f"[调试] 原始: {msgs!r}")
    text = msgs.lower()
    for mode in ["tot", "react", "few_shot", "cot"]:    # 顺序:先长的后短的?不,注意下面
        if mode in text:
            return mode
    print("[警告] 未识别到模式名,兜底 cot")
    return "cot"

def run_mode(mode,question,**kw):
    if mode =="tot":
        schemes, scores, best = tot_solve(question, n=kw.get("n", 3))
        return f"【方案】\n{schemes}\n\n【评审】\n{scores}\n\n【决策】\n{best}"
    if mode =="react":
        out = react_prompt(question) 
        if out["tool_records"]:
        # 展示调用记录
            print("工具调用记录:", out["tool_records"])
        else:
         # ⚠️ 模型没调工具,可能是在猜(幻觉风险)
            print("警告:模型未调用任何工具,回答可能为模型推断")
        return out["answer"]
         #return fc_loop(question, RealLLM("deepseek")) 
    if mode not in BUILDERS:
          raise ValueError(f"未知模式:{mode},可选 {list(BUILDERS) + ['tot']}")
    msgs = BUILDERS[mode](question, **kw)
    return get_response(msgs, **kw)         
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    mode = auto_select(user_input) 
    print(f"[使用模式] {mode}")
    result = run_mode(mode, user_input)     # ② 按模式调度(统一返回字符串)
    print("Agent导师:", result)     