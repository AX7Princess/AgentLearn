import json
from .modes import BUILDERS


def fc_loop(llm, messages, registry, executor, max_rounds=3):
    """
    Function Calling 主循环
    1. llm.chat_for_tools 返回 message 对象 → 能拿到 tool_calls（原 rep.choices[0].message）
    2. registry.get_schemas() 从 config.json 动态生成 schema（原 TOOLS_SCHEMA 写死）
    3. executor.execute_with_healing 带自愈 → 替代原 run_tool 的裸 try/except [2]
    """
    tool_records = []
    for _ in range(max_rounds):
        msg = llm.chat_for_tools(messages, registry.get_schemas())
        if not msg.tool_calls:
            # 模型没调工具 → 返回答案 + 记录（[] = 模型可能是在猜，原警告逻辑 [2]）
            return {"answer": msg.content, "tool_records": tool_records}
        messages.append(msg)
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception as e:
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": f"参数解析失败:{e}"})
                continue
            result = executor.execute_with_healing(tc.function.name, args)  # 自愈执行
            tool_records.append({"tool": tc.function.name, "args": args, "result": result})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
    return {"answer": "达到最大工具轮数", "tool_records": tool_records}


def get_response(msgs, llm, **kw):
    """调 LLM 生成回复（原 get_response [2]）"""
    return llm.chat(msgs, **kw)


def run_mode(mode, question, llm, builders=None, **kw):
    """按模式调度：查注册表 → 构造消息 → 调 LLM（原 run_mode [2]）"""
    builders = builders or BUILDERS
    if mode not in builders:
        raise ValueError(f"未知模式:{mode},可选 {list(builders)}")
    msgs = builders[mode](question, **kw)
    return get_response(msgs, llm, **kw)