"""
提示词
"""

RISK_VALIDATION_PROMPT = '''
任务：根据风险描述，生成风险验证代码

要求：
1. 代码必须调用传入的数据字典data_dict中的'model_items'字段来获取验证所需的所有数据
2. 生成的代码必须包含一个名为'check_risk'的函数,该函数接收一个data_dict字典参数
3. 函数返回值必须是布尔类型:True表示存在风险,False表示不存在风险
4. 验证所用到的行业分位数(如85%)或行业均值，直接使用类型为"行业"的那一个数据点的值，**不需要计算分位数**
5. 风险描述中的"本年"指的是2024年
6. 代码必须在函数内部处理所有可能的异常情况，使用try-except语句，特别是数据类型转换、除零错误等常见问题，确保使用try-except语句并指定具体的异常类型（如ValueError, TypeError, ZeroDivisionError等）
7. 代码必须包含必要的模块导入语句（如需要使用numpy等）
8. 当数据缺失或不足时，函数默认返回False
9. 确保生成的代码语法正确，特别是缩进和引号的使用

数据结构说明：
- data_dict是一个字典,包含'model_items'字段
- 'model_items'是一个列表，包含多个字典，每个字典代表一个项目的数据
- 每个项目数据字典包含：'项目名称'、'类型'（企业/行业）、'2023'、'2024'等字段

风险公式：{risk_formula}

请生成完整的验证代码：
'''

RISK_DESCRIPTION_PROMPT = '''
任务：分析企业财务数据，生成结构化的风险描述

要求：
1. 描述必须基于实际数据分析结果

企业名称：{company_name}
风险类型：{risk_type}
风险公式：{risk_formula}
验证结果：{validation_result}
相关财务数据：{financial_data}

请生成风险描述：
'''

FORMULA_ANALYSIS_PROMPT = '''
任务：分析风险公式代码结构，提取关键信息

风险公式：{risk_formula}

请提取以下信息：
1. 涉及的财务指标
2. 比较条件

请以JSON格式输出结果：
'''

CODE_VALIDATION_PROMPT = '''
任务：验证生成的代码是否符合要求

生成的代码：
{python_code}

验证要求：
1. 代码是否包含一个名为'check_risk'的函数
2. 函数是否接收一个data_dict字典参数
3. 函数返回值是否为布尔类型
4. 代码是否严格使用data_dict中的'model_items'字段获取数据
5. 代码是否处理了异常情况（使用try-except语句）
6. 代码是否正确导入了必要的模块
7. 代码中是否直接使用行业数据点作为分位数或均值，而不是计算分位数
8. 当数据缺失或不足时，是否返回False

请以JSON格式输出验证结果，包含'is_valid'（布尔值）和'reason'（字符串）字段：
'''


def load_prompt_template(template_file='prompt_template.py'):
    """
    加载提示词
    
    Args:
        template_file: 模板文件路径
        
    Returns:
        dict: 包含所有提示词模板的字典
    """
    import os
    
    if not os.path.isabs(template_file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_file = os.path.join(current_dir, template_file)
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        template_globals = {}
        exec(content, template_globals)
        
        prompts = {}
        for key, value in template_globals.items():
            if key.endswith('_PROMPT') and isinstance(value, str):
                prompts[key] = value
        
        return prompts
        
    except Exception as e:
        print(f"加载提示词模板失败: {str(e)}")
        return {
            'RISK_VALIDATION_PROMPT': '',
            'RISK_DESCRIPTION_PROMPT': '',
            'FORMULA_ANALYSIS_PROMPT': '',
            'CODE_VALIDATION_PROMPT': ''
        }

if __name__ == '__main__':
    prompts = load_prompt_template()
    print(f"成功加载了{len(prompts)}个提示词模板")
    for key in prompts:
        print(f"- {key}")