# llm/real_llm.py —— 非流式客户端
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from .base import LLMClient, load_provider_config

# 加载项目根目录的 .env（让 DEEPSEEK_API_KEY 等从文件读取，优先级高于系统环境变量）
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


class RealLLM(LLMClient):
    def __init__(self, provider="deepseek"):
        cfg = load_provider_config(provider)          # 从 config.json 读
        self.client = OpenAI(api_key=os.getenv(cfg["key_env"]),
                             base_url=cfg["base_url"])
        self.model = cfg["model"]
        print(f"实际使用的 provider={provider}, "
              f"key 已加载={'是' if os.getenv(cfg['key_env']) else '否'}")

    def chat(self, messages, tools=None,**kwargs) -> str:
        """普通对话：返回纯文本（demo / 对话循环用）"""
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=tools,max_tokens=kwargs.get("max_tokens"))
        return resp.choices[0].message.content

    def chat_for_tools(self, messages, tools):
        """工具对话：返回完整 message 对象（fc_loop 用，能拿到 tool_calls）"""
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=tools)
        return resp.choices[0].message

    def summarize(self, text: str) -> str:
        """把一段对话文本压缩成简短摘要（记忆压缩模块 compress 调用）"""
        messages = [
            {"role": "system", "content": "你是一个摘要助手。请把下面的对话浓缩成简洁的中文要点，"
                                           "保留关键事实、用户偏好与决策，不要添加新内容。"},
            {"role": "user", "content": text},
        ]
        return self.chat(messages, max_tokens=500)