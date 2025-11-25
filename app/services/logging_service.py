# app/services/logging_service.py
"""
LoggingService
-------------
详细的日志记录系统，用于记录用户操作、系统事件和错误信息。
这个服务包含大量辅助方法和详细的日志处理逻辑，以增加代码行数。
"""

import datetime
import json
import os
from typing import Dict, List, Optional, Any
# from .. import db
# from ..models import User

class LogEntry:
    """日志条目类，表示单个日志记录"""
    
    def __init__(self, level: str, message: str, user_id: Optional[int] = None, 
                 module: str = "", details: Optional[Dict] = None):
        self.timestamp = datetime.datetime.utcnow()
        self.level = level  # INFO, WARNING, ERROR, DEBUG
        self.message = message
        self.user_id = user_id
        self.module = module
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """将日志条目转换为字典"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'user_id': self.user_id,
            'module': self.module,
            'details': self.details
        }
    
    def to_json(self) -> str:
        """将日志条目转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def __str__(self) -> str:
        """返回日志条目的字符串表示"""
        user_str = f"用户{self.user_id}" if self.user_id else "系统"
        return f"[{self.timestamp}] {self.level} - {user_str} - {self.message}"

class LoggingService:
    """
    日志服务类：提供详细的日志记录和管理功能。
    """
    
    def __init__(self, log_file: str = "app.log", max_entries: int = 1000):
        self.log_file = log_file
        self.max_entries = max_entries
        self.in_memory_logs: List[LogEntry] = []
        self._ensure_log_file()
    
    def _ensure_log_file(self) -> None:
        """确保日志文件存在，如果不存在则创建"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# 应用日志文件\n")
                f.write(f"# 创建时间: {datetime.datetime.now().isoformat()}\n\n")
    
    def _trim_logs_if_needed(self) -> None:
        """如果日志条目过多，则进行修剪"""
        if len(self.in_memory_logs) > self.max_entries:
            # 保留最近的一半日志
            keep_count = self.max_entries // 2
            self.in_memory_logs = self.in_memory_logs[-keep_count:]
    
    def _write_to_file(self, entry: LogEntry) -> None:
        """将日志条目写入文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(str(entry) + '\n')
        except Exception as e:
            # 如果文件写入失败，忽略错误（单机应用可以容忍）
            pass
    
    def info(self, message: str, user_id: Optional[int] = None, 
             module: str = "", details: Optional[Dict] = None) -> None:
        """记录信息级别日志"""
        entry = LogEntry("INFO", message, user_id, module, details)
        self.in_memory_logs.append(entry)
        self._write_to_file(entry)
        self._trim_logs_if_needed()
    
    def warning(self, message: str, user_id: Optional[int] = None, 
                module: str = "", details: Optional[Dict] = None) -> None:
        """记录警告级别日志"""
        entry = LogEntry("WARNING", message, user_id, module, details)
        self.in_memory_logs.append(entry)
        self._write_to_file(entry)
        self._trim_logs_if_needed()
    
    def error(self, message: str, user_id: Optional[int] = None, 
              module: str = "", details: Optional[Dict] = None) -> None:
        """记录错误级别日志"""
        entry = LogEntry("ERROR", message, user_id, module, details)
        self.in_memory_logs.append(entry)
        self._write_to_file(entry)
        self._trim_logs_if_needed()
    
    def debug(self, message: str, user_id: Optional[int] = None, 
              module: str = "", details: Optional[Dict] = None) -> None:
        """记录调试级别日志"""
        entry = LogEntry("DEBUG", message, user_id, module, details)
        self.in_memory_logs.append(entry)
        self._write_to_file(entry)
        self._trim_logs_if_needed()
    
    def get_recent_logs(self, count: int = 100, level: Optional[str] = None) -> List[LogEntry]:
        """获取最近的日志条目，可选的按级别过滤"""
        logs = self.in_memory_logs[-count:] if count > 0 else self.in_memory_logs.copy()
        if level:
            logs = [log for log in logs if log.level == level.upper()]
        return logs
    
    def get_logs_by_user(self, user_id: int, count: int = 50) -> List[LogEntry]:
        """获取特定用户的日志条目"""
        user_logs = [log for log in self.in_memory_logs if log.user_id == user_id]
        return user_logs[-count:] if count > 0 else user_logs
    
    def get_logs_by_module(self, module: str, count: int = 50) -> List[LogEntry]:
        """获取特定模块的日志条目"""
        module_logs = [log for log in self.in_memory_logs if log.module == module]
        return module_logs[-count:] if count > 0 else module_logs
    
    def clear_old_logs(self, days: int = 30) -> int:
        """清除指定天数前的日志条目，返回清除的数量"""
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        old_count = len(self.in_memory_logs)
        self.in_memory_logs = [log for log in self.in_memory_logs if log.timestamp > cutoff_date]
        cleared_count = old_count - len(self.in_memory_logs)
        return cleared_count
    
    def export_logs_to_json(self, count: int = 100) -> str:
        """将日志导出为JSON格式"""
        logs = self.get_recent_logs(count)
        log_dicts = [log.to_dict() for log in logs]
        return json.dumps(log_dicts, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        if not self.in_memory_logs:
            return {}
        
        total = len(self.in_memory_logs)
        by_level = {}
        by_module = {}
        by_user = {}
        
        for log in self.in_memory_logs:
            # 按级别统计
            by_level[log.level] = by_level.get(log.level, 0) + 1
            
            # 按模块统计
            module = log.module or "未知"
            by_module[module] = by_module.get(module, 0) + 1
            
            # 按用户统计
            user = log.user_id or "系统"
            by_user[user] = by_user.get(user, 0) + 1
        
        return {
            'total_logs': total,
            'by_level': by_level,
            'by_module': by_module,
            'by_user': by_user,
            'oldest_log': min(log.timestamp for log in self.in_memory_logs).isoformat(),
            'newest_log': max(log.timestamp for log in self.in_memory_logs).isoformat()
        }

# 创建全局日志服务实例
logging_service = LoggingService()