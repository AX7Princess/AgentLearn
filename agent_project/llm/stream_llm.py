# llm/stream_llm.py —— 流式客户端
import os
from openai import OpenAI
from .base import LLMClient, load_provider_config


class StreamLLM(LLMClient):
    def __init__(self, provider="deepseek"):
        cfg = load_provider_config(provider)
        self.client = OpenAI(api_key=os.getenv(cfg["key_env"]),
                             base_url=cfg["base_url"])
        self.model = cfg["model"]

    def chat_stream(self, messages, **kwargs):
        """流式：yield 逐段吐（边收边显示）"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            reasoning_effort=kwargs.get("reasoning_effort", "low"),
            extra_body={"thinking": {"type": "enabled"}},
            max_tokens=kwargs.get("max_tokens", 500),
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:                     # 过滤空 chunk（思考过程不吐）
                yield delta