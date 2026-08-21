"""集中管理所有落盘路径, 避免各处硬编码 './xxx' (相对路径会随 cwd 漂移)."""
# ============ 隐私分流（设计约定, 不是代码自动给的） ============
# 🔒 永远留本地、绝不进 prompt: 用户真实姓名 / 联系方式 / 密钥 / 明文敏感偏好
# 🌐 会发到云端 LLM API: 你主动塞进 system/user 消息的"召回结果"
#     (如"已知用户长期事实: 喜欢 DeepSeek")
# ⚠️ 敏感事实: 存本地, 但召回时不自动进 prompt, 需用户显式确认才带上
# ==============================================================

import os
BASE = os.path.dirname(os.path.abspath(__file__))
MEM_STORE   = os.path.join(BASE, "mem_store")    # Chroma 向量库
PROFILE_DB  = os.path.join(BASE, "memory.db")    # SQLite 用户画像
FACTS_JSON  = os.path.join(BASE, "facts.json")   # 纯本地简单事实
if __name__=="__main__":
    print(BASE,"\n",MEM_STORE,"\n",PROFILE_DB,"\n",FACTS_JSON)