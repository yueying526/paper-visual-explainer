#!/usr/bin/env python3
"""
论文下载脚本
支持从arXiv、Google Scholar等学术网站搜索并下载论文PDF
"""

import argparse
import os
import re
import requests
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin


def download_from_arxiv(arxiv_url_or_id, output_dir="."):
    """
    从arXiv下载论文PDF

    Args:
        arxiv_url_or_id: arXiv URL或论文ID (如 2401.12345 或 https://arxiv.org/abs/2401.12345)
        output_dir: 输出目录

    Returns:
        下载的PDF文件路径,如果失败返回None
    """
    # 提取arXiv ID
    arxiv_id_pattern = r'(\d{4}\.\d{4,5})(v\d+)?'

    if 'arxiv.org' in arxiv_url_or_id:
        match = re.search(arxiv_id_pattern, arxiv_url_or_id)
        if match:
            arxiv_id = match.group(1)
        else:
            print(f"❌ 无法从URL中提取arXiv ID: {arxiv_url_or_id}")
            return None
    else:
        # 假设直接提供的是ID
        match = re.match(arxiv_id_pattern, arxiv_url_or_id)
        if match:
            arxiv_id = match.group(1)
        else:
            print(f"❌ 无效的arXiv ID格式: {arxiv_url_or_id}")
            return None

    # 构建PDF下载URL
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # 构建输出文件路径
    output_path = Path(output_dir) / f"arxiv_{arxiv_id}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📥 正在从arXiv下载论文...")
    print(f"   论文ID: {arxiv_id}")
    print(f"   下载URL: {pdf_url}")

    try:
        # 下载PDF
        response = requests.get(pdf_url, stream=True, timeout=60)
        response.raise_for_status()

        # 检查是否真的是PDF文件
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            print(f"❌ 下载的文件不是PDF格式: {content_type}")
            return None

        # 保存文件
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   进度: {progress:.1f}%", end='', flush=True)

        print()  # 换行
        print(f"✅ 论文下载成功: {output_path}")
        print(f"   文件大小: {downloaded / 1024:.1f} KB")

        return str(output_path)

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {e}")
        return None


def get_arxiv_metadata(arxiv_id):
    """
    获取arXiv论文元数据

    Args:
        arxiv_id: arXiv论文ID

    Returns:
        包含标题、作者、摘要等信息的字典
    """
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()

        # 简单解析XML (使用正则表达式,避免引入xml库)
        content = response.text

        title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Unknown"

        summary_match = re.search(r'<summary>(.*?)</summary>', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

        # 提取所有作者
        authors = re.findall(r'<name>(.*?)</name>', content)

        return {
            'title': title,
            'authors': authors,
            'summary': summary,
            'arxiv_id': arxiv_id
        }

    except Exception as e:
        print(f"⚠️  获取论文元数据失败: {e}")
        return None


def search_arxiv(query, max_results=5):
    """
    搜索arXiv论文

    Args:
        query: 搜索关键词
        max_results: 最多返回结果数

    Returns:
        论文列表
    """
    api_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results={max_results}"

    print(f"🔍 正在arXiv搜索: {query}")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()

        content = response.text

        # 提取所有entry
        entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)

        results = []
        for entry in entries:
            # 提取ID
            id_match = re.search(r'<id>http://arxiv.org/abs/(\d{4}\.\d{4,5})(v\d+)?</id>', entry)
            if not id_match:
                continue
            arxiv_id = id_match.group(1)

            # 提取标题
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Unknown"

            # 提取作者
            authors = re.findall(r'<name>(.*?)</name>', entry)

            # 提取摘要
            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else ""

            results.append({
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors[:3],  # 只保留前3个作者
                'summary': summary[:200] + '...' if len(summary) > 200 else summary
            })

        return results

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='从arXiv等学术网站下载论文PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 通过arXiv URL下载
  %(prog)s https://arxiv.org/abs/2401.12345

  # 通过arXiv ID下载
  %(prog)s 2401.12345

  # 搜索并下载
  %(prog)s --search "transformer attention mechanism" --download-first

  # 仅搜索不下载
  %(prog)s --search "deepseek mhc" --max-results 10
        """
    )

    parser.add_argument(
        'url_or_id',
        nargs='?',
        help='arXiv URL或论文ID'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='输出目录 (默认: 当前目录)'
    )

    parser.add_argument(
        '-s', '--search',
        help='搜索关键词'
    )

    parser.add_argument(
        '-m', '--max-results',
        type=int,
        default=5,
        help='搜索最多返回结果数 (默认: 5)'
    )

    parser.add_argument(
        '--download-first',
        action='store_true',
        help='搜索后自动下载第一个结果'
    )

    parser.add_argument(
        '--metadata',
        action='store_true',
        help='显示论文元数据'
    )

    args = parser.parse_args()

    # 搜索模式
    if args.search:
        results = search_arxiv(args.search, args.max_results)

        if not results:
            print("❌ 未找到相关论文")
            return 1

        print(f"\n✅ 找到 {len(results)} 篇相关论文:\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. [{paper['arxiv_id']}] {paper['title']}")
            print(f"   作者: {', '.join(paper['authors'])}")
            print(f"   摘要: {paper['summary']}")
            print()

        if args.download_first and results:
            print(f"📥 自动下载第一篇论文...")
            download_from_arxiv(results[0]['arxiv_id'], args.output)

        return 0

    # 直接下载模式
    if not args.url_or_id:
        parser.print_help()
        return 1

    # 获取元数据
    if args.metadata:
        # 提取arXiv ID
        arxiv_id_pattern = r'(\d{4}\.\d{4,5})'
        match = re.search(arxiv_id_pattern, args.url_or_id)
        if match:
            arxiv_id = match.group(1)
            metadata = get_arxiv_metadata(arxiv_id)
            if metadata:
                print(f"\n📄 论文元数据:")
                print(f"   标题: {metadata['title']}")
                print(f"   作者: {', '.join(metadata['authors'])}")
                print(f"   摘要: {metadata['summary'][:300]}...")
                print()

    # 下载论文
    pdf_path = download_from_arxiv(args.url_or_id, args.output)

    if pdf_path:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
