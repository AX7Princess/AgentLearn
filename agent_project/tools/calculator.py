# 计算器工具
from .base import BaseTool
import ast


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "四则运算（如 1+2*3）"
    parameters = {
        "type": "object",
        "properties": {"expr": {"type": "string", "description": "数学表达式"}},
        "required": ["expr"],
    }

    def execute(self, expr: str) -> str:
        try:
            tree = ast.parse(expr, mode="eval")
            # 只允许数字和四则运算，防止模型注入危险代码
            allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                       ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub)
            for node in ast.walk(tree):
                if not isinstance(node, allowed):
                    return f"表达式包含不允许的语法: {type(node).__name__}"
            result = eval(compile(tree, "<string>", "eval"),
                          {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"计算失败: {e}"