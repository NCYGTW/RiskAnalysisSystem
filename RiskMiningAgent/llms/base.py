"""
LLM基类
定义所有LLM客户端的基础接口
"""

from abc import ABC, abstractmethod
from typing import Optional
import time
import logging

class BaseLLM(ABC):
    """LLM基类"""
    
    def __init__(self, api_key: str, model_name: str):
        """
        初始化LLM客户端
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def call_llm(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用LLM API
        """
        pass
    
    def get_model_info(self) -> str:
        """获取模型信息"""
        return f"{self.__class__.__name__}({self.model_name})"
    
    def retry_call(self, prompt: str, max_retries: int = 3, delay: float = 1.0, **kwargs) -> Optional[str]:
        """
        带重试机制的LLM调用
        """
        for attempt in range(max_retries):
            try:
                result = self.call_llm(prompt, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                self.logger.error(f"LLM调用错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                self.logger.info(f"{delay}秒后重试...")
                time.sleep(delay)
                delay *= 2  # 指数退避
        
        self.logger.error(f"LLM调用失败，已达到最大重试次数 {max_retries}")
        return None