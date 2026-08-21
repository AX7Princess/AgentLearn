# 路由：选模型 + 选推理模式
def route_model(question: str, default: str = "deepseek") -> str:
    """从用户输入里找模型名,找不到用默认"""
    for name in ["kimi", "deepseek", "qwen", "gpt"]:
        if name in question.lower():
            return name
    return default


def auto_select(question: str, llm=None) -> str:
    """
    判断问题适合哪种推理模式
    升级可选：让 LLM 输出 JSON 再解析，比关键词匹配更稳（防格式漂移）
    """
    if llm is not None:
        text = (f"判断下面用户的问题适合哪种回答，只输出以下之一：cot / few_shot / react / tot。"
                f"规则：需要动手查/调工具用 react；需要多方案权衡用 tot；"
                f"需要解释原因用 cot；需要举例对比用 few_shot。\n问题:{question}")
        out = llm.chat([{"role": "user", "content": text}]).lower()
        for mode in ["tot", "react", "few_shot", "cot"]:
            if mode in out:
                return mode
            
    q = question.lower()
    if any(k in q for k in ["帮我", "执行", "查询", "搜索"]):
        return "react"
    if any(k in q for k in ["如果", "方案", "计划"]):
        return "tot"
    if any(k in q for k in ["比较", "对比", "哪个"]):
        return "few_shot"
    return "cot"   # 默认