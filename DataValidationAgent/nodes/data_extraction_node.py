"""
DataExtractionNode
"""

from typing import Dict, Any
from .base_node import BaseNode

class DataExtractionNode(BaseNode):
    """数据提取节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict:
        """
        从数据字典中提取风险验证代码所需的数据
        
        Args:
            input_data: 输入数据，包含生成的Python代码和完整数据字典
            
        Returns:
            提取的数据
        """
        python_code = input_data.get("python_code", "")
        data_dict = input_data.get("data_dict", {})
        
        # 提取公司名称和模型涉及项目
        company_name = data_dict.get("company_name", "")
        model_items = data_dict.get("model_items", [])
        
        extracted_data = {
            "company_name": company_name,
            "model_items": model_items,
            "model_data_by_name_type": {}
        }
        
        # 构建索引
        for item in model_items:
            name = item.get("项目名称", "")
            item_type = item.get("类型", "")
            key = f"{name}_{item_type}"
            extracted_data["model_data_by_name_type"][key] = item
        
        return extracted_data