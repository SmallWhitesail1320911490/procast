# ProCast 使用示例

本文档提供了 ProCast 的详细使用示例。

## 基础示例

### 1. 简单的音频转录

```bash
# 转录单个音频文件
procast transcribe my_podcast.mp3
```

输出：
```
output/transcripts/my_podcast.txt
output/transcripts/my_podcast.json
```

### 2. 从转录文本提取金句

```bash
# 提取 10 条金句
procast extract output/transcripts/my_podcast.txt
```

输出：
```
output/quotes/my_podcast_quotes.json
```

### 3. 生成金句卡片

```bash
# 生成所有金句的卡片
procast generate output/quotes/my_podcast_quotes.json
```

输出：
```
output/cards/card_001.png
output/cards/card_002.png
...
```

## 完整流程示例

### 一键处理播客

```bash
# 使用默认设置
procast pipeline podcast.mp3

# 自定义输出目录
procast pipeline podcast.mp3 --output-dir my_project

# 提取更多金句，只保留高分的
procast pipeline podcast.mp3 --num 20 --min-score 8.0

# 使用更大的 Whisper 模型以提高转录质量
procast pipeline podcast.mp3 --whisper-model medium

# 生成优雅风格的卡片
procast pipeline podcast.mp3 --style elegant
```

## 进阶示例

### 1. 批量处理多个播客

创建一个脚本 `batch_process.py`：

```python
#!/usr/bin/env python3
from pathlib import Path
import subprocess

# 播客文件夹
podcast_dir = Path("podcasts")

# 处理所有 mp3 文件
for audio_file in podcast_dir.glob("*.mp3"):
    print(f"Processing: {audio_file.name}")
    
    subprocess.run([
        "procast", "pipeline", 
        str(audio_file),
        "--output-dir", f"output/{audio_file.stem}",
        "--min-score", "7.5"
    ])
    
    print(f"Completed: {audio_file.name}\n")
```

运行：
```bash
chmod +x batch_process.py
./batch_process.py
```

### 2. 使用 Python API 进行精细控制

创建脚本 `custom_extract.py`：

```python
from procast import AudioTranscriber, QuoteExtractor, CardGenerator
from procast.config import config
from pathlib import Path

# 配置
audio_file = "podcast.mp3"
output_dir = Path("output/custom")
output_dir.mkdir(parents=True, exist_ok=True)

# 步骤 1: 转录
print("Step 1: 转录音频...")
transcriber = AudioTranscriber(model_name="base", language="zh")
transcript_path = output_dir / "transcript.txt"
result = transcriber.transcribe(audio_file, str(transcript_path))
print(f"✓ 转录完成，文本长度: {len(result['text'])} 字符")

# 步骤 2: 提取金句
print("\nStep 2: 提取金句...")
extractor = QuoteExtractor(
    api_key=config.get("llm.api_key"),
    model=config.get("llm.model"),
    base_url=config.get("llm.base_url")
)

# 自定义提取参数
quotes = extractor.extract(
    result['text'],
    num_quotes=15,
    categories=["技术洞察", "产品思维", "商业智慧", "人生感悟"]
)

# 按分数排序并保存
quotes.sort(key=lambda q: q.score, reverse=True)
import json
quotes_data = [q.to_dict() for q in quotes]
with open(output_dir / "quotes.json", 'w', encoding='utf-8') as f:
    json.dump(quotes_data, f, ensure_ascii=False, indent=2)

# 显示前 5 条
print(f"\n✓ 提取了 {len(quotes)} 条金句，前 5 条:")
for i, quote in enumerate(quotes[:5], 1):
    print(f"{i}. [{quote.category}] {quote.text[:50]}... (分数: {quote.score})")

# 步骤 3: 生成多种风格的卡片
print("\nStep 3: 生成卡片...")
generator = CardGenerator(
    background_color="#1a1a2e",
    text_color="#ffffff",
    accent_color="#e94560",
    font_size=52
)

# 只为高分金句（>= 8.0）生成卡片
high_quality_quotes = [q for q in quotes if q.score >= 8.0]

for style in ["minimal", "elegant", "modern"]:
    style_dir = output_dir / f"cards_{style}"
    generator.generate_batch(
        high_quality_quotes,
        str(style_dir),
        title="播客金句",
        style=style
    )
    print(f"✓ {style} 风格卡片已生成到: {style_dir}")

print("\n✓ 全部完成！")
```

### 3. 分类金句并生成不同主题的卡片

