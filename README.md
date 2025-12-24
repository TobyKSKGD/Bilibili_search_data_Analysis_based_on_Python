# Bilibili_search_data_Analysis_based_on_Python
基于 Python 的 B 站搜索数据分析

项目**所有单独可执行代码**放在 `scripts` 文件夹中。

## 项目功能总览

本项目围绕“B 站搜索数据与评论数据”的采集与分析，形成一条完整的数据处理链路：**关键词搜索 → 结构化落盘（CSV）→ 文本与统计分析 → 可视化展示 → 调用大语言模型 API 做评论情感分析**。项目所有可独立运行的脚本集中放在 `scripts/` 目录中，整体流程可通过 `demonstration.ipynb` 进行演示与复现（详见下文的 Getting Start 部分）。

### 1) 数据采集（Data Collection）
- **搜索结果爬取**：使用 `bili_search_scraper.py` 按关键词与页数抓取 B 站搜索结果，支持自定义 `keyword / pages / page_size / proxy`，输出 `{keyword}_搜索.csv`。
  - 运行前需配置 `cookie.txt`（从浏览器开发者工具复制 Cookie 到脚本同路径），否则脚本无法正常请求数据。
- **视频评论爬取**：使用 `bilibili_comments.py` 通过视频 BV 号抓取评论，支持自定义 `bvid / max_comments`，输出 `{bvid}_comments.csv`。

### 2) 数据分析与可视化（Analysis & Visualization）
- **Top10 统计可视化**：`bilibili_search_top10.py` 对搜索结果进行统计，输出：UP 主出现次数 Top10、视频分区（type_name）Top10、标签（tag）Top10 等图表。
- **标题文本分析（词频）**：`bilibili_title_wordfreq.py` 对搜索结果标题进行分词与词频统计（含停用词过滤与关键词过滤），输出词频结果 CSV。
- **标题文本分析（词云）**：`bilibili_title_wordcloud.py` 基于词频结果生成中文词云图，支持自动选择中文字体与自定义词云参数（尺寸、最大词数等）。

### 3) 大语言模型情感分析（LLM Sentiment）
- **评论情绪分类**：`api_comments.py` 调用大语言模型（DeepSeek）对 `{bvid}_comments.csv` 中的评论文本进行情绪分类与理由解释，生成带 `sentiment_label / judgment_reason` 的输出文件（例如 `{bvid}_comments_with_sentiment.csv`）。
  - 运行前需创建 `api_key.txt` 并填入个人密钥，用于 API 鉴权。

### 4) Notebook 演示（Reproducible Demo）
- `demonstration.ipynb` 提供从参数配置、脚本调用、结果落盘到可视化/情感分析的完整演示流程，便于展示与复现。

> 注意：`cookie.txt` 与 `api_key.txt` 均包含个人敏感信息，建议仅本地保存，不要上传到公开仓库。

## Getting Start

项目的流程演示可以直接使用 `demonstration.ipynb` 进行查看。

安装项目用到的所有依赖项：

```bash
pip install -r requirements.txt
```

**参考后文 bili_search_scraper.py 中的 cookie.txt 的创建方法【否则无法运行脚本！】**。按需修改第一个 Python 单元格，其他按需运行各个代码单元格即可：

```python
# -------------设置搜索参数-----------------
keyword = "深度学习" # 搜索关键词
pages = 30 # 搜索页数
page_size = 30 # 每页结果数量(默认30)
```

## bili_search_scraper.py

爬取 B 站搜索数据内容的脚本为 `bili_search_scraper.py`。

用户可以根据自己的需求自行更改以下参数运行脚本，找到脚本最下面 `main` 中：

```python
if __name__ == "__main__":
    # ====== 手动修改搜索关键词 ======
    keyword = "Python" # 搜索关键词
    pages = 3 # 爬取页数
    out = f"{keyword}_搜索.csv" # 输出的文件名
    page_size = 30 # 每页数量（默认30）
    proxy = None # 如不使用代理，设为 None

    cookie = load_cookie(None)
```

