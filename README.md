# Bilibili_search_data_Analysis_based_on_Python
基于 Python 的 B 站搜索数据分析

项目**所有单独可执行代码**放在 `scripts` 文件夹中。

## Getting Start

项目的流程演示可以直接使用 `demonstration.ipynb` 进行查看。

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
