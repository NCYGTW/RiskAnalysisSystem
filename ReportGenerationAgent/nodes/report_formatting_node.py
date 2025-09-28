"""
报告格式化
"""

import json
from typing import Dict, Any
from datetime import datetime
from .base_node import BaseNode

class ReportFormattingNode(BaseNode):
    """报告格式化节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> str:
        """  
        Args:
            input_data: 输入数据，包含分析结果、模板和可视化数据
            
        Returns:
            格式化后的报告内容
        """
        analysis_results = input_data.get("analysis_results", [])
        template = input_data.get("template", "")
        visualizations = input_data.get("visualizations", {})
        
        # 统计风险数据
        total_risks = len(analysis_results)
        detected_risks = sum(1 for r in analysis_results if r.get("is_risk", False))
        detection_rate = (detected_risks / total_risks * 100) if total_risks > 0 else 0
        
        # 生成风险详情
        risk_details = ""
        for result in analysis_results:
            risk_status = "存在风险" if result.get("is_risk", False) else "无风险"
            risk_details += f"- {result.get('company_name', '')} - {result.get('risk_category', '')}: {risk_status}\n"
        
        # 生成结论
        conclusions = "根据分析结果，建议关注检测到的高风险项，并采取相应的风险控制措施。"
        
        # 填充模板
        report_content = template.format(
            total_risks=total_risks,
            detected_risks=detected_risks,
            detection_rate=f"{detection_rate:.1f}",
            risk_details=risk_details,
            conclusions=conclusions,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return report_content