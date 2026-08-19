class ShortTermMemory:
    def __init__(self,window=10,maxtokens:int=500,system_roles=("system",)):
        self.window=window #聊天窗口大小
        self.maxtokens=maxtokens #最大tokens
        self.system_roles=system_roles 
        self.buffer=[] #消息缓存

    def _tokens(self,msgs) ->int: # 估算token数
        return sum(max(1,len(m.get("content",""))//3)for m in msgs) #1 个 token ≈ 3~4 个英文字符（约 0.75 个英文单词）

    def add(self,msg:dict):#消息缓存
        self.buffer.append(msg)

    def context(self)->list[dict]: # 返回最近n条消息，滑动窗口
        sys_msgs=[m for m in self.buffer if m.get("role") in self.system_roles]
        others=[m for m in self.buffer if m.get("role") not in self.system_roles]
        return sys_msgs+others[-self.window:]
        
    def trim(self): #消息裁剪
        sys_msgs= [m for m in self.buffer if m.get("role") in self.system_roles]
        others =[m for m in self.buffer if m.get("role") not in self.system_roles]
        while self._tokens(others) >self.maxtokens and len(others)>1:
            others.pop(0)
        self.buffer=sys_msgs+others
        return self.buffer
        
