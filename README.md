# Paper Visual Explainer 📄✨

**Turn academic papers into beautiful, interactive visual reports that anyone can understand.**

将学术论文转化为小白也能看懂的互动可视化解读报告。

![Demo — Attention Is All You Need](docs/demo.png)

> Example: [Full interactive report for "Attention Is All You Need"](docs/example-transformer.html) (download and open in browser)

## Why This Tool?

Reading academic papers is hard. This tool transforms dense research papers into engaging, visual reports with:

- 🎯 **Plain language summaries** — what problem, what method, what limitations, in one paragraph
- 📖 **Term + Analogy cards** — every key term gets a plain explanation, a life analogy, and a real case (expandable)
- 🏭 **Industry applications** — specific industries, specific use cases, no fluff
- 📊 **Data-driven insights** — quantified impact with real numbers
- 🎨 **AI-generated illustrations** — via Nano Banana API
- 📱 **Interactive HTML report** — reading progress bar, nav highlighting, scroll animations, number counters
- 📄 **PDF export** — print-ready, full Chinese support

Perfect for: tech bloggers, WeChat/公众号 writers, students, and anyone who wants to explain research to a broader audience.

## Quick Start

```bash
# Install dependencies
pip install requests PyPDF2 pdfplumber reportlab

# One-click: download → extract → generate illustrations → build report
python3 scripts/generate_all.py 1706.03762

# Fast mode (simpler illustrations, ~40% faster)
python3 scripts/generate_all.py 1706.03762 --fast
```

Or run each step individually:

```bash
python3 scripts/download_paper.py "1706.03762" -o /tmp/papers/
python3 scripts/extract_pdf.py paper.pdf -o extracted --structure
python3 scripts/call_nano_banana.py "your prompt" -o img.png --fast
python3 scripts/generate_html_report.py meta.json content.json -o report.html
```

## Writing Style: Kazike (卡兹克风格)

Reports use an engaging Chinese science communication style:

- **Extended metaphors** running through the entire article (e.g., comparing a neural network to a "101-story company building")
- **Conversational tone** — "对吧", "咋办呢", "牛逼坏了"
- **Shocking data comparisons** — "3000:1.6 — a 3 order of magnitude reduction"
- **Progressive narrative** — history → problem → solution → impact

## Use as Claude Code Skill

This tool is also available as a [Claude Code](https://claude.ai/code) skill. Once installed, just say:

> "帮我解读这篇论文: [arXiv link]"

It will automatically download, analyze, and generate a visual report.

## Project Structure

```
paper-visual-explainer/
├── scripts/
│   ├── generate_html_report.py   # Interactive HTML report generator
│   ├── generate_pdf_report.py    # PDF report generator  
│   ├── download_paper.py         # arXiv paper downloader
│   ├── extract_pdf.py            # PDF content extractor
│   └── call_nano_banana.py       # AI illustration generator
├── references/
│   ├── kazike_style_guide.md     # Writing style guide
│   └── nano_banana_api.md        # Illustration API docs
└── SKILL.md                      # Claude Code skill config
```

## Contributing

PRs welcome! Especially for:
- New writing style templates
- Additional report themes  
- Support for more paper sources beyond arXiv
- Multilingual report generation (English output)

## Examples

**Attention Is All You Need** (Vaswani et al., 2017) — [Download HTML report](docs/example-transformer.html)

More examples coming soon.

## License

MIT

---

**Author:** [Yueying Wu](https://yueyingai.com) · [GitHub](https://github.com/yueying526) · [X](https://x.com/wuyueying526)
