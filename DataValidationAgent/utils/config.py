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
    output_dir: str = "outputs"
    log_dir: str = "logs"
    data_dir: str = "data"
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
        # 如果环境变量中没有，尝试从现有配置文件中读取
        try:
            # 这里可以添加从文件读取配置的逻辑
            pass
        except:
            pass
    
    # 如果没有API密钥，使用默认值（注意：在生产环境中应该要求用户提供API密钥）
    if not config.openrouter_api_key:
        config.openrouter_api_key = "sk-or-v1-your-api-key-here"
    
    return config