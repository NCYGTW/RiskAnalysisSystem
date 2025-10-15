"""
系统配置文件
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    """系统配置类"""
    openrouter_api_key: str = "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"
    default_model: str = "tngtech/deepseek-r1t2-chimera:free"
    output_dir: str = "outputs"
    log_dir: str = "logs"
    data_dir: str = "data"
    max_retries: int = 5  # 重试次数
    retry_delay: float = 3.0  # 重试延迟
    api_timeout: int = 60  # 超时时间

# 全局配置实例
config = Config()

def load_config_from_env():
    """从环境变量中加载配置"""
    config.openrouter_api_key = os.getenv('OPENROUTER_API_KEY',  config.openrouter_api_key)
    config.default_model = os.getenv('DEFAULT_MODEL', config.default_model)
    config.output_dir = os.getenv('OUTPUT_DIR', config.output_dir)
    config.log_dir = os.getenv('LOG_DIR', config.log_dir)
    config.data_dir = os.getenv('DATA_DIR', config.data_dir)
    config.max_retries = int(os.getenv('MAX_RETRIES', config.max_retries))
    config.retry_delay = float(os.getenv('RETRY_DELAY', config.retry_delay))
    config.api_timeout = int(os.getenv('API_TIMEOUT', config.api_timeout))

# 初始化配置
load_config_from_env()