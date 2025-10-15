"""
知识库模块
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

class KnowledgeBase:
    """知识库，用于存储处理后的文档信息"""
    
    def __init__(self, storage_file: str = "knowledge_base.json"):
        """
        初始化知识库
        
        Args:
            storage_file: 存储文件路径
        """
        self.storage_file = storage_file
        self.documents = self._load_documents()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _load_documents(self) -> List[Dict[str, Any]]:
        """从文件加载已存储的文档"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    else:
                        return []
            except (json.JSONDecodeError, Exception) as e:
                logging.error(f"加载知识库文件失败: {str(e)}")
                return []
        return []
    
    def _save_documents(self):
        """保存文档到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8-sig') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存知识库文件失败: {str(e)}")
    
    def add_document(self, doc_info: Dict[str, Any]):
        """
        添加文档到知识库
        
        Args:
            doc_info: 包含文档信息的字典
        """
        # 添加时间戳
        doc_info['added_at'] = datetime.now().isoformat()
        
        # 检查是否已存在相同的文件名
        existing_index = None
        for i, doc in enumerate(self.documents):
            if doc.get('filename') == doc_info.get('filename'):
                existing_index = i
                break
        
        if existing_index is not None:
            # 更新已存在的文档
            self.documents[existing_index] = doc_info
            logging.info(f"更新了知识库中的文档: {doc_info.get('filename', 'Unknown')}")
        else:
            # 添加新文档
            self.documents.append(doc_info)
            logging.info(f"添加了新文档到知识库: {doc_info.get('filename', 'Unknown')}")
        
        # 保存到文件
        self._save_documents()
    
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档"""
        return self.documents
    
    def get_document_count(self) -> int:
        """获取文档总数"""
        return len(self.documents)
    
    def export_to_file(self, filename: str = None) -> str:
        """
        导出知识库到文件
        
        Args:
            filename: 导出文件名，如果为None则自动生成带时间戳的文件名
            
        Returns:
            导出文件的路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"knowledge_base_export_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logging.info(f"知识库已导出到: {filename}")
            return filename
        except Exception as e:
            logging.error(f"导出知识库失败: {str(e)}")
            return ""