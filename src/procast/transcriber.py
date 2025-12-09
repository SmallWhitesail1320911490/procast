"""
音频转文字模块
使用 OpenAI Whisper 进行音频转录
"""

import os
from pathlib import Path
from typing import Optional, Dict
import whisper
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class AudioTranscriber:
    """音频转文字处理类"""
    
    def __init__(self, model_name: str = "base", language: str = "zh"):
        """
        初始化转录器
        
        Args:
            model_name: Whisper 模型名称 (tiny, base, small, medium, large)
            language: 语言代码，默认中文
        """
        self.model_name = model_name
        self.language = language
        self.model = None
        
    def _load_model(self):
        """加载 Whisper 模型"""
        if self.model is None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(
                    description=f"正在加载 Whisper {self.model_name} 模型...",
                    total=None
                )
                self.model = whisper.load_model(self.model_name)
            console.print(f"✓ 模型加载完成", style="green")
    
    def transcribe(
        self,
        audio_path: str,
        output_path: Optional[str] = None,
        verbose: bool = True
    ) -> Dict[str, any]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            output_path: 输出文件路径，如果为 None 则不保存
            verbose: 是否显示详细信息
        
        Returns:
            包含转录结果的字典
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 加载模型
        self._load_model()
        
        # 转录
        if verbose:
            console.print(f"正在转录: {audio_path.name}", style="cyan")
        
        result = self.model.transcribe(
            str(audio_path),
            language=self.language,
            verbose=False
        )
        
        # 保存结果
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存纯文本
            text_path = output_path.with_suffix('.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            # 保存详细结果（包含时间戳）
            import json
            json_path = output_path.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            if verbose:
                console.print(f"✓ 转录完成，已保存到: {text_path}", style="green")
        
        return result
    
    def transcribe_with_timestamps(
        self,
        audio_path: str,
        output_path: Optional[str] = None
    ) -> list:
        """
        转录音频并返回带时间戳的片段
        
        Args:
            audio_path: 音频文件路径
            output_path: 输出文件路径
        
        Returns:
            包含时间戳的片段列表
        """
        result = self.transcribe(audio_path, output_path, verbose=True)
        
        segments = []
        for segment in result.get('segments', []):
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        return segments
    
    def get_full_text(self, audio_path: str) -> str:
        """
        获取音频的完整文本（不保存文件）
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            完整文本
        """
        result = self.transcribe(audio_path, output_path=None, verbose=False)
        return result['text']


if __name__ == "__main__":
    # 测试代码
    transcriber = AudioTranscriber(model_name="base", language="zh")
    
    # 示例：转录音频文件
    # result = transcriber.transcribe("podcast.mp3", "output/transcript.txt")
    # print(result['text'])
