"""
金句提取模块
使用 LLM 从文本中提取有价值的金句
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Quote:
    """金句数据类"""
    
    def __init__(
        self,
        text: str,
        context: str = "",
        category: str = "",
        score: float = 0.0,
        timestamp: Optional[Dict[str, float]] = None
    ):
        self.text = text
        self.context = context
        self.category = category
        self.score = score
        self.timestamp = timestamp or {}
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "text": self.text,
            "context": self.context,
            "category": self.category,
            "score": self.score,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Quote":
        """从字典创建"""
        return cls(
            text=data.get("text", ""),
            context=data.get("context", ""),
            category=data.get("category", ""),
            score=data.get("score", 0.0),
            timestamp=data.get("timestamp", {})
        )


class QuoteExtractor:
    """金句提取器"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.7
    ):
        """
        初始化金句提取器
        
        Args:
            api_key: API 密钥
            model: 模型名称
            base_url: API 基础 URL
            temperature: 温度参数
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
    
    def extract(
        self,
        text: str,
        num_quotes: int = 10,
        min_length: int = 10,
        max_length: int = 200,
        categories: Optional[List[str]] = None
    ) -> List[Quote]:
        """
        从文本中提取金句
        
        Args:
            text: 输入文本
            num_quotes: 期望提取的金句数量
            min_length: 金句最小长度
            max_length: 金句最大长度
            categories: 金句分类列表
        
        Returns:
            金句列表
        """
        if not categories:
            categories = ["启发", "观点", "方法论", "故事", "其他"]
        
        prompt = self._build_prompt(text, num_quotes, min_length, max_length, categories)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(description="正在提取金句...", total=None)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容编辑，擅长从播客或文章中提取有价值的金句。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
        
        result = json.loads(response.choices[0].message.content)
        quotes = []
        
        for item in result.get("quotes", []):
            quote = Quote(
                text=item.get("text", ""),
                context=item.get("context", ""),
                category=item.get("category", ""),
                score=item.get("score", 0.0)
            )
            quotes.append(quote)
        
        console.print(f"✓ 成功提取 {len(quotes)} 条金句", style="green")
        return quotes
    
    def _build_prompt(
        self,
        text: str,
        num_quotes: int,
        min_length: int,
        max_length: int,
        categories: List[str]
    ) -> str:
        """构建提示词"""
        return f"""请从以下文本中提取最有价值的金句。

文本内容：
{text}

要求：
1. 提取约 {num_quotes} 条最有价值的金句
2. 每条金句长度在 {min_length}-{max_length} 字之间
3. 金句应该具有启发性、观点性或实用性
4. 为每条金句分配一个分类：{', '.join(categories)}
5. 为每条金句打分（0-10分），分数越高表示越有价值
6. 提供简短的上下文说明（可选）

请以 JSON 格式返回结果，格式如下：
{{
  "quotes": [
    {{
      "text": "金句内容",
      "context": "上下文说明",
      "category": "分类",
      "score": 8.5
    }}
  ]
}}
"""
    
    def extract_from_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> List[Quote]:
        """
        从文件中提取金句
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            **kwargs: 传递给 extract 方法的参数
        
        Returns:
            金句列表
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")
        
        # 读取文本
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 提取金句
        quotes = self.extract(text, **kwargs)
        
        # 保存结果
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            quotes_data = [q.to_dict() for q in quotes]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(quotes_data, f, ensure_ascii=False, indent=2)
            
            console.print(f"✓ 金句已保存到: {output_path}", style="green")
        
        return quotes
    
    def filter_quotes(
        self,
        quotes: List[Quote],
        min_score: float = 0.0,
        category: Optional[str] = None,
        max_count: Optional[int] = None
    ) -> List[Quote]:
        """
        过滤金句
        
        Args:
            quotes: 金句列表
            min_score: 最低分数
            category: 分类过滤
            max_count: 最大数量
        
        Returns:
            过滤后的金句列表
        """
        filtered = quotes
        
        # 按分数过滤
        if min_score > 0:
            filtered = [q for q in filtered if q.score >= min_score]
        
        # 按分类过滤
        if category:
            filtered = [q for q in filtered if q.category == category]
        
        # 排序并限制数量
        filtered.sort(key=lambda q: q.score, reverse=True)
        
        if max_count:
            filtered = filtered[:max_count]
        
        return filtered


if __name__ == "__main__":
    # 测试代码
    from procast.config import config
    
    extractor = QuoteExtractor(
        api_key=config.get("llm.api_key"),
        model=config.get("llm.model"),
        base_url=config.get("llm.base_url")
    )
    
    # 示例文本
    sample_text = """
    人生的意义不在于你拥有多少，而在于你创造了什么价值。
    真正的成长来自于走出舒适区，勇敢面对未知的挑战。
    在这个快速变化的时代，保持学习能力是最重要的竞争力。
    """
    
    # quotes = extractor.extract(sample_text, num_quotes=3)
    # for quote in quotes:
    #     print(f"{quote.text} (分数: {quote.score})")
