# agent/__init__.py —— 暴露主入口常用的函数
from .core import fc_loop, get_response, run_mode
from .router import auto_select, route_model

__all__ = ["fc_loop", "get_response", "run_mode", "auto_select", "route_model"]
