"""
ResultValidationNode
验证代码执行结果
"""

from typing import Dict, Any
from .base_node import BaseNode

class ResultValidationNode(BaseNode):
    """结果验证节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        验证代码执行结果
        
        Args:
            input_data: 输入数据，包含代码执行结果
            
        Returns:
            验证结果
        """
        execution_result = input_data.get("execution_result")
        
        # 验证结果是否为布尔值
        is_risk = isinstance(execution_result, bool) and execution_result
        
        return {
            "is_risk": is_risk,
            "execution_result": execution_result
        }