# RiskResearchAgent

RiskResearchAgent 是一个基于LLM的风险研究系统，专门用于分析CSV格式的文档内容，从中提取与财务造假相关的经验规则，并构建结构化的风险知识库。

## 系统概述

RiskResearchAgent 采用模块化架构设计，通过自然语言处理和机器学习技术，自动化分析CSV文档内容，识别潜在风险点，并将提取的知识存储在结构化的知识库中。系统设计遵循代理（Agent）架构模式，实现了从文档输入到知识输出的端到端处理流程。

## 核心功能

- **CSV文档分析**：自动读取和解析CSV文件内容，提取关键信息片段
- **风险规则提取**：利用大语言模型（LLM）从文档中识别和提取风险判断规则
- **知识库管理**：构建和维护结构化风险知识库，支持文档的增删改查
- **智能检索**：提供基于关键词和语义的高效知识检索功能
- **批量处理**：支持批量处理多个CSV文件，提高分析效率
- **结果导出**：将提取的知识以JSON格式导出，便于后续分析和集成

## 系统架构

```
RiskResearchAgent/
├── agent.py              # Agent 主类
├── main.py              # 主程序入口点
├── prompt_template.py   # 提示词模板管理器
├── requirements.txt     # Python依赖包
├── README.md           # 说明文档
├── config/             # 配置管理
│   ├── __init__.py
│   └── config.py       # 环境配置
├── llms/               # LLM接口层
│   ├── __init__.py
│   ├── base.py         # BaseLLM抽象基类，定义LLM接口
│   └── openrouter_llm.py # 提供具体的LLM服务调用
├── tools/              # 工具模块
│   ├── __init__.py
│   └── knowledge_base.py # KnowledgeBase类，提供知识库存储功能
├── knowledge_base.json # 知识库
└── risk_research.log   # 日志
```

## 环境配置

### 1. 依赖安装

```bash
pip install -r requirements.txt
```

### 2. API密钥配置

系统需要OpenRouter API密钥来调用大语言模型。可以通过以下方式配置：

#### 环境变量配置

```bash
export OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

#### 修改配置文件

编辑 `config/config.py` 文件中的 `openrouter_api_key` 字段。

### 3. 系统配置项

- `OPENROUTER_API_KEY`: OpenRouter API密钥
- `DEFAULT_MODEL`: 默认LLM模型名称（默认: "deepseek/deepseek-chat-v3.1:free"）
- `OUTPUT_DIR`: 输出目录（默认: "outputs"）
- `LOG_DIR`: 日志目录（默认: "logs"）
- `DATA_DIR`: 数据目录（默认: "data"）
- `MAX_RETRIES`: API调用最大重试次数（默认: 5）
- `RETRY_DELAY`: 重试延迟时间（默认: 3.0秒）
- `API_TIMEOUT`: API调用超时时间（默认: 60秒）

## 使用指南

### 1. 系统启动

直接运行主程序：

```bash
python main.py
```

程序将自动：
- 初始化RiskResearchAgent实例
- 读取默认CSV文件 `wechat_search_20251010_174035.csv`
- 调用LLM分析文档内容
- 提取风险规则并更新知识库
- 导出知识库到JSON文件

### 2. 代码集成

作为模块在其他Python程序中使用：

```python
from agent import RiskResearchAgent

# 创建代理实例
research_agent = RiskResearchAgent()

# 处理CSV文件内容
with open("your_csv_file.csv", 'r', encoding='utf-8') as f:
    csv_content = f.read()

result = research_agent.process_csv_content(csv_content, "your_csv_file.csv")

# 导出知识库
export_file = research_agent.export_knowledge_base()
```

### 3. 知识库操作

获取知识库摘要信息：

```python
summary = research_agent.get_knowledge_base_summary()
print(f"文档数量: {summary['document_count']}")
print(f"总字符数: {summary['total_characters']}")
```

## 核心组件

### RiskResearchAgent类 (`agent.py`)

系统主控制器，负责协调各组件工作：

- 实现了`process_csv_content()`方法处理CSV内容
- 使用`_extract_knowledge_from_csv()`方法调用LLM进行知识提取
- 维护KnowledgeBase实例管理知识库
- 实现重试机制和错误处理

### PromptTemplate类 (`prompt_template.py`)

提示词管理器，提供结构化的LLM交互协议：

- `get_csv_analysis_prompt()`: 生成提示词模板
- 定义了数据处理的约束和输出格式规范
- 支持规则提取的标准化输出格式

### OpenRouterLLM类 (`llms/openrouter_llm.py`)

LLM服务客户端，实现与OpenRouter API的交互：

- 继承自BaseLLM抽象基类
- 实现了`call_llm()`方法进行模型调用
- 包含速率限制控制和重试机制
- 使用指数退避策略处理API异常

### KnowledgeBase类 (`tools/knowledge_base.py`)

知识库管理器，提供数据持久化功能：

- 存储格式化的风险知识文档
- 支持文档的添加、更新和删除操作
- 实现JSON文件的序列化和反序列化
- 提供文档计数和导出功能

### BaseLLM抽象基类 (`llms/base.py`)

定义LLM客户端的接口契约：

- 使用ABC（Abstract Base Classes）实现抽象接口
- 定义`call_llm()`抽象方法
- 提供通用的重试机制实现
- 包含模型信息获取功能

## 数据流程

1. **输入阶段**: 从CSV文件读取原始数据内容
2. **预处理阶段**: 通过`PromptTemplate`构造标准化的提示词
3. **LLM处理阶段**: 调用`OpenRouterLLM`进行内容分析和规则提取
4. **知识存储阶段**: 将提取结果存入`KnowledgeBase`进行持久化
5. **输出阶段**: 支持JSON格式的知识库导出

## 输出格式

系统生成以下文件：

- `knowledge_base.json`: 主知识库文件，存储所有处理文档
- `knowledge_base_YYYYMMDD_HHMMSS.json`: 带时间戳的知识库导出文件
- `risk_research.log`: 系统运行日志，记录处理过程和错误信息
- `outputs/`目录: 临时和最终输出文件

## 错误处理与监控

- **API重试机制**: 实现5次重试，使用指数退避策略
- **速率限制控制**: 每次API调用间隔至少2秒
- **异常捕获**: 全面的异常处理，包括网络错误、解析错误等
- **日志记录**: 详细的处理流程日志，便于问题定位
- **状态监控**: 实时报告处理进度和结果状态

## 性能优化

- **并发控制**: 通过速率限制避免API过载
- **缓存机制**: 知识库文件缓存，避免重复加载
- **内存管理**: 分批处理大量数据，避免内存溢出
- **连接复用**: OpenAI SDK客户端复用，减少连接开销

## 扩展性设计

- **插件化LLM**: 通过BaseLLM抽象基类支持多种LLM服务
- **模块化架构**: 各组件职责分离，便于独立开发和测试
- **配置驱动**: 支持通过环境变量动态调整系统参数
- **接口标准化**: 定义清晰的组件接口，支持功能扩展