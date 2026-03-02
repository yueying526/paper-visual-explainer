---
name: paper-visual-explainer
description: 论文可视化解读工具。用于将学术论文转化为通俗易懂、层次分明、配图丰富的解读文章。使用卡兹克风格(超长比喻、口语化表达、数据震撼)生成文章,调用nano banana API生成配图,输出现代互动HTML报告和PDF报告。适用场景:(1) 需要将arXiv/学术论文转化为大众可读的科普文章 (2) 生成带配图的论文解读报告 (3) 制作技术博客或公众号内容 (4) 学习理解复杂论文时需要通俗化解释
---

# Paper Visual Explainer

## 概述

这个skill帮助你将复杂的学术论文转化为小白也能看懂的解读文章，并生成精美的可视化报告。

**核心功能**:
1. 从arXiv等学术网站自动搜索并下载论文PDF
2. 提取论文的文本、结构、关键概念
3. 使用卡兹克风格生成通俗易懂的解读文章（超长比喻、口语化、数据对比）
4. 调用nano banana API生成AI配图
5. 输出现代互动风格的HTML报告（进度条、导航高亮、滚动动画、折叠卡片）
6. 输出PDF报告（支持中文、层级结构、配图插入）

**卡兹克风格特点**:
- 用贯穿全文的超长比喻（如"101大厦公司"）让抽象概念具象化
- 极度口语化（"对吧"、"咋办呢"、"牛逼坏了"）
- 震撼性数据对比（"3000:1.6，降低3个数量级"）
- 层层递进的叙事（历史背景→问题→方案→价值）

**HTML报告互动特性**:
- 顶部阅读进度条
- 锁定导航栏 + 当前位置高亮
- 卡片滚动显现动画
- 关键数字计数动画
- 术语卡片点击展开/折叠

## 完整工作流程

### 前提条件

1. **设置API密钥**:
```bash
export POE_API_KEY="lrFLIAceZqTgZ7EQvx_WC_fb4-3RZh-WsYtnN5QmWwU"
```

2. **安装依赖**:
```bash
pip install requests PyPDF2 pdfplumber openai reportlab
```

### Step 1: 下载论文

有两种方式获取论文PDF:

**方式1: 通过arXiv URL或ID下载**

```bash
# 通过URL下载
python scripts/download_paper.py https://arxiv.org/abs/2401.12345 -o papers/

# 通过ID下载
python scripts/download_paper.py 2401.12345 -o papers/

# 查看论文元数据
python scripts/download_paper.py 2401.12345 --metadata
```

**方式2: 搜索并下载**

```bash
# 搜索论文
python scripts/download_paper.py --search "deepseek mhc" --max-results 10

# 搜索并自动下载第一个结果
python scripts/download_paper.py --search "transformer attention" --download-first -o papers/
```

**输出**: `papers/arxiv_2401.12345.pdf`

### Step 2: 提取PDF内容

从论文PDF中提取文本、结构、表格等信息:

```bash
# 基础提取
python scripts/extract_pdf.py papers/arxiv_2401.12345.pdf -o extracted/paper

# 同时提取表格
python scripts/extract_pdf.py papers/arxiv_2401.12345.pdf -o extracted/paper --tables

# 显示论文结构
python scripts/extract_pdf.py papers/arxiv_2401.12345.pdf --structure --metadata
```

**输出**:
- `extracted/paper.txt` - 全文文本
- `extracted/paper.json` - 结构化数据（标题、摘要、章节、引用数等）
- `extracted/paper_tables.json` - 表格数据（如果使用--tables）

### Step 3: 生成卡兹克风格解读文章

这一步需要你根据提取的论文内容，使用`references/kazike_style_guide.md`中的写作指南，生成解读文章。

**关键步骤**:

1. **阅读风格指南**:
```bash
cat references/kazike_style_guide.md
```

2. **分析论文内容**:
   - 用一句话总结：解决了什么问题、用了什么方法、得到了什么结论
   - 设计超长比喻体系（如何将技术概念映射到生活场景）
   - 每个术语必须搭配：通俗解释 + 生动比喻 + 真实案例
   - 识别关键数据对比点
   - 梳理具体行业应用场景和贡献

3. **生成文章JSON**:

创建一个`article_content.json`文件，包含以下结构:

