"""
RiskFormulaParserAgent主类
负责将风险描述转化为Python代码
"""

import json
import os
import logging
from typing import Optional, Dict, Any, List
from llms import OpenRouterLLM, BaseLLM
from nodes import (
    FormulaAnalysisNode,
    CodeGenerationNode,
    ValidationNode
)
from state import RiskAnalysisState
from utils.config import *

class RiskFormulaParserAgent:
    """Risk Formula Parser Agent主类"""
    
    def __init__(self, config: Optional[Config] = config):
        """
        初始化Risk Formula Parser Agent
        
        Args:
            config: 配置对象，如果不提供则自动加载
        """
        # 加载配置
        self.config = config or load_config()
        
        # 初始化LLM客户端
        self.llm_client = self._initialize_llm()
        
        # 初始化节点
        self._initialize_nodes()
        
        # 状态
        self.state = RiskAnalysisState()
        
        # 确保输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        print(f"RiskFormulaParser Agent已初始化")
        print(f"使用LLM: {self.llm_client.get_model_info()}")
    
    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM客户端"""
        return OpenRouterLLM(
            api_key=self.config.openrouter_api_key,
            model_name=self.config.default_model
        )
    
    def _initialize_nodes(self):
        """初始化处理节点"""
        self.formula_analysis_node = FormulaAnalysisNode(self.llm_client)
        self.code_generation_node = CodeGenerationNode(self.llm_client)
        self.validation_node = ValidationNode(self.llm_client)
    
    def parse_risk_formula(self, risk_description: str, model_items: List[Dict]) -> Optional[str]:
        """
        将风险描述转化为Python代码
        
        Args:
            risk_description: 风险描述
            model_items: 模型涉及项目列表
            
        Returns:
            生成的Python代码
        """
        print(f"开始解析风险公式: {risk_description[:50]}...")
        
        try:
            # Step 1: 分析风险公式结构
            analysis_result = self._analyze_formula_structure(risk_description, model_items)
            
            # Step 2: 生成Python代码并添加验证重试机制
            max_retries = 3
            retry_count = 0
            code = None
            validation_result = None
            
            while retry_count < max_retries:
                if retry_count == 0:
                    # 首次生成代码
                    code = self._generate_python_code(analysis_result)
                else:
                    # 重试时使用验证结果改进代码
                    print(f"  - 第{retry_count+1}次重试生成代码...")
                    # 将验证问题和建议添加到分析结果中
                    enhanced_analysis = analysis_result.copy()
                    if validation_result:
                        enhanced_analysis["validation_issues"] = validation_result.get("issues", [])
                        enhanced_analysis["validation_suggestions"] = validation_result.get("suggestions", [])
                    code = self._generate_python_code(enhanced_analysis)
                
                # Step 3: 验证生成的代码
                validation_result = self._validate_generated_code_with_details(code, model_items)
                is_valid = validation_result.get("is_valid", False)
                
                if is_valid:
                    print("风险公式解析成功")
                    return code
                else:
                    retry_count += 1
                    issues = validation_result.get("issues", [])
                    print(f"  - 代码验证失败，问题: {issues}")
                    if retry_count >= max_retries:
                        print(f"已达到最大重试次数({max_retries})，代码验证仍未通过")
                        return None
            
            return None
            
        except Exception as e:
            print(f"解析风险公式时发生错误: {str(e)}")
            return None
    
    def _analyze_formula_structure(self, risk_description: str, model_items: List[Dict]) -> Dict:
        """分析风险公式结构"""
        print("  - 分析风险公式结构...")
        
        # 准备分析输入
        analysis_input = {
            "risk_description": risk_description,
            "model_items": model_items
        }
        
        # 执行分析
        analysis_result = self.formula_analysis_node.run(analysis_input)
        
        print("  - 风险公式结构分析完成")
        return analysis_result
    
    def _generate_python_code(self, analysis_result: Dict) -> str:
        """生成Python代码"""
        print("  - 生成Python代码...")
        
        # 生成代码
        code = self.code_generation_node.run(analysis_result)
        
        print("  - Python代码生成完成")
        return code
    
    def _validate_generated_code(self, code: str, model_items: List[Dict]) -> bool:
        """验证生成的代码"""
        print("  - 验证生成的代码...")
        
        # 准备验证输入
        validation_input = {
            "python_code": code,
            "model_items": model_items
        }
        
        # 执行验证
        validation_result = self.validation_node.run(validation_input)
        
        is_valid = validation_result.get("is_valid", False)
        print(f"  - 代码验证完成: {'通过' if is_valid else '失败'}")
        return is_valid

    def _validate_generated_code_with_details(self, code: str, model_items: List[Dict]) -> Dict:
        """验证生成的代码并返回详细结果"""
        print("  - 验证生成的代码...")
        
        # 准备验证输入
        validation_input = {
            "python_code": code,
            "model_items": model_items
        }
        
        # 执行验证
        validation_result = self.validation_node.run(validation_input)
        
        is_valid = validation_result.get("is_valid", False)
        issues = validation_result.get("issues", [])
        suggestions = validation_result.get("suggestions", [])
        
        print(f"  - 代码验证完成: {'通过' if is_valid else '失败'}")
        if not is_valid:
            print(f"  - 验证问题: {issues}")
            print(f"  - 改进建议: {suggestions}")
        
        return validation_result


def create_agent(config_file: Optional[str] = None) -> RiskFormulaParserAgent:
    """
    创建Risk Formula Parser Agent实例的便捷函数
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        RiskFormulaParserAgent实例
    """
    config = load_config(config_file)
    return RiskFormulaParserAgent(config)