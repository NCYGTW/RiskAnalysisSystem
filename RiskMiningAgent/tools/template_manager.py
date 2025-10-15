#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模板管理器模块 - 负责管理和生成提示词模板
"""

import logging
import json
import os

logger = logging.getLogger(__name__)

class TemplateManager:
    """
    提示词模板管理器类
    """
    
    def __init__(self):
        """初始化模板管理器"""
        self.template = self._load_template()
        self.example_rules = self._load_example_rules()
        self.financial_fraud_knowledge = self._load_financial_fraud_knowledge()
    
    def _load_template(self):
        """加载提示词模板"""
        return """
角色：你是审计与财务风控专家。你的任务是为给定"风险点"产出一条可执行的判断规则。
约束：规则里的阈值必须来自"统计摘要"，措辞尽量贴近"年报片段"的表述风格。输出严格遵守"输出JSON模式"。禁止虚构变量名。

【财务造假判断经验准则】
{financial_fraud_knowledge}
# 财务造假判断的重要参考依据

【风险点】
{risk_point}

【变量字典】
{variable_catalog_json}
# 仅保留本MVP所需变量；示例：
# a=营业收入YoY%，e=应收账款YoY%，g=经营活动现金流净额/营业收入(TTM)，
# c=行业营业收入YoY Q75，q25_g_ind=行业g分位25%，q75_e_ind=行业应收YoY Q75

【年报片段】
{text_snippets}
# 简短短语级摘要，作为措辞与口径参考，如
# \"收入确认以控制权转移为前提\"、\"行业协会口径：收入同比中位数7.8%\"

【示范规则（few-shot）】
{few_shots_json_array}
# 2–3条示例，每条含 rule_text + dsl + variables_used

【任务】
仅生成"1条"新规则，满足：
1) 自然语言表述（贴近年报措辞），含明确阈值/对比基准；
2) 对应DSL布尔表达式（仅允许 + - * / () > < >= <= && || !）；
3) variables_used 完整映射（单位/周期一致）；
4) 提供 source_refs 说明阈值来自"统计摘要/片段"的哪些键；
5) 给出 safety_hints（缺失/除零/单位换算）。

【输出JSON模式】
{{
  "id": "rule_YYYYMMDD_xxx",
  "risk_point": "...",
  "rule_text": "...",
  "dsl": "...",
  "variables_used": {{ ... }},
  "source_refs": ["stats:...", "text:..."],
  "safety_hints": ["...", "..."]
}}
        """
    
    def _load_financial_fraud_knowledge(self):
        """
        加载财务造假判断经验准则
        从RiskResearchAgent的parsed_risk_rules.json文件中直接加载原始内容
        """
        knowledge_base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'RiskResearchAgent',
            'parsed_risk_rules.json'
        )
        
        try:
            if os.path.exists(knowledge_base_path):
                with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                    logger.info(f"成功加载完整知识库文件: {knowledge_base_path}")
                    return f.read()
            
            logger.warning(f"未找到知识库文件: {knowledge_base_path}")
            return "知识库文件加载失败"
            
        except Exception as e:
            logger.error(f"加载知识库文件时出错: {str(e)}")
            return "知识库文件加载失败"
    
    def _load_example_rules(self):
        """加载示例规则"""
        return [
            {
                "id": "rule_example_1",
                "risk_point": "应收账款异常增长",
                "rule_text": "当应收账款同比增幅超过营业收入同比增幅15个百分点时，可能存在应收账款异常增长风险",
                "dsl": "e - a > 15.0",
                "variables_used": {
                    "a": {"name": "营业收入同比(%)", "period": "YoY", "unit": "pct"},
                    "e": {"name": "应收账款同比(%)", "period": "YoY", "unit": "pct"}
                },
                "source_refs": ["stats:行业基准数据", "text:年报措辞参考"],
                "safety_hints": ["检查是否存在数据缺失", "注意单位一致性"]
            },
            {
                "id": "rule_example_2",
                "risk_point": "经营活动现金流恶化",
                "rule_text": "当经营活动现金流净额/营业收入(TTM)低于行业75分位值时，可能存在现金流恶化风险",
                "dsl": "g < q25_g_ind",
                "variables_used": {
                    "g": {"name": "经营活动现金流净额/营业收入", "period": "TTM", "unit": "ratio"},
                    "q25_g_ind": {"name": "行业g分位25%", "period": "TTM", "unit": "ratio"}
                },
                "source_refs": ["stats:行业基准数据", "text:年报措辞参考"],
                "safety_hints": ["检查除零错误", "注意财务期间匹配"]
            },
            {
                "id": "rule_example_3",
                "risk_point": "毛利率显著下降",
                "rule_text": "当毛利率同比下降超过5个百分点时，可能存在毛利率显著下降风险",
                "dsl": "c < -5.0",
                "variables_used": {
                    "c": {"name": "毛利率同比变化", "period": "YoY", "unit": "pct"}
                },
                "source_refs": ["stats:行业基准数据", "text:年报措辞参考"],
                "safety_hints": ["注意去年同期数据可得性", "检查数据质量"]
            }
        ]
    
    def generate_prompt(self, risk_point, example_rules=None, variable_catalog=None, text_snippets=None):
        """
        生成提示词
        """
        logger.info(f"为风险点生成提示词: {risk_point}")
        
        # 使用默认的变量字典
        if variable_catalog is None:
            variable_catalog = {
                "a": {"name": "营业收入同比(%)", "period": "YoY", "unit": "pct"},
                "e": {"name": "应收账款同比(%)", "period": "YoY", "unit": "pct"},
                "g": {"name": "经营活动现金流净额/营业收入", "period": "TTM", "unit": "ratio"},
                "c": {"name": "行业营业收入YoY Q75", "period": "YoY", "unit": "pct"},
                "q25_g_ind": {"name": "行业g分位25%", "period": "TTM", "unit": "ratio"},
                "q75_e_ind": {"name": "行业应收YoY Q75", "period": "YoY", "unit": "pct"}
            }
        
        # 使用默认的年报片段
        if text_snippets is None:
            text_snippets = [
                "收入确认以控制权转移为前提",
                "行业协会口径：收入同比中位数7.8%",
                "应收账款周转率下降15%",
                "经营性现金流同比下降5%",
                "毛利率下降超过5个百分点"
            ]
        
        # 如果没有提供示例规则，使用空列表
        if example_rules is None:
            example_rules = []
        
        # 准备模板变量
        variable_catalog_json = json.dumps(variable_catalog, ensure_ascii=False, indent=2)
        text_snippets_str = "\n".join([f"- {snippet}" for snippet in text_snippets])
        few_shots_json_array = json.dumps(example_rules, ensure_ascii=False, indent=2)
        
        # 填充模板
        prompt = self.template.format(
            risk_point=risk_point,
            variable_catalog_json=variable_catalog_json,
            text_snippets=text_snippets_str,
            few_shots_json_array=few_shots_json_array,
            financial_fraud_knowledge=self.financial_fraud_knowledge
        )
        
        return prompt
    
    def get_example_rules(self):
        """
        获取示例规则
        """
        return self.example_rules
    
    def set_example_rules(self, example_rules):
        """
        设置示例规则
        """
        self.example_rules = example_rules
        logger.info(f"已更新示例规则，共{len(example_rules)}条")