```json
{
  "paper_overview": {
    "problem": "用一两句大白话说清楚这篇论文想解决什么问题，为什么这个问题让人头疼",
    "method": "他们用了什么核心思路或方法来解决这个问题（不用太技术，说个大概）",
    "conclusion": "最终达到了什么效果，有多厉害，和原来比提升了多少",
    "industries": ["金融风控", "医疗影像", "自动驾驶", "工业质检"],
    "limitations": ["在小数据集上效果有限", "推理速度比原始模型慢20%", "需要大量标注数据"]
  },

  "key_stats": [
    {"number": "87", "suffix": "%", "label": "准确率提升", "color": "blue"},
    {"number": "3.2", "suffix": "x", "label": "推理速度提升", "color": "green"},
    {"number": "60", "suffix": "%", "label": "误报率降低", "color": "purple"}
  ],

  "core_insights": [
    {
      "title": "核心创新点",
      "content": "这篇论文最核心的创新是...... 它让原来做不到的事情变成了可能"
    },
    {
      "title": "解决了什么长期痛点",
      "content": "在这之前，业界一直被......这个问题困扰了很多年，因为......"
    }
  ],

  "innovations": [
    {
      "title": "双重随机矩阵约束",
      "description": "通过两条铁律约束信息流，保证每个节点既不会信息爆炸，也不会信息断流"
    },
    {
      "title": "自适应权重分配",
      "description": "根据实时负载动态调整各通道权重，不再是死板的固定分配"
    }
  ],

  "terminology": [
    {
      "term": "梯度消失",
      "short_def": "信号在深层网络中衰减殆尽的现象",
      "explanation": "在深度神经网络里，反向传播时误差信号从最后一层往前传，每经过一层就衰减一点，传到很深的层就几乎没了，网络就学不动了",
      "analogy_icon": "📞",
      "analogy": "就像你玩传声筒游戏，话从第1个人传到第20个人，\"今晚吃火锅\"可能就变成了\"今晚睡觉\"。层数越多，信号失真越严重，最后完全走样。",
      "real_example": "早期的深度神经网络（超过10层）训练几乎不可能收敛，2014年之前业界都认为超深网络是个伪命题，直到ResNet的残差连接才解决这个问题。",
      "example_label": "历史案例"
    }
  ],

  "comparisons": [
    {
      "before_title": "之前的HC架构",
      "before_content": "信息能量最高到3000，训练极不稳定，动不动就崩",
      "after_title": "DeepSeek的mHC",
      "after_content": "信息能量稳定在1.6，降低接近3个数量级，训练丝般顺滑"
    }
  ],

  "applications": [
    {
      "industry": "金融风控",
      "icon": "💰",
      "use_case": "实时交易欺诈检测",
      "benefit": "毫秒级识别异常交易，准确率提升40%，每年可以减少数亿元的欺诈损失",
      "badge": "已有落地案例"
    },
    {
      "industry": "医疗影像",
      "icon": "🏥",
      "use_case": "CT/MRI辅助诊断",
      "benefit": "将放射科医生的读片时间从30分钟压缩到5分钟，敏感性提升15个百分点",
      "badge": "临床试验中"
    },
    {
      "industry": "自动驾驶",
      "icon": "🚗",
      "use_case": "复杂路况感知融合",
      "benefit": "在雨天、夜间等恶劣条件下目标识别准确率提升22%，误检率大幅降低",
      "badge": "研究阶段"
    }
  ],

  "industry_outlook": [
    {
      "industry": "医疗健康行业",
      "icon": "🏥",
      "impact": "AI辅助诊断精度的提升有望缓解优质医疗资源不均衡问题，让县级医院也能享受三甲医院水平的AI辅助。初步估计可将基层误诊率降低20-30%。",
      "use_cases": ["CT影像辅助诊断", "药物分子设计加速", "基因组学分析", "手术机器人精度提升"]
    },
    {
      "industry": "工业制造行业",
      "icon": "🏭",
      "impact": "质检环节引入该技术后，缺陷检出率可达99.7%，相比人工质检的95%有显著提升，同时将质检人力成本削减60%以上，提升整体产线效率。",
      "use_cases": ["芯片缺陷自动检测", "焊接质量实时判定", "产品外观瑕疵识别"]
    },
    {
      "industry": "金融科技行业",
      "icon": "💳",
      "impact": "在量化交易、风险定价、合规监测三大场景均有重要应用价值。尤其是实时风险预警系统，有望将银行坏账预测准确率从75%提升至90%以上。",
      "use_cases": ["高频交易风险实时管控", "信贷违约早期预警", "反洗钱行为模式识别"]
    }
  ],

  "conclusion": "用一段有感染力的话收尾：这篇论文用XX的代价换来了XX的收益，对整个行业意味着什么，未来的研究方向在哪里，为什么这个工作值得被记住。"
}
```

