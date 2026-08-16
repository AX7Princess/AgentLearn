import pytest
from short_term import ShortTermMemory

# ── ① 窗口测试:滑动窗口只回最近 N 条,且不改 buffer ──
def test_window_returns_recent():
    mem = ShortTermMemory(window=3)
    mem.add({"role": "system", "content": "你是Agent"})
    for i in range(10):                      # 聊 10 轮 = 20 条
        mem.add({"role": "user", "content": f"第{i}轮"})
        mem.add({"role": "assistant", "content": f"回答{i}"})

    ctx = mem.context()

    # 系统提示永留
    assert ctx[0]["role"] == "system"
    # 非系统消息只回最近 3 条
    non_sys = [m for m in ctx if m["role"] != "system"]
    assert len(non_sys) == 3
    # 最新一条在窗口里
    assert non_sys[-1]["content"] == "回答9"
    # 第 0 轮已滑出窗口
    assert non_sys[0]["content"] != "第0轮"
    # ★ 关键:窗口不改 buffer! buffer 还是全量(1系统 + 20条)
    assert len(mem.buffer) == 21

# ── ② 裁剪测试:超 token 真删,但系统提示一个不少 ──
def test_trim_keeps_system_and_shrinks():
    mem = ShortTermMemory(max_tokens=100)
    mem.add({"role": "system", "content": "红线"})
    for i in range(20):
        mem.add({"role": "user", "content": "超长文本" * 50})   # 每条约 66 token

    before = len(mem.buffer)
    mem.trim()
    after = len(mem.buffer)

    assert after < before                                  # buffer 真变短了
    assert mem._tokens(mem.buffer) <= 100                  # token 合规
    sys_count = [m for m in mem.buffer if m["role"] == "system"]
    assert len(sys_count) == 1                             # 系统提示一个没少

# ── ③ 不崩测试:极端情况不报错 ──
def test_trim_no_crash():
    mem = ShortTermMemory()
    mem.trim()                             # 空 buffer 不崩
    mem.add({"role": "system", "content": "只有系统"})
    mem.trim()                             # 只剩系统不被删
    assert len(mem.buffer) == 1

# ── ④ 进阶:系统消息不在开头也能保留 ──
def test_system_anywhere_preserved():
    mem = ShortTermMemory(window=2)
    mem.add({"role": "user", "content": "先说话"})
    mem.add({"role": "system", "content": "规则"})    # 系统夹在中间
    mem.add({"role": "user", "content": "后说话"})
    ctx = mem.context()
    roles = [m["role"] for m in ctx]
    assert roles.count("system") == 1     # 无论在哪,系统消息都保留