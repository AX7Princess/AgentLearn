# memory/test_compress.py —— 无需 API key，本地直接跑
from compress import compress, maybe_compress

class FakeLLM:
    """假的 summarize：直接截断，模拟 LLM 效果。生产换真实 LLM。"""
    def __init__(self):
        self.call_count = 0
    def summarize(self, text: str) -> str:
        self.call_count += 1
        t = " ".join(text.split())
        return t[:80] + ("…" if len(t) > 80 else "")

def make_dialog(rounds: int) -> list[dict]:
    msgs = [{"role": "system", "content": "你是客服助手小M。"}]
    for i in range(rounds):
        msgs.append({"role": "user", "content": f"问题{i}：我想了解产品{i}的退款政策"})
        msgs.append({"role": "assistant", "content": f"回答{i}：产品{i}支持7天无理由退款。"})
    return msgs

llm = FakeLLM()

# 测试1：21 条 → 6 条（system + 1摘要 + 4原文）
msgs = make_dialog(10)
out = compress(msgs, llm, keep=4)
assert len(out) == 6, f"期望6条, 实际{len(out)}"
print(f"✓ 测试1 压缩生效: {len(msgs)}条 → {len(out)}条")

# 测试2：摘要只有一条
assert len([m for m in out if m.get("is_summary")]) == 1
print("✓ 测试2 摘要只有一条")

# 测试3：继续聊 4 轮再压 → 摘要仍只有一条（滚动合并）
out2 = compress(out + make_dialog(4)[1:], llm, keep=4)
assert len([m for m in out2 if m.get("is_summary")]) == 1
print(f"✓ 测试3 滚动摘要: 压两次摘要仍1条 (LLM共调用{llm.call_count}次)")

# 测试4：没超阈值 → 不压（原样返回）
short = make_dialog(1)
assert maybe_compress(short, llm, max_tokens=200, keep=4) is short
print("✓ 测试4 没超阈值 → 原样返回")

# 测试5：超阈值 → 自动压缩
long = make_dialog(10)
out4 = maybe_compress(long, llm, max_tokens=200, keep=4)
assert len(out4) == 6
print(f"✓ 测试5 超阈值 → 自动压缩: {len(long)}条 → {len(out4)}条")

print("\n✅ 全部通过")