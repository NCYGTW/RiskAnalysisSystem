#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置包初始化文件
"""

# 从config.py导入配置和加载函数，便于其他模块直接从config包导入
from config.config import config, load_config_from_env

__all__ = ['config', 'load_config_from_env']