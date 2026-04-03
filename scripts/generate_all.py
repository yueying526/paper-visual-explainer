#!/usr/bin/env python3
"""
一键论文可视化解读工具
用法: python3 scripts/generate_all.py <arxiv_id_or_url> [--output-dir /tmp/reports] [--no-cache]
示例: python3 scripts/generate_all.py 1706.03762
"""

import argparse
import json
import os
import re
import subprocess
import sys
import webbrowser
import concurrent.futures
from datetime import datetime
from pathlib import Path

# 确保脚本所在目录在 Python 路径中，以便直接 import 同目录脚本
SCRIPTS_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPTS_DIR))


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def parse_arxiv_id(raw: str) -> str | None:
    """从 URL 或裸 ID 中提取 arXiv ID（如 1706.03762）"""
    pattern = r'(\d{4}\.\d{4,5})'
    match = re.search(pattern, raw)
    return match.group(1) if match else None


def step(msg: str):
    """打印带分隔线的步骤标题"""
    print(f"\n{'─' * 60}")
    print(f"  {msg}")
    print(f"{'─' * 60}")


def ok(msg: str):
    print(f"✅ {msg}")


def warn(msg: str):
    print(f"⚠️  {msg}")


def err(msg: str):
    print(f"❌ {msg}")


# ──────────────────────────────────────────────
# Step 1: 下载论文
# ──────────────────────────────────────────────

def download_paper(arxiv_id: str, paper_path: Path, no_cache: bool) -> bool:
    """下载论文 PDF，若缓存已存在则跳过"""
    if paper_path.exists() and not no_cache:
        ok(f"论文已缓存，跳过下载: {paper_path}")
        return True

    step(f"[1/5] 下载论文 {arxiv_id}")
    from download_paper import download_from_arxiv
    result = download_from_arxiv(arxiv_id, str(paper_path.parent))
    if not result:
        err("下载失败")
        return False

    # download_from_arxiv 保存为 arxiv_{id}.pdf，统一重命名为 paper.pdf
    downloaded = paper_path.parent / f"arxiv_{arxiv_id}.pdf"
    if downloaded.exists() and downloaded != paper_path:
        downloaded.rename(paper_path)
        ok(f"重命名为 {paper_path.name}")

    return paper_path.exists()


# ──────────────────────────────────────────────
# Step 2: 提取 PDF 内容
# ──────────────────────────────────────────────

def extract_pdf(paper_path: Path, txt_path: Path, json_path: Path, no_cache: bool) -> bool:
    """提取 PDF 文本，若缓存已存在则跳过"""
    if txt_path.exists() and json_path.exists() and not no_cache:
        ok(f"提取结果已缓存，跳过: {txt_path.name}, {json_path.name}")
        return True

    step("[2/5] 提取 PDF 内容")
    from extract_pdf import (
        extract_text_pdfplumber,
        extract_metadata,
        extract_paper_structure,
        save_extracted_content,
    )

    text, num_pages = extract_text_pdfplumber(str(paper_path))
    if not text:
        err("PDF 文本提取失败")
        return False

    print(f"   共 {num_pages} 页，{len(text)} 字符")
    metadata = extract_metadata(str(paper_path))
    structure = extract_paper_structure(text)

    save_extracted_content(
        str(txt_path.with_suffix('')),
        {
            'text': text,
            'metadata': metadata,
            'structure': structure,
            'tables': [],
            'num_pages': num_pages,
        }
    )
    return txt_path.exists()


# ──────────────────────────────────────────────
# Step 3: 生成 article_content.json（LLM 步骤）
# ──────────────────────────────────────────────

ARTICLE_CONTENT_TEMPLATE = {
    "paper_overview": {
        "problem": "（请填写：这篇论文想解决什么问题）",
        "method": "（请填写：用了什么核心方法）",
        "conclusion": "（请填写：达到了什么效果）",
        "industries": ["金融风控", "医疗影像", "自动驾驶"],
        "limitations": ["（请填写局限性1）", "（请填写局限性2）"]
    },
    "key_stats": [
        {"number": "XX", "suffix": "%", "label": "某指标提升", "color": "blue"}
    ],
    "core_insights": [
        {"title": "核心创新点", "content": "（请填写）"},
        {"title": "解决了什么长期痛点", "content": "（请填写）"}
    ],
    "innovations": [
        {"title": "创新点1", "description": "（请填写）"}
    ],
    "terminology": [
        {
            "term": "关键术语",
            "short_def": "简短定义",
            "explanation": "详细解释",
            "analogy_icon": "🔬",
            "analogy": "生活比喻",
            "real_example": "真实案例",
            "example_label": "案例来源"
        }
    ],
    "comparisons": [
        {
            "before_title": "之前的方法",
            "before_content": "（请填写）",
            "after_title": "本文方法",
            "after_content": "（请填写）"
        }
    ],
    "applications": [
        {
            "industry": "行业名称",
            "icon": "🏭",
            "use_case": "具体使用场景",
            "benefit": "带来的具体收益",
            "badge": "研究阶段"
        }
    ],
    "industry_outlook": [
        {
            "industry": "行业",
            "icon": "🚀",
            "impact": "（请填写）",
            "use_cases": ["场景1", "场景2"]
        }
    ],
    "conclusion": "（请填写总结段落）"
}


