"""
金句卡片生成模块
使用 Pillow 生成精美的金句分享卡片
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rich.console import Console

console = Console()


class CardGenerator:
    """金句卡片生成器"""
    
    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        background_color: str = "#1a1a2e",
        text_color: str = "#ffffff",
        accent_color: str = "#e94560",
        font_path: Optional[str] = None,
        font_size: int = 48,
        padding: int = 100
    ):
        """
        初始化卡片生成器
        
        Args:
            width: 卡片宽度
            height: 卡片高度
            background_color: 背景颜色
            text_color: 文字颜色
            accent_color: 强调色
            font_path: 字体文件路径
            font_size: 字体大小
            padding: 内边距
        """
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.accent_color = accent_color
        self.padding = padding
        
        # 加载字体
        self.font = self._load_font(font_path, font_size)
        self.title_font = self._load_font(font_path, int(font_size * 0.6))
        self.small_font = self._load_font(font_path, int(font_size * 0.5))
    
    def _load_font(self, font_path: Optional[str], size: int) -> ImageFont.ImageFont:
        """加载字体"""
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                console.print(f"⚠ 无法加载字体 {font_path}: {e}", style="yellow")
        
        # 尝试使用系统字体
        system_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
            "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
        ]
        
        for font in system_fonts:
            if os.path.exists(font):
                try:
                    return ImageFont.truetype(font, size)
                except:
                    continue
        
        # 使用默认字体
        return ImageFont.load_default()
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为 RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _wrap_text(
        self,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int
    ) -> list:
        """自动换行"""
        lines = []
        words = text
        
        # 对于中文，按字符分割
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # 中文文本
            current_line = ""
            for char in text:
                test_line = current_line + char
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
                
                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            
            if current_line:
                lines.append(current_line)
        else:
            # 英文文本
            words = text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
                
                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def generate(
        self,
        quote_text: str,
        title: str = "播客金句",
        subtitle: str = "",
        output_path: str = "card.png",
        style: str = "minimal"
    ) -> str:
        """
        生成金句卡片
        
        Args:
            quote_text: 金句文本
            title: 标题
            subtitle: 副标题（如播客名称、分类等）
            output_path: 输出路径
            style: 卡片风格 (minimal, elegant, modern)
        
        Returns:
            输出文件路径
        """
        # 创建画布
        img = Image.new('RGB', (self.width, self.height), self._hex_to_rgb(self.background_color))
        draw = ImageDraw.Draw(img)
        
        # 根据风格生成不同的卡片
        if style == "minimal":
            self._draw_minimal_card(draw, quote_text, title, subtitle)
        elif style == "elegant":
            self._draw_elegant_card(draw, quote_text, title, subtitle)
        elif style == "modern":
            self._draw_modern_card(draw, quote_text, title, subtitle)
        else:
            self._draw_minimal_card(draw, quote_text, title, subtitle)
        
        # 保存图片
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=95)
        
        console.print(f"✓ 卡片已生成: {output_path}", style="green")
        return str(output_path)
    
    def _draw_minimal_card(
        self,
        draw: ImageDraw.ImageDraw,
        quote_text: str,
        title: str,
        subtitle: str
    ):
        """绘制极简风格卡片"""
        # 绘制顶部装饰线
        accent_rgb = self._hex_to_rgb(self.accent_color)
        draw.rectangle(
            [0, 0, self.width, 10],
            fill=accent_rgb
        )
        
        # 绘制标题
        title_y = self.padding
        draw.text(
            (self.padding, title_y),
            title,
            font=self.title_font,
            fill=self._hex_to_rgb(self.text_color)
        )
        
        # 绘制引号
        quote_y = title_y + 120
        draw.text(
            (self.padding, quote_y),
            '"',
            font=ImageFont.truetype(self.font.path, 120) if hasattr(self.font, 'path') else self.font,
            fill=accent_rgb
        )
        
        # 绘制金句文本
        text_y = quote_y + 100
        max_width = self.width - 2 * self.padding
        lines = self._wrap_text(quote_text, self.font, max_width)
        
        for line in lines:
            draw.text(
                (self.padding, text_y),
                line,
                font=self.font,
                fill=self._hex_to_rgb(self.text_color)
            )
            text_y += self.font.size * 1.5
        
        # 绘制副标题
        if subtitle:
            subtitle_y = self.height - self.padding - 60
            draw.text(
                (self.padding, subtitle_y),
                subtitle,
                font=self.small_font,
                fill=accent_rgb
            )
    
    def _draw_elegant_card(
        self,
        draw: ImageDraw.ImageDraw,
        quote_text: str,
        title: str,
        subtitle: str
    ):
        """绘制优雅风格卡片"""
        # 绘制渐变背景效果（简化版）
        accent_rgb = self._hex_to_rgb(self.accent_color)
        
        # 绘制装饰边框
        border_width = 3
        draw.rectangle(
            [self.padding - 20, self.padding - 20,
             self.width - self.padding + 20, self.height - self.padding + 20],
            outline=accent_rgb,
            width=border_width
        )
        
        # 绘制标题
        title_y = self.padding + 40
        bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = bbox[2] - bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text(
            (title_x, title_y),
            title,
            font=self.title_font,
            fill=accent_rgb
        )
        
        # 绘制分隔线
        line_y = title_y + 80
        line_margin = 150
        draw.line(
            [line_margin, line_y, self.width - line_margin, line_y],
            fill=accent_rgb,
            width=2
        )
        
        # 绘制金句文本（居中）
        text_y = line_y + 100
        max_width = self.width - 2 * self.padding - 40
        lines = self._wrap_text(quote_text, self.font, max_width)
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.font)
            line_width = bbox[2] - bbox[0]
            line_x = (self.width - line_width) // 2
            draw.text(
                (line_x, text_y),
                line,
                font=self.font,
                fill=self._hex_to_rgb(self.text_color)
            )
            text_y += self.font.size * 1.6
        
        # 绘制副标题（居中）
        if subtitle:
            subtitle_y = self.height - self.padding - 80
            bbox = draw.textbbox((0, 0), subtitle, font=self.small_font)
            subtitle_width = bbox[2] - bbox[0]
            subtitle_x = (self.width - subtitle_width) // 2
            draw.text(
                (subtitle_x, subtitle_y),
                subtitle,
                font=self.small_font,
                fill=accent_rgb
            )
    
    def _draw_modern_card(
        self,
        draw: ImageDraw.ImageDraw,
        quote_text: str,
        title: str,
        subtitle: str
    ):
        """绘制现代风格卡片"""
        accent_rgb = self._hex_to_rgb(self.accent_color)
        
        # 绘制左侧装饰条
        draw.rectangle(
            [0, 0, 20, self.height],
            fill=accent_rgb
        )
        
        # 绘制圆角矩形背景
        box_padding = 60
        box_left = self.padding + 20
        box_top = self.padding + 100
        box_right = self.width - self.padding
        box_bottom = self.height - self.padding - 100
        
        # 绘制标题
        title_y = box_padding
        draw.text(
            (box_left, title_y),
            title.upper(),
            font=self.title_font,
            fill=accent_rgb
        )
        
        # 绘制金句文本
        text_y = box_top + 80
        max_width = box_right - box_left - 40
        lines = self._wrap_text(quote_text, self.font, max_width)
        
        for line in lines:
            draw.text(
                (box_left + 20, text_y),
                line,
                font=self.font,
                fill=self._hex_to_rgb(self.text_color)
            )
            text_y += self.font.size * 1.5
        
        # 绘制底部信息
        if subtitle:
            draw.rectangle(
                [box_left, box_bottom - 80, box_right, box_bottom],
                fill=accent_rgb
            )
            draw.text(
                (box_left + 20, box_bottom - 60),
                subtitle,
                font=self.small_font,
                fill=self._hex_to_rgb(self.background_color)
            )
    
    def generate_batch(
        self,
        quotes: list,
        output_dir: str,
        title: str = "播客金句",
        style: str = "minimal"
    ) -> list:
        """
        批量生成金句卡片
        
        Args:
            quotes: 金句列表 (Quote 对象或字典)
            output_dir: 输出目录
            title: 标题
            style: 卡片风格
        
        Returns:
            生成的文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_paths = []
        
        for i, quote in enumerate(quotes, 1):
            # 处理不同的输入格式
            if hasattr(quote, 'text'):
                quote_text = quote.text
                subtitle = getattr(quote, 'category', '')
            elif isinstance(quote, dict):
                quote_text = quote.get('text', '')
                subtitle = quote.get('category', '')
            else:
                quote_text = str(quote)
                subtitle = ''
            
            output_path = output_dir / f"card_{i:03d}.png"
            self.generate(
                quote_text=quote_text,
                title=title,
                subtitle=subtitle,
                output_path=str(output_path),
                style=style
            )
            output_paths.append(str(output_path))
        
        console.print(f"✓ 批量生成完成，共 {len(output_paths)} 张卡片", style="green")
        return output_paths


if __name__ == "__main__":
    # 测试代码
    generator = CardGenerator()
    
    # 生成单张卡片
    # generator.generate(
    #     quote_text="真正的成长来自于走出舒适区，勇敢面对未知的挑战。",
    #     title="播客金句",
    #     subtitle="个人成长",
    #     output_path="output/test_card.png",
    #     style="minimal"
    # )
