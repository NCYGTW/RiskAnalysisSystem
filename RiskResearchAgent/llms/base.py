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
        
        Args:
            api_key: API密钥
            model_name: 模型名称
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def call_llm(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用LLM API
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
            
        Returns:
            LLM返回的文本
        """
        pass
    
    def get_model_info(self) -> str:
        """获取模型信息"""
        return f"{self.__class__.__name__}({self.model_name})"
    
    def retry_call(self, prompt: str, max_retries: int = 3, delay: float = 1.0, **kwargs) -> Optional[str]:
        """
        带重试机制的LLM调用
        
        Args:
            prompt: 提示词
            max_retries: 最大重试次数
            delay: 初始重试延迟（秒）
            **kwargs: 额外参数
            
        Returns:
            LLM返回的文本
        """
        for attempt in range(max_retries):
            try:
                result = self.call_llm(prompt, **kwargs)
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # 使用指数退避策略
                    time.sleep(delay * (2 ** attempt))
                else:
                    self.logger.error(f"LLM调用最终失败: {str(e)}")
        
        return None