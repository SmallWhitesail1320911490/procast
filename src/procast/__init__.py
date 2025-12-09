"""
ProCast - 播客金句提取与卡片生成工具

使用 LLM 从播客音频中提取金句并生成精美的分享卡片
"""

__version__ = "0.1.0"
__author__ = "SmallWhitesail"

from .transcriber import AudioTranscriber
from .extractor import QuoteExtractor
from .card_generator import CardGenerator

__all__ = [
    "AudioTranscriber",
    "QuoteExtractor", 
    "CardGenerator",
]
