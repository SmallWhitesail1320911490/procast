"""
命令行界面工具
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from procast.config import config
from procast.transcriber import AudioTranscriber
from procast.extractor import QuoteExtractor
from procast.card_generator import CardGenerator

app = typer.Typer(
    name="procast",
    help="播客金句提取与卡片生成工具",
    add_completion=False
)
console = Console()


@app.command()
def transcribe(
    audio_path: str = typer.Argument(..., help="音频文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    model: str = typer.Option("base", "--model", "-m", help="Whisper 模型 (tiny/base/small/medium/large)"),
    language: str = typer.Option("zh", "--language", "-l", help="语言代码"),
):
    """转录音频文件为文字"""
    console.print("[bold cyan]开始音频转录...[/bold cyan]")
    
    # 创建转录器
    transcriber = AudioTranscriber(model_name=model, language=language)
    
    # 设置默认输出路径
    if output is None:
        output_dir = Path(config.get("output.transcript_dir", "output/transcripts"))
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_name = Path(audio_path).stem
        output = str(output_dir / f"{audio_name}.txt")
    
    # 转录
    try:
        result = transcriber.transcribe(audio_path, output)
        console.print(f"\n[bold green]✓ 转录成功！[/bold green]")
        console.print(f"输出文件: {output}")
    except Exception as e:
        console.print(f"[bold red]✗ 转录失败: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def extract(
    text_path: str = typer.Argument(..., help="文本文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    num: int = typer.Option(10, "--num", "-n", help="提取金句数量"),
    min_score: float = typer.Option(0.0, "--min-score", help="最低分数过滤"),
):
    """从文本中提取金句"""
    console.print("[bold cyan]开始提取金句...[/bold cyan]")
    
    # 创建提取器
    extractor = QuoteExtractor(
        api_key=config.get("llm.api_key"),
        model=config.get("llm.model"),
        base_url=config.get("llm.base_url"),
        temperature=config.get("llm.temperature", 0.7)
    )
    
    # 设置默认输出路径
    if output is None:
        output_dir = Path(config.get("output.quotes_dir", "output/quotes"))
        output_dir.mkdir(parents=True, exist_ok=True)
        text_name = Path(text_path).stem
        output = str(output_dir / f"{text_name}_quotes.json")
    
    # 提取金句
    try:
        quotes = extractor.extract_from_file(
            text_path,
            output,
            num_quotes=num
        )
        
        # 过滤金句
        if min_score > 0:
            quotes = extractor.filter_quotes(quotes, min_score=min_score)
        
        # 显示结果
        console.print(f"\n[bold green]✓ 成功提取 {len(quotes)} 条金句[/bold green]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("序号", style="dim", width=6)
        table.add_column("金句", width=60)
        table.add_column("分类", width=12)
        table.add_column("分数", justify="right", width=8)
        
        for i, quote in enumerate(quotes, 1):
            table.add_row(
                str(i),
                quote.text[:60] + "..." if len(quote.text) > 60 else quote.text,
                quote.category,
                f"{quote.score:.1f}"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗ 提取失败: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def generate(
    quotes_path: str = typer.Argument(..., help="金句 JSON 文件路径"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="输出目录"),
    title: str = typer.Option("播客金句", "--title", "-t", help="卡片标题"),
    style: str = typer.Option("minimal", "--style", "-s", help="卡片风格 (minimal/elegant/modern)"),
    min_score: float = typer.Option(0.0, "--min-score", help="最低分数过滤"),
    max_count: int = typer.Option(0, "--max-count", help="最大生成数量"),
):
    """生成金句卡片"""
    console.print("[bold cyan]开始生成金句卡片...[/bold cyan]")
    
    # 加载金句
    import json
    from procast.extractor import Quote
    
    with open(quotes_path, 'r', encoding='utf-8') as f:
        quotes_data = json.load(f)
    
    quotes = [Quote.from_dict(q) for q in quotes_data]
    
    # 过滤金句
    if min_score > 0 or max_count > 0:
        from procast.extractor import QuoteExtractor
        extractor = QuoteExtractor(
            api_key=config.get("llm.api_key"),
            model=config.get("llm.model")
        )
        quotes = extractor.filter_quotes(
            quotes,
            min_score=min_score,
            max_count=max_count if max_count > 0 else None
        )
    
    # 设置默认输出路径
    if output_dir is None:
        output_dir = Path(config.get("output.cards_dir", "output/cards"))
    output_dir = Path(output_dir)
    
    # 创建卡片生成器
    generator = CardGenerator(
        width=config.get("card.width", 1080),
        height=config.get("card.height", 1920),
        background_color=config.get("card.background_color", "#1a1a2e"),
        text_color=config.get("card.text_color", "#ffffff"),
        accent_color=config.get("card.accent_color", "#e94560"),
        font_path=config.get("card.font_path"),
        font_size=config.get("card.font_size", 48),
        padding=config.get("card.padding", 100)
    )
    
    # 生成卡片
    try:
        output_paths = generator.generate_batch(
            quotes,
            str(output_dir),
            title=title,
            style=style
        )
        console.print(f"\n[bold green]✓ 成功生成 {len(output_paths)} 张卡片[/bold green]")
        console.print(f"输出目录: {output_dir}")
    except Exception as e:
        console.print(f"[bold red]✗ 生成失败: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def pipeline(
    audio_path: str = typer.Argument(..., help="音频文件路径"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="输出目录"),
    num_quotes: int = typer.Option(10, "--num", "-n", help="提取金句数量"),
    min_score: float = typer.Option(7.0, "--min-score", help="最低分数过滤"),
    style: str = typer.Option("minimal", "--style", "-s", help="卡片风格"),
    whisper_model: str = typer.Option("base", "--whisper-model", help="Whisper 模型"),
):
    """完整流程：转录 -> 提取金句 -> 生成卡片"""
    console.print("[bold cyan]开始完整处理流程...[/bold cyan]\n")
    
    audio_path = Path(audio_path)
    audio_name = audio_path.stem
    
    # 设置输出目录
    if output_dir is None:
        output_dir = Path("output") / audio_name
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 步骤 1: 转录音频
    console.print("[bold]步骤 1/3: 转录音频[/bold]")
    transcriber = AudioTranscriber(model_name=whisper_model, language="zh")
    transcript_path = output_dir / "transcript.txt"
    
    try:
        transcriber.transcribe(str(audio_path), str(transcript_path))
    except Exception as e:
        console.print(f"[bold red]✗ 转录失败: {e}[/bold red]")
        raise typer.Exit(1)
    
    # 步骤 2: 提取金句
    console.print(f"\n[bold]步骤 2/3: 提取金句[/bold]")
    extractor = QuoteExtractor(
        api_key=config.get("llm.api_key"),
        model=config.get("llm.model"),
        base_url=config.get("llm.base_url"),
        temperature=config.get("llm.temperature", 0.7)
    )
    quotes_path = output_dir / "quotes.json"
    
    try:
        quotes = extractor.extract_from_file(
            str(transcript_path),
            str(quotes_path),
            num_quotes=num_quotes
        )
        
        # 过滤金句
        quotes = extractor.filter_quotes(quotes, min_score=min_score)
        
        if not quotes:
            console.print(f"[bold yellow]⚠ 没有找到分数 >= {min_score} 的金句[/bold yellow]")
            raise typer.Exit(0)
        
    except Exception as e:
        console.print(f"[bold red]✗ 提取失败: {e}[/bold red]")
        raise typer.Exit(1)
    
    # 步骤 3: 生成卡片
    console.print(f"\n[bold]步骤 3/3: 生成卡片[/bold]")
    generator = CardGenerator(
        width=config.get("card.width", 1080),
        height=config.get("card.height", 1920),
        background_color=config.get("card.background_color", "#1a1a2e"),
        text_color=config.get("card.text_color", "#ffffff"),
        accent_color=config.get("card.accent_color", "#e94560"),
        font_path=config.get("card.font_path"),
        font_size=config.get("card.font_size", 48),
        padding=config.get("card.padding", 100)
    )
    cards_dir = output_dir / "cards"
    
    try:
        generator.generate_batch(
            quotes,
            str(cards_dir),
            title="播客金句",
            style=style
        )
    except Exception as e:
        console.print(f"[bold red]✗ 生成卡片失败: {e}[/bold red]")
        raise typer.Exit(1)
    
    # 完成
    console.print(f"\n[bold green]✓ 全部完成！[/bold green]")
    console.print(f"输出目录: {output_dir}")
    console.print(f"- 转录文本: {transcript_path}")
    console.print(f"- 金句数据: {quotes_path}")
    console.print(f"- 卡片图片: {cards_dir}")


@app.command()
def config_show():
    """显示当前配置"""
    import json
    console.print("[bold cyan]当前配置:[/bold cyan]\n")
    console.print(json.dumps(config.config, indent=2, ensure_ascii=False))


@app.command()
def version():
    """显示版本信息"""
    from procast import __version__
    console.print(f"ProCast version {__version__}")


if __name__ == "__main__":
    app()