**写作技巧**:
- 参考`references/kazike_style_guide.md`中的具体句式模板
- 使用"对吧"、"咋办呢"等口语化表达
- **每个术语必须配齐**：通俗解释 + 生活比喻（带emoji图标）+ 真实案例，三合一才有代入感
- 比喻要贯穿全文，反复使用同一个比喻体系
- 数据对比要用独立对比框突出（如"3000 → 1.6"）
- 应用场景要写具体业务，不要写"可以用于XX领域"这种废话，要写"具体做什么、提升多少、解决什么痛点"
- 行业展望要有真实数据支撑，写出行业的具体改变而不是空泛描述

### Step 4: 生成AI配图

使用nano banana API生成论文解读配图:

**单张图片生成**:

```bash
python scripts/call_nano_banana.py \
  "创建简洁现代的插图，展示深度学习神经网络概念，如梦似幻的奇幻艺术，壮丽，空灵，绘画般" \
  -o illustrations/concept.png \
  --style "技术示意图，极简主义，2026设计趋势"
```

**批量生成**（推荐）:

```bash
cat > paper_content.json << EOF
{
  "title": "DeepSeek mHC: Manifold-Constrained Hyper-Connections",
  "abstract": "本文提出了一种新的超连接架构...",
  "key_concepts": ["双重随机矩阵约束", "信息能量守恒", "梯度稳定性"]
}
EOF

python scripts/call_nano_banana.py \
  --paper-json paper_content.json \
  --output-dir illustrations/ \
  --num-images 3
```

**输出**:
- `illustrations/concept_illustration.png` - 核心概念示意图
- `illustrations/architecture_diagram.png` - 技术架构图
- `illustrations/comparison_chart.png` - 对比效果图

**提示词技巧**:
- 参考`references/nano_banana_api.md`中的提示词模板
- 使用"如梦似幻的奇幻艺术，壮丽，绘画般"等关键词提升视觉效果
- 中文提示词更准确，专业术语可保留英文
- 每次请求间隔2-3秒避免限流

### Step 5: 生成HTML报告

生成现代互动风格HTML报告（进度条、导航高亮、滚动动画、计数动画）:

```bash
cat > paper_meta.json << EOF
{
  "title": "DeepSeek mHC: Manifold-Constrained Hyper-Connections",
  "authors": ["DeepSeek Team"],
  "date": "2026-01-01"
}
EOF

python scripts/generate_html_report.py \
  paper_meta.json \
  article_content.json \
  -o reports/paper_explained.html
```

**输出**: `reports/paper_explained.html`

**HTML互动特性**:
- 顶部渐变阅读进度条（蓝→紫）
- 顶部锁定导航栏 + 当前章节自动高亮
- 所有卡片滚动到视口时触发显现动画
- key_stats 关键数字进入视口时触发计数动画
- 术语卡片点击展开/折叠（显示解释、比喻、案例三合一）
- 悬停时卡片上浮效果
- 响应式布局，支持手机/平板/桌面

### Step 6: 生成PDF报告

```bash
python scripts/generate_pdf_report.py \
  paper_meta.json \
  article_content.json \
  -o reports/paper_explained.pdf \
  --images-dir illustrations/
```

**PDF特性**:
- 自动检测并使用系统中文字体
- 封面设计（标题、作者、日期）
- 分章节展示（速读总览、核心观点、创新点、术语、应用、展望、总结）
- 配图自动插入并添加说明
- A4页面，专业排版

## 快速开始示例

完整流程示例（从论文链接到生成报告）:

```bash
# 1. 下载DeepSeek mHC论文
python scripts/download_paper.py \
  --search "deepseek mhc manifold" \
  --download-first \
  -o papers/

# 2. 提取内容
python scripts/extract_pdf.py \
  papers/arxiv_*.pdf \
  -o extracted/deepseek_mhc \
  --tables --structure

# 3. 查看卡兹克风格指南
cat references/kazike_style_guide.md

# 4. 手动创建article_content.json和paper_meta.json
# (参考Step 3的JSON格式，重点填好：
#  - paper_overview（小白速读，含局限性）
#  - terminology（术语+比喻+真实案例）
#  - applications（具体行业业务）
#  - industry_outlook（具体贡献与突破）)

# 5. 生成配图
python scripts/call_nano_banana.py \
  --paper-json paper_content.json \
  --output-dir illustrations/ \
  --num-images 3

# 6. 生成HTML报告
python scripts/generate_html_report.py \
  paper_meta.json \
  article_content.json \
  -o reports/deepseek_mhc.html

# 7. 生成PDF报告
python scripts/generate_pdf_report.py \
  paper_meta.json \
  article_content.json \
  -o reports/deepseek_mhc.pdf \
  --images-dir illustrations/
```

