# RiskMiningAgent

RiskMiningAgent 是一个无监督风险模型挖掘系统，通过大语言模型（LLM）为给定的风险点自动生成风险规则和模型。

## 功能特点

- 从输入的风险点列表自动生成风险规则
- 调用LLM生成结构化的风险检测规则
- 自动验证生成的规则格式和逻辑正确性
- 支持规则修复机制，对验证失败的规则进行自动修复
- 输出可执行的DSL规则

## 系统架构

```
RiskMiningAgent/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖
├── README.md           # 说明文件
├── llms/               # LLM接口模块
│   ├── __init__.py
│   ├── base.py         # LLM基类
│   └── openrouter_llm.py # OpenRouter LLM实现
├── nodes/              # 核心节点
│   ├── __init__.py
│   └── rule_generator.py # 规则生成器
├── tools/              # 工具模块
│   ├── __init__.py
│   ├── data_loader.py  # 数据加载器
│   ├── rule_validator.py # 规则验证器
│   └── template_manager.py # 提示词模板管理器
├── config/             # 配置文件
├── data/               # 输入风险点目录
├── outputs/            # 规则输出目录
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 环境配置

首先在环境变量或配置文件中设置 API 密钥：

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

### 2. 直接运行主程序

```bash
python main.py
```

程序将自动加载配置、风险点列表，并开始生成相应的风险规则。

### 3. 作为模块使用

```python
from nodes.rule_generator import RuleGenerator
from tools.rule_validator import RuleValidator
from tools.template_manager import TemplateManager

# 初始化组件
template_manager = TemplateManager()
rule_generator = RuleGenerator()
rule_validator = RuleValidator()

# 生成提示词
prompt = template_manager.generate_prompt(
    risk_point="应收账款周转率异常",
    example_rules=example_rules
)

# 生成风险规则
rule_json = rule_generator.generate_rule(prompt)

# 验证规则
is_valid, errors = rule_validator.validate(rule_json)

if is_valid:
    print(f"规则生成成功: {rule_json['id']}")
```

## 主要组件

### RuleGenerator
通过LLM生成风险规则的核心组件，支持规则修复功能。

### RuleValidator
对生成的规则进行格式和逻辑校验，确保规则的正确性。

### TemplateManager
管理风险规则生成的提示词模板。

### DataLoader
加载风险点列表和示例规则数据。

### OpenRouterLLM
与大语言模型的接口，用于风险规则生成。

## 规则格式

生成的规则包含以下字段：
- `id`: 规则唯一标识符
- `risk_point`: 风险点描述
- `rule_text`: 规则文字描述
- `dsl`: DSL表达式
- `variables_used`: 变量映射表
- `source_refs`: 数据源引用
- `safety_hints`: 安全提示

## 输出

- 规则文件：`outputs/rules_output_YYYYMMDD_HHMMSS.json`
- 日志：`risk_mining.log`