- `keyword`：搜索关键词
- `pages`：爬取页数
- `out`：输出的文件名
- `page_size`：每页数量（默认30）
- `proxy`：如不使用代理，设为 None
- `cookie`：注意用户需要自行将自己运行 B 站时浏览器的 Cookie 保存到 `cookie.txt` 中，否则无法运行脚本。【具体的方法参考下文】

### cookie.txt

首先在浏览器登陆 B 站，在 B 站的随便一个网页中右键 -> 检查，点击右上角的网络图标。

![](./pictures/b_1.png)

随便选择一个名称里的元素，在标头中往下找到一个叫 Cookie 的变量，复制右边的值。【注意这个值关系到个人账号的隐私，不要外传给他人】

在 `bili_search_scraper.py` 的同一路径下，新建一个文本文件，名字一定要叫 `cookie.txt`，将复制的 Cookie 值粘贴到 cookie.txt 中。

![](./pictures/b_2.png)

### {keyword}_搜索.csv

输出的表格参数含义如下：

- `title` —— 视频标题
- `author` —— UP 主名称
- `bvid` —— 视频唯一 ID
- `aid` —— 旧版视频 ID
- `pub_ts` —— 发布时间（时间戳）
- `pub_time` —— 发布时间
- `duration` —— 视频时长
- `danmaku` —— 弹幕数
- `like` —— 点赞数
- `view` —— 播放量
- `favorite` —— 收藏数
- `type_name` —— 视频分区
- `tag` —— 标签信息
- `description` —— 视频简介
- `link` —— 视频直链

## bilibili_search_top10.py

统计该关键词（在 `main()` 函数中修改）下的出现最多的 UP 主 Top10 柱状图、视频分区（type_name）出现次数 Top10 和标签（tag）出现次数 Top10。

```python
def main():
    keyword = "深度学习" # 搜索关键词
```

## bilibili_title_wordfreq.py

分词、统计标题词频。

B站搜索结果标题文本分析
功能：

1. 从 CSV 中提取 title 保存为 txt
2. 使用 jieba 分词
3. 去除停用词和搜索关键词
4. 统计词频
5. 输出 Top10 并保存完整词频 CSV

**参数设置**：

```python
keyword = "深度学习"
csv_file = f"{keyword}_搜索.csv"
title_txt = f"{keyword}_titles.txt"
stopwords_file = "stopwords.txt"
output_csv = f"{keyword}_title_word_freq.csv"
```

## bilibili_title_wordcloud.py

脚本功能说明：

1. 读取指定关键词的标题词频 CSV 文件（例如：{keyword}_title_word_freq.csv）。
2. 根据词频数据生成中文词云图，可视化视频标题中高频词。
3. 自动选择系统可用中文字体，解决中文显示乱码或缺字问题。
4. 可自定义词云参数：
   - 背景颜色（background_color）
   - 图像尺寸（width, height）
   - 最大词数（max_words）
   - 防止高频词拆分（collocations=False）
   - 优先水平显示词语（prefer_horizontal=1.0）
5. 输出效果：Matplotlib 显示词云图，可用于分析关键词在视频标题中的热点词汇分布。

## bilibili_comments.py

B 站视频评论爬取，请按需修改需要爬取的视频 BV 号与最大评论数。结果将会保存在代码同级目录下。

```python
bvid = "BV1wK2QBPEDv" # 目标视频的 BV 号
max_comments = 50 # 最大评论数量

cookie = bc.load_cookie()
session = bc.build_session(cookie=cookie)
```

## api_comments.py

调用大语言模型（DeepSeek）对评论进行情感分析

请新建 `api_key.txt`，请将自己的密钥填入 `api_key.txt` 文件中。(否则无法调用 DeepSeek)

DeepSeek密钥生成：https://platform.deepseek.com

结果同样会保存在代码同级目录下。
