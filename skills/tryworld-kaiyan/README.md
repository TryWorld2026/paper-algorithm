# 试界开言 TryWorld Kaiyan

把选题或素材写成中文短视频口播稿。只交付文字，不做封面、配音、分镜、渲染或视频合成。

## 用法

在对话里说“试界开言，写口播稿”，或者直接给一个主题、链接、新闻和素材。没有主题时，Skill 会先拉 AIHOT 最近 7 天精选，给出 3 到 5 张选题卡并停下等选择。

完整写稿包包含六部分。

1. 选题卡
2. 事实来源表
3. 主稿
4. 抖音、视频号、小红书、B站的开头和收尾变体
5. 三类轻提示
6. 自检报告

## 工具

拉取 AIHOT v1 最近精选。

```text
python scripts/fetch_topics.py --days 7 --take 100
```

检查纯主稿文本。

```text
python scripts/check_script.py <file> [--platform master|douyin|xiaohongshu|bilibili] [--short] [--json]
```

退出码 `0` 表示没有硬伤，`1` 表示需要修改，`2` 表示输入或参数错误。

## 边界

AIHOT 只用于发现线索。重要事实回到发布方原文。对外商业产品、公开镜像或批量再分发 AIHOT 数据前，需要确认使用授权。

检查器部分逻辑与词表源自 `human-writing`，MIT 许可见 `LICENSES/human-writing-MIT.txt`。
