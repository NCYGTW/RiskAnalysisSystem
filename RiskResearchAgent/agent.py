"""
RiskResearchAgent主类
负责将CSV文件内容传递给LLM、分析内容、提取信息并构建知识库
"""

import json
import os
import sys
import logging
from typing import Optional, Dict, Any
from llms import OpenRouterLLM, BaseLLM  
from tools import KnowledgeBase
from prompt_template import PromptTemplate
from config.config import config

class RiskResearchAgent:
    """Risk Research Agent主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化Risk Research Agent
        
        Args:
            config_file: 配置文件路径
        """
        # 加载配置
        self.config = config
        
        # 初始化LLM客户端
        self.llm_client = self._initialize_llm()
        
        self.knowledge_base = KnowledgeBase("knowledge_base.json")
        
        # 输出目录存在
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        print(f"RiskResearch Agent已初始化")
        print(f"使用LLM: {self.llm_client.get_model_info()}")
        print(f"知识库文档数量: {self.knowledge_base.get_document_count()}")
    
    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM客户端"""
        return OpenRouterLLM(
            api_key=self.config.openrouter_api_key,
            model_name=self.config.default_model
        )

    def process_csv_content(self, csv_content: str, filename: str) -> Dict[str, Any]:
        """
        处理CSV文件内容
        
        Args:
            csv_content: CSV文件的内容
            filename: CSV文件名
            
        Returns:
            处理结果
        """
        print(f"开始处理CSV文件: {filename}")
        
        try:
            knowledge_result = self._extract_knowledge_from_csv(csv_content, filename)
            
            if knowledge_result:
                # 将提取的知识添加到知识库
                processed_doc = {
                    'filename': filename,
                    'knowledge': knowledge_result,
                    'processed_at': self._get_timestamp()
                }
                
                self.knowledge_base.add_document(processed_doc)
                
                print(f"CSV文件分析完成并已添加到知识库")
                return {
                    'filename': filename,
                    'success': True,
                    'knowledge': knowledge_result
                }
            else:
                print(f"知识提取失败")
                return {
                    'filename': filename,
                    'success': False,
                    'error': '知识提取失败'
                }
                
        except Exception as e:
            print(f"处理CSV文件时出错: {str(e)}")
            return {
                'filename': filename,
                'success': False,
                'error': str(e)
            }
    
    def _extract_knowledge_from_csv(self, csv_content: str, filename: str) -> Optional[Dict[str, Any]]: 
        try:
            print(f"开始使用LLM提取CSV内容知识...")
            
            # 生成分析提示词，传递CSV内容
            prompt = PromptTemplate.get_csv_analysis_prompt(csv_content, filename)
            
            knowledge_text = self.llm_client.call_llm(
                prompt, 
                temperature=0.1, 
                max_tokens=3000,
                max_retries=5,  
                retry_delay=3.0,
                timeout=60  
            )
            
            if knowledge_text:
                knowledge_result = {
                    'extracted_knowledge': knowledge_text,
                    'filename': filename,
                    'timestamp': self._get_timestamp()
                }
                
                print(f"知识提取完成")
                return knowledge_result
            else:
                print(f"LLM调用失败")
                return None
                
        except Exception as e:
            print(f"提取知识时出错: {str(e)}")
            return None
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """获取知识库摘要信息"""
        doc_count = self.knowledge_base.get_document_count()
        all_docs = self.knowledge_base.get_all_documents()
        
        total_chars = 0
        for doc in all_docs:
            if 'knowledge' in doc and 'extracted_knowledge' in doc['knowledge']:
                total_chars += len(doc['knowledge']['extracted_knowledge'])
        
        summary = {
            'document_count': doc_count,
            'total_characters': total_chars,
            'avg_doc_length': total_chars // doc_count if doc_count > 0 else 0,
            'last_updated': self._get_timestamp()
        }
        
        return summary
    
    def export_knowledge_base(self, filename: str = None) -> str:
        """
        导出知识库到文件
        
        Args:
            filename: 导出文件名
            
        Returns:
            导出文件的路径
        """
        return self.knowledge_base.export_to_file(filename)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