## 常见使用场景

### 场景1: 技术博客文章

```bash
# 下载论文 → 提取内容 → 写解读文章 → 生成配图 → 输出HTML
# 可以直接把HTML发布到博客平台
```

### 场景2: 公众号推送

```bash
# 使用卡兹克风格生成通俗易懂的文章
# 用nano banana生成视觉冲击力强的配图
# HTML报告可以复制粘贴到公众号编辑器
```

### 场景3: 学习笔记

```bash
# 把难懂的论文转化为易理解的笔记
# PDF报告可以打印或分享给同学
# 术语卡片展开功能帮助逐步理解概念
```

### 场景4: 科研汇报

```bash
# 用卡兹克风格讲述论文故事
# 用配图增强演示效果
# PDF报告作为汇报材料
```

## 参考资源

### scripts/

所有脚本都支持`--help`查看详细用法:

- `download_paper.py` - arXiv论文下载，支持搜索和批量下载
- `extract_pdf.py` - PDF内容提取，支持表格和结构分析
- `call_nano_banana.py` - nano banana API调用，生成AI配图
- `generate_html_report.py` - 现代互动HTML报告生成（进度条/动画/折叠卡片）
- `generate_pdf_report.py` - PDF报告生成，支持中文和配图

### references/

- `kazike_style_guide.md` - **必读**: 卡兹克写作风格完整指南，包含:
  - 超长比喻法技巧
  - 口语化表达清单
  - 叙事结构模板
  - 数据对比技巧
  - 术语解释模式（解释+比喻+案例三件套）
  - 实战案例分析

- `nano_banana_api.md` - nano banana API调用文档，包含:
  - API配置说明
  - 提示词技巧
  - 常用风格关键词
  - 错误处理
  - 最佳实践

## 注意事项

1. **API密钥**: 使用前必须设置`POE_API_KEY`环境变量

2. **论文下载**: arXiv允许合理使用，请勿频繁批量下载

3. **图片生成**: nano banana API有频率限制，建议每次请求间隔2-3秒

4. **中文支持**: PDF生成需要系统有中文字体，脚本会自动检测

5. **文章质量**: Step 3的文章生成是核心。**术语**要配齐解释+比喻+案例，**应用场景**要写具体业务细节，**行业展望**要有实质性贡献描述。

6. **版权**: 生成的解读文章建议注明原论文出处和作者

## 常见问题

### Q: 术语卡片怎么写才有代入感？

A: 一个术语卡片需要三层：
1. **通俗解释**（说人话就是...）- 不用任何技术词汇说清楚这是什么
2. **生活比喻**（就像...一样）- 找一个读者熟悉的生活场景打比方，加emoji图标
3. **真实案例**（历史上某某产品/事件中...）- 用真实的行业案例让读者有代入感

### Q: 应用场景写什么？

A: 不要写"可以用于XX领域"这种废话。要写：
- **哪个行业的哪个具体业务**（金融风控 · 实时欺诈检测）
- **能做到什么、提升多少**（准确率提升40%，误报率降低60%）
- **当前状态**（已落地 / 试验中 / 研究阶段）

### Q: 行业展望怎么写才有价值？

A: 要有具体的行业场景 + 量化估计：
- 不要写："可以推动医疗行业发展"
- 要写："有望将基层医院误诊率降低20-30%，缓解优质医疗资源分配不均的问题"

### Q: nano banana API调用失败怎么办？

A: 检查:
1. `POE_API_KEY`是否正确设置
2. 网络连接是否正常
3. 是否触发频率限制（增加请求间隔）
4. 查看`references/nano_banana_api.md`的错误处理章节

### Q: HTML/PDF报告样式需要调整？

A:
1. HTML样式在`scripts/generate_html_report.py`的`HTML_TEMPLATE`中的`<style>`块
2. PDF样式在`scripts/generate_pdf_report.py`的`create_custom_styles`函数中
3. 可以修改颜色变量（`--blue`、`--purple`等）
4. 调整字体大小、间距等参数

## 技巧和最佳实践

1. **先小后大**: 先用一篇短论文练手，熟悉流程后再处理长论文

2. **分步验证**: 每一步都检查输出质量，不要一口气跑完所有步骤

3. **术语卡三件套**: 解释、比喻、案例缺一不可——光有解释太枯燥，光有比喻不落地，光有案例不易懂

4. **保存模板**: 把满意的`article_content.json`结构保存为模板，下次复用

5. **batch处理**: 如果要处理多篇论文，可以写shell脚本自动化流程

6. **版本控制**: 建议用git管理生成的文章和报告，方便回溯和协作
