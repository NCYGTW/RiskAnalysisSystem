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
            "X-Title": "Risk Research Agent"
        }
        # 请求速率限制控制
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 最小请求间隔2秒
    
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
        
        # 从kwargs中获取重试参数，默认值更高
        max_retries = kwargs.pop('max_retries', 5)  # 最大重试次数5次
        retry_delay = kwargs.pop('retry_delay', 3.0)  # 重试延迟3秒
        
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
                            "content": "你是一个专业的风险研究专家，擅长分析和总结文档内容，特别是关于造假案例、政策法规等信息。请严格按照要求提取和总结文档内容。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=kwargs.get("temperature", 0.1),
                    max_tokens=kwargs.get("max_tokens", 2000),
                    timeout=kwargs.get("timeout", 60)  
                )
                
                self.logger.info(f"成功获取API响应: {completion}")
                
                if completion and hasattr(completion, 'choices') and completion.choices:
                    choice = completion.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content = choice.message.content
                        if content:
                            return content
                
                self.logger.error(f"API调用返回了有效状态码但内容无效: completion={completion}")
                return None
                    
            except RateLimitError as e:
                self.logger.warning(f"达到速率限制 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    #退避策略：基础延迟 * (2^attempt) + 随机延迟
                    sleep_time = retry_delay * (2 ** attempt)
                    self.logger.info(f"将在 {sleep_time:.2f} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"达到速率限制，已重试 {max_retries} 次仍失败: {str(e)}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"调用LLM API时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # 非速率限制错误同样使用指数退避
                    sleep_time = retry_delay * (2 ** attempt)
                    self.logger.info(f"将在 {sleep_time:.2f} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"LLM调用最终失败: {str(e)}")
                    return None
        
        return None