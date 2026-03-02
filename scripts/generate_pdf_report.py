#!/usr/bin/env python3
"""
生成PDF格式的论文解读报告
支持层级结构、重点标注、配图插入
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    from reportlab.platypus import Table, TableStyle, KeepTogether
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("❌ 缺少依赖库,请安装:")
    print("   pip install reportlab")
    sys.exit(1)


# 颜色定义 (2026设计趋势)
PRIMARY_COLOR = HexColor('#2563eb')      # 主色调-蓝色
SECONDARY_COLOR = HexColor('#7c3aed')    # 次色调-紫色
ACCENT_COLOR = HexColor('#f59e0b')       # 强调色-橙色
TEXT_COLOR = HexColor('#1f2937')         # 文本-深灰
LIGHT_BG = HexColor('#f9fafb')           # 浅背景
HIGHLIGHT_BG = HexColor('#fef3c7')       # 高亮背景


def setup_chinese_fonts():
    """
    设置中文字体支持
    尝试使用系统中文字体,如果失败则使用英文字体
    """
    try:
        # macOS/Linux常见中文字体路径
        chinese_fonts = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS PingFang
            '/System/Library/Fonts/STHeiti Medium.ttc',  # macOS 黑体
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
            'C:\\Windows\\Fonts\\msyh.ttc',  # Windows 微软雅黑
        ]

        for font_path in chinese_fonts:
            if Path(font_path).exists():
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                return 'ChineseFont'

        print("⚠️  未找到中文字体,将使用英文字体")
        return 'Helvetica'

    except Exception as e:
        print(f"⚠️  中文字体加载失败: {e}")
        return 'Helvetica'


def create_custom_styles(font_name='Helvetica'):
    """创建自定义样式"""
    styles = getSampleStyleSheet()

    # 标题样式
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=20,
        alignment=TA_CENTER,
        bold=True
    ))

    # 一级标题
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=10,
        bold=True
    ))

    # 二级标题
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=8,
        bold=True
    ))

    # 正文
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=11,
        textColor=TEXT_COLOR,
        spaceBefore=6,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=16
    ))

    # 高亮框
    styles.add(ParagraphStyle(
        name='HighlightBox',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=11,
        textColor=TEXT_COLOR,
        backColor=HIGHLIGHT_BG,
        spaceBefore=10,
        spaceAfter=10,
        leftIndent=15,
        rightIndent=15,
        borderWidth=1,
        borderColor=ACCENT_COLOR,
        borderPadding=10
    ))

    # 术语
    styles.add(ParagraphStyle(
        name='Term',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=10,
        textColor=SECONDARY_COLOR,
        backColor=LIGHT_BG,
        bold=True
    ))

    return styles


def create_cover_page(title, authors, date):
    """创建封面"""
    cover_elements = []

    cover_elements.append(Spacer(1, 2*inch))

    # 标题
    cover_title = Paragraph(title, ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=PRIMARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=30
    ))
    cover_elements.append(cover_title)

    cover_elements.append(Spacer(1, 0.5*inch))

    # 副标题
    subtitle = Paragraph("论文解读报告", ParagraphStyle(
        name='Subtitle',
        fontName='Helvetica',
        fontSize=18,
        textColor=SECONDARY_COLOR,
        alignment=TA_CENTER
    ))
    cover_elements.append(subtitle)

    cover_elements.append(Spacer(1, 1*inch))

    # 作者
    author_text = Paragraph(f"作者: {authors}", ParagraphStyle(
        name='Author',
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_CENTER
    ))
    cover_elements.append(author_text)

    cover_elements.append(Spacer(1, 0.2*inch))

    # 日期
    date_text = Paragraph(f"日期: {date}", ParagraphStyle(
        name='Date',
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_CENTER
    ))
    cover_elements.append(date_text)

    cover_elements.append(PageBreak())

    return cover_elements


def add_section(elements, styles, title, content_list):
    """添加章节"""
    # 章节标题
    elements.append(Paragraph(title, styles['CustomHeading1']))
    elements.append(Spacer(1, 0.2*inch))

    # 章节内容
    for content in content_list:
        if isinstance(content, str):
            elements.append(Paragraph(content, styles['CustomBody']))
        elif isinstance(content, dict):
            # 处理结构化内容
            if content.get('type') == 'highlight':
                elements.append(Paragraph(content['text'], styles['HighlightBox']))
            elif content.get('type') == 'image':
                add_image(elements, content['path'], content.get('caption', ''))

    elements.append(Spacer(1, 0.3*inch))


def add_image(elements, image_path, caption='', max_width=5*inch):
    """添加图片"""
    try:
        if not Path(image_path).exists():
            print(f"⚠️  图片不存在: {image_path}")
            return

        img = Image(image_path, width=max_width, height=max_width*0.75)
        elements.append(img)

        if caption:
            caption_style = ParagraphStyle(
                name='Caption',
                fontName='Helvetica-Oblique',
                fontSize=9,
                textColor=HexColor('#6b7280'),
                alignment=TA_CENTER,
                spaceAfter=15
            )
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(caption, caption_style))

    except Exception as e:
        print(f"⚠️  图片添加失败: {e}")


def generate_pdf_from_json(paper_data, article_content, output_path, images_dir=None):
    """
    根据JSON数据生成PDF报告

    Args:
        paper_data: 论文元数据字典
        article_content: 解读文章内容字典
        output_path: 输出PDF路径
        images_dir: 图片目录路径
    """
    # 创建PDF文档
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    elements = []

    # 设置字体
    font_name = setup_chinese_fonts()
    styles = create_custom_styles(font_name)

    # 封面
    title = paper_data.get('title', '未知标题')
    authors = ', '.join(paper_data.get('authors', ['未知作者']))
    date = paper_data.get('date', datetime.now().strftime('%Y-%m-%d'))

    cover = create_cover_page(title, authors, date)
    elements.extend(cover)

    # 1. 核心观点解读
    if 'core_insights' in article_content:
        add_section(
            elements,
            styles,
            '核心观点解读',
            article_content['core_insights']
        )

    # 2. 技术创新点
    if 'innovations' in article_content:
        innovation_content = []
        for i, innovation in enumerate(article_content['innovations'], 1):
            innovation_content.append({
                'type': 'highlight',
                'text': f"<b>创新点 {i}: {innovation.get('title', '')}</b><br/>{innovation.get('description', '')}"
            })

        add_section(elements, styles, '技术创新点', innovation_content)

    # 3. 关键术语解释
    if 'terminology' in article_content:
        term_content = []
        for term in article_content['terminology']:
            term_text = f"<b>{term.get('term', '')}</b>: {term.get('explanation', '')}"
            term_content.append(term_text)

        add_section(elements, styles, '关键术语解释', term_content)

    # 4. 比喻说明
    if 'analogies' in article_content:
        analogy_content = []
        for analogy in article_content['analogies']:
            analogy_content.append({
                'type': 'highlight',
                'text': f"{analogy.get('icon', '💡')} {analogy.get('content', '')}"
            })

        add_section(elements, styles, '通俗易懂的比喻', analogy_content)

    # 5. 可视化配图
    if images_dir:
        images_path = Path(images_dir)
        if images_path.exists():
            image_files = list(images_path.glob('*.png')) + list(images_path.glob('*.jpg'))
            if image_files:
                elements.append(Paragraph('可视化示意图', styles['CustomHeading1']))
                elements.append(Spacer(1, 0.2*inch))

                for img_file in sorted(image_files):
                    caption = img_file.stem.replace('_', ' ').title()
                    add_image(elements, str(img_file), caption)

                elements.append(Spacer(1, 0.3*inch))

    # 6. 实际应用场景
    if 'applications' in article_content:
        add_section(
            elements,
            styles,
            '实际应用场景',
            article_content['applications']
        )

    # 7. 总结与展望
    if 'conclusion' in article_content:
        add_section(
            elements,
            styles,
            '总结与展望',
            [article_content['conclusion']]
        )

    # 页脚
    footer_text = Paragraph(
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 由AI自动生成 | 基于卡兹克风格",
        ParagraphStyle(
            name='Footer',
            fontName='Helvetica',
            fontSize=8,
            textColor=HexColor('#6b7280'),
            alignment=TA_CENTER
        )
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(footer_text)

    # 生成PDF
    doc.build(elements)


def main():
    parser = argparse.ArgumentParser(
        description='生成PDF格式的论文解读报告',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'paper_json',
        help='论文数据JSON文件路径'
    )

    parser.add_argument(
        'article_json',
        help='解读文章内容JSON文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出PDF文件路径'
    )

    parser.add_argument(
        '--images-dir',
        help='图片目录路径'
    )

    args = parser.parse_args()

    try:
        # 读取论文数据
        with open(args.paper_json, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)

        # 读取文章内容
        with open(args.article_json, 'r', encoding='utf-8') as f:
            article_content = json.load(f)

        # 生成PDF
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"📄 正在生成PDF报告...")

        generate_pdf_from_json(paper_data, article_content, output_path, args.images_dir)

        file_size = output_path.stat().st_size / 1024  # KB
        print(f"✅ PDF报告生成成功: {output_path}")
        print(f"   文件大小: {file_size:.1f} KB")

        return 0

    except Exception as e:
        print(f"❌ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
