import os
import time
import random
from typing import Optional, Dict, List

import requests
import pandas as pd

DEFAULT_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "referer": "https://www.bilibili.com/",
}

def polite_sleep(a=0.8, b=1.5):
    time.sleep(random.uniform(a, b))

def load_cookie(cookie_arg: Optional[str] = None) -> Optional[str]:
    if cookie_arg and cookie_arg.strip():
        return cookie_arg.strip()
    env = os.getenv("BILI_COOKIE")
    if env and env.strip():
        return env.strip()
    if os.path.exists("cookie.txt"):
        with open("cookie.txt", "r", encoding="utf-8") as f:
            txt = f.read().strip()
            return txt if txt else None
    return None

def build_session(cookie: Optional[str] = None, proxies: Optional[Dict[str, str]] = None):
    s = requests.Session()
    headers = dict(DEFAULT_HEADERS)
    if cookie:
        headers["cookie"] = cookie
    s.headers.update(headers)
    if proxies:
        s.proxies = proxies
    return s

def bvid_to_aid(bvid: str, session: requests.Session) -> int:
    # 通过视频信息接口拿到 aid（av号），评论 oid 用这个
    url = "https://api.bilibili.com/x/web-interface/view"
    r = session.get(url, params={"bvid": bvid}, timeout=(10, 30))
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(f"BV转aid失败：code={j.get('code')} msg={j.get('message')}")
    return int(j["data"]["aid"])

def fetch_comments(bvid: str, session: requests.Session, max_comments: int = 100) -> pd.DataFrame:
    aid = bvid_to_aid(bvid, session)

    all_comments: List[dict] = []
    next_page = 0  # reply/main 常见从 0 或 1 开始，0 更常见
    while len(all_comments) < max_comments:
        url = "https://api.bilibili.com/x/v2/reply/main"
        params = {
            "type": 1,
            "oid": aid,
            "next": next_page,
            "mode": 3,   # 常见：3=按时间（不同资料说法略有差异，但可用）
            "plat": 1,
        }
        r = session.get(url, params=params, timeout=(10, 30))
        j = r.json()

        if j.get("code") != 0:
            # 关键：把错误信息打印出来，别“默默只拿到几条”
            raise RuntimeError(f"评论接口返回错误：code={j.get('code')} msg={j.get('message')}")

        data = j.get("data") or {}
        replies = data.get("replies") or []
        cursor = data.get("cursor") or {}

        if not replies:
            print("[INFO] 本页无 replies，停止。")
            break

        for rep in replies:
            all_comments.append({
                "rpid": rep.get("rpid"),
                "mid": rep.get("member", {}).get("mid"),
                "uname": rep.get("member", {}).get("uname"),
                "content": rep.get("content", {}).get("message"),
                "like": rep.get("like"),
                "ctime": rep.get("ctime"),
            })
            if len(all_comments) >= max_comments:
                break

        # 用 cursor 翻页
        if cursor.get("is_end"):
            print("[INFO] cursor.is_end=True，已经到末页。")
            break
        next_page = cursor.get("next")
        if next_page is None:
            print("[WARN] cursor.next 缺失，停止。")
            break

        polite_sleep()

    return pd.DataFrame(all_comments)

if __name__ == "__main__":
    bvid = "BV1wK2QBPEDv"
    max_comments = 50

    cookie = load_cookie()
    session = build_session(cookie=cookie)

    df = fetch_comments(bvid, session, max_comments=max_comments)
    df.to_csv(f"{bvid}_comments.csv", index=False, encoding="utf_8_sig")
    print(f"[OK] 保存完成：{bvid}_comments.csv  行数={len(df)}")
