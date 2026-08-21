# agent/modes/cot.py —— 思维链（把原 agent.py 的 cot_prompt 搬进来 [2]）
def cot_prompt(question: str) -> list[dict]:
    return [
        {"role": "system", "content": "你是擅长逐步推理的专家,请一步一步思考,先列思路再给结论。"},
        {"role": "user", "content": question},
    ]