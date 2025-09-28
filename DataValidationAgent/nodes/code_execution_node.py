"""
CodeExecutionNode
负责执行生成的Python代码
"""

from typing import Dict, Any
from .base_node import BaseNode

class CodeExecutionNode(BaseNode):
    """代码执行节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Any:
        """
        执行生成的Python代码
        
        Args:
            input_data: 输入数据，包含Python代码和提取的数据
            
        Returns:
            代码执行结果
        """
        python_code = input_data.get("python_code", "")
        extracted_data = input_data.get("extracted_data", {})
        
        try:
            # 构建安全的执行环境
            safe_globals = {
                '__builtins__': {
                    'abs': abs,
                    'min': min,
                    'max': max,
                    'round': round,
                    'len': len,
                    'sum': sum,
                    'any': any,
                    'all': all,
                    'bool': bool,
                    'int': int,
                    'float': float,
                    'str': str,
                    'ValueError': ValueError,
                    'KeyError': KeyError,
                    'TypeError': TypeError,
                    'IndexError': IndexError,
                    'ZeroDivisionError': ZeroDivisionError,
                    'AttributeError': AttributeError,
                    'Exception': Exception,
                    '__import__': __import__
                }
            }
            
             #执行代码
            exec(python_code, safe_globals)
            
            if 'check_risk' in safe_globals:
                result = safe_globals['check_risk'](extracted_data)
                return result
            else:
                raise Exception("代码中未找到check_risk函数")
                
        except Exception as e:
            print(f"执行代码时出错: {str(e)}")
            return None