"""
Bilibili 搜索数据分析脚本
功能：
1. 读取 B 站搜索结果 CSV
2. 统计 UP 主 / 分区 / 标签 Top10
3. 绘制柱状图并标注数值
"""

import pandas as pd
import matplotlib.pyplot as plt
import platform
import warnings
import matplotlib.font_manager as fm


# =========================
# 1. 中文字体自动适配
# =========================
def set_chinese_font():
    font_map = {
        'Darwin': ['Arial Unicode MS', 'PingFang SC', 'Heiti SC'],
        'Windows': ['SimHei', 'Microsoft YaHei', 'KaiTi'],
        'Linux': ['Noto Sans CJK SC', 'WenQuanYi Micro Hei']
    }

    system = platform.system()
    candidates = font_map.get(system, font_map['Linux'])

    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in candidates:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font]
            break
    else:
        warnings.warn('未找到合适的中文字体，图表中文可能显示为方块')

    plt.rcParams['axes.unicode_minus'] = False


# =========================
# 2. 数据读取
# =========================
def load_data(keyword):
    filename = f"{keyword}_搜索.csv"
    df = pd.read_csv(filename, encoding="utf_8_sig")
    return df


# =========================
# 3. Top10 统计函数
# =========================
def get_top10_author(df):
    top10 = (
        df['author']
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10.columns = ['author', 'count']
    return top10


def get_top10_type(df):
    top10 = (
        df['type_name']
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10.columns = ['type_name', 'count']
    return top10


def get_top10_tag(df):
    tags = (
        df['tag']
        .dropna()
        .str.split(',')
        .explode()
        .str.strip()
    )

    top10 = (
        tags
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10.columns = ['tag', 'count']
    return top10


# =========================
# 4. 通用柱状图绘制函数
# =========================
def plot_bar(df, x_col, y_col, title, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df[x_col], df[y_col])

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.xticks(rotation=45, ha='right')

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{int(height)}',
            ha='center',
            va='bottom',
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


# =========================
# 5. 主程序入口
# =========================
def main():
    keyword = "深度学习" # 搜索关键词

    set_chinese_font()

    df = load_data(keyword)

    top10_author_df = get_top10_author(df)
    top10_type_df = get_top10_type(df)
    top10_tag_df = get_top10_tag(df)

    plot_bar(
        top10_author_df,
        x_col='author',
        y_col='count',
        title='UP主出现次数 Top10',
        xlabel='UP主名称',
        ylabel='视频数量'
    )

    plot_bar(
        top10_type_df,
        x_col='type_name',
        y_col='count',
        title='视频分区出现次数 Top10',
        xlabel='视频分区',
        ylabel='视频数量'
    )

    plot_bar(
        top10_tag_df,
        x_col='tag',
        y_col='count',
        title='标签出现次数 Top10',
        xlabel='标签',
        ylabel='出现次数'
    )


if __name__ == '__main__':
    main()
