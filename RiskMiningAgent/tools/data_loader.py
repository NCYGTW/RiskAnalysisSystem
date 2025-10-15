#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据加载器模块 - 负责加载风险点列表和示例规则
"""

import logging
import os
import json
from .template_manager import TemplateManager

logger = logging.getLogger(__name__)

def load_risk_points(file_path=None):
    """
    加载风险点列表
    """
    if file_path and os.path.exists(file_path):
        target_path = file_path
    else:
        default_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'risk_points.json')
        if os.path.exists(default_file_path):
            target_path = default_file_path
        else:
            error_msg = f"无法找到风险点文件: {file_path} 或 {default_file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
    
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            risk_points = json.load(f)
        logger.info(f"从文件 {target_path} 加载到 {len(risk_points)} 个风险点")
        return risk_points
    except json.JSONDecodeError as e:
        error_msg = f"解析风险点文件失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"加载风险点文件失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def load_example_rules(file_path=None):
    """
    加载示例规则
    """
    # 如果提供了文件路径且文件存在，则从文件加载
    if file_path and os.path.exists(file_path):
        target_path = file_path
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                example_rules = json.load(f)
            logger.info(f"从文件 {target_path} 加载到 {len(example_rules)} 条示例规则")
            return example_rules
        except json.JSONDecodeError as e:
            error_msg = f"解析示例规则文件失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"加载示例规则文件失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # 如果文件路径不存在，从 TemplateManager 获取默认示例规则
    try:
        template_manager = TemplateManager()
        example_rules = template_manager.get_example_rules()
        logger.info(f"从 TemplateManager 加载到 {len(example_rules)} 条示例规则")
        return example_rules
    except Exception as e:
        error_msg = f"从 TemplateManager 加载示例规则失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def save_rules(rules, output_file):
    """
    保存生成的规则
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存 {len(rules)} 条规则到 {output_file}")
        return True
    except Exception as e:
        logger.error(f"保存规则失败: {str(e)}")
        return False