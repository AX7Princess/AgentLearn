# test_manager.py —— 根目录运行: python test_manager.py
from memory.memory_manager import MemoryManager

class FakeLLM:
    def summarize(self, text):
        return "用户咨询了多款产品退款政策，均支持7天无理由退款"[:60]

mm = MemoryManager(window=8, max_tokens=300, keep=4, llm=FakeLLM())
mm.add({"role": "system", "content": "你是客服助手小M。"})
mm.add({"role": "user", "content": "我喜欢用 DeepSeek"}, persist=True)  # 落长期
for i in range(10):                                                       # 10轮对话
    mm.add({"role": "user", "content": f"问题{i}: 产品{i}的退款政策"})
    mm.add({"role": "assistant", "content": f"回答{i}: 产品{i}支持7天无理由退款"})

ctx = mm.get_context(query="用户偏好什么模型?")
assert any("DeepSeek" in m["content"] for m in ctx), "① 长期召回失败"
assert not any("已知用户长期事实" in m["content"] for m in mm.stm.buffer), "② 污染buffer"
print("① 召回进上下文 ✓  ② 不污染buffer ✓")

mm.maybe_compress()
assert len([m for m in mm.stm.buffer if m.get("is_summary")]) == 1
print(f"③ 压缩后{len(mm.stm.buffer)}条, 摘要1条 ✓")

mm2 = MemoryManager(window=8, max_tokens=300, keep=4)   # 模拟重启
assert mm2.recall("用户偏好什么模型?"), "④ 重启后应能召回"
print("④ 重启后 recall 成功 ✓")

assert any(m["role"] == "system" and not m.get("is_summary") for m in mm.stm.buffer)
print("⑤ 系统提示永留 ✓\n✅ 全部通过")