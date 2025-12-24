# -*- coding: utf-8 -*-
"""
B站搜索结果标题文本分析
功能：
1. 从 CSV 中提取 title 保存为 txt
2. 使用 jieba 分词
3. 去除停用词和搜索关键词
4. 统计词频
5. 输出 Top10 并保存完整词频 CSV
"""

import pandas as pd
import jieba


# =========================
# 1. 参数设置
# =========================
keyword = "深度学习"
csv_file = f"{keyword}_搜索.csv"
title_txt = f"{keyword}_titles.txt"
stopwords_file = "stopwords.txt"
output_csv = f"{keyword}_title_word_freq.csv"


# =========================
# 2. 从 CSV 提取标题并保存为 txt
# =========================
df = pd.read_csv(csv_file, encoding="utf_8_sig")

titles = df['title'].dropna().astype(str)

with open(title_txt, 'w', encoding='utf-8') as f:
    for t in titles:
        f.write(t + '\n')

print(f"已保存标题文本：{title_txt}")


# =========================
# 3. 读取标题文本
# =========================
with open(title_txt, 'r', encoding='utf-8') as f:
    content = f.read()

print("文本前200字示例：")
print(content[:200])


# =========================
# 4. 加载停用词表
# =========================
with open(stopwords_file, 'r', encoding='utf-8') as f:
    stopwords = set(f.read().splitlines())


# =========================
# 5. jieba 分词并统计词频
# =========================
exclude_words = set(jieba.cut(keyword))
print("搜索词分词：", exclude_words)

words = jieba.cut(content)

word_counts = {}

for word in words:
    word = word.strip()

    # 过滤规则
    if not word:
        continue
    if word in stopwords:
        continue
    if word == keyword:
        continue
    if word in exclude_words:   # 剔除搜索词分词后的所有子词
        continue
    if len(word) <= 1:
        continue

    word_counts[word] = word_counts.get(word, 0) + 1


# =========================
# 6. 输出 Top10 高频词
# =========================
sorted_words = sorted(
    word_counts.items(),
    key=lambda x: x[1],
    reverse=True
)

print("\n标题中出现频率最高的词 Top10：")
for word, count in sorted_words[:10]:
    print(f"{word}: {count}")


# =========================
# 7. 保存完整词频结果为 CSV
# =========================
word_freq_df = pd.DataFrame(
    sorted_words,
    columns=['word', 'count']
)

word_freq_df.to_csv(output_csv, index=False, encoding='utf_8_sig')

print(f"\n[OK] 词频统计结果已保存为：{output_csv}")
