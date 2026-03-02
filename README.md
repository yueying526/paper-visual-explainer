# 📄 Paper Visual Explainer

> 将学术论文转化为小白也能看懂的可视化解读报告

## 功能特性

- **论文速读**：用大白话说清楚论文解决了什么问题、用了什么方法、有哪些局限
- **术语+比喻融合**：每个关键术语配通俗解释、生活比喻、真实案例，点击展开
- **行业应用场景**：具体行业的具体业务，不写废话
- **行业展望**：有量化数据支撑的行业贡献分析
- **互动 HTML 报告**：阅读进度条、导航高亮、滚动动画、数字计数动画
- **PDF 报告**：支持中文，可打印分享

## 快速开始

```bash
pip install requests PyPDF2 pdfplumber reportlab

python scripts/generate_html_report.py paper_meta.json article_content.json -o report.html
```

## 文件结构

```
paper-visual-explainer/
├── scripts/
│   ├── generate_html_report.py   # HTML 报告生成（含互动元素）
│   ├── generate_pdf_report.py    # PDF 报告生成
│   ├── download_paper.py         # arXiv 论文下载
│   ├── extract_pdf.py            # PDF 内容提取
│   └── call_nano_banana.py       # AI 配图生成
├── references/
│   ├── kazike_style_guide.md     # 写作风格指南
│   └── nano_banana_api.md        # 配图 API 文档
└── assets/
```

## License

MIT
