#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
无监督风险模型挖掘系统 - 主入口
"""

import os
import sys
from datetime import datetime
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config import config, load_config_from_env
from nodes.rule_generator import RuleGenerator
from tools.rule_validator import RuleValidator
from tools.template_manager import TemplateManager
from tools.data_loader import load_risk_points, load_example_rules

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("risk_mining.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    主函数 - 协调整个风险规则生成流程
    """
    logger.info("无监督风险模型挖掘系统启动")
    
    try:
        # 加载配置信息
        load_config_from_env()
        logger.info(f"使用模型: {config.default_model}")
        
        # 加载风险点列表
        risk_points = load_risk_points()
        logger.info(f"加载到 {len(risk_points)} 个风险点")
        
        # 初始化核心组件
        template_manager = TemplateManager()
        rule_generator = RuleGenerator()
        rule_validator = RuleValidator()
        
        # 加载示例规则
        example_rules = load_example_rules()
        
        # 处理每个风险点
        results = []
        for risk_point in risk_points:
            logger.info(f"处理风险点: {risk_point}")
            
            try:
                # 生成提示词
                prompt = template_manager.generate_prompt(
                    risk_point=risk_point,
                    example_rules=example_rules
                )
                
                # 调用LLM生成规则
                rule_json = rule_generator.generate_rule(prompt)
                
                # 检查规则是否生成成功
                if rule_json is None:
                    logger.warning(f"无法生成规则: {risk_point}")
                    continue  # 跳过此风险点，处理下一个
                
                # 验证规则
                is_valid, errors = rule_validator.validate(rule_json)
                
                if is_valid:
                    logger.info(f"规则验证通过: {risk_point}")
                    rule_json['compiled'] = True  # 保留标记
                    results.append(rule_json)
                else:
                    logger.warning(f"规则验证失败: {risk_point}, 错误: {errors}")
                    # 重新请求修复规则
                    fixed_rule_json = rule_generator.generate_rule_with_fix(
                        prompt=prompt,
                        original_rule=rule_json,
                        error_hints=errors
                    )
                    
                    # 检查修复后的规则是否生成成功
                    if fixed_rule_json is None:
                        logger.warning(f"无法修复规则: {risk_point}")
                        continue  # 跳过此风险点，处理下一个
                    
                    # 再次验证修复后的规则
                    is_fixed_valid, fixed_errors = rule_validator.validate(fixed_rule_json)
                    if is_fixed_valid:
                        logger.info(f"修复后的规则验证通过: {risk_point}")
                        fixed_rule_json['compiled'] = True  # 保留标记
                        results.append(fixed_rule_json)
                    else:
                        logger.error(f"修复后的规则仍验证失败: {risk_point}, 错误: {fixed_errors}")
            except Exception as e:
                # 捕获单个风险点处理过程中的异常
                logger.error(f"处理风险点 {risk_point} 时出错: {str(e)}")
        
        # 保存结果
        output_dir = config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"rules_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"处理完成，共生成 {len(results)} 条有效规则，保存至 {output_file}")
        
    except Exception as e:
        # 捕获全局异常
        logger.error(f"系统运行错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()