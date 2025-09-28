"""
ReportGenerationAgent主类
"""

import json
import os
from typing import Optional, Dict, Any, List
from .nodes import (
    TemplateSelectionNode,
    DataVisualizationNode,
    ReportFormattingNode
)
from .state import RiskAnalysisState
from .utils import Config, load_config

class ReportGenerationAgent:
    """生成分析报告"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化Report Generation Agent
        
        Args:
            config: 配置对象，如果不提供则自动加载
        """
        # 加载配置
        self.config = config or load_config()
        
        # 初始化节点
        self._initialize_nodes()
        
        # 状态
        self.state = RiskAnalysisState()
        
        # 确保输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        print(f"ReportGeneration Agent已初始化")
    
    def _initialize_nodes(self):
        """初始化处理节点"""
        self.template_selection_node = TemplateSelectionNode()
        self.data_visualization_node = DataVisualizationNode()
        self.report_formatting_node = ReportFormattingNode()
    
    def generate_report(self, analysis_results: List[Dict], save_report: bool = True) -> str:
        """
        生成分析报告
        
        Args:
            analysis_results: 分析结果列表
            save_report: 是否保存报告到文件
            
        Returns:
            生成的报告内容
        """
        print("开始生成分析报告...")
        
        try:
            # Step 1: 选择模板
            template = self._select_template(analysis_results)
            
            # Step 2: 数据可视化
            visualizations = self._create_visualizations(analysis_results)
            
            # Step 3: 格式化报告
            report_content = self._format_report(analysis_results, template, visualizations)
            
            # Step 4: 保存报告
            if save_report:
                self._save_report(report_content)
            
            print("分析报告生成完成")
            return report_content
                
        except Exception as e:
            print(f"生成分析报告时发生错误: {str(e)}")
            return ""

    def _select_template(self, analysis_results: List[Dict]) -> str:
        """选择报告模板"""
        print("  - 选择报告模板...")
        
        template_input = {
            "analysis_results": analysis_results
        }
        
        template = self.template_selection_node.run(template_input)
        
        print("  - 报告模板选择完成")
        return template
    
    def _create_visualizations(self, analysis_results: List[Dict]) -> Dict:
        """创建数据可视化"""
        print("  - 创建数据可视化...")
        
        visualization_input = {
            "analysis_results": analysis_results
        }
        
        visualizations = self.data_visualization_node.run(visualization_input)
        
        print("  - 数据可视化创建完成")
        return visualizations
    
    def _format_report(self, analysis_results: List[Dict], template: str, visualizations: Dict) -> str:
        """格式化报告"""
        print("  - 格式化报告...")
        
        formatting_input = {
            "analysis_results": analysis_results,
            "template": template,
            "visualizations": visualizations
        }
        
        # 格式化报告
        report_content = self.report_formatting_node.run(formatting_input)
        
        print("  - 报告格式化完成")
        return report_content
    
    def _save_report(self, report_content: str):
        """保存报告到文件"""
        # 生成文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"risk_analysis_report_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已保存到: {filepath}")

def create_agent(config_file: Optional[str] = None) -> ReportGenerationAgent:
    """
    创建Report Generation Agent实例的便捷函数
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        ReportGenerationAgent实例
    """
    config = load_config(config_file)
    return ReportGenerationAgent(config)