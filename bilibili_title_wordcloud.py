import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# -------------设置搜索参数-----------------
keyword = "深度学习" # 搜索关键词 
pages = 30 # 搜索页数
page_size = 30 # 每页结果数量(默认30)

freq_df = pd.read_csv(
    f"{keyword}_title_word_freq.csv",
    encoding="utf_8_sig"
)

word_freq = dict(
    zip(freq_df['word'], freq_df['count'])
)

font_map = {
    'Darwin':  ['Arial Unicode MS', 'PingFang SC', 'Heiti SC'],
    'Windows': ['SimHei', 'Microsoft YaHei'],
    'Linux':   ['Noto Sans CJK SC', 'WenQuanYi Micro Hei']
}

sys_name = platform.system()
candidates = font_map.get(sys_name, font_map['Linux'])

font_path = None
for f in fm.fontManager.ttflist:
    if f.name in candidates:
        font_path = f.fname
        break

if font_path is None:
    raise RuntimeError("未找到可用的中文字体")

wc = WordCloud(
    font_path=font_path,
    background_color='white',
    width=900,
    height=450,
    max_words=100,
    collocations=False,
    prefer_horizontal=1.0
)

wc.generate_from_frequencies(word_freq)

plt.figure(figsize=(12, 6))
plt.imshow(wc)
plt.axis('off')
plt.title(f'B站“{keyword}”视频标题高频词词云')
plt.show()