```python
from procast.extractor import QuoteExtractor, Quote
from procast.card_generator import CardGenerator
from procast.config import config
import json

# 加载金句
with open("output/quotes/podcast_quotes.json", 'r', encoding='utf-8') as f:
    quotes_data = json.load(f)
quotes = [Quote.from_dict(q) for q in quotes_data]

# 按分类分组
categories = {}
for quote in quotes:
    if quote.category not in categories:
        categories[quote.category] = []
    categories[quote.category].append(quote)

# 为每个分类生成卡片
generator = CardGenerator()

for category, category_quotes in categories.items():
    # 过滤高分金句
    high_score = [q for q in category_quotes if q.score >= 7.5]
    
    if high_score:
        output_dir = f"output/cards_by_category/{category}"
        generator.generate_batch(
            high_score,
            output_dir,
            title=f"{category} • 播客金句",
            style="elegant"
        )
        print(f"✓ {category}: {len(high_score)} 张卡片")
```

### 4. 自定义卡片样式

```python
from procast.card_generator import CardGenerator

# 创建自定义风格的生成器
custom_generator = CardGenerator(
    width=1080,
    height=1920,
    background_color="#0f0e17",  # 深色背景
    text_color="#fffffe",         # 白色文字
    accent_color="#ff8906",       # 橙色强调
    font_size=56,
    padding=120
)

# 生成卡片
custom_generator.generate(
    quote_text="在不确定性中寻找确定性，是创业者的核心能力。",
    title="创业思考",
    subtitle="科技播客",
    output_path="custom_card.png",
    style="modern"
)
```

### 5. 处理长音频（分段处理）

对于超长播客，可以分段处理以提高效率：

```python
from procast import AudioTranscriber, QuoteExtractor
from pydub import AudioSegment
from pathlib import Path

# 加载长音频
audio = AudioSegment.from_mp3("long_podcast.mp3")
duration_ms = len(audio)
segment_length_ms = 10 * 60 * 1000  # 10 分钟一段

# 分段转录
transcriber = AudioTranscriber(model_name="base")
extractor = QuoteExtractor(
    api_key=config.get("llm.api_key"),
    model=config.get("llm.model")
)

all_quotes = []
output_dir = Path("output/segmented")
output_dir.mkdir(parents=True, exist_ok=True)

for i, start_ms in enumerate(range(0, duration_ms, segment_length_ms)):
    end_ms = min(start_ms + segment_length_ms, duration_ms)
    segment = audio[start_ms:end_ms]
    
    # 保存段落
    segment_path = output_dir / f"segment_{i:03d}.mp3"
    segment.export(segment_path, format="mp3")
    
    # 转录并提取
    print(f"Processing segment {i+1}...")
    result = transcriber.transcribe(str(segment_path), None)
    quotes = extractor.extract(result['text'], num_quotes=5)
    all_quotes.extend(quotes)

# 合并所有金句并去重
unique_quotes = []
seen_texts = set()
for quote in all_quotes:
    if quote.text not in seen_texts:
        unique_quotes.append(quote)
        seen_texts.add(quote.text)

print(f"✓ Total unique quotes: {len(unique_quotes)}")
```

## 配置示例

### 使用不同的 LLM 提供商

#### OpenAI GPT-4

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1"
  }
}
```

#### 国内 OpenAI 兼容服务

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-api-key",
    "base_url": "https://your-proxy-service.com/v1"
  }
}
```

### 自定义卡片配色方案

#### 暗夜蓝主题
```json
{
  "card": {
    "background_color": "#0f0e17",
    "text_color": "#fffffe",
    "accent_color": "#ff8906"
  }
}
```

#### 优雅粉主题
```json
{
  "card": {
    "background_color": "#ffe5ec",
    "text_color": "#2b2d42",
    "accent_color": "#d62828"
  }
}
```

#### 科技绿主题
```json
{
  "card": {
    "background_color": "#001219",
    "text_color": "#e9ecef",
    "accent_color": "#00f5d4"
  }
}
```

## 常见问题

### Q: 如何提高转录质量？

使用更大的 Whisper 模型：
```bash
procast pipeline podcast.mp3 --whisper-model medium
```

### Q: 如何只生成最好的金句卡片？

使用 `--min-score` 过滤：
```bash
procast pipeline podcast.mp3 --min-score 8.5
```

### Q: 如何自定义金句分类？

在 Python 代码中使用：
```python
quotes = extractor.extract(
    text,
    categories=["你的", "自定义", "分类"]
)
```

### Q: 卡片中的中文显示不正常？

指定中文字体路径：
```json
{
  "card": {
    "font_path": "/path/to/chinese-font.ttf"
  }
}
```

## 更多资源

- [完整 API 文档](docs/api.md)
- [配置详解](docs/configuration.md)
- [常见问题](docs/faq.md)
