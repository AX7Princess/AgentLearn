# test_e2e.py —— 端到端：不压(正确) + 压(正确) + 召回 + 系统提示永留
from memory.memory_manager import MemoryManager

class FakeSummarize:
    def __init__(self):
        self.count = 0
    def summarize(self, text):
        self.count += 1
        return "历史浓缩: 用户咨询了多款产品退款政策，均支持7天无理由退款"

# ===== 场景1：没超阈值 → 不该压（验证"不压"是正确行为）=====
mm = MemoryManager(window=8, max_tokens=2000, keep=4, llm=FakeSummarize())
mm.add({"role": "system", "content": "你是客服助手小M。"})
mm.add({"role": "user", "content": "我叫小明，喜欢蓝色"}, persist=True)  # 落长期
for i in range(20):
    mm.add({"role": "user", "content": f"问题{i}: 产品{i}退款政策"})
    mm.add({"role": "assistant", "content": f"回答{i}: 支持7天无理由"})
    mm.maybe_compress()
assert len([m for m in mm.stm.buffer if m.get("is_summary")]) == 0
print(f"✓ 场景1 没超阈值不压: {len(mm.stm.buffer)}条, 摘要0条(正确!)")

# ===== 场景2：超阈值 → 该压（把阈值调小到300，20轮必超）=====
mm2 = MemoryManager(window=8, max_tokens=300, keep=4, llm=FakeSummarize())
mm2.add({"role": "system", "content": "你是客服助手小M。"})
for i in range(20):
    mm2.add({"role": "user", "content": f"问题{i}: 产品{i}退款政策"})
    mm2.add({"role": "assistant", "content": f"回答{i}: 支持7天无理由"})
    mm2.maybe_compress()
sum_cnt = len([m for m in mm2.stm.buffer if m.get("is_summary")])
assert sum_cnt == 1, f"场景2 摘要应=1, 实际{sum_cnt}"
print(f"✓ 场景2 超阈值自动压: {len(mm2.stm.buffer)}条, 摘要{sum_cnt}条")

# ===== 场景3：早期信息靠长期召回（重启后）=====
mm3 = MemoryManager(window=8, max_tokens=2000, keep=4)
assert mm3.recall("用户叫什么名字?"), "场景3 早期信息(长期召回)丢失!"
print("✓ 场景3 重启后 recall 早期信息成功")

# ===== 场景4：系统提示永留 =====
sys_ok = any(m["role"] == "system" and not m.get("is_summary")
             for m in mm2.stm.buffer)
assert sys_ok, "场景4 系统提示被压掉了!"
print("✓ 场景4 系统提示永留")

print("\n✅ 端到端全部通过")