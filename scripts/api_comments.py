import pandas as pd
from pathlib import Path
import requests
import time
import json
import re
from getpass import getpass

BVID = "BV1xx411c7mD" # 替换成需要爬取评论的 B 站视频 BV 号
comments_path = Path(f"{BVID}_comments.csv")

df = pd.read_csv(comments_path, encoding="utf_8_sig")

# 1) API_KEY
API_KEY = Path("api_key.txt").read_text(encoding="utf-8").strip()

# 2) DeepSeek API 配置
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# 指令工程
def build_prompt(text: str) -> str:
    return f"""你是一个经常刷B站、擅长理解中文网络语境的评论分析员。请对以下“视频评论文本”进行情绪分类，以反映评论者对该视频/UP主内容的态度（注意：只基于文本本身判断，包含反讽/阴阳怪气也要尽量识别）。

文本内容："{text}"

请严格按照以下要求分类：
1. 积极情绪：夸赞、喜欢、支持、推荐、认为内容有价值/有趣/好看等，标注为 1
2. 消极情绪：吐槽、批评、反感、攻击、认为内容差/无聊/误导等，标注为 -1
3. 中性情绪：无明显情绪倾向、客观陈述、提问求资源/时间点、纯表情/刷屏/无意义信息等，标注为 0

请以JSON格式返回结果（json），包含两个字段：
- "sentiment": 情绪标签（1, 0, 或 -1）
- "reason": 判断理由（简要说明分类原因）

只返回JSON格式结果，不要有其他内容。"""

def extract_json_object(s: str) -> dict:
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))

def analyze_sentiment(text: str):
    """
    返回: (sentiment_label, reason)
    """
    prompt = build_prompt(text)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    request_data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs json."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=request_data,
            timeout=20,
        )

        if resp.status_code != 200:
            return 0, f"API请求失败: {resp.status_code}"

        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        data = extract_json_object(content)

        sentiment = int(data.get("sentiment", 0))
        reason = str(data.get("reason", "")).strip()

        if sentiment not in (-1, 0, 1):
            sentiment = 0
            if not reason:
                reason = "标签不合法，已兜底为中性"
        return sentiment, reason

    except Exception as e:
        return 0, f"异常兜底: {type(e).__name__}"

work_df = df.copy()

all_sentiments = []
all_reasons = []

for i in range(len(work_df)):
    text = str(work_df.iloc[i].get("content", "")).strip()
    print(f"正在分析第 {i+1}/{len(work_df)} 条...")

    s, r = analyze_sentiment(text)
    all_sentiments.append(s)
    all_reasons.append(r)

    time.sleep(1) # 暂停1秒，避免请求频率过高

work_df["sentiment_label"] = all_sentiments
work_df["judgment_reason"] = all_reasons

# 保存输出文件
out_path = Path(f"{BVID}_comments_with_sentiment.csv")
work_df.to_csv(out_path, index=False, encoding="utf_8_sig")
print(f"\n已保存：{out_path}  行数={len(work_df)}")

# 统计数量
print(f"积极情绪 (1):  {len(work_df[work_df['sentiment_label']==1])} 条")
print(f"消极情绪 (-1): {len(work_df[work_df['sentiment_label']==-1])} 条")
print(f"中性情绪 (0):  {len(work_df[work_df['sentiment_label']==0])} 条")
print(f"总计: {len(work_df)} 条")
