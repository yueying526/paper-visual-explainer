#!/usr/bin/env python3
"""
PDF内容提取脚本
从学术论文PDF中提取文本、图表、公式等内容
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("❌ 缺少依赖库,请安装:")
    print("   pip install PyPDF2 pdfplumber")
    sys.exit(1)


def extract_text_pypdf2(pdf_path):
    """
    使用PyPDF2提取PDF文本

    Args:
        pdf_path: PDF文件路径

    Returns:
        提取的文本内容
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            text = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text.append(f"--- Page {page_num + 1} ---\n{page_text}\n")

            return '\n'.join(text), num_pages

    except Exception as e:
        print(f"❌ PyPDF2提取失败: {e}")
        return None, 0


def extract_text_pdfplumber(pdf_path):
    """
    使用pdfplumber提取PDF文本(更精确)

    Args:
        pdf_path: PDF文件路径

    Returns:
        提取的文本内容和页数
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)

            text = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"--- Page {page_num} ---\n{page_text}\n")

            return '\n'.join(text), num_pages

    except Exception as e:
        print(f"❌ pdfplumber提取失败: {e}")
        return None, 0


def extract_tables(pdf_path):
    """
    提取PDF中的表格

    Args:
        pdf_path: PDF文件路径

    Returns:
        表格列表
    """
    try:
        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()

                for table_num, table in enumerate(page_tables, 1):
                    if table:
                        tables.append({
                            'page': page_num,
                            'table_num': table_num,
                            'data': table
                        })

        return tables

    except Exception as e:
        print(f"❌ 表格提取失败: {e}")
        return []


def extract_metadata(pdf_path):
    """
    提取PDF元数据

    Args:
        pdf_path: PDF文件路径

    Returns:
        元数据字典
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata

            if metadata:
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                }

        return {}

    except Exception as e:
        print(f"⚠️  元数据提取失败: {e}")
        return {}


def extract_paper_structure(text):
    """
    从论文文本中提取结构化信息

    Args:
        text: 论文全文文本

    Returns:
        结构化信息字典
    """
    structure = {
        'title': '',
        'abstract': '',
        'sections': [],
        'references': []
    }

    # 提取标题 (通常在第一页前几行)
    lines = text.split('\n')
    first_lines = [l.strip() for l in lines[:20] if l.strip()]

    # 查找可能的标题 (通常是较短的行,全大写或标题化)
    for line in first_lines:
        if len(line) > 10 and len(line) < 200:
            if line.isupper() or line.istitle():
                structure['title'] = line
                break

    # 提取摘要
    abstract_match = re.search(
        r'(?:Abstract|ABSTRACT)\s*[\n:]?\s*(.*?)(?:Introduction|INTRODUCTION|1\.|Keywords)',
        text,
        re.DOTALL | re.IGNORECASE
    )
    if abstract_match:
        structure['abstract'] = abstract_match.group(1).strip()

    # 提取章节标题
    section_pattern = r'^(?:\d+\.?\s+|#+\s+)([A-Z][A-Za-z\s]+)$'
    sections = re.findall(section_pattern, text, re.MULTILINE)
    structure['sections'] = sections[:20]  # 最多保留20个章节

    # 提取参考文献数量
    refs_match = re.search(r'(?:References|REFERENCES)(.*)', text, re.DOTALL | re.IGNORECASE)
    if refs_match:
        refs_text = refs_match.group(1)
        # 统计参考文献条目 (通常以 [数字] 或 数字. 开头)
        ref_items = re.findall(r'^\s*(?:\[\d+\]|\d+\.)', refs_text, re.MULTILINE)
        structure['references'] = ref_items[:100]  # 最多保留100条引用

    return structure


