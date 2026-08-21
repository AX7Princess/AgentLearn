def ask(llm, question, system_prompt="你是擅长多种角度对比方案的资深决策专家",
        max_tokens=500):
    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    return llm.chat(msgs, max_tokens=max_tokens)


def tot_solve(question, n=3, llm=None):
    """三段式：发散 → 评审 → 决策（三次调用）"""
    if llm is None:
        raise ValueError("tot 模式需要注入 llm")

    schemes = ask(llm,
        f"请针对以下问题给出{n}种不同解决思路,编号列出:\n{question}\n",
        system_prompt="你是擅长发散思维的规划专家", max_tokens=600)
    scores = ask(llm,
        f"请对以下 {n} 个方案根据实行难度,风险评估逐一打分(1-10分),并各用一句话说明理由:\n{schemes}",
        system_prompt="你是严格的评审专家,打分要客观", max_tokens=500)
    best = ask(llm,
        f"综合以下评分,选出最优方案,并给出具体实施步骤:\n{scores}",
        system_prompt="你是决策专家,直接给最终选择", max_tokens=600)
    return schemes, scores, best