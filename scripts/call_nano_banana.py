#!/usr/bin/env python3
"""
Nano Banana图片生成API调用脚本
用于生成论文解读配图
通过Poe API调用nano-banana-2模型
"""

import argparse
import json
import os
import sys
import time
import re
from pathlib import Path

try:
    import openai
    import requests
except ImportError:
    print("❌ 缺少依赖库,请安装:")
    print("   pip install openai requests")
    sys.exit(1)


# Poe API配置
POE_API_BASE_URL = os.getenv('POE_API_BASE_URL', 'https://api.poe.com/v1')
POE_API_KEY = os.getenv('POE_API_KEY', '')
NANO_BANANA_MODEL = 'nano-banana-2'


FAST_PROMPT_SUFFIX = ", simple flat illustration, minimal, clean lines"
FULL_PROMPT_SUFFIX = ", 如梦似幻的奇幻艺术, 壮丽, 空灵, 绘画般, 史诗, 魔幻, 奇幻艺术, 封面艺术, 梦幻"


def generate_image(prompt, output_path, style='', width=1024, height=1024, fast=False):
    """
    调用Nano Banana API生成图片

    Args:
        prompt: 图片生成提示词
        output_path: 输出图片路径
        style: 图片风格描述 (可选,会追加到prompt中)
        width: 图片宽度 (默认: 1024)
        height: 图片高度 (默认: 1024)
        fast: 使用更简单的提示词后缀以加快生成速度 (默认: False)

    Returns:
        生成的图片路径,如果失败返回None
    """
    if not POE_API_KEY:
        print("❌ 未设置API密钥,请设置环境变量 POE_API_KEY")
        return None

    # 构建完整提示词
    prompt_suffix = FAST_PROMPT_SUFFIX if fast else FULL_PROMPT_SUFFIX
    full_prompt = prompt + prompt_suffix
    if style:
        full_prompt = f"{full_prompt}, 风格: {style}"

    print(f"🎨 正在生成图片...")
    print(f"   提示词: {full_prompt[:150]}...")

    try:
        # 初始化OpenAI客户端
        client = openai.OpenAI(
            api_key=POE_API_KEY,
            base_url=POE_API_BASE_URL
        )

        # 调用nano-banana-2模型生成图片
        response = client.chat.completions.create(
            model=NANO_BANANA_MODEL,
            messages=[{
                "role": "user",
                "content": full_prompt
            }]
        )

        # 获取生成结果
        result_content = response.choices[0].message.content

        # nano-banana-2返回的是图片URL(通常在Markdown格式中)
        # 尝试从返回内容中提取图片URL
        image_url = None

        # 尝试匹配Markdown图片格式: ![](url)
        markdown_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
        match = re.search(markdown_pattern, result_content)
        if match:
            image_url = match.group(1)
        else:
            # 尝试匹配纯URL
            url_pattern = r'(https?://[^\s]+\.(?:png|jpg|jpeg|gif|webp))'
            match = re.search(url_pattern, result_content, re.IGNORECASE)
            if match:
                image_url = match.group(1)

        if not image_url:
            print(f"⚠️  返回内容中未找到图片URL")
            print(f"   返回内容: {result_content[:500]}")
            return None

        print(f"   图片URL: {image_url}")

        # 下载图片
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_response.content)

        file_size = len(img_response.content) / 1024  # KB
        print(f"✅ 图片生成成功: {output_path}")
        print(f"   文件大小: {file_size:.1f} KB")

        return str(output_path)

    except openai.APIError as e:
        print(f"❌ API调用失败: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 图片下载失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 图片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_paper_illustrations(paper_content, output_dir, num_images=3, fast=False, parallel=False):
    """
    根据论文内容生成多张配图

    Args:
        paper_content: 论文内容字典,包含标题、摘要、关键概念等
        output_dir: 输出目录
        num_images: 生成图片数量 (默认: 3)
        fast: 使用更简单的提示词后缀以加快生成速度 (默认: False)
        parallel: 并行生成图片 (默认: False)

    Returns:
        生成的图片路径列表
    """
    import concurrent.futures

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    title = paper_content.get('title', '')
    abstract = paper_content.get('abstract', '')
    key_concepts = paper_content.get('key_concepts', [])

    # 构建所有任务
    tasks = []

    # 图片1: 论文核心概念示意图
    if title or abstract:
        prompt1 = f"创建一个简洁现代的插图,展示这个概念: {title}。摘要: {abstract[:150]}"
        style1 = "技术示意图,极简主义,2026设计趋势,柔和色彩"
        img_path1 = output_dir / "img1.png"
        tasks.append((prompt1, img_path1, style1))

    # 图片2: 技术架构示意图
    if key_concepts:
        concepts_str = ', '.join(key_concepts[:5])
        prompt2 = f"创建技术架构图,展示这些概念之间的关系: {concepts_str}"
        style2 = "系统架构,流程图,现代科技插图,简洁线条"
        img_path2 = output_dir / "img2.png"
        tasks.append((prompt2, img_path2, style2))

    # 图片3: 对比/效果示意图
    if len(key_concepts) >= 2:
        prompt3 = f"创建前后对比可视化图: {key_concepts[0]} 对比 {key_concepts[1]}"
        style3 = "信息图表,数据可视化,简洁现代,2026设计趋势"
        img_path3 = output_dir / "img3.png"
        tasks.append((prompt3, img_path3, style3))

    tasks = tasks[:num_images]

    def run_task(args):
        p, path, s = args
        return generate_image(p, path, style=s, fast=fast)

    generated_images = []

    if parallel and len(tasks) > 1:
        print(f"🚀 并行生成 {len(tasks)} 张图片...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {executor.submit(run_task, t): t for t in tasks}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    generated_images.append(result)
    else:
        for i, task in enumerate(tasks):
            result = run_task(task)
            if result:
                generated_images.append(result)
            if i < len(tasks) - 1:
                time.sleep(2)  # 串行时避免频率限制

    return generated_images


def main():
    parser = argparse.ArgumentParser(
        description='调用Nano Banana API生成论文解读配图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成单张图片
  %(prog)s "神经网络架构示意图" -o output/diagram.png

  # 指定风格
  %(prog)s "transformer模型" -o output/model.png --style "技术插图,现代简洁"

  # 从JSON文件读取论文内容,生成多张配图
  %(prog)s --paper-json paper_content.json --output-dir illustrations/ --num-images 5

环境变量:
  POE_API_KEY        Poe API密钥 (必需)
  POE_API_BASE_URL   Poe API端点 (可选,默认: https://api.poe.com/v1)
        """
    )

    parser.add_argument(
        'prompt',
        nargs='?',
        help='图片生成提示词'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出图片路径'
    )

    parser.add_argument(
        '--style',
        default='',
        help='图片风格描述 (可选,会追加到提示词中)'
    )

    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='图片宽度 (默认: 1024)'
    )

    parser.add_argument(
        '--height',
        type=int,
        default=1024,
        help='图片高度 (默认: 1024)'
    )

    parser.add_argument(
        '--paper-json',
        help='论文内容JSON文件路径'
    )

    parser.add_argument(
        '--output-dir',
        help='批量生成时的输出目录'
    )

    parser.add_argument(
        '--num-images',
        type=int,
        default=3,
        help='批量生成图片数量 (默认: 3)'
    )

    parser.add_argument(
        '--fast',
        action='store_true',
        help='使用更简单的提示词后缀以加快生成速度'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        help='并行生成多张图片 (使用 concurrent.futures)'
    )

    args = parser.parse_args()

    # 批量生成模式
    if args.paper_json:
        if not args.output_dir:
            print("❌ 批量生成模式需要指定 --output-dir")
            return 1

        try:
            with open(args.paper_json, 'r', encoding='utf-8') as f:
                paper_content = json.load(f)

            images = generate_paper_illustrations(
                paper_content,
                args.output_dir,
                args.num_images,
                fast=args.fast,
                parallel=args.parallel,
            )

            print(f"\n✅ 成功生成 {len(images)} 张图片:")
            for img_path in images:
                print(f"   - {img_path}")

            return 0

        except Exception as e:
            print(f"❌ 批量生成失败: {e}")
            return 1

    # 单张生成模式
    if not args.prompt or not args.output:
        parser.print_help()
        return 1

    result = generate_image(args.prompt, args.output, args.style, args.width, args.height, fast=args.fast)

    return 0 if result else 1


if __name__ == '__main__':
    sys.exit(main())
