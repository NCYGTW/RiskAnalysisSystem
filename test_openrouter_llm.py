import os
import sys

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from RiskFormulaParserAgent.llms.openrouter_llm import OpenRouterLLM
from config.config import config

def test_openrouter_llm_call():
    """
    测试OpenRouterLLM的调用功能
    """
    # 从配置文件中获取API密钥
    api_key = config.openrouter_api_key
    
    if not api_key:
        print("请在 config/config.py 文件或环境变量中设置您的 OpenRouter API 密钥。")
        return

    # 初始化OpenRouterLLM
    # 使用配置文件中的模型名称
    llm = OpenRouterLLM(api_key=api_key, model_name=config.default_model)

    # 定义一个测试提示
    prompt = "你好，请介绍一下你自己。"
    # prompt = "99+11="

    print(f"正在使用模型: {llm.get_model_info()}")
    print(f"发送提示: \n{prompt}")

    # 调用LLM
    response = llm.call_llm(prompt)

    # 打印响应
    if response:
        print(f"收到的响应: \n{response}")
    else:
        print("调用LLM失败，没有收到响应。")

if __name__ == "__main__":
    test_openrouter_llm_call()