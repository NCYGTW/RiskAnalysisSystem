"""
配置管理模块
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """配置类"""
    openrouter_api_key: str = ""
    default_model: str = "deepseek/deepseek-chat-v3.1:free"
    output_dir: str = "../outputs"
    log_dir: str = "../logs"
    data_dir: str = "../data"
    max_retries: int = 3
    retry_delay: float = 1.0
    api_timeout: int = 30

def load_config(config_file: Optional[str] = None) -> Config:
    """
    加载配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Config对象
    """
    config = Config()
    
    # 从环境变量获取API密钥
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        config.openrouter_api_key = api_key
    else:
        # 使用默认的API密钥
        config.openrouter_api_key = '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'
    
    return config