def ensure_article_content(article_path: Path, txt_path: Path, no_cache: bool) -> bool:
    """
    检查 article_content.json 是否存在。
    - 若存在且非 no_cache 模式，直接使用。
    - 否则创建模板并提示用户手动填写或由 LLM 生成。
    """
    if article_path.exists() and not no_cache:
        ok(f"article_content.json 已存在: {article_path}")
        return True

    step("[3/5] 生成文章内容 (article_content.json)")

    # 先打印提取的论文摘要供参考
    if txt_path.exists():
        text = txt_path.read_text(encoding='utf-8')
        preview = text[:2000].strip()
        print("\n📄 论文内容预览 (前 2000 字符):\n")
        print(preview)
        print("\n" + "─" * 60)

    # 写入模板
    article_path.parent.mkdir(parents=True, exist_ok=True)
    with open(article_path, 'w', encoding='utf-8') as f:
        json.dump(ARTICLE_CONTENT_TEMPLATE, f, ensure_ascii=False, indent=2)

    print(f"""
⚠️  article_content.json 尚未生成。

已在以下路径创建模板文件:
  {article_path}

请通过以下方式之一生成内容：

  方式1 (推荐) — 在 Claude Code 中运行:
    请阅读 {txt_path}
    并根据 references/kazike_style_guide.md 风格
    填写 {article_path}

  方式2 — 手动编辑模板文件后重新运行本脚本。

填写完毕后，重新执行:
  python3 scripts/generate_all.py {article_path.parent.name}
""")
    return False


# ──────────────────────────────────────────────
# Step 4: 并行生成插图
# ──────────────────────────────────────────────