def save_extracted_content(output_path, content_dict):
    """
    保存提取的内容到文件

    Args:
        output_path: 输出文件路径
        content_dict: 内容字典
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存文本内容
    text_path = output_path.with_suffix('.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(content_dict.get('text', ''))
    print(f"✅ 文本内容已保存: {text_path}")

    # 保存JSON格式的结构化数据
    json_path = output_path.with_suffix('.json')
    json_data = {
        'metadata': content_dict.get('metadata', {}),
        'structure': content_dict.get('structure', {}),
        'num_pages': content_dict.get('num_pages', 0),
        'num_tables': len(content_dict.get('tables', [])),
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 结构化数据已保存: {json_path}")

    # 保存表格 (如果有)
    tables = content_dict.get('tables', [])
    if tables:
        tables_path = output_path.parent / f"{output_path.stem}_tables.json"
        with open(tables_path, 'w', encoding='utf-8') as f:
            json.dump(tables, f, ensure_ascii=False, indent=2)
        print(f"✅ 表格数据已保存: {tables_path}")


def main():
    parser = argparse.ArgumentParser(
        description='从学术论文PDF中提取文本、图表、元数据等内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提取PDF内容到文本文件
  %(prog)s paper.pdf -o extracted/paper

  # 同时提取表格
  %(prog)s paper.pdf --tables

  # 显示论文结构概览
  %(prog)s paper.pdf --structure

  # 使用PyPDF2引擎
  %(prog)s paper.pdf --engine pypdf2
        """
    )

    parser.add_argument(
        'pdf_path',
        help='PDF文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出文件路径前缀 (默认: 与PDF同名)'
    )

    parser.add_argument(
        '--engine',
        choices=['pdfplumber', 'pypdf2'],
        default='pdfplumber',
        help='PDF提取引擎 (默认: pdfplumber)'
    )

    parser.add_argument(
        '--tables',
        action='store_true',
        help='提取表格'
    )

    parser.add_argument(
        '--structure',
        action='store_true',
        help='显示论文结构'
    )

    parser.add_argument(
        '--metadata',
        action='store_true',
        help='显示PDF元数据'
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)

    if not pdf_path.exists():
        print(f"❌ 文件不存在: {pdf_path}")
        return 1

    print(f"📄 正在处理: {pdf_path}")

    # 提取文本
    if args.engine == 'pdfplumber':
        print("🔧 使用pdfplumber引擎...")
        text, num_pages = extract_text_pdfplumber(pdf_path)
    else:
        print("🔧 使用PyPDF2引擎...")
        text, num_pages = extract_text_pypdf2(pdf_path)

    if not text:
        print("❌ 文本提取失败")
        return 1

    print(f"✅ 成功提取 {num_pages} 页内容")
    print(f"   文本长度: {len(text)} 字符")

    # 提取元数据
    metadata = extract_metadata(pdf_path)
    if args.metadata and metadata:
        print(f"\n📋 PDF元数据:")
        for key, value in metadata.items():
            if value:
                print(f"   {key}: {value}")

    # 提取论文结构
    structure = extract_paper_structure(text)
    if args.structure:
        print(f"\n📚 论文结构:")
        if structure['title']:
            print(f"   标题: {structure['title']}")
        if structure['abstract']:
            print(f"   摘要长度: {len(structure['abstract'])} 字符")
            print(f"   摘要预览: {structure['abstract'][:200]}...")
        if structure['sections']:
            print(f"   章节数: {len(structure['sections'])}")
            print(f"   主要章节: {', '.join(structure['sections'][:5])}")
        if structure['references']:
            print(f"   参考文献数: {len(structure['references'])}")

    # 提取表格
    tables = []
    if args.tables:
        print(f"\n📊 正在提取表格...")
        tables = extract_tables(pdf_path)
        print(f"✅ 找到 {len(tables)} 个表格")

    # 保存结果
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = pdf_path.with_suffix('')

    content_dict = {
        'text': text,
        'metadata': metadata,
        'structure': structure,
        'tables': tables,
        'num_pages': num_pages
    }

    save_extracted_content(output_path, content_dict)

    return 0


if __name__ == '__main__':
    sys.exit(main())
