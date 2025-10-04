"""
报告生成工具
将 ReportGenerationAgent 的非LLM节点逻辑重构为可复用的工具函数。
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import os


def select_template(analysis_results: List[Dict[str, Any]]) -> str:
    """选择报告模板（复用默认模板逻辑）"""
    return _get_default_template()


def _get_default_template() -> str:
    """获取默认模板（与 TemplateSelectionNode 一致）"""
    return """
# 风险分析报告

## 执行摘要

本报告对五家企业的财务风险进行了分析与验证。

## 风险概览

- 总风险数: {total_risks}
- 检测到风险数: {detected_risks}
- 风险检测率: {detection_rate}%

## 详细分析

{risk_details}

## 结论与建议

{conclusions}

---
*报告生成时间: {generation_time}*
"""


def create_visualizations(analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """创建数据可视化占位（与 DataVisualizationNode 当前行为一致）"""
    return {
        "charts": [],
        "graphs": [],
        "tables": [],
    }


def format_report(
    analysis_results: List[Dict[str, Any]],
    template: str,
    visualizations: Optional[Dict[str, Any]] = None,
) -> str:
    """格式化报告内容（与 ReportFormattingNode 保持一致）"""
    visualizations = visualizations or {}

    # 统计风险数据
    total_risks = len(analysis_results)
    detected_risks = sum(1 for r in analysis_results if r.get("is_risk", False))
    detection_rate = (detected_risks / total_risks * 100) if total_risks > 0 else 0

    # 生成风险详情
    risk_details = ""
    for result in analysis_results:
        risk_status = "存在风险" if result.get("is_risk", False) else "无风险"
        risk_details += f"- {result.get('company_name', '')} - {result.get('risk_category', '')}: {risk_status}\n"

    # 生成结论
    conclusions = "根据分析结果，建议关注检测到的高风险项，并采取相应的风险控制措施。"

    # 填充模板
    report_content = template.format(
        total_risks=total_risks,
        detected_risks=detected_risks,
        detection_rate=f"{detection_rate:.1f}",
        risk_details=risk_details,
        conclusions=conclusions,
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    return report_content


def save_report(report_content: str, output_dir: Optional[str] = None) -> str:
    """保存报告到文件并返回路径

    - 优先使用传入的 `output_dir`
    - 未传入时，默认保存至项目 `RiskAnalysisSystem/outputs`
    """
    # 解析默认输出目录（相对当前文件位置）
    if output_dir is None:
        # tools 文件位于 RiskAnalysisSystem/RiskFormulaParserAgent/tools/
        # 默认输出目录设为 RiskAnalysisSystem/outputs
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        output_dir = os.path.join(project_root, "outputs")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"risk_analysis_report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)

    return filepath


def generate_report(
    analysis_results: List[Dict[str, Any]],
    save: bool = True,
    output_dir: Optional[str] = None,
) -> str:
    """一体化报告生成：选择模板、可视化占位、格式化、可选保存

    返回报告内容，如果 `save=True` 同时写入文件。
    """
    template = select_template(analysis_results)
    visualizations = create_visualizations(analysis_results)
    content = format_report(analysis_results, template, visualizations)

    if save:
        save_report(content, output_dir=output_dir)

    return content