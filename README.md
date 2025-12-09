# ProCast - 播客金句提取与卡片生成工具

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

一个强大的工具，使用 LLM 从播客音频中智能提取金句，并生成精美的分享卡片。

[功能特点](#功能特点) • [快速开始](#快速开始) • [使用指南](#使用指南) • [配置说明](#配置说明) • [示例](#示例)

</div>

---

## ✨ 功能特点

- 🎙️ **音频转文字**: 使用 OpenAI Whisper 高质量转录播客音频
- 🤖 **智能提取金句**: 利用 LLM (GPT-4/Claude/Gemini) 自动识别有价值的内容
- 🎨 **精美卡片生成**: 支持多种风格的金句分享卡片
- ⚡ **一键式流程**: 从音频到卡片的完整自动化处理
- 🎯 **灵活配置**: 支持自定义模型、风格、过滤条件等
- 📊 **智能评分**: 为每条金句评分，便于筛选高质量内容

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/SmallWhitesail1320911490/procast.git
cd procast

# 安装依赖
pip install -r requirements.txt

# 或使用 setup.py 安装
pip install -e .
```

### 系统依赖

需要安装 ffmpeg 用于音频处理：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载 ffmpeg 并添加到 PATH
```

### 配置

1. 复制配置文件模板：
```bash
cp config.example.json config.json
cp .env.example .env
```

2. 编辑 `.env` 文件，添加你的 API 密钥：
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

3. （可选）自定义 `config.json` 中的其他配置

### 快速使用

```bash
# 完整流程：音频 -> 转录 -> 提取金句 -> 生成卡片
procast pipeline your_podcast.mp3

# 查看输出结果
ls output/your_podcast/
```

## 📖 使用指南

### 命令行工具

ProCast 提供了简洁的 CLI 工具：

#### 1. 转录音频

```bash
# 基本用法
procast transcribe audio.mp3

# 指定输出路径和模型
procast transcribe audio.mp3 --output transcript.txt --model medium

# 支持的模型: tiny, base, small, medium, large
```

#### 2. 提取金句

```bash
# 从文本文件提取金句
procast extract transcript.txt

# 自定义数量和过滤
procast extract transcript.txt --num 15 --min-score 7.5 --output quotes.json
```

#### 3. 生成卡片

```bash
# 从金句 JSON 生成卡片
procast generate quotes.json

# 自定义风格和过滤
procast generate quotes.json --style elegant --min-score 8.0 --title "我的播客"
```

#### 4. 完整流程

```bash
# 一键处理
procast pipeline podcast.mp3

# 自定义参数
procast pipeline podcast.mp3 \
  --output-dir my_output \
  --num 20 \
  --min-score 7.5 \
  --style modern \
  --whisper-model medium
```

#### 5. 其他命令

```bash
# 查看配置
procast config-show

# 查看版本
procast version
```

### Python API

也可以在 Python 代码中使用：

```python
from procast import AudioTranscriber, QuoteExtractor, CardGenerator
from procast.config import config

# 1. 转录音频
transcriber = AudioTranscriber(model_name="base")
result = transcriber.transcribe("podcast.mp3", "transcript.txt")

# 2. 提取金句
extractor = QuoteExtractor(
    api_key=config.get("llm.api_key"),
    model="gpt-4-turbo-preview"
)
quotes = extractor.extract_from_file("transcript.txt", "quotes.json")

# 3. 生成卡片
generator = CardGenerator(
    background_color="#1a1a2e",
    accent_color="#e94560"
)
generator.generate_batch(quotes, "cards/", style="minimal")
```

## ⚙️ 配置说明

### LLM 配置

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

支持的 LLM 提供商：
- OpenAI (GPT-4, GPT-3.5)
- 兼容 OpenAI API 的服务（如国内的各种 API）

### Whisper 配置

```json
{
  "whisper": {
    "model": "base",
    "language": "zh"
  }
}
```

模型大小对比：
- `tiny`: 最快，准确度较低
- `base`: **推荐**，平衡速度和准确度
- `small`: 较慢，准确度更高
- `medium`: 很慢，高准确度
- `large`: 最慢，最高准确度

### 卡片样式配置

```json
{
  "card": {
    "width": 1080,
    "height": 1920,
    "background_color": "#1a1a2e",
    "text_color": "#ffffff",
    "accent_color": "#e94560",
    "font_size": 48,
    "padding": 100
  }
}
```

支持的卡片风格：
- `minimal`: 极简风格，左对齐布局
- `elegant`: 优雅风格，居中布局，带装饰边框
- `modern`: 现代风格，左侧装饰条

## 📸 示例

### 输入示例

音频文件：`podcast.mp3` (任意格式的音频文件)

### 输出示例

```
output/podcast/
├── transcript.txt          # 转录文本
├── transcript.json         # 带时间戳的转录结果
├── quotes.json            # 提取的金句数据
└── cards/                 # 生成的卡片图片
    ├── card_001.png
    ├── card_002.png
    └── ...
```

### 金句示例

```json
{
  "quotes": [
    {
      "text": "真正的成长来自于走出舒适区，勇敢面对未知的挑战。",
      "context": "讨论个人成长的话题时提到",
      "category": "个人成长",
      "score": 8.5
    }
  ]
}
```

## 🎨 卡片风格预览

### Minimal 风格
- 极简设计
- 左对齐布局
- 顶部装饰线
- 适合正式内容

### Elegant 风格
- 优雅大方
- 居中对齐
- 装饰边框
- 适合文艺内容

### Modern 风格
- 现代感强
- 左侧装饰条
- 底部色块
- 适合科技内容

## 🔧 进阶功能

### 自定义字体

在配置文件中指定字体路径：

```json
{
  "card": {
    "font_path": "/path/to/your/font.ttf"
  }
}
```

### 批量处理

```python
import os
from pathlib import Path
from procast.cli import pipeline

# 批量处理多个音频文件
audio_dir = Path("podcasts")
for audio_file in audio_dir.glob("*.mp3"):
    pipeline(str(audio_file))
```

### 自定义金句提取规则

```python
# 自定义分类
quotes = extractor.extract(
    text,
    num_quotes=15,
    categories=["技术", "产品", "管理", "思考"]
)

# 自定义过滤
filtered_quotes = extractor.filter_quotes(
    quotes,
    min_score=8.0,
    category="技术",
    max_count=5
)
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 音频转录
- [OpenAI API](https://openai.com/) - LLM 服务
- [Pillow](https://python-pillow.org/) - 图像处理
- [Typer](https://typer.tiangolo.com/) - CLI 框架

## 📮 联系方式

- GitHub: [@SmallWhitesail1320911490](https://github.com/SmallWhitesail1320911490)
- 项目地址: [https://github.com/SmallWhitesail1320911490/procast](https://github.com/SmallWhitesail1320911490/procast)

---

<div align="center">
Made with ❤️ by SmallWhitesail
</div>