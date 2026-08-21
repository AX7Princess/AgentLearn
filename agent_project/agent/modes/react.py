def react_prompt(question, system_prompt="你是会调用工具的智能助手，"
                 "需要查询/计算/记忆时调用工具，并把工具结果结合进回答。"):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]