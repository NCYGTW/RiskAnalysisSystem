#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则校验器模块
"""

import logging
import re

logger = logging.getLogger(__name__)

class RuleValidator:
    """
    规则校验器类
    """
    
    def __init__(self):
        """初始化规则校验器"""
        self.required_fields = ["id", "risk_point", "rule_text", "dsl", "variables_used", "source_refs", "safety_hints"]
    
    def validate(self, rule_json):
        """
        验证规则是否有效
        
        Args:
            rule_json: 规则JSON对象
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        logger.info(f"开始验证规则: {rule_json.get('id', 'Unknown')}")
        
        errors = []
        
        # 检查必要字段
        missing_fields = [field for field in self.required_fields if field not in rule_json]
        if missing_fields:
            errors.append(f"缺少必要字段: {', '.join(missing_fields)}")
            return False, errors
        
        # 验证各字段
        validators = [
            (self._validate_id_format, rule_json["id"], f"ID格式不正确: {rule_json['id']}，应为 'rule_YYYYMMDD_xxx' 格式"),
            (lambda x: isinstance(x, list) and len(x) > 0, rule_json["source_refs"], "source_refs 必须是非空列表"),
            (lambda x: isinstance(x, list), rule_json["safety_hints"], "safety_hints 必须是列表"),
            (lambda x: x and isinstance(x, str), rule_json["rule_text"], "rule_text 必须是非空字符串"),
            (lambda x: x and isinstance(x, str), rule_json["risk_point"], "risk_point 必须是非空字符串"),
            (self._validate_rule_text_thresholds, rule_json["rule_text"], "rule_text 应包含明确的阈值和比较基准"),
        ]
        
        for validator, value, error_msg in validators:
            if not validator(value):
                errors.append(error_msg)
        
        # 验证DSL和变量
        errors.extend(self._validate_dsl(rule_json["dsl"]))
        errors.extend(self._validate_variables(rule_json["variables_used"], rule_json["dsl"]))
        
        is_valid = len(errors) == 0
        log_func = logger.info if is_valid else logger.warning
        log_func(f"规则验证{'通过' if is_valid else '失败'}: {rule_json['id']}, 错误: {errors}")
        
        return is_valid, errors
    
    def _validate_id_format(self, rule_id):
        """验证规则ID格式"""
        pattern = r'^rule_\d{8}_\d{3,}$'
        return bool(re.match(pattern, rule_id))
    
    def _validate_dsl(self, dsl):
        """验证DSL表达式"""
        errors = []

        # 检查括号匹配
        stack = []
        for char in dsl:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    errors.append("括号不匹配: 多余的右括号")
                    break
                stack.pop()
        
        if stack:
            errors.append("括号不匹配: 缺少右括号")

        # 检查是否为空
        if not dsl or not dsl.strip():
            errors.append("DSL表达式不能为空")
        
        return errors
    
    def _validate_variables(self, variables_used, dsl):
        """验证变量映射"""
        errors = []

        # 检查variables_used是否为字典
        if not isinstance(variables_used, dict):
            errors.append("variables_used 必须是字典类型")
            return errors

        # 检查每个变量的定义
        for var_name, var_info in variables_used.items():
            if not isinstance(var_info, dict):
                errors.append(f"变量 {var_name} 的定义必须是字典类型")
                continue
            
            # 检查变量定义的必要字段
            required_var_fields = ["name", "period", "unit"]
            for field in required_var_fields:
                if field not in var_info:
                    errors.append(f"变量 {var_name} 缺少必要字段: {field}")
        
        # 检查DSL中使用的变量是否都在variables_used中定义
        variable_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
        found_variables = variable_pattern.findall(dsl)

        # 过滤掉操作符和数字
        operators = set(['and', 'or', 'not', 'True', 'False', 'None'])
        numeric_literals = set()
        for var in found_variables:
            if var.isdigit() or (var[0].isdigit() and '.' in var):
                numeric_literals.add(var)

        # 检查未定义的变量
        undefined_vars = []
        for var in found_variables:
            if var not in variables_used and var not in operators and var not in numeric_literals:
                undefined_vars.append(var)

        if undefined_vars:
            errors.append(f"DSL中使用了未定义的变量: {', '.join(undefined_vars)}")
        
        return errors
    
    def _validate_rule_text_thresholds(self, rule_text):
        """验证规则文本是否包含明确的阈值和比较基准"""
        # 检查是否包含数字阈值
        has_number = bool(re.search(r'\d+(?:\.\d+)?%?', rule_text))

        # 检查是否包含比较词
        comparison_words = ['大于', '小于', '高于', '低于', '超过', '不少于', '不大于']
        has_comparison = any(word in rule_text for word in comparison_words)

        # 规则文本应包含数字阈值和比较词
        return has_number and has_comparison