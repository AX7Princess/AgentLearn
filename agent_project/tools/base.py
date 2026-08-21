class BaseTool:
    name: str = ""              # 工具名（模型调用时用）
    description: str = ""       # 给模型看的说明（决定它会不会调）
    parameters: dict = {}       # JSON Schema（声明参数格式）

    def __init__(self, **kwargs):
        pass   # 允许注册时传入 mm=... 等依赖，不需要的工具直接忽略

    def execute(self, **kwargs) -> str:
        raise NotImplementedError("子类必须实现 execute()")