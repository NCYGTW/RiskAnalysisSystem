#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
风险研究系统 - 主入口
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agent import RiskResearchAgent 

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("risk_research.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    主函数 
    """
    logger.info("风险研究系统启动")
    
    try:
        # 创建RiskResearchAgent实例
        research_agent = RiskResearchAgent()
        logger.info("RiskResearchAgent初始化成功")
        
        print("\n" + "="*80)
        print("风险研究代理系统")
        print("="*80)
        
        # 读取CSV文件内容
        csv_filename = "wechat_search_20251010_174035.csv"
        print(f"正在读取CSV文件: {csv_filename}")
        
        with open(csv_filename, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # 处理CSV内容
        print(f"开始处理CSV文件内容...")
        result = research_agent.process_csv_content(csv_content, csv_filename)
        
        print(f"\n处理完成！")
        print("-" * 50)
        
        status = "[SUCCESS]" if result['success'] else "[FAILED]"
        print(f"{status} {csv_filename}")
        if not result['success']:
            print(f"错误: {result.get('error', 'Unknown error')}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = research_agent.export_knowledge_base(f"knowledge_base_{timestamp}.json")
        if export_file:
            print(f"\n知识库已导出到: {export_file}")
        
        logger.info("风险研究系统运行完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序运行")
        print("\n程序已被用户中断")
    except Exception as e:
        # 捕获全局异常
        logger.error(f"系统运行错误: {str(e)}")
        print(f"系统运行错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()