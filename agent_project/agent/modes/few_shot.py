# agent/modes/few_shot.py —— 少样本：纯消息构造（原 few_shot_prompt [2]）
DEFAULT_EXAMPLES = [
    {"question": "我明天下午3点约了张医生复诊",
     "answer": "时间:明天下午3点;人物:张医生;事项:复诊"},
    {"question": "周五晚上和李总在望江楼吃饭",
     "answer": "时间:周五晚上;人物:李总;事项:吃饭"},
]

def few_shot_prompt(question, examples=DEFAULT_EXAMPLES,
                    system_prompt="你是擅长信息抽取的助手"):
    msgs = [{"role": "system", "content": system_prompt}]
    for ex in examples:
        msgs.append({"role": "user", "content": ex["question"]})
        msgs.append({"role": "assistant", "content": ex["answer"]})
    msgs.append({"role": "user", "content": question})
    return msgs