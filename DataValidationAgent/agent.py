"""
DataValidationAgent主类
负责数据验证和风险代码执行
"""

import json
import logging
from typing import Optional, Dict, Any, List
from .nodes import (
    DataExtractionNode,
    CodeExecutionNode,
    ResultValidationNode
)
from .state import RiskAnalysisState
from .utils import Config, load_config

class DataValidationAgent:
    """Data Validation Agent主类"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化Data Validation Agent
        
        Args:
            config: 配置对象，如果不提供则自动加载
        """
        # 加载配置
        self.config = config or load_config()
        
        # 初始化节点
        self._initialize_nodes()
        
        # 状态
        self.state = RiskAnalysisState()
        
        print(f"DataValidation Agent已初始化")
    
    def _initialize_nodes(self):
        """初始化处理节点"""
        self.data_extraction_node = DataExtractionNode()
        self.code_execution_node = CodeExecutionNode()
        self.result_validation_node = ResultValidationNode()
    
    def validate_risk(self, python_code: str, data_dict: Dict) -> bool:
        """
        验证风险公式
        
        Args:
            python_code: 生成的Python代码
            data_dict: 数据字典
            
        Returns:
            验证结果
        """
        print("开始验证风险公式...")
        
        try:
            # Step 1: 提取所需数据
            extracted_data = self._extract_required_data(python_code, data_dict)
            
            # Step 2: 执行代码
            execution_result = self._execute_code(python_code, extracted_data)
            
            # Step 3: 验证结果
            is_risk = self._validate_result(execution_result)
            
            print(f"风险验证完成: {'存在风险' if is_risk else '无风险'}")
            return is_risk
                
        except Exception as e:
            print(f"验证风险公式时发生错误: {str(e)}")
            return False
    
    def _extract_required_data(self, python_code: str, data_dict: Dict) -> Dict:
        """提取所需数据"""
        print("  - 提取所需数据...")
        
        #传入生成的代码和数据字典
        extraction_input = {
            "python_code": python_code,
            "data_dict": data_dict
        }
        
        extracted_data = self.data_extraction_node.run(extraction_input)
        
        print("  - 数据提取完成")
        return extracted_data
    
    def _execute_code(self, python_code: str, extracted_data: Dict) -> Any:
        """执行代码"""
        print("  - 执行代码...")
        
        #传入生成的代码和提取到的数据
        execution_input = {
            "python_code": python_code,
            "extracted_data": extracted_data
        }
        
        # 执行代码
        execution_result = self.code_execution_node.run(execution_input)
        
        print("  - 代码执行完成")
        return execution_result
    
    def _validate_result(self, execution_result: Any) -> bool:
        """验证结果"""
        print("  - 验证结果...")
        
        # 传入代码执行的结果
        validation_input = {
            "execution_result": execution_result
        }
        
        # 执行验证
        validation_result = self.result_validation_node.run(validation_input)
        
        is_risk = validation_result.get("is_risk", False)
        print(f"  - 结果验证完成: {'存在风险' if is_risk else '无风险'}")
        return is_risk

def create_agent(config_file: Optional[str] = None) -> DataValidationAgent:
    """
    创建Data Validation Agent实例
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        DataValidationAgent实例
    """
    config = load_config(config_file)
    return DataValidationAgent(config)