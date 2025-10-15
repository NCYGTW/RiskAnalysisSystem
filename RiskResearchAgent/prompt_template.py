"""
提示词模板
"""

class PromptTemplate:
    """提示词模板"""
    
    @staticmethod
    def get_csv_analysis_prompt(csv_content: str, filename: str) -> str:  
        """
        生成CSV内容分析提示词
        
        Args:
            csv_content: CSV文件的内容
            filename: CSV文件名
            
        Returns:
            提示词模板
        """
        prompt = f"""
你是一名文献分析专家。目标：从 CSV 文本中抽取对"财务造假判断"有用的经验准则：
[输入]
filename: {filename}
<<CSV_START>>
{csv_content}
<<CSV_END>>

[操作步骤]
1) 去噪：忽略广告/转载声明/纯链接/图片占位。
2) 规则提取：用自然语言写清"指标—比较—基准/阈值—时间窗口"。


CSV文件名: {filename}

CSV内容:
{csv_content}

[输出]
- 只输出 JSON，分两段：
  A. rules.jsonl —— 每行一个 JSON 对象：
  B. summary.json —— 仅一个 JSON 对象，作为最后一行单独输出。
- 所有 JSON 必须可解析，使用半角标点，不要写注释，参考格式如下：
{{
  "rules": [
    {{"risk_point":"…","rule_nl":"…"}},
    …
  ],
  "summary": {{"file":"…","total_rules":"…"}}
}}

A. 单条规则 JSON Schema：
{{
  "risk_point": "string",
  "rule_nl": "string",      //自然语言描述规则，包含指标、比较运算符、基准/阈值、时间窗口
}}

B. 汇总 JSON Schema：
{{
  "file": "{filename}",
  "total_rules": "number",
}}

[约束]
- 不输出除 JSON 以外的任何文字。
- 尽量多思考一段时间，至少输出20条规则。
"""
        return prompt
