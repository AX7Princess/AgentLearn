# test_a2.py —— 测试"绝对路径不漂移"
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 保证从任何目录都能 import

from memory.paths import MEM_STORE, PROFILE_DB
from memory.long_term import LongTermMemory
from memory.profile_store import ProfileStore

print("向量库路径:", MEM_STORE)
print("数据库路径:", PROFILE_DB)

lt = LongTermMemory(path=MEM_STORE)          # 绝对路径
ps = ProfileStore(db_path=PROFILE_DB)        # 绝对路径

# 第 1 次运行时:存一条(如果库里已有,这步会覆盖,无妨)
ps.set_profile("model", "deepseek")
lt.add_fact("用户喜欢 DeepSeek, 回答快", fid="f_test_a2")

# 读回验证
print("画像读回:", ps.get_profile("model"))
print("向量召回:", lt.recall("用户偏好什么模型"))