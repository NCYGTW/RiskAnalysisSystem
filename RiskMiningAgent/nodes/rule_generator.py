#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则生成器模块 - 负责调用LLM生成风险规则
"""

import logging
import json
import re
from datetime import datetime
import random

from llms.openrouter_llm import OpenRouterLLM
from config.config import config

logger = logging.getLogger(__name__)

class RuleGenerator:
    """
    风险规则生成器类
    """
    
    def __init__(self):
        """初始化规则生成器"""
        if config.openrouter_api_key:
            self.llm = OpenRouterLLM(
                api_key=config.openrouter_api_key,
                model_name=config.default_model
            )
            logger.info(f"使用OpenRouter LLM: {self.llm.get_model_info()}")
        else:
            logger.warning("未配置OpenRouter API密钥")
            self.llm = None
    
    def _extract_risk_point(self, prompt):
        """从提示词中提取风险点"""
        match = re.search(r'【风险点】\s*(.*?)\s*【', prompt, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "未知风险点"
    
    def generate_rule(self, prompt):
        """
        根据提示词生成规则
        """
        logger.info("开始生成规则")
        
        risk_point = self._extract_risk_point(prompt)
        rule_id = f"rule_{datetime.now().strftime('%Y%m%d')}_{random.randint(100, 999)}"
        
        if self.llm:
            try:
                llm_response = self.llm.call_llm(prompt)
                if llm_response:
                    try:
                        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                        if json_match:
                            rule_data = json.loads(json_match.group(0))
                            rule_data["id"] = rule_id
                            rule_data["risk_point"] = risk_point
                            logger.info(f"规则生成完成: {rule_id}")
                            return rule_data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析错误: {str(e)}")
            except Exception as e:
                logger.error(f"LLM调用错误: {str(e)}")
        
        logger.warning("LLM不可用或调用失败，无法生成规则")
        return None
    
    def generate_rule_with_fix(self, prompt, original_rule, error_hints):
        """
        根据错误提示重新生成修复后的规则
        """
        logger.info(f"开始修复规则，错误提示: {error_hints}")
        
        fix_prompt = f"{prompt}\n\n【需要修复的规则】\n{json.dumps(original_rule, ensure_ascii=False, indent=2)}\n\n【错误提示】\n{error_hints}\n\n请修复上述规则，确保符合JSON格式和所有要求。"
        
        if self.llm:
            try:
                llm_response = self.llm.call_llm(fix_prompt)
                if llm_response:
                    try:
                        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                        if json_match:
                            fixed_rule = json.loads(json_match.group(0))
                            if "id" in original_rule:
                                fixed_rule["id"] = original_rule["id"]
                            logger.info(f"规则修复完成: {fixed_rule.get('id', 'unknown')}")
                            return fixed_rule
                    except json.JSONDecodeError as e:
                        logger.error(f"修复后JSON解析错误: {str(e)}")
            except Exception as e:
                logger.error(f"LLM修复调用错误: {str(e)}")
        
        logger.warning("LLM不可用或调用失败，无法修复规则")
        return None