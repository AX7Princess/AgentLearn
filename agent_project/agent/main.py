# main.py —— 组装所有层
import sys
from pathlib import Path

# 让 agent/main.py 直接运行时也能找到项目根目录的 llm/memory/tools 包
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm import RealLLM
from memory import MemoryManager
from tools import ToolRegistry, ToolExecutor
from agent import fc_loop, auto_select

llm = RealLLM("deepseek")
mm = MemoryManager(window=8, max_tokens=1500, keep=4, llm=llm)
registry = ToolRegistry(str(PROJECT_ROOT / "config.json"), deps={"mm": mm}).register_all()
executor = ToolExecutor(registry)

while True:
    u = input("你: ")
    if u.lower() == "exit":
        break
    mm.add({"role": "user", "content": u}, persist=u.startswith("记住:"))
    ctx = mm.get_context(query=u)
    out = fc_loop(llm, ctx, registry, executor)   # 返回 {"answer", "tool_records"}
    mm.add({"role": "assistant", "content": out["answer"]})
    mm.maybe_compress()
    print("Agent:", out["answer"])