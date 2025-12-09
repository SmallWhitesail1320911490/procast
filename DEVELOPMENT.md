# 开发说明

## 项目结构

```
procast/
├── src/procast/           # 源代码
│   ├── __init__.py       # 包初始化
│   ├── config.py         # 配置管理
│   ├── transcriber.py    # 音频转文字
│   ├── extractor.py      # 金句提取
│   ├── card_generator.py # 卡片生成
│   └── cli.py            # 命令行工具
├── output/               # 输出目录（gitignore）
├── config.json           # 用户配置（gitignore）
├── config.example.json   # 配置模板
├── .env                  # 环境变量（gitignore）
├── .env.example          # 环境变量模板
├── requirements.txt      # 依赖列表
├── setup.py              # 安装脚本
├── README.md             # 项目说明
├── EXAMPLES.md           # 使用示例
└── LICENSE               # 许可证
```

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/SmallWhitesail1320911490/procast.git
cd procast
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. 安装开发依赖

```bash
pip install -e .
pip install pytest black flake8 mypy
```

### 4. 配置环境

```bash
cp .env.example .env
cp config.example.json config.json
# 编辑 .env 文件添加你的 API 密钥
```

## 模块说明

### config.py - 配置管理

负责加载和管理配置文件，支持：
- JSON 配置文件
- 环境变量覆盖
- 默认配置

### transcriber.py - 音频转文字

使用 OpenAI Whisper 进行音频转录：
- 支持多种模型大小
- 自动加载模型
- 输出带时间戳的转录结果

### extractor.py - 金句提取

使用 LLM 提取金句：
- 支持自定义分类
- 自动评分和排序
- 支持过滤和筛选

### card_generator.py - 卡片生成

生成精美的金句卡片：
- 支持多种风格
- 自动文本换行
- 支持自定义字体和配色

### cli.py - 命令行工具

提供友好的命令行界面：
- transcribe: 转录音频
- extract: 提取金句
- generate: 生成卡片
- pipeline: 完整流程

## 测试

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
```

### 代码检查

```bash
flake8 src/
mypy src/
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 发布流程

1. 更新版本号 `src/procast/__init__.py`
2. 更新 CHANGELOG
3. 创建 Git 标签
4. 发布到 PyPI

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

## 已知问题

- Whisper 模型首次加载需要下载，可能需要一些时间
- 中文字体在某些系统上可能需要手动配置
- 长音频转录可能需要较多内存

## 未来计划

- [ ] 支持更多 LLM 提供商（Claude, Gemini）
- [ ] 添加 Web 界面
- [ ] 支持视频字幕提取
- [ ] 添加音频降噪功能
- [ ] 支持批量处理界面
- [ ] 添加金句数据库管理
- [ ] 支持多语言（英文等）
- [ ] 优化长音频处理性能
