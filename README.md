# RiskMiningAgent - 无监督风险模型挖掘系统

## 概述

RiskMiningAgent是一个基于大语言模型（LLM）的无监督风险模型挖掘系统，专门用于自动识别和生成财务风险检测规则，能够从风险点中自动提取可执行的财务风险判断规则。

## 系统架构

RiskMiningAgent采用模块化架构，主要包含以下几个核心组件：

### 1. 主控制流 (main.py)
- **main()函数**: 系统主入口，协调整个风险规则生成流程
- **异常处理机制**: 实现了多层级异常处理，确保系统的稳健性
- **日志记录**: 集成Python logging模块，支持文件和控制台日志输出

### 2. 配置管理 (config/config.py)
- **Config数据类**: 管理系统配置参数，包括API密钥、模型名称、输出目录等
- **环境变量加载**: `load_config_from_env()`函数支持从环境变量动态加载配置
- **可配置参数**:
  - `openrouter_api_key`: OpenRouter API密钥
  - `default_model`: 默认LLM模型名称
  - `output_dir`: 输出目录
  - `max_retries`: API调用最大重试次数
  - `retry_delay`: 重试延迟时间
  - `api_timeout`: API超时设置

### 3. LLM抽象层 (llms/)

#### BaseLLM 抽象基类 (llms/base.py)
- **BaseLLM**: 定义了所有LLM客户端的基础接口
- **抽象方法**: `call_llm()`抽象方法强制子类实现具体的API调用逻辑
- **重试机制**: `retry_call()`方法提供了指数退避重试策略

#### OpenRouter LLM实现 (llms/openrouter_llm.py)
- **OpenRouterLLM**: OpenRouter API客户端具体实现
- **OpenAI SDK**: 使用OpenAI SDK进行API调用
- **速率限制**: 实现了`_rate_limit_delay()`方法防止请求过于频繁
- **错误处理**: 处理认证错误、速率限制、超时等异常情况
- **智能重试**: 实现了指数退避策略，包含随机延迟

### 4. 规则生成器 (nodes/rule_generator.py)

#### RuleGenerator类
- **LLM集成**: 与OpenRouterLLM集成，负责调用LLM生成风险规则
- **规则ID生成**: 自动生成格式为`rule_YYYYMMDD_xxx`的唯一规则ID
- **JSON解析**: 使用正则表达式提取LLM响应中的JSON数据
- **规则修复**: `generate_rule_with_fix()`方法支持基于错误提示生成修复后的规则
- **风险点提取**: `_extract_risk_point()`方法从提示词中提取风险点信息

### 5. 规则验证器 (tools/rule_validator.py)

#### RuleValidator类
- **结构验证**: 验证规则JSON结构的完整性
- **字段验证**: 检查必需字段是否存在 (`id`, `risk_point`, `rule_text`, `dsl`, `variables_used`, `source_refs`, `safety_hints`)
- **ID格式验证**: 验证规则ID是否符合`rule_YYYYMMDD_xxx`格式
- **DSL验证**: 检查DSL表达式的语法正确性，包括括号匹配
- **变量验证**: 验证`variables_used`映射的完整性，确保DSL中使用的变量都在映射中定义
- **阈值验证**: `_validate_rule_text_thresholds()`验证规则文本包含明确的阈值和比较基准

### 6. 模板管理器 (tools/template_manager.py)

#### TemplateManager类
- **提示词模板**: 维护LLM提示词模板，指导风险规则生成
- **知识库加载**: 从RiskResearchAgent的`parsed_risk_rules.json`加载财务造假判断经验准则
- **示例规则管理**: 维护规则生成的few-shot示例
- **动态提示词生成**: `generate_prompt()`方法根据风险点动态生成提示词
- **上下文注入**: 将财务造假经验、变量字典、年报片段等上下文信息注入提示词

### 7. 数据加载器 (tools/data_loader.py)
- **风险点加载**: `load_risk_points()`函数从JSON文件加载待处理的风险点列表
- **示例规则加载**: `load_example_rules()`函数加载示例规则用于few-shot学习
- **规则保存**: `save_rules()`函数将生成的规则保存到JSON文件

## 核心工作流程

### 1. 初始化阶段
1. 加载系统配置 (`load_config_from_env()`)
2. 初始化核心组件 (`TemplateManager`, `RuleGenerator`, `RuleValidator`)
3. 加载示例规则和风险点列表

### 2. 规则生成阶段
1. **提示词生成**: 使用`TemplateManager.generate_prompt()`生成针对特定风险点的提示词
2. **LLM调用**: `RuleGenerator.generate_rule()`调用LLM生成规则JSON
3. **JSON解析**: 提取LLM响应中的JSON数据并验证格式

### 3. 规则验证阶段
1. **结构验证**: `RuleValidator.validate()`验证规则的完整性
2. **错误处理**: 如果验证失败，收集错误信息
3. **规则修复**: 调用`RuleGenerator.generate_rule_with_fix()`基于错误提示修复规则

### 4. 输出阶段
1. **结果保存**: 将有效规则保存到JSON文件
2. **日志记录**: 记录处理结果和统计信息

## 输出格式

生成的规则遵循以下JSON结构：

```json
{
  "id": "rule_YYYYMMDD_xxx",
  "risk_point": "...",
  "rule_text": "...",
  "dsl": "...",
  "variables_used": { ... },
  "source_refs": ["stats:...", "text:..."],
  "safety_hints": ["...", "..."]
}
```

- **id**: 规则唯一标识符
- **risk_point**: 相关风险点描述
- **rule_text**: 自然语言规则描述
- **dsl**: 可执行的DSL布尔表达式
- **variables_used**: 变量映射，包含名称、周期、单位信息
- **source_refs**: 源引用，说明阈值来源
- **safety_hints**: 安全提示，包含缺失值、除零错误等注意事项

## 依赖项

系统依赖于以下外部库：
- `openai`: OpenRouter API客户端
- `config`: 系统配置管理
- 标准库模块: `logging`, `json`, `re`, `datetime`, `random`, `os`, `sys`

