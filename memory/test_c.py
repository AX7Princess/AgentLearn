# test_c.py —— 验证隐私分流
import sys, os
from memory.long_term import LongTermMemory

lt = LongTermMemory()

# 存一条敏感事实(电话) + 一条普通事实(偏好)
lt.add_fact("用户的手机号是 13800001234", fid="f_phone", private=True)
lt.add_fact("用户喜欢用 DeepSeek 模型",   fid="f_like",  private=False)

print("默认召回(不进 prompt):", lt.recall("用户手机号"))
print("显式允许(可进 prompt):", lt.recall("用户手机号", include_private=True))