def build_image_prompts(article_path: Path) -> list[tuple[str, str, str]]:
    """从 article_content.json 中构建 3 个图片生成任务 (prompt, filename, style)"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    overview = content.get('paper_overview', {})
    innovations = content.get('innovations', [])
    comparisons = content.get('comparisons', [])

    title_hint = overview.get('method', '') or overview.get('problem', '')
    innov_titles = [i.get('title', '') for i in innovations[:3]]
    concepts_str = ', '.join(innov_titles) if innov_titles else title_hint

    prompts = []

    # 图片1: 核心概念示意图
    p1 = f"创建一个简洁现代的插图,展示这个AI研究方法: {title_hint[:120]}"
    prompts.append((p1, "img1.png", "技术示意图,极简主义,2026设计趋势,柔和色彩"))

    # 图片2: 技术架构图
    p2 = f"创建技术架构图,展示这些AI技术概念之间的关系: {concepts_str[:120]}"
    prompts.append((p2, "img2.png", "系统架构,流程图,现代科技插图,简洁线条"))

    # 图片3: 对比图
    if comparisons:
        c = comparisons[0]
        before = c.get('before_title', '旧方法')
        after = c.get('after_title', '新方法')
        p3 = f"创建前后对比可视化图: {before} 对比 {after}"
    else:
        p3 = f"创建AI技术进步对比图,展示{title_hint[:80]}的改进效果"
    prompts.append((p3, "img3.png", "信息图表,数据可视化,简洁现代,2026设计趋势"))

    return prompts


def generate_images_parallel(article_path: Path, illus_dir: Path, no_cache: bool, fast: bool) -> list[str]:
    """并行生成 3 张插图，已缓存则跳过"""
    step("[4/5] 并行生成 AI 插图")

    from call_nano_banana import generate_image

    poe_key = os.environ.get('POE_API_KEY', '')
    if not poe_key:
        warn("未设置 POE_API_KEY，跳过图片生成。报告将不含插图。")
        return []

    illus_dir.mkdir(parents=True, exist_ok=True)
    tasks = build_image_prompts(article_path)

    def run_one(task):
        prompt, filename, style = task
        out_path = illus_dir / filename
        if out_path.exists() and not no_cache:
            ok(f"插图已缓存: {filename}")
            return str(out_path)
        print(f"🎨 生成: {filename} ...")
        return generate_image(prompt, str(out_path), style=style, fast=fast)

    results = []
    print(f"🚀 并行生成 {len(tasks)} 张图片...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = [executor.submit(run_one, t) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    ok(f"成功生成 {len(results)}/{len(tasks)} 张图片")
    return results


# ──────────────────────────────────────────────
# Step 5: 生成 HTML 报告
# ──────────────────────────────────────────────

def generate_html(report_dir: Path, arxiv_id: str, no_cache: bool) -> Path | None:
    """生成 self-contained HTML 报告"""
    step("[5/5] 生成 HTML 报告")

    article_path = report_dir / "article_content.json"
    report_path = report_dir / "report.html"
    illus_dir = report_dir / "illustrations"

    if report_path.exists() and not no_cache:
        ok(f"报告已缓存: {report_path}")
        return report_path

    if not article_path.exists():
        err(f"article_content.json 不存在: {article_path}")
        return None

    from generate_html_report import generate_html_from_json

    # 构建 paper_data（元数据）
    json_path = report_dir / "extracted.json"
    paper_data = {"title": arxiv_id, "authors": ["arXiv"], "date": datetime.now().strftime('%Y-%m-%d')}
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            extracted = json.load(f)
        structure = extracted.get('structure', {})
        if structure.get('title'):
            paper_data['title'] = structure['title']

    with open(article_path, 'r', encoding='utf-8') as f:
        article_content = json.load(f)

    images_dir_str = str(illus_dir) if illus_dir.exists() else None
    html = generate_html_from_json(paper_data, article_content, str(report_path), images_dir_str)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    ok(f"HTML 报告生成成功: {report_path}")
    return report_path


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='一键论文可视化解读工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/generate_all.py 1706.03762
  python3 scripts/generate_all.py https://arxiv.org/abs/2501.00001
  python3 scripts/generate_all.py 1706.03762 --output-dir /tmp/reports --no-cache
  python3 scripts/generate_all.py 1706.03762 --fast --no-open
        """
    )
    parser.add_argument('arxiv_id_or_url', help='arXiv ID 或 URL，例如 1706.03762')
    parser.add_argument('--output-dir', default='/tmp/reports', help='报告根目录 (默认: /tmp/reports)')
    parser.add_argument('--no-cache', action='store_true', help='忽略缓存，重新运行所有步骤')
    parser.add_argument('--fast', action='store_true', help='图片生成使用更快的简单提示词')
    parser.add_argument('--no-open', action='store_true', help='生成完成后不自动打开浏览器')
    args = parser.parse_args()

    # ── 解析 arxiv ID ──
    arxiv_id = parse_arxiv_id(args.arxiv_id_or_url)
    if not arxiv_id:
        err(f"无法解析 arXiv ID: {args.arxiv_id_or_url}")
        return 1

    print(f"\n🚀 Paper Visual Explainer")
    print(f"   论文 ID : {arxiv_id}")
    print(f"   输出目录: {args.output_dir}/{arxiv_id}")
    if args.no_cache:
        warn("--no-cache 已启用，将重新运行所有步骤")

    # ── 目录结构 ──
    report_dir = Path(args.output_dir) / arxiv_id
    report_dir.mkdir(parents=True, exist_ok=True)

    paper_path   = report_dir / "paper.pdf"
    txt_path     = report_dir / "extracted.txt"
    json_path    = report_dir / "extracted.json"
    article_path = report_dir / "article_content.json"
    illus_dir    = report_dir / "illustrations"
    report_path  = report_dir / "report.html"

    # ── Step 1: 下载 ──
    if not download_paper(arxiv_id, paper_path, args.no_cache):
        return 1

    # ── Step 2: 提取 ──
    if not extract_pdf(paper_path, txt_path, json_path, args.no_cache):
        return 1

    # ── Step 3: 内容（LLM 步骤）──
    if not ensure_article_content(article_path, txt_path, args.no_cache):
        # 输出模板，等待用户填写后重新运行
        return 2

    # ── Step 4: 生成插图（并行）──
    generate_images_parallel(article_path, illus_dir, args.no_cache, args.fast)

    # ── Step 5: 生成 HTML 报告 ──
    final_report = generate_html(report_dir, arxiv_id, args.no_cache)
    if not final_report:
        return 1

    # ── 完成 ──
    print(f"\n{'═' * 60}")
    print(f"  🎉 完成！")
    print(f"  报告路径: {final_report}")
    print(f"{'═' * 60}\n")

    if not args.no_open:
        print("🌐 正在用默认浏览器打开报告...")
        webbrowser.open(f"file://{final_report.resolve()}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
