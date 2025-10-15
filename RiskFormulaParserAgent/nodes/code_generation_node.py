"""
代码生成节点
负责生成Python代码
"""

import json
import re
import os
import ast  
from typing import Dict, Any
from .base_node import BaseNode

class CodeGenerationNode(BaseNode):
    """代码生成节点"""
    
    def __init__(self, llm_client):
        super().__init__(llm_client)
        # 加载提示词模板
        self.prompts = self._load_prompt_templates()
    
    def _load_prompt_templates(self):
        """加载提示词模板"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../../'))
            template_file = os.path.join(project_root, 'prompt_template.py')
            
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            template_globals = {}
            exec(content, template_globals)
            
            return {
                'RISK_VALIDATION_PROMPT': template_globals.get('RISK_VALIDATION_PROMPT', self._get_default_prompt()),
                'CODE_VALIDATION_PROMPT': template_globals.get('CODE_VALIDATION_PROMPT', '')
            }
            
        except Exception as e:
            print(f"加载提示词模板失败，使用默认提示词: {str(e)}")
            return {
                'RISK_VALIDATION_PROMPT': self._get_default_prompt(),
                'CODE_VALIDATION_PROMPT': ''
            }
    
    def _get_default_prompt(self):
        """获取默认提示词"""
        return '''
任务：根据风险公式描述，生成用于验证该风险的Python代码

重要要求：
1. 代码必须严格使用传入的数据字典中的'model_items'字段来获取验证所需的所有数据
2. 不要尝试从其他数据源获取数据
3. 生成的代码必须包含一个名为'check_risk'的函数，该函数接收一个data_dict参数
4. 函数返回值必须是布尔类型：True表示存在风险，False表示不存在风险
5. 请处理可能出现的数据缺失、类型转换错误等异常情况
6. 请为不同情况下的异常提供合理的默认返回值
7. 请确保生成的代码是有效的Python语法

风险公式：{risk_formula}

请生成完整的验证代码：
'''
    
    def _validate_python_syntax(self, code):
        """验证Python代码语法是否正确"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _fix_common_syntax_errors(self, code):
        """修复常见的语法错误"""
        if 'numpy' in code and 'import numpy' not in code:
            code = "import numpy as np\n" + code
        
        if 'def check_risk(' not in code:
            fixed_code = '''def check_risk(data_dict):
    # 自动生成的风险检查函数
    try:
        # 在这里添加风险检查逻辑
        return False
    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        return False
'''
            return fixed_code
        
        if 'except Exception' in code and 'Exception as e' not in code:
            code = code.replace('except Exception', 'except Exception as e')
        
        if 'return True' not in code and 'return False' not in code:
            if 'def check_risk(' in code:
                lines = code.split('\n')
                func_end_index = None
                indent_level = 0
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('def check_risk('):
                        # 计算缩进级别
                        indent_level = len(line) - len(stripped)
                        # 查找函数体结束位置
                        for j in range(i+1, len(lines)):
                            if lines[j].strip() and len(lines[j]) - len(lines[j].strip()) <= indent_level and j > i+1:
                                func_end_index = j
                                break
                        break
                
                if func_end_index is not None:
                    lines.insert(func_end_index, ' ' * (indent_level + 4) + 'return False')
                    code = '\n'.join(lines)
                elif 'def check_risk(' in code and 'return' not in code:
                    # 如果无法确定函数体结构，添加一个简单的返回语句
                    code = code + '\n    return False'
        
        # 5. 确保使用了正确的行业数据处理方式
        if '行业' in code and ('np.percentile' in code or 'statistics.mean' in code):
            # 替换分位数计算为直接使用行业数据
            code = code.replace('np.percentile', '# 注意：直接使用行业数据点作为分位数')
            code = code.replace('statistics.mean', '# 注意：直接使用行业数据点作为均值')
        
        return code
    
    def run(self, input_data: Dict[str, Any], **kwargs) -> str:
        """
        生成Python代码
        
        Args:
            input_data: 输入数据，包含风险分析结果
            
        Returns:
            生成的Python代码
        """
        risk_description = input_data.get('risk_description', '')
        if not risk_description:
            risk_description = str(input_data)
        
        prompt = self.prompts['RISK_VALIDATION_PROMPT'].format(
            risk_formula=risk_description
        )
        
        print(f"使用模板构建的提示词长度: {len(prompt)}字符")
        
        # 调用LLM生成代码
        code = self.llm_client.call_llm(prompt)
        
        if code:
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                parts = code.split("```")
                if len(parts) >= 2:
                    code = parts[1]
            
            code = code.strip()
            
            # 尝试修复常见的语法错误
            code = self._fix_common_syntax_errors(code)
            
            # 验证修复后的代码语法
            if not self._validate_python_syntax(code):
                print("生成的代码存在语法错误，使用默认代码")
                # 如果代码仍有语法错误，返回一个安全的默认函数
                return '''def check_risk(data_dict):
    # 默认风险检查函数 - 修复后的安全版本
    try:
        return False
    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        return False'''
            
            return code
            default_code = '''def check_risk(data_dict):
    # 默认风险检查函数
    # 这是一个占位函数，在API调用失败时使用
    try:
        return False
    except (ValueError, TypeError, AttributeError, ZeroDivisionError):
        return False'''
            return default_code