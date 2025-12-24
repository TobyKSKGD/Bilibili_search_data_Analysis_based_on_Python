import os
import requests
import pandas as pd
import time
import random
from typing import Optional, Dict

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
    s.trust_env = False
    if proxies:
        s.proxies = proxies
    headers = dict(DEFAULT_HEADERS)
    if cookie:
        headers["cookie"] = cookie
    s.headers.update(headers)
    return s

def fetch_comments(bvid: str, session: requests.Session, max_comments: int = 100):
    """
    爬取指定BV号的视频评论
    参数:
        bvid: 视频BV号
        session: requests.Session
        max_comments: 最大爬取评论数
    """
    all_comments = []
    page = 1
    page_size = 20  # B站每页评论数固定约20
    while len(all_comments) < max_comments:
        url = f"https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={page}&type=1&oid={bvid}&sort=2"
        r = session.get(url, timeout=(10, 30))
        try:
            data = r.json()
        except:
            print(f"[WARN] 第{page}页返回不是JSON，跳过")
            page += 1
            continue

        replies = data.get("data", {}).get("replies") or []
        if not replies:
            print("[INFO] 已经没有更多评论了")
            break

        for rep in replies:
            comment = {
                "rpid": rep.get("rpid"),
                "mid": rep.get("member", {}).get("mid"),
                "uname": rep.get("member", {}).get("uname"),
                "content": rep.get("content", {}).get("message"),
                "like": rep.get("like"),
                "ctime": rep.get("ctime"),
            }
            all_comments.append(comment)
            if len(all_comments) >= max_comments:
                break
        page += 1
        polite_sleep()
    
    df = pd.DataFrame(all_comments)
    return df

# ===== 示例用法 =====
if __name__ == "__main__":
    bvid = "BV1wK2QBPEDv"
    max_comments = 50  # 用户自定义爬取的评论数
    cookie = load_cookie()
    session = build_session(cookie=cookie)
    df_comments = fetch_comments(bvid, session, max_comments=max_comments)
    df_comments.to_csv(f"{bvid}_comments.csv", index=False, encoding="utf_8_sig")
    print(f"[OK] 保存完成：{bvid}_comments.csv  行数={len(df_comments)}")
