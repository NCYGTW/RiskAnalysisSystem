"""
公式分析节点
负责分析风险公式结构
"""

import json
from typing import Dict, Any
from .base_node import BaseNode

class FormulaAnalysisNode(BaseNode):
    """公式分析节点"""
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析风险公式结构
        
        Args:
            input_data: 输入数据，包含风险描述和模型项目
            
        Returns:
            分析结果
        """
        risk_description = input_data.get("risk_description", "")
        model_items = input_data.get("model_items", [])
        
        # 构建提示词
        prompt = f"""
请分析以下风险模型公式的结构：

风险描述：{risk_description}

模型涉及项目：
{json.dumps(model_items, ensure_ascii=False, indent=2)}

请分析并输出以下信息：
1. 风险类型识别
2. 涉及的关键财务指标
3. 判断条件分析
4. 数据需求分析

请以JSON格式输出结果。
"""
        
        # 调用LLM进行分析
        analysis_result = self.llm_client.call_llm(prompt)
        
        if analysis_result:
            try:
                # 尝试解析JSON结果
                result = json.loads(analysis_result)
                result["original_risk_description"] = risk_description
                result["model_items"] = model_items
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回原始文本
                return {
                    "original_risk_description": risk_description,
                    "model_items": model_items,
                    "analysis_text": analysis_result
                }
        else:
            # 如果LLM调用失败，返回基本结构
            return {
                "original_risk_description": risk_description,
                "model_items": model_items,
                "analysis_text": "未能分析风险公式结构"
            }