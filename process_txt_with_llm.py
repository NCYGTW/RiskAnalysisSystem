# -*- coding: utf-8 -*-
"""
处理out目录中的txt文件，使用LLM进行结构化
"""

import os
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleLLMClient:
    """LLM客户端"""
    
    def __init__(self):
        """初始化LLM客户端"""
        # 从环境变量获取API密钥
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key or "your_actual_openrouter_api_key_here" in self.api_key:
            logger.error("错误：未设置有效的API密钥！")
            logger.error("请在代码中直接设置self.api_key或通过环境变量设置OPENROUTER_API_KEY")
            self.api_key = "your_actual_openrouter_api_key_here"
        
        #LLM配置
        self.base_url = "https://openrouter.ai/api/v1"
        self.available_models = [
            "tngtech/deepseek-r1t-chimera:free",  
            "tngtech/deepseek-r1t2-chimera:free",     
            "z-ai/glm-4.5-air:free"  
        ]
        self.model_name = self.available_models[0]  
        self.current_model_index = 0  
        self.min_request_interval = 2.0  
        self.last_request_time = 0
        
        # 创建OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # 请求头
        self.extra_headers = {
            "HTTP-Referer": "http://localhost:10808",
            "X-Title": "Risk Research Agent"
        }
    
    def _rate_limit_delay(self, base_delay=1, backoff_factor=1.5):
        """处理速率限制，添加延迟和指数退避
        
        Args:
            base_delay: 基础延迟时间（秒）
            backoff_factor: 退避因子
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        retry_delay = base_delay * (backoff_factor ** getattr(self, 'current_retry', 0))
        
        required_delay = max(self.min_request_interval - time_since_last_request, retry_delay)
        
        if required_delay > 0:
            logger.info(f"等待 {required_delay:.2f} 秒以避免速率限制")
            time.sleep(required_delay)
        
        self.last_request_time = time.time()
    
    def process_text(self, text, filename):
        """调用LLM处理文本，包含速率限制处理和模型切换"""
        # 生成提示词
        prompt = self._generate_prompt(text, filename)
        
        max_retries = 3
        self.current_retry = 0  # 重置当前重试计数
        
        # 检查API密钥是否有效
        if not self.api_key or "your_actual_openrouter_api_key_here" in self.api_key:
            logger.error(f"跳过文件{filename}：API密钥未设置或无效")
            return "API密钥未设置或无效，请在代码中设置有效的OpenRouter API密钥"
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_delay(backoff_factor=2)  # 使用指数退避
                
                completion = self.client.chat.completions.create(
                    extra_headers=self.extra_headers,
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一名擅长信息抽取与整理的金融监管文书分析专家。请阅读以下TXT文件，并将其结构化输出为统一的json格式。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=3000,
                    timeout=60
                )
                
                # 获取LLM响应
                response = completion.choices[0].message.content
                
                # 验证响应是否为JSON
                try:
                    import json
                    if '```json' in response:
                        json_start = response.find('```json') + 7
                        json_end = response.rfind('```')
                        if json_end > json_start:
                            response = response[json_start:json_end]
                    
                    # 尝试解析JSON
                    json.loads(response)
                    logger.info("LLM输出是有效的JSON格式")
                except json.JSONDecodeError:
                    logger.warning("LLM输出不是有效的JSON格式，但仍将保存")
                except ImportError:
                    logger.warning("无法验证JSON格式，未导入json模块")
                
                return response
                
            except Exception as e:
                error_str = str(e)
                logger.error(f"第{attempt+1}次调用LLM失败: {error_str}")
                
                if "429" in error_str or "rate-limited" in error_str.lower():
                    logger.warning(f"遇到速率限制，尝试切换模型或增加延迟")
                    
                    if hasattr(self, 'available_models') and hasattr(self, 'current_model_index') and self.current_model_index < len(self.available_models) - 1:
                        self.current_model_index += 1
                        self.model_name = self.available_models[self.current_model_index]
                        logger.info(f"已切换到备用模型: {self.model_name}")
                
                if attempt < max_retries - 1:
                    # 指数退避
                    retry_delay = 2 ** (attempt + 1)
                    logger.info(f"{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    self.current_retry += 1
                else:
                    logger.error(f"处理文件{filename}失败: {error_str}")
                    raise
    
    def _generate_prompt(self, text, filename):
        """生成提示词模板"""
        prompt_template = '''
【任务要求】
1. 从文本中提取以下字段（如缺失则填"无"）：
   - 文号
   - 公告类型（行政处罚事先告知书 / 行政处罚决定书 / 立案告知书 / 其他）
   - 监管机构（发布单位）
   - 公司简称
   - 公司全称
   - 国民经济行业
   - 控股股东
   - 实际控制人
   - 主营业务
   - 立案日期（若有）
   - 主要违规事项（以项目符号列出，保持原文表述）
   - 涉案年份（如"2019–2022年"）
   - 涉案金额（如涉及虚增收入、利润、罚款金额等，列出数字及单位）
   - 处罚对象列表（若有表格则逐条列出）：
       - 对象名称
       - 身份或职务
       - 违规类型
       - 处罚类型
       - 处罚金额（万元）
       - 处罚期限（如"10年市场禁入"）
   - 法律依据（提取涉及的《证券法》《行政处罚法》《禁入规定》等条款）
   - 总结或监管意见（尽量保留原文）

2. 输出格式：
   使用 **JSON 格式** 输出结果，结构如下：
   ```json
   {{ 
     "文号": "",
     "公告类型": "",
     "监管机构": "",
     "发布日期": "",
     "公司信息": {{ 
       "简称": "",
       "全称": "",
       "行业": "",
       "控股股东": "",
       "实际控制人": "",
       "主营业务": ""
     }},
     "案件信息": {{ 
       "立案日期": "",
       "涉案年份": "",
       "主要违规事项": [],
       "涉案金额": "",
       "处罚对象": [
         {{ 
           "对象名称": "",
           "身份": "",
           "违规类型": "",
           "处罚类型": "",
           "处罚金额_万元": "",
           "处罚期限": ""
         }}
       ],
       "法律依据": [],
       "总结": ""
     }}
   }}
   ```

请处理以下文本内容：
{text_content}
'''
        return prompt_template.format(text_content=text[:10000])  # 限制输入长度

def process_files_in_directory(directory, output_dir):
    """遍历目录处理所有txt文件"""
    # 输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化LLM客户端
    llm_client = SimpleLLMClient()
    
    # 获取所有txt文件
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    txt_files.sort()
    
    total_files = len(txt_files)
    logger.info(f"找到{total_files}个txt文件")
    
    # 逐个处理文件
    for idx, filename in enumerate(txt_files, 1):
        file_path = os.path.join(directory, filename)
        output_path = os.path.join(output_dir, f"structured_{filename}")
        
        logger.info(f"处理文件{idx}/{total_files}: {filename}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 调用LLM处理文本
            structured_text = llm_client.process_text(text, filename)
            
            # 保存结构化结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(structured_text)
            
            logger.info(f"成功保存结果: {output_path}")
            
        except Exception as e:
            logger.error(f"处理文件{filename}失败: {str(e)}")
            error_path = os.path.join(output_dir, f"error_{filename}")
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(f"处理失败: {str(e)}")

def main():
    """主函数"""
    input_dir = r"c:\Users\lenovo\Desktop\spider\out"
    output_dir = r"c:\Users\lenovo\Desktop\spider\structured_output"
    
    process_files_in_directory(input_dir, output_dir)
    logger.info("所有文件处理完成")

if __name__ == "__main__":
    main()