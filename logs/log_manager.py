#!/usr/bin/env python3
"""
Advanced Logging System for MCP Manager

Implements a comprehensive logging system with rotation and management.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
import gzip
import shutil
from typing import Optional
import threading
import time


class MCPLogManager:
    """Manages logging for the MCP system with rotation and archiving."""
    
    def __init__(self):
        # Create logs directories if they don't exist
        self.logs_dir = Path("logs")
        self.manager_log_dir = self.logs_dir / "manager"
        self.server_log_dir = self.logs_dir / "mcp_servers"
        self.monitoring_log_dir = self.logs_dir / "monitoring"
        
        for log_dir in [self.manager_log_dir, self.server_log_dir, self.monitoring_log_dir]:
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.max_log_size = self._parse_size(os.getenv("LOG_MAX_SIZE", "10MB"))
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        self.log_rotation_enabled = os.getenv("LOG_ROTATION_ENABLED", "true").lower() == "true"
        
        # Initialize loggers
        self.loggers = {}
        
        # Setup file rotation thread
        self.rotation_thread = None
        self.rotation_enabled = True
        
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)  # Assume bytes if no unit specified
    
    def get_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Get a configured logger instance."""
        if name in self.loggers:
            return self.loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        
        # Prevent adding handlers multiple times
        if logger.handlers:
            return logger
        
        # Set formatter
        formatter = logging.Formatter(self.log_format)
        
        # Determine log file path
        if log_file is None:
            if name.startswith('manager'):
                log_file = self.manager_log_dir / f"{name}.log"
            elif name.startswith('server'):
                log_file = self.server_log_dir / f"{name}.log"
            elif name.startswith('monitor'):
                log_file = self.monitoring_log_dir / f"{name}.log"
            else:
                log_file = self.manager_log_dir / f"{name}.log"
        
        # Create file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Also add console handler for important messages
        if os.getenv("LOG_TO_CONSOLE", "true").lower() == "true":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Store and return logger
        self.loggers[name] = logger
        return logger
    
    def get_server_logger(self, server_name: str) -> logging.Logger:
        """Get a logger for a specific server."""
        return self.get_logger(f"server_{server_name}", self.server_log_dir / f"{server_name}.log")
    
    def get_manager_logger(self) -> logging.Logger:
        """Get the main manager logger."""
        return self.get_logger("manager_main", self.manager_log_dir / "manager.log")
    
    def get_monitoring_logger(self) -> logging.Logger:
        """Get the monitoring logger."""
        return self.get_logger("monitoring_main", self.monitoring_log_dir / "monitoring.log")
    
    def rotate_logs(self):
        """Manually trigger log rotation."""
        for logger in self.loggers.values():
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
    
    def archive_old_logs(self, days_to_keep: int = 30):
        """Archive logs older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_dir in [self.manager_log_dir, self.server_log_dir, self.monitoring_log_dir]:
            for log_file in log_dir.glob("*.log*"):  # Include rotated files
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    # Create archive directory
                    archive_dir = log_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    
                    # Compress and move old files
                    archive_path = archive_dir / f"{log_file.name}.gz"
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original file
                    log_file.unlink()
    
    def get_log_stats(self) -> dict:
        """Get statistics about log files."""
        stats = {}
        
        for log_dir_name, log_dir in [
            ("manager", self.manager_log_dir), 
            ("servers", self.server_log_dir),
            ("monitoring", self.monitoring_log_dir)
        ]:
            dir_stats = []
            for log_file in log_dir.glob("*.log*"):
                file_stat = log_file.stat()
                dir_stats.append({
                    "name": log_file.name,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "path": str(log_file)
                })
            stats[log_dir_name] = dir_stats
        
        return stats
    
    def start_log_cleanup_daemon(self, interval_hours: int = 24):
        """Start a background thread to clean up old logs."""
        def cleanup_loop():
            while self.rotation_enabled:
                try:
                    days_to_keep = int(os.getenv("LOG_RETENTION_DAYS", "30"))
                    self.archive_old_logs(days_to_keep)
                    time.sleep(interval_hours * 3600)
                except Exception as e:
                    print(f"Log cleanup error: {e}")
        
        self.rotation_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.rotation_thread.start()


# Global log manager instance
_log_manager = None
def get_log_manager() -> MCPLogManager:
    global _log_manager
    if _log_manager is None:
        _log_manager = MCPLogManager()
    return _log_manager


if __name__ == "__main__":
    # Example usage
    log_manager = get_log_manager()
    
    # Test logging
    manager_logger = log_manager.get_manager_logger()
    server_logger = log_manager.get_server_logger("test_server")
    monitor_logger = log_manager.get_monitoring_logger()
    
    manager_logger.info("Manager logging test")
    server_logger.info("Server logging test")
    monitor_logger.info("Monitoring logging test")
    
    print("Log stats:", log_manager.get_log_stats())