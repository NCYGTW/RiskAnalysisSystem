# 风险解析与验证系统

## 系统概述

本系统是一个基于大语言模型和数据分析的企业财务风险解析与验证系统。该系统通过分析企业的财务数据，自动识别和验证潜在的财务风险，并生成详细的分析报告。

系统采用模块化设计，主要包括以下核心组件：
- **RiskFormulaParserAgent**
- **DataValidationAgent**
- **ReportGenerationAgent**
- **ForumEngine**

## 系统架构

```text
RiskAnalysisSystem/
├── main.py                    # 系统主入口
├── prompt_template.py         # 提示词模板
├── requirements.txt           # 项目依赖
├── config/                    # 配置文件目录
│   ├── __init__.py
│   └── config.py
├── data/                      # 数据文件目录
│   ├── risk_warning.json      # 风险预警数据
│   ├── key_indicators.json    # 关键指标数据
│   ├── project_changes.json   # 项目变更数据
│   └── thirteen_table_data.json # 十三张表数据
├── DataValidationAgent/       # 数据验证模块
│   ├── __init__.py
│   ├── agent.py               # 代理主类
│   ├── nodes/                 # 处理节点
│   ├── state/                 # 状态管理
│   └── utils/                 # 工具函数
├── ReportGenerationAgent/     # 报告生成模块
│   ├── __init__.py
│   ├── agent.py               # 代理主类
│   ├── nodes/                 # 处理节点
│   ├── state/                 # 状态管理
│   ├── templates/             # 报告模板
│   └── utils/                 # 工具函数
├── RiskFormulaParserAgent/    # 风险解析模块
│   ├── __init__.py
│   ├── agent.py               # 代理主类
│   ├── llms/                  # LLM接口
│   ├── nodes/                 # 处理节点
│   ├── state/                 # 状态管理
│   └── utils/                 # 工具函数
├── ForumEngine/               # 论坛引擎模块
├── logs/                      # 日志目录
├── outputs/                   # 输出目录
└── README.md                  # 项目说明文档
```

## 核心组件

### 1. 主程序 (main.py)

`main.py`是系统的主入口文件，负责整个系统的初始化和运行流程。

主要功能：
- 初始化各个代理模块（RiskFormulaParserAgent, DataValidationAgent, ReportGenerationAgent）
- 加载风险数据文件 (`data/risk_warning.json`)
- 逐个处理风险项
- 生成最终的风险分析报告

### 2. 风险公式解析 (RiskFormulaParserAgent)

该代理负责将自然语言描述的风险公式转化为可执行的Python代码。

核心流程：
1. **FormulaAnalysisNode**: 分析风险公式结构，提取关键信息
2. **CodeGenerationNode**: 根据分析结果生成Python代码
3. **ValidationNode**: 验证生成的代码是否符合规范

### 3. 数据验证 (DataValidationAgent)

该代理负责执行生成的风险验证代码，并根据企业财务数据判断是否存在风险。

核心流程：
1. **DataExtractionNode**: 从原始数据中提取验证所需的数据
2. **CodeExecutionNode**: 安全执行生成的Python代码
3. **ResultValidationNode**: 验证执行结果的合理性

### 4. 报告生成 (ReportGenerationAgent)

该代理负责将分析结果整理成结构化的报告。

核心流程：
1. **TemplateSelectionNode**: 选择合适的报告模板
2. **DataVisualizationNode**: 创建数据可视化图表
3. **ReportFormattingNode**: 格式化生成最终报告

### 5. 提示词模板 (prompt_template.py)

包含系统使用的所有提示词模板，用于指导LLM生成代码和文本。

主要模板：
- `RISK_VALIDATION_PROMPT`: 风险验证代码生成提示词
- `RISK_DESCRIPTION_PROMPT`: 风险描述生成提示词
- `FORMULA_ANALYSIS_PROMPT`: 公式结构分析提示词
- `CODE_VALIDATION_PROMPT`: 代码验证提示词

## 数据文件说明

### risk_warning.json

包含企业的风险预警数据，是系统的主要输入文件。数据结构如下：

```json
{
  "generated_time": "生成时间",
  "company_count": "公司数量",
  "data": {
    "公司名称": {
      "风险类别": [
        {
          "具体风险和模型公式编号": "风险描述和公式编号",
          "模型涉及项目": [
            {
              "项目名称": "财务指标名称",
              "类型": "企业/行业",
              "年份": "数值"
            }
          ]
        }
      ]
    }
  }
}
```

## 配置文件

### config.py

系统配置文件，包含以下配置项：
- LLM API密钥
- 默认模型名称
- 输出目录路径
- 日志配置等

## 安装与运行

### 环境要求

- Python 3.7+
- 依赖包见 `requirements.txt`

### 安装步骤

1. 克隆项目代码
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量（API密钥等）
4. 运行系统：
   ```bash
   python main.py
   ```

## 输出文件

系统运行后会在 `outputs/` 目录下生成以下文件：
- `generated_risk_codes_*.json`: 生成的风险验证代码
- `risk_analysis_report_*.md`: 最终的风险分析报告

## 注意事项

1. 系统依赖大语言模型API，需要配置有效的API密钥
