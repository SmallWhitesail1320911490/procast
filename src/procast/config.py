"""
配置管理模块
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为环境变量 CONFIG_PATH 或 config.json
        """
        if config_path is None:
            config_path = os.getenv("CONFIG_PATH", "config.json")
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._override_with_env()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 返回默认配置
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "llm": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "whisper": {
                "model": "base",
                "language": "zh"
            },
            "card": {
                "width": 1080,
                "height": 1920,
                "background_color": "#1a1a2e",
                "text_color": "#ffffff",
                "accent_color": "#e94560",
                "font_path": None,
                "font_size": 48,
                "padding": 100
            },
            "output": {
                "transcript_dir": "output/transcripts",
                "quotes_dir": "output/quotes",
                "cards_dir": "output/cards"
            }
        }
    
    def _override_with_env(self):
        """使用环境变量覆盖配置"""
        # LLM 配置
        if os.getenv("OPENAI_API_KEY"):
            self.config["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_BASE_URL"):
            self.config["llm"]["base_url"] = os.getenv("OPENAI_BASE_URL")
        if os.getenv("ANTHROPIC_API_KEY"):
            self.config["llm"]["anthropic_key"] = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("GOOGLE_API_KEY"):
            self.config["llm"]["google_key"] = os.getenv("GOOGLE_API_KEY")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 "llm.model"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)


# 全局配置实例
config = Config()
