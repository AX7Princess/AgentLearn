# 读 config.json 动态注册工具
import json, importlib
from .base import BaseTool


class ToolRegistry:
    def __init__(self, config_path: str, deps: dict = None):
        self._deps = deps or {}          # 依赖注入：{"mm": MemoryManager实例}
        self._tools = {}
        with open(config_path, encoding="utf-8") as f:
            self._config = json.load(f)

    def register_all(self):
        """按 config.json 的 tools 列表加载所有工具
        self._tools     类型: dict
                内容: {
                    "get_weather": <WeatherTool对象>,
                    "save_fact":   <SaveFactTool对象>
               }       
        """
        for item in self._config.get("tools", []): # item类型: dict      → {"module": "tools.weather", "class": "WeatherTool"}
            mod = importlib.import_module(item["module"])   # 按路径导入模块 类型: module    → <module 'tools.weather' from '.../tools/weather.py'>
            cls = getattr(mod, item["class"])               # 取类 类型: type(类)  → <class 'tools.weather.WeatherTool'>
            tool = cls(**self._deps)                        # 实例化（注入依赖）
            self._tools[tool.name] = tool
        return self

    def get_schemas(self): 
        """给 LLM 的说明书，返回openai可读的格式"""
        return [{"type": "function", "function": {
            "name": t.name, "description": t.description, "parameters": t.parameters,
        }} for t in self._tools.values()]

    def execute(self, name: str, args: dict) -> str:
        #查表执行
        if name not in self._tools:
            return f"未注册的工具: {name}"
        return self._tools[name].execute(**args) #  查到 → 调工具实例的 execute