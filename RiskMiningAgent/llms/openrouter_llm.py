"""
OpenRouter API客户端
"""

import time
import logging
from typing import Optional
from openai import OpenAI, RateLimitError, AuthenticationError, APITimeoutError
from .base import BaseLLM
import random  

class OpenRouterLLM(BaseLLM):
    """OpenRouter API客户端"""
    
    def __init__(self, api_key: str, model_name: str = "deepseek/deepseek-chat-v3.1:free"):
        """
        初始化OpenRouter API客户端
        """
        super().__init__(api_key, model_name)
        self.base_url = "https://openrouter.ai/api/v1"
        # 使用OpenAI SDK创建客户端
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )

            self.logger.info(f"OpenRouter客户端初始化成功，模型: {model_name}")
        except Exception as e:
            self.logger.error(f"OpenRouter客户端初始化失败: {str(e)}")
            raise
        
        # 设置请求头
        self.extra_headers = {
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Risk Mining System"
        }

        self.last_request_time = 0
        self.min_request_interval = 2.0  # 最小请求间隔为2秒
    
    def _rate_limit_delay(self):
        """实施速率限制延迟"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self.logger.debug(f"实施速率限制，等待 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)

        self.last_request_time = time.time()
    
    def call_llm(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用OpenRouter API
        """
        # 速率限制
        self._rate_limit_delay()

        max_retries = kwargs.get("max_retries", 3)
        retry_delay = kwargs.get("retry_delay", 1.0)

        for attempt in range(max_retries):
            try:
                self.logger.info(f"LLM调用尝试 {attempt + 1}/{max_retries}: 模型={self.model_name}, 提示词长度={len(prompt)}字符")
                
                # 使用OpenAI SDK调用API
                completion = self.client.chat.completions.create(
                    extra_headers=self.extra_headers,
                    extra_body={},
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的财务风险分析专家，擅长根据风险点生成自然语言判断规则和可执行的DSL公式。请严格按照要求输出JSON格式的规则。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=kwargs.get("temperature", 0.1),
                    max_tokens=kwargs.get("max_tokens", 2000),
                    timeout=kwargs.get("timeout", 30)  # 设置超时时间
                )
                
                # 提取响应内容
                if completion and completion.choices:
                    response_content = completion.choices[0].message.content
                    self.logger.info(f"LLM调用成功，响应长度={len(response_content)}字符")
                    return response_content
                else:
                    self.logger.error(f"API调用未返回有效响应: completion对象={completion}")
                    return None
                    
            except AuthenticationError as e:
                # 身份验证错误，通常是API密钥问题
                self.logger.error(f"身份验证错误 (尝试 {attempt + 1}/{max_retries}): API密钥可能无效或已过期。详细错误: {str(e)}")
                break
            except RateLimitError as e:
                self.logger.warning(f"达到速率限制 (尝试 {attempt + 1}/{max_retries}): {str(e)}。请稍后再试或减少请求频率。")
                if attempt < max_retries - 1:
                    # 指数退避策略，添加随机延迟
                    sleep_time = retry_delay * (2 ** attempt) + random.uniform(0, 1)  # 添加0-1秒的随机延迟
                    self.logger.info(f"{sleep_time:.2f}秒后重试...")
                    time.sleep(sleep_time)
            except APITimeoutError as e:
                self.logger.error(f"API超时错误 (尝试 {attempt + 1}/{max_retries}): 请求超时。详细错误: {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2 ** attempt)
                    self.logger.info(f"{sleep_time:.2f}秒后重试...")
                    time.sleep(sleep_time)
            except Exception as e:
                error_type = type(e).__name__
                self.logger.error(f"API调用错误 (尝试 {attempt + 1}/{max_retries}): 错误类型={error_type}, 详细错误: {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2 ** attempt)
                    self.logger.info(f"{sleep_time:.2f}秒后重试...")
                    time.sleep(sleep_time)

        self.logger.error(f"所有API调用尝试均失败 (最大重试次数: {max_retries})。请检查:")
        self.logger.error(f"1. OPENROUTER_API_KEY 环境变量是否正确设置")
        self.logger.error(f"2. 网络连接是否正常")
        self.logger.error(f"3. OpenRouter API是否可用")
        self.logger.error(f"4. 使用的模型名称 '{self.model_name}' 是否有效")
        return None