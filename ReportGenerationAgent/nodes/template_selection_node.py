"""
TemplateSelectionNode
选择报告模板
"""

from typing import Dict, Any
from .base_node import BaseNode

class TemplateSelectionNode(BaseNode):
    """模板选择节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> str:
        """
        选择报告模板
        
        Args:
            input_data: 输入数据，包含分析结果
            
        Returns:
            选定的模板
        """
        analysis_results = input_data.get("analysis_results", [])
        
        return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """
# 风险分析报告

## 执行摘要

本报告对五家企业的财务风险进行了分析与验证。

## 风险概览

- 总风险数: {total_risks}
- 检测到风险数: {detected_risks}
- 风险检测率: {detection_rate}%

## 详细分析

{risk_details}

## 结论与建议

{conclusions}

---
*报告生成时间: {generation_time}*
"""