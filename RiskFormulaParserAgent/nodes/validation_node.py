"""
验证节点
"""

import json
import re
from typing import Dict, Any
from .base_node import BaseNode
import os
import sys

class ValidationNode(BaseNode):
    """负责验证生成的代码"""
    
    def __init__(self, llm_client):
        super().__init__(llm_client)
        # 加载提示词模板
        self.code_validation_prompt = self._load_code_validation_prompt()
    
    def _load_code_validation_prompt(self):
        """加载代码验证相关的提示词"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../../'))
            template_file = os.path.join(project_root, 'prompt_template.py')
            
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_globals = {}
            exec(content, template_globals)
            
            return template_globals.get('CODE_VALIDATION_PROMPT', '')
        except Exception as e:
            print(f"加载代码验证提示词模板失败: {str(e)}")
            return ''
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        验证生成的代码
        
        Args:
            input_data: 输入数据，包含生成的Python代码和模型项目
            
        Returns:
            验证结果
        """
        python_code = input_data.get("python_code", "")
        model_items = input_data.get("model_items", [])
        
        if self.code_validation_prompt:
            prompt = self.code_validation_prompt.format(python_code=python_code)
        else:
            prompt = f"""
请验证以下Python代码是否符合要求：

生成的Python代码：
{python_code}

模型涉及项目：
{json.dumps(model_items, ensure_ascii=False, indent=2)}

验证要求：
1. 代码是否包含一个名为'check_risk'的函数
2. 函数是否接收一个data_dict字典参数
3. 函数返回值是否为布尔类型
4. 代码是否严格使用data_dict中的'model_items'字段获取数据
5. 代码是否处理了异常情况（使用try-except语句）
6. 代码是否正确导入了必要的模块
7. 代码中是否直接使用行业数据点作为分位数或均值，而不是计算分位数
8. 当数据缺失或不足时，是否返回False

请以JSON格式输出验证结果，包含以下字段：
- is_valid: 布尔值，表示代码是否有效
- issues: 字符串列表，列出发现的问题
- suggestions: 字符串列表，提供改进建议

请严格按照以下JSON格式输出结果：
{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}
"""
        
        # 调用LLM进行验证
        validation_result = self.llm_client.call_llm(prompt)
        
        if validation_result:
            # 从响应中提取JSON
            json_str = self._extract_json_from_response(validation_result)
            if json_str:
                try:
                    # 解析JSON结果
                    result = json.loads(json_str)
                    return result
                except json.JSONDecodeError:
                    print(f"解析验证结果JSON失败: {json_str}")
            else:
                print(f"未能从响应中提取JSON: {validation_result}")
        else:
            print("LLM调用失败，无法验证代码")
        
        # 代码检查
        basic_check_result = self._basic_code_check(python_code)
        if not basic_check_result['is_valid']:
            return basic_check_result
        
        return {
            "is_valid": False,
            "issues": ["验证过程失败，无法确定代码有效性"],
            "suggestions": ["请检查LLM配置和网络连接"]
        }
    
    def _basic_code_check(self, python_code: str) -> Dict[str, Any]:
        """对代码进行基本语法检查"""
        issues = []
        
        # 检查是否包含check_risk函数
        if 'def check_risk(' not in python_code:
            issues.append("代码中未找到名为'check_risk'的函数")
        
        # 检查是否有try-except语句
        if 'try:' not in python_code or 'except' not in python_code:
            issues.append("代码中未包含异常处理语句")
        
        # 检查函数返回值是否为布尔类型
        if 'return True' not in python_code and 'return False' not in python_code:
            issues.append("函数可能没有返回布尔类型的值")
        
        # 检查是否使用了data_dict['model_items']
        if 'data_dict.get(' not in python_code and 'data_dict[' not in python_code:
            issues.append("代码可能没有正确使用data_dict获取数据")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": ["请确保代码符合所有要求"] if issues else []
        }
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        从LLM响应中提取JSON字符串
        
        Args:
            response: LLM响应文本
            
        Returns:
            提取的JSON字符串
        """
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response