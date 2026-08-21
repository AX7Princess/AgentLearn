# llm/base.py —— LLM 抽象接口
from pathlib import Path
import json

# 配置路径：从"llm/ 的上级目录"找 config.json
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_provider_config(provider: str) -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)["providers"][provider]


class LLMClient:

    def chat(self, messages, tools=None):
        raise NotImplementedError("子类必须实现 chat()")

    def chat_stream(self, messages, **kwargs):
        raise NotImplementedError("子类必须实现 chat_stream()")