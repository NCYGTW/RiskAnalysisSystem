"""
ForumEngine
负责Agent间协作和信息交流
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Optional, List
from threading import Lock

class ForumEngine:
    """论坛引擎"""
   
    def __init__(self, log_dir: str = "logs"):
        """初始化论坛引擎"""
        self.log_dir = Path(log_dir)
        self.forum_log_file = self.log_dir / "forum.log"
       
        # 监控状态
        self.is_monitoring = False
        self.monitor_thread = None
        self.write_lock = Lock()  # 锁机制，防止并发写入冲突
       
        self.log_dir.mkdir(exist_ok=True)
   
    def clear_forum_log(self):
        """清空forum.log文件"""
        try:
            if self.forum_log_file.exists():
                self.forum_log_file.unlink()
           
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write_to_forum_log(f"=== ForumEngine 监控开始 - {start_time} ===", "SYSTEM")
               
            print(f"ForumEngine: forum.log 已清空并初始化")
           
        except Exception as e:
            print(f"ForumEngine: 清空forum.log失败: {e}")
   
    def write_to_forum_log(self, content: str, source: str = None):
        """写入内容到forum.log"""
        try:
            with self.write_lock:  # 调用锁
                with open(self.forum_log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    content_one_line = content.replace('\n', '\\n').replace('\r', '\\r')
                    if source:
                        f.write(f"[{timestamp}] [{source}] {content_one_line}\n")
                    else:
                        f.write(f"[{timestamp}] {content_one_line}\n")
                    f.flush()
        except Exception as e:
            print(f"ForumEngine: 写入forum.log失败: {e}")
   
    def get_forum_log_content(self) -> List[str]:
        """获取forum.log的内容"""
        try:
            if not self.forum_log_file.exists():
                return []
           
            with open(self.forum_log_file, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n\r') for line in f.readlines()]
               
        except Exception as e:
            print(f"ForumEngine: 读取forum.log失败: {e}")
            return []

    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            print("ForumEngine: 论坛已经在运行中")
            return False
       
        try:
            # 启动监控
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_forum, daemon=True)
            self.monitor_thread.start()
           
            print("ForumEngine: 论坛已启动")
            return True
           
        except Exception as e:
            print(f"ForumEngine: 启动论坛失败: {e}")
            self.is_monitoring = False
            return False
   
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            print("ForumEngine: 论坛未运行")
            return
       
        try:
            self.is_monitoring = False
           
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
           
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write_to_forum_log(f"=== ForumEngine 论坛结束 - {end_time} ===", "SYSTEM")
           
            print("ForumEngine: 论坛已停止")
           
        except Exception as e:
            print(f"ForumEngine: 停止论坛失败: {e}")

    def _monitor_forum(self):
        """监控论坛"""
        print("ForumEngine: 论坛监控已启动...")
       
        while self.is_monitoring:
            try:
                #此处可以写入具体的监控逻辑
                time.sleep(1)
               
            except Exception as e:
                print(f"ForumEngine: 论坛监控出错: {e}")
                time.sleep(2)
       
        print("ForumEngine: 停止论坛监控")

# 全局监控实例
_monitor_instance = None

def get_monitor() -> ForumEngine:
    """获取全局监控实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ForumEngine()
    return _monitor_instance

def start_forum_monitoring():
    """启动ForumEngine监控"""
    return get_monitor().start_monitoring()

def stop_forum_monitoring():
    """停止ForumEngine监控"""
    get_monitor().stop_monitoring()

def get_forum_log():
    """获取forum.log内容"""
    return get_monitor().get_forum_log_content()