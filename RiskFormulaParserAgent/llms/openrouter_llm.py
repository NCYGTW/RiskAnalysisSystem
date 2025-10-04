"""
OpenRouter API客户端
"""

import os
import json
import time
import logging
from typing import Optional
from openai import OpenAI, RateLimitError
from .base import BaseLLM

class OpenRouterLLM(BaseLLM):
    """OpenRouter API客户端"""
    
    def __init__(self, api_key: str, model_name: str = "deepseek/deepseek-chat-v3.1:free"):
        """
        初始化OpenRouter API客户端
        
        Args:
            api_key: OpenRouter API密钥
            model_name: 模型名称
        """
        super().__init__(api_key, model_name)
        self.base_url = "https://openrouter.ai/api/v1"
        # 使用OpenAI SDK创建客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        # 设置请求头
        self.extra_headers = {
            "HTTP-Referer": "http://localhost:10808",
            "X-Title": "Risk Formula Parser"
        }
        # 添加速率限制控制
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 最小请求间隔（秒）
    
    def _rate_limit_delay(self):
        """实施速率限制延迟"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def call_llm(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用OpenRouter API
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
            
        Returns:
            LLM返回的文本
        """
        # 实施速率限制
        self._rate_limit_delay()
        
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # 使用OpenAI SDK调用API
                completion = self.client.chat.completions.create(
                    extra_headers=self.extra_headers,
                    extra_body={},
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的财务风险分析专家，擅长将自然语言描述的风险模型公式转化为Python代码。请严格按照要求输出可执行的Python代码。"
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
                    return completion.choices[0].message.content
                else:
                    self.logger.error(f"API调用未返回有效响应")
                    return None
                    
            except RateLimitError as e:
                self.logger.warning(f"达到速率限制 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # 指数退避策略
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    self.logger.error(f"达到速率限制，已重试 {max_retries} 次仍失败: {str(e)}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"调用LLM API时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"LLM调用最终失败: {str(e)}")
                    return None
        
        return None