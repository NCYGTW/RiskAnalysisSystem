"""
风险分析状态管理
定义状态数据结构和操作方法
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

@dataclass
class RiskAnalysisState:
    """风险分析状态"""
    task_id: str = ""                    # 任务ID
    company_name: str = ""               # 公司名称
    risk_category: str = ""              # 风险类别
    risk_description: str = ""           # 风险描述
    processing_stage: str = "pending"    # 当前处理阶段
    parsed_formulas: List[Dict] = field(default_factory=list)  # 解析后的公式
    validation_results: List[Dict] = field(default_factory=list)  # 验证结果
    analysis_results: List[Dict] = field(default_factory=list)  # 分析结果
    is_completed: bool = False           # 是否完成
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_stage(self, stage: str):
        """更新处理阶段"""
        self.processing_stage = stage
        self.updated_at = datetime.now().isoformat()
    
    def mark_completed(self):
        """标记为完成"""
        self.is_completed = True
        self.updated_at = datetime.now().isoformat()
    
    def add_parsed_formula(self, formula: Dict):
        """添加解析后的公式"""
        self.parsed_formulas.append(formula)
        self.updated_at = datetime.now().isoformat()
    
    def add_validation_result(self, result: Dict):
        """添加验证结果"""
        self.validation_results.append(result)
        self.updated_at = datetime.now().isoformat()
    
    def add_analysis_result(self, result: Dict):
        """添加分析结果"""
        self.analysis_results.append(result)
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "company_name": self.company_name,
            "risk_category": self.risk_category,
            "risk_description": self.risk_description,
            "processing_stage": self.processing_stage,
            "parsed_formulas": self.parsed_formulas,
            "validation_results": self.validation_results,
            "analysis_results": self.analysis_results,
            "is_completed": self.is_completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskAnalysisState":
        """从字典创建RiskAnalysisState对象"""
        state = cls(
            task_id=data.get("task_id", ""),
            company_name=data.get("company_name", ""),
            risk_category=data.get("risk_category", ""),
            risk_description=data.get("risk_description", ""),
            processing_stage=data.get("processing_stage", "pending"),
            is_completed=data.get("is_completed", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
        
        # 处理列表字段
        state.parsed_formulas = data.get("parsed_formulas", [])
        state.validation_results = data.get("validation_results", [])
        state.analysis_results = data.get("analysis_results", [])
        
        return state
    
    @classmethod
    def from_json(cls, json_str: str) -> "RiskAnalysisState":
        """从JSON字符串创建RiskAnalysisState对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: str):
        """保存状态到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "RiskAnalysisState":
        """从文件加载状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()
        return cls.from_json(json_str)