# 出错重试 / 参数修复（跨工具通用）
from __future__ import annotations

import time


class ToolExecutor:
    def __init__(self, registry:ToolRegistry, max_retries=2):
        self._registry = registry
        self._max_retries = max_retries

    def execute_with_healing(self, name: str, args: dict) -> str:
        last_err = None  # 记录"最后一次错误"，备用
        for attempt in range(self._max_retries + 1): #max_retries+1 次
            try:
                return self._registry.execute(name, args)   #试执行工具
            except TypeError as e:                     # 模型给错参数键，修复重试
                args = self._repair_args(name, args, e) #修复参数再试
                last_err = e
            except Exception as e:                    # 其他异常 → 重试
                last_err = e
                time.sleep(1)
        return f"[自愈失败] 工具 {name} 重试 {self._max_retries} 次仍失败: {last_err}"

    def _repair_args(self, name, args, err):
        """把模型给的别名参数映射回工具要的键名"""
        alias = {"user_fact": "fact", "preference": "fact",
                 "question": "query", "keyword": "query"}
        return {alias.get(k, k): v for k, v in args.items()} 
    # 如果 k 在 alias 里 → 返回翻译后的名（alias[k]）
    # 如果 k 不在 alias 里 → 返回 k 自己（原样保留，不翻译）    