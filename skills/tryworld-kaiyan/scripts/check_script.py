#!/usr/bin/env python3
"""检查短视频口播稿的字面问题与可表演性风险。

TryWorld 改造版。核心硬禁类别与部分词表来自
KKKKhazix/human-writing v1.1.0 的 TryWorld 衍生版
`tryworld-paper/scripts/check_prose.py`。上游代码与词表按 MIT License 使用，
完整许可见 `LICENSES/human-writing-MIT.txt`。

这个检查器只负责字面指纹和可量化节奏，不判断观点是否成立、来源是否充分，
也不替作者改稿。语义层面的判断放在写稿包的自检报告里。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


HAN_PER_MINUTE = 260
FULL_RANGE = (550, 800)
SHORT_RANGE = (300, 450)
LONG_SENTENCE_HAN = 40
LONG_PARAGRAPH_HAN = 180
SHORT_SENTENCE_HAN = 8

HARD_STOPS = (
    "说白了",
    "说穿了",
    "先说结论",
    "废话不多说",
    "众所周知",
)

HARD_JARGON = (
    "赋能",
    "抓手",
    "商业闭环",
    "价值闭环",
    "能力沉淀",
    "拉通",
    "底层逻辑",
    "顶层设计",
    "认知跃迁",
    "价值释放",
    "能力建设",
    "降本增效",
    "内容矩阵",
    "全链路",
    "组合拳",
    "打开想象空间",
    "结构性机会",
    "关键命题",
    "深层逻辑",
    "技术底座",
    "公共底座",
    "技术主权",
    "单点风险",
    "主脊柱",
    "材料锚点",
    "认知增量",
    "迭代闭环",
)

MODEL_SIGNPOSTS = (
    "更微妙的是",
    "还有一层",
    "只说对了一半",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
    "值得一提的是",
    "不难发现",
    "不难看出",
    "由此可见",
    "接下来我们来看",
    "接下来我们看看",
    "让我们来看看",
    "让我们来看",
)

SUMMARY_MARKERS = (
    "总而言之",
    "总的来说",
    "总结一下",
    "最后总结",
    "说到底",
    "归根结底",
    "综上所述",
    "最后我想说",
    "最后再说一句",
    "最后再强调",
    "以上就是今天",
    "以上就是这期",
)

VAGUE_JUDGMENTS = (
    "很重要",
    "值得关注",
    "意义重大",
    "未来可期",
    "影响深远",
    "具有里程碑意义",
    "改变世界",
    "颠覆行业",
    "大有可为",
)

TITLE_LIMITS = {
    "master": 8,
    "douyin": 6,
    "shipinhao": 6,
    "xiaohongshu": 8,
    "bilibili": 8,
}

TITLE_CLICKBAIT = (
    "震惊",
    "炸裂",
    "封神",
    "必看",
    "全网",
    "彻底",
    "颠覆",
    "天花板",
    "王炸",
    "杀疯",
    "再不",
    "就晚了",
    "99%",
    "所有人",
    "看完沉默",
    "速看",
    "重磅",
)

TITLE_VAGUE = (
    "很重要",
    "值得关注",
    "未来已来",
    "时代变了",
    "大有可为",
    "影响深远",
)

TERM_WATCH = (
    "大模型",
    "参数",
    "推理",
    "微调",
    "多模态",
    "Agent",
    "RAG",
    "token",
    "API",
    "工作流",
    "闭环",
    "赋能",
    "抓手",
    "生态",
    "范式",
    "底层逻辑",
    "认知",
    "维度",
    "机制",
    "路径",
    "体系",
    "矩阵",
    "链路",
    "颗粒度",
    "对齐",
    "沉淀",
    "复用",
    "编排",
    "智能体",
)

OPENING_GREETING = re.compile(
    r"^(?:"
    r"大家(?:好|们好)|"
    r"哈喽|嗨|你好|各位(?:观众|朋友)|"
    r"欢迎(?:来到|收看|收听)|"
    r"我是|"
    r"今天(?:我们|想|想和|想跟|和|跟|来)?(?:大家|你)?(?:来)?(?:聊|说|讲)"
    r")"
)

BRAND_OPENING = re.compile(
    r"^(?:"
    r"哈喽[，,]\s*我是\s*TryWorld(?![A-Za-z])\s*[。.]?"
    r"|哈喽大家好[，,]\s*我是\s*TryWorld(?![A-Za-z])\s*[。.]?"
    r"|我是\s*TryWorld(?![A-Za-z])\s*[。.]?"
    r")",
    re.IGNORECASE,
)

SUMMARY_ENDING = re.compile(
    "|".join(re.escape(marker) for marker in SUMMARY_MARKERS)
)

MODEL_SIGNPOST_PATTERNS = tuple(
    re.compile(
        rf"(?:^|[。！？!?]\s*){re.escape(phrase)}[^。！？!?\n]{{0,24}}",
        re.MULTILINE,
    )
    for phrase in MODEL_SIGNPOSTS
)

PIVOT_PATTERNS = (
    re.compile(r"(?:并)?不是[^。！？\n]{0,90}而是"),
    re.compile(r"并非[^。！？\n]{0,90}而是"),
    re.compile(r"不在于[^。！？\n]{0,90}而在于"),
    re.compile(r"与其说[^。！？\n]{0,90}(?:不如|毋宁|倒不如)"),
    re.compile(r"[。！？!?]\s*而是"),
    re.compile(r"表面(?:上)?[^。！？\n]{0,90}(?:其实|实际|实则)"),
    re.compile(r"看似[^。！？\n]{0,90}(?:其实|实际|实则)"),
    re.compile(r"(?:总|一直|曾|都)?以为[^！？\n]{2,60}?(?:其实|才发现|才明白|才知道|后来才)"),
    re.compile(r"回头(?:看|一看)?才(?:发现|明白|知道)"),
    re.compile(r"答案(?:是否定的|恰恰相反)|恰恰相反"),
    re.compile(r"[^，。！？\n]{1,12}不重要，(?:重要|要紧)的是"),
    re.compile(r"真正[^，。！？\n]{0,16}的(?:，)?是"),
)

CTA_PATTERNS = (
    re.compile(
        r"(?:我建议|我的判断是|你可以|你不妨|建议你|最好先|现在就可以|"
        r"今天就|这周就|下次(?:遇到|再)?|我的选择是|我会|我准备|我打算)"
    ),
    re.compile(
        r"(?:^|[。！？!?]\s*)(?:先|别|把|去|打开|关掉|试试|记住|检查|选|"
        r"做|用|留下|删掉|停一下|花[一二三四五六七八九十\d]+分钟)"
    ),
    re.compile(r"如果[^。！？]{0,50}(?:就|那)"),
    re.compile(r"从[^。！？]{1,24}开始"),
)

CUE_LINE = re.compile(
    r"(?m)^[^\n]*\[(?:停顿|重音|交给画面)\][^\n]*$"
)

MASK_PATTERNS = (
    re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"!\[[^\n\]]*\]\([^\n)]*\)"),
    re.compile(r"\[[^\n\]]*\]\([^\n)]*\)"),
    re.compile(r"https?://[^\s)>]+"),
    re.compile(r"<!--.*?-->", re.DOTALL),
    re.compile(r"<[^>\n]+>"),
    re.compile(r"(?m)^[ \t]{0,3}#{1,6}[^\n]*$"),
    re.compile(r"(?m)^[ \t]*\|[^\n]*$"),
    CUE_LINE,
    re.compile(r"(?m)^[ \t]*>[ \t]?"),
    re.compile(r"(?m)^[ \t]*(?:[-*+]|\d+[.)、])[ \t]+"),
    re.compile(r"(?:\*\*|__|~~)"),
)

SENTENCE_RE = re.compile(r"[^。！？!?…\n]+(?:[。！？!?]+|…{1,2}|$)")


@dataclass
class Issue:
    code: str
    line: int
    message: str
    excerpt: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "line": self.line,
            "message": self.message,
            "excerpt": self.excerpt,
        }


@dataclass
class Sentence:
    position: int
    text: str
    han: int


@dataclass
class Paragraph:
    position: int
    text: str
    han: int
    sentences: list[Sentence] = field(default_factory=list)


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def han_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def excerpt(value: str, width: int = 54) -> str:
    clean = re.sub(r"\s+", " ", value).strip()
    if len(clean) <= width:
        return clean
    return clean[: width - 1] + "…"


def _mask_match(match: re.Match[str]) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group())


def mask_markup(text: str) -> str:
    """屏蔽 Markdown 结构、链接、代码和轻提示，保留字符位置与换行。"""

    masked = text
    for pattern in MASK_PATTERNS:
        masked = pattern.sub(_mask_match, masked)
    return masked


def split_sentences(block: str, base_position: int) -> list[Sentence]:
    sentences: list[Sentence] = []
    for line_match in re.finditer(r"[^\n]+", block):
        line = line_match.group()
        line_position = base_position + line_match.start()
        for sentence_match in SENTENCE_RE.finditer(line):
            raw = sentence_match.group()
            count = han_count(raw)
            if count == 0:
                continue
            sentences.append(
                Sentence(
                    position=line_position + sentence_match.start(),
                    text=re.sub(r"\s+", " ", raw).strip(),
                    han=count,
                )
            )
    return sentences


def prose_paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    cursor = 0
    for block in re.split(r"\n\s*\n", text):
        position = text.find(block, cursor)
        if position < 0:
            position = cursor
        cursor = max(cursor, position + len(block))
        leading = len(block) - len(block.lstrip())
        clean = block.strip()
        if not clean:
            continue
        count = han_count(clean)
        if count == 0:
            continue
        block_position = position + leading
        paragraphs.append(
            Paragraph(
                position=block_position,
                text=re.sub(r"\s+", " ", clean).strip(),
                han=count,
                sentences=split_sentences(clean, block_position),
            )
        )
    return paragraphs


def non_overlapping_terms(
    text: str, terms: Iterable[str]
) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    occupied: list[tuple[int, int]] = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text):
            start, end = match.span()
            if any(start < old_end and end > old_start for old_start, old_end in occupied):
                continue
            matches.append((start, term))
            occupied.append((start, end))
    return sorted(matches)


def punctuation_issues(prose: str, original: str) -> list[Issue]:
    issues: list[Issue] = []
    index = 0
    while index < len(prose):
        char = prose[index]
        if char not in ("：", ":", "—", "–"):
            index += 1
            continue

        if char in (":", "–"):
            previous_is_digit = index > 0 and prose[index - 1].isdigit()
            next_is_digit = index + 1 < len(prose) and prose[index + 1].isdigit()
            if previous_is_digit and next_is_digit:
                index += 1
                continue

        if char == "—":
            end = index + 1
            while end < len(prose) and prose[end] == "—":
                end += 1
            raw = prose[index:end]
            label = "破折号" if end - index > 1 else "长破折号"
        else:
            end = index + 1
            raw = char
            label = {
                "：": "中文冒号",
                ":": "英文冒号",
                "–": "连接号式破折号",
            }[char]

        issues.append(
            Issue(
                code="punctuation",
                line=line_number(original, index),
                message=f"{label}“{raw}”不适合口播稿，改成句号或直接重写。",
                excerpt=excerpt(
                    prose[max(0, index - 18) : min(len(prose), end + 18)]
                ),
            )
        )
        index = end
    return issues


def term_issues(
    prose: str,
    original: str,
    terms: Iterable[str],
    code: str,
    label: str,
) -> list[Issue]:
    issues = []
    for position, term in non_overlapping_terms(prose, terms):
        issues.append(
            Issue(
                code=code,
                line=line_number(original, position),
                message=f"{label}“{term}”",
                excerpt=excerpt(prose[max(0, position - 20) : position + len(term) + 20]),
            )
        )
    return issues


def pattern_issues(
    prose: str,
    original: str,
    patterns: Iterable[re.Pattern[str]],
    code: str,
    label: str,
) -> list[Issue]:
    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(prose))
    matches.sort(key=lambda match: match.start())
    issues = []
    seen: set[tuple[int, int]] = set()
    for match in matches:
        if match.span() in seen:
            continue
        seen.add(match.span())
        issues.append(
            Issue(
                code=code,
                line=line_number(original, match.start()),
                message=f"{label}“{excerpt(match.group(), 36)}”",
                excerpt=excerpt(match.group()),
            )
        )
    return issues


def opening_issue(paragraphs: list[Paragraph], original: str) -> list[Issue]:
    if not paragraphs:
        return []
    target = paragraphs[0]
    remainder = target.text

    brand_match = BRAND_OPENING.match(remainder)
    if brand_match:
        remainder = remainder[brand_match.end() :].strip()
        remainder = remainder.lstrip("，,。.！!？? \t")
        if not remainder:
            if len(paragraphs) < 2:
                return []
            target = paragraphs[1]
            remainder = target.text

    match = OPENING_GREETING.match(remainder)
    if not match:
        return []
    return [
        Issue(
            code="opening_greeting",
            line=line_number(original, target.position),
            message="开头在问候或自我介绍，0 到 5 秒应先给冲突、代价或结论。",
            excerpt=excerpt(remainder),
        )
    ]


def ending_issues(paragraphs: list[Paragraph], original: str) -> list[Issue]:
    if not paragraphs:
        return []
    issues: list[Issue] = []
    final = paragraphs[-1]
    ending_match = SUMMARY_ENDING.search(final.text)
    if ending_match:
        position = final.position + ending_match.start()
        issues.append(
            Issue(
                code="summary_ending",
                line=line_number(original, position),
                message="结尾落进了总结腔，改成一个具体判断、取舍或下一步动作。",
                excerpt=excerpt(final.text),
            )
        )

    paragraphs_with_summary = sum(
        1 for paragraph in paragraphs if SUMMARY_ENDING.search(paragraph.text)
    )
    if paragraphs_with_summary >= 2:
        issues.append(
            Issue(
                code="summary_tone",
                line=line_number(original, final.position),
                message="全文多段使用总结路标，形成通篇总结腔，删掉重复的收束套话。",
                excerpt=excerpt(final.text),
            )
        )
    return issues


def has_concrete_cta(paragraphs: list[Paragraph]) -> bool:
    if not paragraphs:
        return False
    tail = " ".join(paragraph.text for paragraph in paragraphs[-2:])
    return any(pattern.search(tail) for pattern in CTA_PATTERNS)


def short_streak_issues(
    paragraphs: list[Paragraph], original: str
) -> list[Issue]:
    issues = []
    for paragraph in paragraphs:
        run: list[Sentence] = []
        for sentence in paragraph.sentences:
            if sentence.han < SHORT_SENTENCE_HAN:
                run.append(sentence)
            else:
                if len(run) >= 3:
                    issues.append(_streak_issue(run, original))
                run = []
        if len(run) >= 3:
            issues.append(_streak_issue(run, original))
    return issues


def _streak_issue(run: list[Sentence], original: str) -> Issue:
    return Issue(
        code="short_streak",
        line=line_number(original, run[0].position),
        message=(
            f"连续 {len(run)} 句都少于 {SHORT_SENTENCE_HAN} 个汉字，"
            "容易变成排队喊结论，至少合并或展开一句。"
        ),
        excerpt=excerpt(" ".join(sentence.text for sentence in run)),
    )


def parallelism_issues(
    paragraphs: list[Paragraph], original: str
) -> list[Issue]:
    issues = []
    for paragraph in paragraphs:
        for sentence in paragraph.sentences:
            clauses = [
                clause.strip()
                for clause in re.split(r"[，、；,;]", sentence.text)
                if han_count(clause) >= 3
            ]
            if len(clauses) < 3:
                continue
            run = 1
            found = False
            for previous, current in zip(clauses, clauses[1:]):
                if (
                    len(previous) >= 2
                    and len(current) >= 2
                    and previous[:2] == current[:2]
                    and re.match(r"[\u4e00-\u9fff]{2}", current)
                ):
                    run += 1
                    if run >= 3:
                        found = True
                        break
                else:
                    run = 1
            if found:
                issues.append(
                    Issue(
                        code="parallelism",
                        line=line_number(original, sentence.position),
                        message="三项以上同构排比，口播里容易变成模型腔，留两项或换说法。",
                        excerpt=excerpt(sentence.text),
                    )
                )
    return issues


def title_char_count(title: str) -> int:
    """Count displayed characters, ignoring whitespace; punctuation counts."""

    return len([char for char in title if not char.isspace()])


def check_title(title: str, platform: str) -> dict:
    """Validate the short video title against length and tone rules."""

    clean = title.strip()
    count = title_char_count(clean)
    limit = TITLE_LIMITS[platform]
    errors: list[Issue] = []
    warnings: list[Issue] = []

    if not clean:
        errors.append(
            Issue(
                code="title_empty",
                line=1,
                message="标题为空，需要给一个不超过规定字数的视频标题。",
            )
        )

    if count > limit:
        errors.append(
            Issue(
                code="title_length",
                line=1,
                message=(
                    f"标题 {count} 个字符，超过 {platform} 的 {limit} 字上限。"
                    "标点计入，空格不计，短标题优先。"
                ),
                excerpt=excerpt(clean),
            )
        )

    for term in TITLE_CLICKBAIT:
        if term in clean:
            errors.append(
                Issue(
                    code="title_clickbait",
                    line=1,
                    message=f"标题含夸张或标题党用语“{term}”，换成具体对象或后果。",
                    excerpt=excerpt(clean),
                )
            )
            break

    for term in TITLE_VAGUE:
        if term in clean:
            warnings.append(
                Issue(
                    code="title_vague",
                    line=1,
                    message=f"标题含空泛判断“{term}”，换成观众能立刻感知的变化。",
                    excerpt=excerpt(clean),
                )
            )
            break

    punctuation = re.findall(r"[，。！？、,.!?；;：:]", clean)
    if len(punctuation) > 2:
        warnings.append(
            Issue(
                code="title_punctuation",
                line=1,
                message="标题标点偏多，短标题尽量只保留一个语气点。",
                excerpt=excerpt(clean),
            )
        )

    return {
        "text": clean,
        "platform": platform,
        "characters": count,
        "limit": limit,
        "remaining": limit - count,
        "passed": not errors,
        "errors": [issue.as_dict() for issue in errors],
        "warnings": [issue.as_dict() for issue in warnings],
    }


def term_density_issues(
    prose: str, original: str, total_han: int
) -> list[Issue]:
    matches = non_overlapping_terms(prose, TERM_WATCH)
    if not matches:
        return []

    distinct = sorted({term for _, term in matches})
    density = len(matches) / total_han * 100 if total_han else 0
    if len(distinct) < 3 and density <= 2:
        return []

    first_position, first_term = matches[0]
    return [
        Issue(
            code="term_density",
            line=line_number(original, first_position),
            message=(
                f"检测到 {len(matches)} 处专业或抽象词（{('、'.join(distinct[:6]))}），"
                "先确认普通观众能不能听懂。能换成动作和场景的，换成动作和场景。"
            ),
            excerpt=excerpt(
                prose[
                    max(0, first_position - 20) : first_position
                    + len(first_term)
                    + 40
                ]
            ),
        )
    ]


def check_text(
    text: str,
    path_label: str,
    short: bool,
    platform: str,
    title: str | None = None,
) -> dict:
    prose = mask_markup(text)
    total_han = han_count(prose)
    paragraphs = prose_paragraphs(prose)
    sentences = [
        sentence for paragraph in paragraphs for sentence in paragraph.sentences
    ]

    errors: list[Issue] = []
    warnings: list[Issue] = []

    lower, upper = SHORT_RANGE if short else FULL_RANGE
    if total_han < lower or total_han > upper:
        errors.append(
            Issue(
                code="length",
                line=1,
                message=(
                    f"汉字数 {total_han}，{'短版' if short else '主稿'}要求 "
                    f"{lower} 到 {upper} 个汉字。"
                ),
            )
        )

    errors.extend(punctuation_issues(prose, text))
    errors.extend(
        term_issues(prose, text, HARD_STOPS, "hard_stop", "硬停词")
    )
    errors.extend(
        term_issues(prose, text, HARD_JARGON, "jargon", "黑话")
    )
    errors.extend(
        pattern_issues(
            prose,
            text,
            MODEL_SIGNPOST_PATTERNS,
            "model_signpost",
            "模型路标",
        )
    )
    errors.extend(
        pattern_issues(prose, text, PIVOT_PATTERNS, "pivot", "翻案句")
    )
    errors.extend(opening_issue(paragraphs, text))
    errors.extend(ending_issues(paragraphs, text))

    if total_han > 0 and total_han <= upper:
        for sentence in sentences:
            if sentence.han > LONG_SENTENCE_HAN:
                warnings.append(
                    Issue(
                        code="long_sentence",
                        line=line_number(text, sentence.position),
                        message=(
                            f"句子有 {sentence.han} 个汉字，超过 "
                            f"{LONG_SENTENCE_HAN} 字，口播时一口气可能说不完。"
                        ),
                        excerpt=excerpt(sentence.text),
                    )
                )

    for paragraph in paragraphs:
        if paragraph.han > LONG_PARAGRAPH_HAN:
            warnings.append(
                Issue(
                    code="long_paragraph",
                    line=line_number(text, paragraph.position),
                    message=(
                        f"段落有 {paragraph.han} 个汉字，超过 "
                        f"{LONG_PARAGRAPH_HAN} 字，建议按信息动作拆开。"
                    ),
                    excerpt=excerpt(paragraph.text),
                )
            )

    warnings.extend(short_streak_issues(paragraphs, text))
    warnings.extend(parallelism_issues(paragraphs, text))
    warnings.extend(term_density_issues(prose, text, total_han))

    if total_han > 0 and not has_concrete_cta(paragraphs):
        final_line = line_number(
            text, paragraphs[-1].position if paragraphs else 0
        )
        warnings.append(
            Issue(
                code="missing_cta",
                line=final_line,
                message=(
                    "最后两段没有可执行动作或明确取舍，补一个观众今天能做的"
                    "具体判断，不必强行点赞关注。"
                ),
            )
        )

    for position, phrase in non_overlapping_terms(prose, VAGUE_JUDGMENTS):
        warnings.append(
            Issue(
                code="vague_judgment",
                line=line_number(text, position),
                message=(
                    f"“{phrase}”是空泛判断，换成具体变化、代价或可观察结果。"
                ),
                excerpt=excerpt(
                    prose[max(0, position - 20) : position + len(phrase) + 20]
                ),
            )
        )

    sentence_count = len(sentences)
    longest = max((sentence.han for sentence in sentences), default=0)
    estimated_seconds = round(total_han / HAN_PER_MINUTE * 60)
    average = (
        round(sum(sentence.han for sentence in sentences) / sentence_count, 1)
        if sentence_count
        else 0.0
    )
    title_report = check_title(title, platform) if title is not None else None
    passed = not errors and (title_report is None or title_report["passed"])

    return {
        "passed": passed,
        "path": path_label,
        "platform": platform,
        "short": short,
        "title": title_report,
        "metrics": {
            "han": total_han,
            "estimated_seconds": estimated_seconds,
            "estimated_minutes": round(estimated_seconds / 60, 2),
            "sentences": sentence_count,
            "avg_sentence_han": average,
            "longest_sentence_han": longest,
            "paragraphs": len(paragraphs),
        },
        "errors": [issue.as_dict() for issue in errors],
        "warnings": [issue.as_dict() for issue in warnings],
    }


def print_human_report(report: dict) -> None:
    metrics = report["metrics"]
    print(f"文件 {report['path']}")
    print(f"平台 {report['platform']} | {'短版' if report['short'] else '标准稿'}")
    seconds = metrics["estimated_seconds"]
    print(
        f"汉字 {metrics['han']} | 约 {seconds // 60} 分 {seconds % 60} 秒"
        f"（{seconds} 秒）"
    )
    print(
        f"句子 {metrics['sentences']} | 平均 {metrics['avg_sentence_han']} 字"
        f" | 最长 {metrics['longest_sentence_han']} 字"
        f" | 段落 {metrics['paragraphs']}"
    )

    title = report.get("title")
    if title is not None:
        print(
            f"标题「{title['text']}」| {title['characters']}/{title['limit']} 字"
            f" | 剩余 {title['remaining']}"
        )

    if report["errors"]:
        print("\n需要修改")
        for issue in report["errors"]:
            print(f"- [{issue['code']}] 第 {issue['line']} 行 {issue['message']}")

    if title is not None and title["errors"]:
        print("\n标题需要修改")
        for issue in title["errors"]:
            print(f"- [{issue['code']}] {issue['message']}")

    if report["warnings"]:
        print("\n需要人工判断")
        for issue in report["warnings"]:
            print(f"- [{issue['code']}] 第 {issue['line']} 行 {issue['message']}")

    if title is not None and title["warnings"]:
        print("\n标题需要人工判断")
        for issue in title["warnings"]:
            print(f"- [{issue['code']}] {issue['message']}")

    if report["passed"]:
        suffix = f"，另有 {len(report['warnings'])} 条警告" if report["warnings"] else ""
        print(f"\n结论 通过{suffix}")
    else:
        title_errors = len(title["errors"]) if title is not None else 0
        print(
            f"\n结论 不通过，正文 {len(report['errors'])} 处硬伤，"
            f"标题 {title_errors} 处硬伤"
        )


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    configure_stdout()
    parser = argparse.ArgumentParser(
        description="检查短视频口播稿的字面硬伤与节奏风险"
    )
    parser.add_argument("path", help="口播稿文件路径，使用 - 从标准输入读取")
    parser.add_argument(
        "--platform",
        choices=(
            "master",
            "douyin",
            "shipinhao",
            "xiaohongshu",
            "bilibili",
        ),
        default="master",
        help="目标平台，仅用于校验和报告",
    )
    parser.add_argument(
        "--title",
        help="可选视频标题；同时校验字数、平台上限和标题党用语",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="按 300 到 450 字的短版检查",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出机器可读 JSON",
    )
    args = parser.parse_args(argv)

    try:
        text = read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件。{error}", file=sys.stderr)
        return 2

    if han_count(mask_markup(text)) == 0:
        print("没有检测到可检查的口播正文。", file=sys.stderr)
        return 2

    report = check_text(
        text,
        args.path,
        args.short,
        args.platform,
        title=args.title,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_report(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
