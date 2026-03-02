# Nano Banana API 文档

## 概述

Nano Banana是一个AI图片生成模型,通过Poe API平台调用。它使用`nano-banana-2`模型生成高质量的艺术风格图片。

## API配置

### 端点信息

- **Base URL**: `https://api.poe.com/v1`
- **模型名称**: `nano-banana-2`
- **认证方式**: Bearer Token (API Key)

### 环境变量

```bash
export POE_API_KEY="your_api_key_here"
export POE_API_BASE_URL="https://api.poe.com/v1"  # 可选
```

## 使用方法

### Python调用示例

```python
import openai

# 初始化客户端
client = openai.OpenAI(
    api_key="your_poe_api_key",  # 或使用 os.getenv("POE_API_KEY")
    base_url="https://api.poe.com/v1"
)

# 生成图片
response = client.chat.completions.create(
    model="nano-banana-2",
    messages=[{
        "role": "user",
        "content": "如梦似幻的奇幻艺术中的龙，壮丽、天上、空灵、绘画般、史诗、魔幻、奇幻艺术、封面艺术、梦幻"
    }]
)

# 获取结果
result = response.choices[0].message.content
print(result)
```

### 请求格式

nano-banana-2使用标准的OpenAI Chat Completions API格式:

```json
{
  "model": "nano-banana-2",
  "messages": [
    {
      "role": "user",
      "content": "图片生成提示词"
    }
  ]
}
```

### 响应格式

API返回的`content`字段通常包含:
- Markdown格式的图片链接: `![description](image_url)`
- 或直接的图片URL

示例响应:
```
![生成的图片](https://example.com/generated_image.png)
```

## 提示词技巧

### 基础结构

```
[主题描述] + [风格关键词] + [质量增强词]
```

### 常用风格关键词

**艺术风格**:
- 如梦似幻的奇幻艺术
- 壮丽、空灵、绘画般
- 史诗、魔幻、奇幻艺术
- 封面艺术、梦幻

**技术插图**:
- 技术示意图、架构图
- 极简主义、现代简洁
- 2026设计趋势
- 柔和色彩、清晰线条

**数据可视化**:
- 信息图表、数据可视化
- 简洁现代、专业商务
- 对比图、流程图

### 示例提示词

1. **论文概念插图**:
```
创建一个简洁现代的插图，展示深度学习神经网络的概念。
如梦似幻的奇幻艺术，壮丽，空灵，绘画般，史诗，魔幻，奇幻艺术，封面艺术，梦幻
风格: 技术示意图，极简主义，2026设计趋势，柔和色彩
```

2. **技术架构图**:
```
创建技术架构图，展示Transformer、注意力机制、编码器解码器之间的关系。
如梦似幻的奇幻艺术，壮丽，绘画般，奇幻艺术
风格: 系统架构，流程图，现代科技插图，简洁线条
```

3. **对比可视化**:
```
创建前后对比可视化图: 传统方法 对比 深度学习方法。
如梦似幻的奇幻艺术，壮丽，绘画般，魔幻，奇幻艺术
风格: 信息图表，数据可视化，简洁现代，2026设计趋势
```

## 最佳实践

### 1. 提示词优化

- **具体明确**: 清晰描述想要的主题和元素
- **风格一致**: 使用统一的艺术风格关键词
- **分层描述**: 主题 → 风格 → 质量增强

### 2. 中英文混用

nano-banana-2支持中文提示词,建议:
- 主要描述使用中文(更准确)
- 专业术语保留英文或中文均可
- 风格关键词可以重复使用已验证有效的模板

### 3. 频率限制

- 建议每次请求间隔 **2-3秒**
- 批量生成时使用`time.sleep(3)`避免被限流

### 4. 错误处理

```python
try:
    response = client.chat.completions.create(...)
    content = response.choices[0].message.content

    # 提取图片URL
    import re
    url_match = re.search(r'!\[.*?\]\((https?://[^\)]+)\)', content)
    if url_match:
        image_url = url_match.group(1)
    else:
        # 处理URL提取失败
        pass

except openai.APIError as e:
    print(f"API调用失败: {e}")
except Exception as e:
    print(f"发生错误: {e}")
```

## 常见问题

### Q: 返回内容中没有图片URL怎么办?

A: 检查以下几点:
1. API密钥是否正确
2. 提示词是否符合模型要求
3. 返回内容格式,可能需要调整URL提取正则表达式
4. 查看完整返回内容: `print(response.choices[0].message.content)`

### Q: 生成的图片风格不符合预期?

A: 尝试:
1. 添加更多风格关键词
2. 参考已验证有效的提示词模板
3. 在主题描述后明确指定风格偏好

### Q: 如何控制图片尺寸?

A: nano-banana-2的图片尺寸由模型自动决定,通常为标准尺寸(如1024x1024)。如需调整,可以在下载后使用PIL等库进行缩放。

### Q: API调用失败率高怎么办?

A:
1. 检查网络连接
2. 增加timeout时间
3. 添加重试机制
4. 检查API配额和限流状态

## 成本和限制

- 具体计费方式请参考Poe官方文档
- 建议设置合理的请求间隔避免超额使用
- 生成的图片会在Poe服务器上保存一段时间,建议及时下载

## 参考资源

- Poe API官方文档: https://developer.poe.com/
- OpenAI Python SDK: https://github.com/openai/openai-python
- nano-banana-2模型页面: https://poe.com/nano-banana-2
