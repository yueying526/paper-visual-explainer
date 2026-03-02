#!/usr/bin/env python3
"""
生成现代互动风格的HTML论文解读报告
- 小白友好的「论文速读」总览开篇
- 术语与比喻融合展示（可展开卡片）
- 丰富的行业应用场景与展望
- 阅读进度条、导航高亮、滚动动画、计数器动画等互动元素
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def escape_html(text):
    """转义HTML特殊字符"""
    if not isinstance(text, str):
        text = str(text)
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def process_text(text):
    """处理文本：转义HTML并转换换行符"""
    if not isinstance(text, str):
        text = str(text)
    text = escape_html(text)
    text = text.replace('\\n\\n', '<br><br>')
    text = text.replace('\\n', '<br>')
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    return text


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 论文解读</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --text: #1e293b;
            --text-light: #64748b;
            --bg: #f8fafc;
            --bg-card: #ffffff;
            --border: #e2e8f0;
            --blue: #3b82f6;
            --blue-light: #eff6ff;
            --blue-border: rgba(59,130,246,0.2);
            --purple: #8b5cf6;
            --purple-light: #f5f3ff;
            --green: #10b981;
            --green-light: #ecfdf5;
            --orange: #f59e0b;
            --orange-light: #fffbeb;
            --red: #ef4444;
            --red-light: #fef2f2;
            --shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.04);
            --shadow-hover: 0 4px 20px rgba(0,0,0,0.1), 0 8px 32px rgba(0,0,0,0.07);
            --radius: 14px;
            --radius-sm: 9px;
        }}

        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                         "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.75;
            color: var(--text);
            background: var(--bg);
            font-size: 16px;
        }}

        /* ── 阅读进度条 ── */
        #progress-bar {{
            position: fixed;
            top: 0; left: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--blue), var(--purple));
            z-index: 1000;
            border-radius: 0 3px 3px 0;
            transition: width 0.1s linear;
        }}

        /* ── 顶部导航 ── */
        .nav-bar {{
            position: sticky; top: 0;
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            z-index: 100;
        }}
        .nav-inner {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            gap: 4px;
            height: 52px;
            overflow-x: auto;
            scrollbar-width: none;
        }}
        .nav-inner::-webkit-scrollbar {{ display: none; }}
        .nav-tag {{
            font-size: 13px;
            color: var(--text-light);
            white-space: nowrap;
            cursor: pointer;
            padding: 5px 12px;
            border-radius: 20px;
            transition: all 0.2s;
            text-decoration: none;
            flex-shrink: 0;
        }}
        .nav-tag:hover {{ background: var(--blue-light); color: var(--blue); }}
        .nav-tag.active {{ background: var(--blue); color: #fff; }}

        /* ── 主体容器 ── */
        .main-wrapper {{
            max-width: 900px;
            margin: 0 auto;
            padding: 28px 24px 80px;
        }}

        /* ── 论文标题卡 ── */
        .paper-header {{
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 36px 44px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }}
        .paper-header h1 {{
            font-size: 26px;
            font-weight: 700;
            line-height: 1.35;
            color: var(--text);
            margin-bottom: 10px;
        }}
        .paper-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            color: var(--text-light);
            font-size: 14px;
            margin-top: 12px;
        }}

        /* ── 关键数字统计 ── */
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }}
        .stat-box {{
            text-align: center;
            padding: 18px 12px;
            background: var(--bg);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
        }}
        .stat-number {{
            font-size: 34px;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 6px;
        }}
        .stat-number.blue {{ color: var(--blue); }}
        .stat-number.green {{ color: var(--green); }}
        .stat-number.purple {{ color: var(--purple); }}
        .stat-number.orange {{ color: var(--orange); }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-light);
            line-height: 1.4;
        }}

        /* ── 通用卡片 ── */
        .card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 28px 32px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            transition: box-shadow 0.25s, transform 0.25s;
        }}
        .card:hover {{
            box-shadow: var(--shadow-hover);
            transform: translateY(-1px);
        }}

        .section-heading {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-heading .badge {{
            font-size: 20px;
            width: 36px; height: 36px;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg);
            border: 1px solid var(--border);
            flex-shrink: 0;
        }}

        /* ── 论文速读：总览区 ── */
        .overview-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }}
        .overview-item {{
            background: var(--bg);
            border-radius: var(--radius-sm);
            padding: 18px 20px;
            border: 1px solid var(--border);
        }}
        .overview-item.full {{ grid-column: 1 / -1; }}
        .overview-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 8px;
        }}
        .overview-label.problem {{ color: var(--blue); }}
        .overview-label.method {{ color: var(--purple); }}
        .overview-label.conclusion {{ color: var(--green); }}
        .overview-label.limit {{ color: var(--red); }}
        .overview-label.industry {{ color: var(--orange); }}
        .overview-content {{
            font-size: 15px;
            line-height: 1.65;
            color: var(--text);
        }}
        .tag-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 4px;
        }}
        .tag {{
            padding: 3px 11px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }}
        .tag-blue {{ background: var(--blue-light); color: var(--blue); }}
        .tag-red {{ background: var(--red-light); color: var(--red); }}
        .tag-orange {{ background: var(--orange-light); color: var(--orange); }}
        .tag-green {{ background: var(--green-light); color: var(--green); }}

        /* ── 核心观点 ── */
        .insight-item {{
            padding: 18px 20px;
            border-left: 3px solid var(--blue);
            background: var(--blue-light);
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            margin-bottom: 14px;
        }}
        .insight-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--blue);
            margin-bottom: 6px;
        }}
        .insight-content {{
            font-size: 15px;
            line-height: 1.7;
        }}

        /* ── 创新点卡片网格 ── */
        .innovation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
        }}
        .innovation-card {{
            background: linear-gradient(135deg, var(--purple-light), var(--bg));
            border: 1px solid rgba(139,92,246,0.18);
            border-radius: var(--radius-sm);
            padding: 20px;
            transition: all 0.25s;
            position: relative;
            overflow: hidden;
        }}
        .innovation-card:hover {{
            border-color: var(--purple);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }}
        .innovation-num {{
            font-size: 42px;
            font-weight: 900;
            color: var(--purple);
            opacity: 0.15;
            line-height: 1;
            margin-bottom: 6px;
        }}
        .innovation-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 8px;
        }}
        .innovation-desc {{
            font-size: 14px;
            color: var(--text-light);
            line-height: 1.6;
        }}

        /* ── 术语+比喻融合：可展开卡片 ── */
        .term-card {{
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            margin-bottom: 12px;
            overflow: hidden;
            transition: border-color 0.2s;
        }}
        .term-card:hover {{ border-color: var(--blue-border); }}
        .term-card.expanded {{ border-color: var(--blue); }}

        .term-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            cursor: pointer;
            background: var(--bg);
            user-select: none;
            transition: background 0.2s;
            gap: 12px;
        }}
        .term-header:hover {{ background: var(--blue-light); }}
        .term-card.expanded .term-header {{ background: var(--blue-light); }}

        .term-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }}
        .term-badge {{
            background: var(--blue);
            color: #fff;
            font-size: 13px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 20px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .term-short {{
            font-size: 14px;
            color: var(--text-light);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .term-arrow {{
            font-size: 14px;
            color: var(--text-light);
            transition: transform 0.25s;
            flex-shrink: 0;
        }}
        .term-card.expanded .term-arrow {{ transform: rotate(180deg); }}

        .term-body {{
            display: none;
            padding: 18px;
            border-top: 1px solid var(--border);
            background: var(--bg-card);
        }}
        .term-card.expanded .term-body {{ display: block; }}

        .term-explain {{
            background: var(--blue-light);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            margin-bottom: 10px;
            font-size: 15px;
            line-height: 1.7;
            border-left: 3px solid var(--blue);
        }}
        .term-explain strong {{ color: var(--blue); }}

        .term-analogy {{
            background: var(--orange-light);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            margin-bottom: 10px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
            border-left: 3px solid var(--orange);
        }}
        .analogy-emoji {{ font-size: 26px; line-height: 1; flex-shrink: 0; margin-top: 2px; }}
        .term-analogy-text {{ font-size: 15px; line-height: 1.7; }}

        .term-example {{
            background: var(--green-light);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            border-left: 3px solid var(--green);
        }}
        .example-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--green);
            margin-bottom: 6px;
        }}
        .example-content {{ font-size: 14px; line-height: 1.65; }}

        /* ── 数据对比 ── */
        .comparison-wrap {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 20px;
            margin-bottom: 14px;
        }}
        .comparison-row {{
            display: grid;
            grid-template-columns: 1fr 40px 1fr;
            gap: 12px;
            align-items: center;
        }}
        .comp-box {{
            padding: 16px;
            border-radius: var(--radius-sm);
            text-align: center;
        }}
        .comp-before {{
            background: var(--red-light);
            border: 1px solid rgba(239,68,68,0.2);
        }}
        .comp-after {{
            background: var(--green-light);
            border: 1px solid rgba(16,185,129,0.2);
        }}
        .comp-label {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }}
        .comp-before .comp-label {{ color: var(--red); }}
        .comp-after .comp-label {{ color: var(--green); }}
        .comp-value {{
            font-size: 20px;
            font-weight: 700;
            line-height: 1.35;
        }}
        .comp-before .comp-value {{ color: var(--red); }}
        .comp-after .comp-value {{ color: var(--green); }}
        .comp-arrow {{ text-align: center; font-size: 22px; color: var(--text-light); }}

        /* ── 应用场景：行业卡片网格 ── */
        .app-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
        }}
        .app-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 22px;
            transition: all 0.25s;
        }}
        .app-card:hover {{
            border-color: var(--blue);
            box-shadow: 0 0 0 3px var(--blue-light), var(--shadow-hover);
            transform: translateY(-2px);
        }}
        .app-icon {{ font-size: 34px; margin-bottom: 10px; display: block; }}
        .app-industry {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--blue);
            margin-bottom: 6px;
        }}
        .app-usecase {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .app-benefit {{
            font-size: 14px;
            color: var(--text-light);
            line-height: 1.6;
        }}
        .app-badge {{
            display: inline-block;
            margin-top: 12px;
            padding: 3px 10px;
            background: var(--green-light);
            color: var(--green);
            font-size: 12px;
            font-weight: 600;
            border-radius: 20px;
        }}

        /* ── 行业展望 ── */
        .outlook-list {{ display: flex; flex-direction: column; gap: 14px; }}
        .outlook-item {{
            display: flex;
            gap: 16px;
            padding: 20px;
            background: var(--bg);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            transition: all 0.2s;
        }}
        .outlook-item:hover {{
            border-color: var(--purple);
            background: var(--purple-light);
        }}
        .outlook-icon-box {{
            width: 48px; height: 48px;
            border-radius: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }}
        .outlook-body h3 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 6px;
        }}
        .outlook-impact {{
            font-size: 14px;
            color: var(--text-light);
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        .outlook-tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}

        /* ── 总结 ── */
        .conclusion-box {{
            background: linear-gradient(135deg, var(--blue-light), var(--purple-light));
            border-radius: var(--radius-sm);
            padding: 24px 28px;
            font-size: 16px;
            line-height: 1.8;
            color: var(--text);
            border: 1px solid var(--blue-border);
        }}

        /* ── 滚动显现动画 ── */
        .reveal {{
            opacity: 0;
            transform: translateY(24px);
            transition: opacity 0.55s ease, transform 0.55s ease;
        }}
        .reveal.visible {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* ── 页脚 ── */
        .footer {{
            text-align: center;
            color: var(--text-light);
            font-size: 13px;
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}

        /* ── 响应式 ── */
        @media (max-width: 640px) {{
            .paper-header {{ padding: 24px 20px; }}
            .card {{ padding: 20px; }}
            .main-wrapper {{ padding: 16px 14px 64px; }}
            .overview-grid {{ grid-template-columns: 1fr; }}
            .overview-item.full {{ grid-column: 1; }}
            .comparison-row {{ grid-template-columns: 1fr; }}
            .comp-arrow {{ display: none; }}
            .app-grid {{ grid-template-columns: 1fr; }}
            .term-short {{ display: none; }}
            .paper-header h1 {{ font-size: 20px; }}
        }}
    </style>
</head>
<body>
    <div id="progress-bar"></div>

    <nav class="nav-bar">
        <div class="nav-inner">
            <a class="nav-tag" href="#overview">📋 论文速读</a>
            <a class="nav-tag" href="#insights">💡 核心观点</a>
            <a class="nav-tag" href="#innovations">🔬 技术创新</a>
            <a class="nav-tag" href="#terms">📚 关键术语</a>
            {comparisons_nav}
            <a class="nav-tag" href="#applications">🏭 应用场景</a>
            <a class="nav-tag" href="#outlook">🚀 行业展望</a>
            <a class="nav-tag" href="#conclusion">🎯 总结</a>
        </div>
    </nav>

    <div class="main-wrapper">
        <!-- 标题卡 -->
        <div class="paper-header reveal">
            <h1>{title}</h1>
            <div class="paper-meta">
                <span>👤 {authors}</span>
                <span>📅 {date}</span>
                <span>🤖 AI解读</span>
            </div>
            {key_stats_html}
        </div>

        {content_sections}

        <div class="footer">
            生成时间: {generation_time} · 由 AI 自动生成
        </div>
    </div>

    <script>
        // 阅读进度条
        const bar = document.getElementById('progress-bar');
        window.addEventListener('scroll', () => {{
            const d = document.documentElement;
            bar.style.width = (d.scrollTop / (d.scrollHeight - d.clientHeight) * 100) + '%';
        }});

        // 术语卡展开/折叠
        document.querySelectorAll('.term-header').forEach(h => {{
            h.addEventListener('click', () => {{
                h.closest('.term-card').classList.toggle('expanded');
            }});
        }});

        // 滚动显现
        const revealObs = new IntersectionObserver(entries => {{
            entries.forEach(e => {{
                if (e.isIntersecting) {{
                    e.target.classList.add('visible');
                    revealObs.unobserve(e.target);
                }}
            }});
        }}, {{ threshold: 0.08 }});
        document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

        // 导航高亮
        const sections = document.querySelectorAll('[id]');
        const navTags = document.querySelectorAll('.nav-tag');
        const navObs = new IntersectionObserver(entries => {{
            entries.forEach(e => {{
                if (e.isIntersecting) {{
                    navTags.forEach(t => {{
                        t.classList.toggle('active', t.getAttribute('href') === '#' + e.target.id);
                    }});
                }}
            }});
        }}, {{ rootMargin: '-35% 0px -55% 0px' }});
        sections.forEach(s => navObs.observe(s));

        // 数字计数动画
        function animateCount(el, target, suffix) {{
            const dur = 1200;
            const t0 = performance.now();
            const isFloat = target % 1 !== 0;
            const tick = now => {{
                const p = Math.min((now - t0) / dur, 1);
                const eased = 1 - Math.pow(1 - p, 3);
                const val = eased * target;
                el.textContent = (isFloat ? val.toFixed(1) : Math.floor(val)) + suffix;
                if (p < 1) requestAnimationFrame(tick);
            }};
            requestAnimationFrame(tick);
        }}
        const countObs = new IntersectionObserver(entries => {{
            entries.forEach(e => {{
                if (e.isIntersecting) {{
                    const raw = e.target.dataset.count;
                    if (raw) {{
                        const m = raw.match(/^([\\d.]+)(.*)$/);
                        if (m) animateCount(e.target, parseFloat(m[1]), m[2]);
                    }}
                    countObs.unobserve(e.target);
                }}
            }});
        }}, {{ threshold: 0.5 }});
        document.querySelectorAll('.stat-number[data-count]').forEach(el => countObs.observe(el));
    </script>
</body>
</html>
'''


# ─────────────────────────────────────────────
#  各板块 HTML 生成函数
# ─────────────────────────────────────────────

def build_key_stats(key_stats):
    """关键数字统计行"""
    if not key_stats:
        return ''
    color_map = {'blue': 'blue', 'green': 'green', 'purple': 'purple', 'orange': 'orange'}
    items = []
    for s in key_stats:
        number = escape_html(str(s.get('number', '')))
        suffix = escape_html(str(s.get('suffix', '')))
        label = escape_html(s.get('label', ''))
        color = color_map.get(s.get('color', 'blue'), 'blue')
        data_count = f'data-count="{number}{suffix}"' if number else ''
        items.append(f'''
        <div class="stat-box">
            <div class="stat-number {color}" {data_count}>{number}{suffix}</div>
            <div class="stat-label">{label}</div>
        </div>''')
    return f'<div class="stats-row">{"".join(items)}</div>'


def build_overview(overview):
    """论文速读：小白友好的总览卡"""
    if not overview:
        return ''
    problem = process_text(overview.get('problem', ''))
    method = process_text(overview.get('method', ''))
    conclusion = process_text(overview.get('conclusion', ''))
    industries = overview.get('industries', [])
    limitations = overview.get('limitations', [])

    industry_tags = ''.join(f'<span class="tag tag-orange">🏭 {escape_html(i)}</span>' for i in industries)
    limit_tags = ''.join(f'<span class="tag tag-red">⚠️ {escape_html(l)}</span>' for l in limitations)

    industry_html = f'<div class="tag-list">{industry_tags}</div>' if industries else ''
    limit_html = f'<div class="tag-list">{limit_tags}</div>' if limitations else ''

    return f'''
    <div id="overview" class="card reveal">
        <div class="section-heading">
            <span class="badge">📋</span> 论文速读 · 先搞懂这件事
        </div>
        <div class="overview-grid">
            <div class="overview-item">
                <div class="overview-label problem">🎯 解决的问题</div>
                <div class="overview-content">{problem}</div>
            </div>
            <div class="overview-item">
                <div class="overview-label method">🔧 用了什么方法</div>
                <div class="overview-content">{method}</div>
            </div>
            <div class="overview-item full">
                <div class="overview-label conclusion">✅ 得出的结论</div>
                <div class="overview-content">{conclusion}</div>
            </div>
            <div class="overview-item">
                <div class="overview-label industry">🏭 受益行业</div>
                {industry_html if industry_html else '<div class="overview-content">—</div>'}
            </div>
            <div class="overview-item">
                <div class="overview-label limit">⚠️ 主要局限</div>
                {limit_html if limit_html else '<div class="overview-content">—</div>'}
            </div>
        </div>
    </div>
    '''


def build_core_insights(insights):
    """核心观点板块"""
    if not insights:
        return ''
    items = []
    for ins in insights:
        if isinstance(ins, dict):
            title = escape_html(ins.get('title', ''))
            content = process_text(ins.get('content', ''))
            items.append(f'''
            <div class="insight-item">
                <div class="insight-title">{title}</div>
                <div class="insight-content">{content}</div>
            </div>''')
        elif isinstance(ins, str):
            items.append(f'<div class="insight-item"><div class="insight-content">{process_text(ins)}</div></div>')

    return f'''
    <div id="insights" class="card reveal">
        <div class="section-heading">
            <span class="badge">💡</span> 核心观点
        </div>
        {"".join(items)}
    </div>
    '''


def build_innovations(innovations):
    """技术创新点网格"""
    if not innovations:
        return ''
    cards = []
    for i, inn in enumerate(innovations):
        if isinstance(inn, dict):
            title = escape_html(inn.get('title', ''))
            desc = process_text(inn.get('description', ''))
            cards.append(f'''
            <div class="innovation-card">
                <div class="innovation-num">0{i+1}</div>
                <div class="innovation-title">{title}</div>
                <div class="innovation-desc">{desc}</div>
            </div>''')

    return f'''
    <div id="innovations" class="card reveal">
        <div class="section-heading">
            <span class="badge">🔬</span> 技术创新点
        </div>
        <div class="innovation-grid">{"".join(cards)}</div>
    </div>
    '''


def build_terminology(terms):
    """关键术语 + 比喻融合，可展开卡片"""
    if not terms:
        return ''
    cards = []
    for term in terms:
        if not isinstance(term, dict):
            continue
        term_name = escape_html(term.get('term', ''))
        short_def = escape_html(term.get('short_def', ''))
        explanation = process_text(term.get('explanation', ''))
        analogy_icon = escape_html(term.get('analogy_icon', '💡'))
        analogy = process_text(term.get('analogy', term.get('content', '')))  # 兼容旧格式
        real_example = process_text(term.get('real_example', ''))
        example_label = escape_html(term.get('example_label', '实际案例'))

        analogy_html = ''
        if analogy:
            analogy_html = f'''
            <div class="term-analogy">
                <span class="analogy-emoji">{analogy_icon}</span>
                <div class="term-analogy-text">{analogy}</div>
            </div>'''

        example_html = ''
        if real_example:
            example_html = f'''
            <div class="term-example">
                <div class="example-label">📌 {example_label}</div>
                <div class="example-content">{real_example}</div>
            </div>'''

        explain_html = ''
        if explanation:
            explain_html = f'<div class="term-explain"><strong>说人话就是：</strong>{explanation}</div>'

        cards.append(f'''
        <div class="term-card">
            <div class="term-header">
                <div class="term-left">
                    <span class="term-badge">{term_name}</span>
                    <span class="term-short">{short_def}</span>
                </div>
                <span class="term-arrow">▾</span>
            </div>
            <div class="term-body">
                {explain_html}
                {analogy_html}
                {example_html}
            </div>
        </div>''')

    return f'''
    <div id="terms" class="card reveal">
        <div class="section-heading">
            <span class="badge">📚</span> 关键术语 · 点击展开通俗解释
        </div>
        {"".join(cards)}
    </div>
    '''


def build_comparisons(comparisons):
    """数据对比板块"""
    if not comparisons:
        return ''
    items = []
    for comp in comparisons:
        if not isinstance(comp, dict):
            continue
        before_title = escape_html(comp.get('before_title', '改进前'))
        before_content = process_text(comp.get('before_content', ''))
        after_title = escape_html(comp.get('after_title', '改进后'))
        after_content = process_text(comp.get('after_content', ''))

        items.append(f'''
        <div class="comparison-wrap">
            <div class="comparison-row">
                <div class="comp-box comp-before">
                    <div class="comp-label">{before_title}</div>
                    <div class="comp-value">{before_content}</div>
                </div>
                <div class="comp-arrow">→</div>
                <div class="comp-box comp-after">
                    <div class="comp-label">{after_title}</div>
                    <div class="comp-value">{after_content}</div>
                </div>
            </div>
        </div>''')

    return f'''
    <div id="comparisons" class="card reveal">
        <div class="section-heading">
            <span class="badge">📊</span> 效果对比 · 一眼看出差距
        </div>
        {"".join(items)}
    </div>
    '''


def build_applications(apps):
    """实际应用场景：行业卡片网格"""
    if not apps:
        return ''
    cards = []
    for app in apps:
        # 支持旧格式（字符串列表）
        if isinstance(app, str):
            cards.append(f'''
            <div class="app-card">
                <div class="app-usecase">{process_text(app)}</div>
            </div>''')
            continue
        if not isinstance(app, dict):
            continue
        icon = escape_html(app.get('icon', '🏭'))
        industry = escape_html(app.get('industry', ''))
        use_case = escape_html(app.get('use_case', app.get('title', '')))
        benefit = process_text(app.get('benefit', app.get('description', '')))
        badge = escape_html(app.get('badge', ''))

        badge_html = f'<span class="app-badge">✅ {badge}</span>' if badge else ''

        cards.append(f'''
        <div class="app-card">
            <span class="app-icon">{icon}</span>
            <div class="app-industry">{industry}</div>
            <div class="app-usecase">{use_case}</div>
            <div class="app-benefit">{benefit}</div>
            {badge_html}
        </div>''')

    return f'''
    <div id="applications" class="card reveal">
        <div class="section-heading">
            <span class="badge">🏭</span> 实际应用场景
        </div>
        <div class="app-grid">{"".join(cards)}</div>
    </div>
    '''


def build_industry_outlook(outlook):
    """行业展望：具体行业贡献"""
    if not outlook:
        return ''
    items = []
    for item in outlook:
        if not isinstance(item, dict):
            continue
        icon = escape_html(item.get('icon', '🏢'))
        industry = escape_html(item.get('industry', ''))
        impact = process_text(item.get('impact', ''))
        use_cases = item.get('use_cases', [])

        tags_html = ''.join(
            f'<span class="tag tag-purple">▸ {escape_html(u)}</span>'
            for u in use_cases
        )

        items.append(f'''
        <div class="outlook-item">
            <div class="outlook-icon-box">{icon}</div>
            <div class="outlook-body">
                <h3>{industry}</h3>
                <div class="outlook-impact">{impact}</div>
                <div class="outlook-tags">{tags_html}</div>
            </div>
        </div>''')

    return f'''
    <div id="outlook" class="card reveal">
        <div class="section-heading">
            <span class="badge">🚀</span> 行业展望 · 具体贡献与突破方向
        </div>
        <div class="outlook-list">{"".join(items)}</div>
    </div>
    '''


def build_conclusion(conclusion):
    """总结"""
    if not conclusion:
        return ''
    content = process_text(conclusion)
    return f'''
    <div id="conclusion" class="card reveal">
        <div class="section-heading">
            <span class="badge">🎯</span> 总结
        </div>
        <div class="conclusion-box">{content}</div>
    </div>
    '''


# ─────────────────────────────────────────────
#  主生成函数
# ─────────────────────────────────────────────

def generate_html_from_json(paper_data, article_content, output_path, images_dir=None):
    title = paper_data.get('title', '未知标题')
    authors = ', '.join(paper_data.get('authors', ['未知作者']))
    date = paper_data.get('date', datetime.now().strftime('%Y-%m-%d'))

    sections = []

    # 1. 论文速读总览（替换叠甲）
    if 'paper_overview' in article_content:
        sections.append(build_overview(article_content['paper_overview']))

    # 2. 核心观点
    if 'core_insights' in article_content:
        sections.append(build_core_insights(article_content['core_insights']))

    # 3. 技术创新点
    if 'innovations' in article_content:
        sections.append(build_innovations(article_content['innovations']))

    # 4. 关键术语 + 比喻融合
    if 'terminology' in article_content:
        sections.append(build_terminology(article_content['terminology']))

    # 5. 数据对比
    has_comparisons = 'comparisons' in article_content and article_content['comparisons']
    if has_comparisons:
        sections.append(build_comparisons(article_content['comparisons']))

    # 6. 实际应用场景（行业卡片）
    if 'applications' in article_content:
        sections.append(build_applications(article_content['applications']))

    # 7. 行业展望
    if 'industry_outlook' in article_content:
        sections.append(build_industry_outlook(article_content['industry_outlook']))

    # 8. 总结
    if 'conclusion' in article_content:
        sections.append(build_conclusion(article_content['conclusion']))

    # 导航中条件显示「对比」
    comparisons_nav = (
        '<a class="nav-tag" href="#comparisons">📊 效果对比</a>'
        if has_comparisons else ''
    )

    # 关键数字统计
    key_stats_html = build_key_stats(article_content.get('key_stats', []))

    html = HTML_TEMPLATE.format(
        title=escape_html(title),
        authors=escape_html(authors),
        date=escape_html(date),
        key_stats_html=key_stats_html,
        comparisons_nav=comparisons_nav,
        content_sections=''.join(sections),
        generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    return html


def main():
    parser = argparse.ArgumentParser(description='生成现代互动风格的HTML论文解读报告')
    parser.add_argument('paper_json', help='论文元数据JSON文件路径')
    parser.add_argument('article_json', help='解读文章内容JSON文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出HTML文件路径')
    parser.add_argument('--images-dir', help='图片目录路径（暂留接口）')
    args = parser.parse_args()

    try:
        with open(args.paper_json, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        with open(args.article_json, 'r', encoding='utf-8') as f:
            article_content = json.load(f)

        html = generate_html_from_json(paper_data, article_content, args.output, args.images_dir)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ HTML报告生成成功: {output_path}")
        return 0
    except Exception as e:
        print(f"❌ HTML生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
