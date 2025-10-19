# RiskResearchAgent - 风险研究代理系统

## 概述

RiskResearchAgent是一个智能化的风险研究与知识提取系统，专门用于分析文档内容、提取财务造假判断经验准则，并构建结构化的风险知识库。

## 系统架构

RiskResearchAgent采用模块化设计，主要包含以下几个核心组件：

### 1. 主控制流 (main.py)
- **main()函数**: 系统主入口点，协调整个风险研究流程
- **日志配置**: 配置文件和控制台日志输出，记录系统运行状态
- **CSV文件处理**: 读取并处理CSV文件内容，调用RiskResearchAgent进行分析
- **知识库导出**: 将分析结果导出为结构化的知识库文件

### 2. 主代理类 (agent.py)
- **RiskResearchAgent类**: 核心代理类，负责协调各组件完成风险研究任务
- **process_csv_content()方法**: 处理CSV文件内容的主要接口
- **_extract_knowledge_from_csv()方法**: 使用LLM从CSV内容中提取知识
- **get_knowledge_base_summary()方法**: 获取知识库摘要信息
- **export_knowledge_base()方法**: 导出知识库到文件
- **_get_timestamp()方法**: 生成时间戳信息

### 3. 配置管理 (config/config.py)
- **Config数据类**: 管理系统配置参数
- **全局配置**: 全局配置实例，包含API密钥、模型名称、输出目录等参数
- **环境变量支持**: `load_config_from_env()`函数支持从环境变量动态加载配置
- **可配置参数**:
  - `openrouter_api_key`: OpenRouter API密钥
  - `default_model`: 默认LLM模型名称
  - `output_dir`: 输出目录
  - `max_retries`: 最大重试次数
  - `retry_delay`: 重试延迟时间
  - `api_timeout`: API超时设置

### 4. LLM抽象层 (llms/)

#### BaseLLM 抽象基类 (llms/base.py)
- **BaseLLM**: LLM客户端基础接口
- **call_llm()抽象方法**: 强制子类实现LLM调用逻辑
- **retry_call()方法**: 提供指数退避重试策略
- **get_model_info()方法**: 获取模型信息

#### OpenRouter LLM实现 (llms/openrouter_llm.py)
- **OpenRouterLLM**: OpenRouter API客户端实现
- **OpenAI SDK**: 使用OpenAI SDK进行API调用
- **速率限制控制**: `_rate_limit_delay()`方法实现请求频率控制
- **错误处理**: 处理速率限制、超时等异常情况
- **指数退避**: 实现智能重试策略，支持高重试次数和延迟

### 5. 知识库管理 (tools/knowledge_base.py)
- **KnowledgeBase类**: 知识库管理系统
- **_load_documents()方法**: 从文件加载已存储的文档
- **_save_documents()方法**: 保存文档到文件
- **add_document()方法**: 添加文档到知识库，支持更新已存在文档
- **get_all_documents()方法**: 获取所有文档
- **get_document_count()方法**: 获取文档总数
- **export_to_file()方法**: 导出知识库到文件

### 6. 提示词模板 (prompt_template.py)
- **PromptTemplate类**: 提示词模板管理
- **get_csv_analysis_prompt()方法**: 生成CSV内容分析提示词
- **去噪处理**: 忽略广告、转载声明、纯链接、图片占位符等噪声
- **规则提取**: 从CSV内容中提取"指标—比较—基准/阈值—时间窗口"格式的风险规则
- **JSON输出**: 强制输出可解析的JSON格式数据

## 工作流程

### 1. 初始化
1. 加载系统配置 (config/config.py)
2. 初始化LLM客户端 (llms/openrouter_llm.py)
3. 创建知识库实例 (tools/knowledge_base.py)
4. 初始化RiskResearchAgent (agent.py)

### 2. CSV内容分析
1. **文件读取**: 读取指定的CSV文件内容
2. **提示词生成**: 使用PromptTemplate生成分析提示词
3. **LLM调用**: 通过OpenRouterLLM调用LLM进行内容分析
4. **知识提取**: 从LLM响应中提取结构化风险规则

### 3. 知识库构建
1. **文档处理**: 将提取的知识包装为文档格式
2. **去重更新**: 检查是否已存在相同文件名的文档，进行更新或添加
3. **持久化存储**: 保存文档到知识库文件

### 4. 输出
1. **知识库导出**: 将完整的知识库导出为JSON文件
2. **日志记录**: 记录处理过程和结果

## 数据格式规范

### 1. CSV分析提示词格式
系统使用特定的提示词模板对CSV内容进行分析：
- **文件名标识**: 标识待处理的CSV文件
- **内容边界**: 使用`<<CSV_START>>`和`<<CSV_END>>`标记内容范围
- **去噪指令**: 指示LLM忽略广告、转载声明等噪声内容
- **规则提取要求**: 要求提取"指标—比较—基准/阈值—时间窗口"格式的规则

### 2. 输出JSON格式
系统输出的JSON格式包含两个部分：
- **A. rules.jsonl**: 每行一个JSON对象，包含单条风险规则
- **B. summary.json**: 汇总JSON对象，包含文件信息和规则总数

### 3. 风险规则JSON Schema
```json
{
  "risk_point": "string",
  "rule_nl": "string"
}
```
- **risk_point**: 风险点描述
- **rule_nl**: 自然语言描述规则，包含指标、比较运算符、基准/阈值、时间窗口

### 4. 汇总信息JSON Schema
```json
{
  "file": "string",
  "total_rules": "number"
}
```

## 输出文件

### 1. 知识库文件
- **knowledge_base.json**: 持久化存储的知识库文件
- **parsed_risk_rules.json**: 已解析的风险规则文件

### 2. 日志文件
- **risk_research.log**: 系统运行日志

### 3. 分析报告
- **knowledge_base_export_YYYYMMDD_HHMMSS.json**: 导出的知识库文件

## 依赖项

系统依赖于以下外部库：
- `openai`: OpenRouter API客户端
- `dataclasses`: 数据类定义
- `json`: JSON数据处理
- 标准库模块: `os`, `sys`, `logging`, `datetime`, `typing`

## 数据结构

### 风险规则数据结构
```json
[
  {
    "risk_point": "风险点描述",
    "rule_nl": "自然语言规则描述，包含指标比较基准和时间窗口"
  },
  {
    "file": "原始文件名",
    "total_rules": "规则总数"
  }
]
```

### 知识库文档结构
```json
{
  "filename": "CSV文件名",
  "knowledge": {
    "extracted_knowledge": "提取的知识内容",
    "filename": "原文件名",
    "timestamp": "处理时间戳"
  },
  "processed_at": "处理时间",
  "added_at": "添加到知识库时间"
}
```