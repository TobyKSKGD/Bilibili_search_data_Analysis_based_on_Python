import os
import re
import time
import random
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
import pandas as pd

DEFAULT_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "origin": "https://search.bilibili.com",
    "referer": "https://search.bilibili.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "connection": "close",
}

SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"


def polite_sleep(a=0.8, b=1.5):
    time.sleep(random.uniform(a, b))


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def cn_number_to_int(x) -> Optional[int]:
    """
    B站搜索结果里有时会返回 '1.2万' 这种字符串。
    此函数做转换。
    """
    if x is None:
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return int(x)

    s = str(x).strip()
    if s == "":
        return None

    if s.isdigit():
        return int(s)

    m = re.match(r"([\d.]+)\s*([万亿])", s)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        if unit == "万":
            return int(num * 10000)
        if unit == "亿":
            return int(num * 100000000)

    digits = re.findall(r"\d+", s)
    if digits:
        try:
            return int("".join(digits))
        except:
            return None
    return None


def parse_duration(sec_or_str) -> Optional[str]:
    """
    搜索接口中 duration 常见为 '12:34' 字符串。
    做个容错。最终统一输出 'mm:ss' 或 'hh:mm:ss'。
    """
    if sec_or_str is None:
        return None
    s = str(sec_or_str).strip()
    if ":" in s:
        return s
    if s.isdigit():
        sec = int(s)
        h = sec // 3600
        m = (sec % 3600) // 60
        ss = sec % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{ss:02d}"
        return f"{m:02d}:{ss:02d}"
    return s


def load_cookie(cookie_arg: Optional[str]) -> Optional[str]:
    """
    Cookie 读取优先级：
    1) 命令行 --cookie
    2) 环境变量 BILI_COOKIE
    3) 当前目录 cookie.txt
    """
    if cookie_arg and cookie_arg.strip():
        return cookie_arg.strip()

    env = os.getenv("BILI_COOKIE")
    if env and env.strip():
        return env.strip()

    if os.path.exists("cookie.txt"):
        try:
            with open("cookie.txt", "r", encoding="utf-8") as f:
                txt = f.read().strip()
                return txt if txt else None
        except:
            return None

    return None


def build_session(cookie: Optional[str], proxies: Optional[Dict[str, str]] = None) -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    s.proxies = proxies or {}

    headers = dict(DEFAULT_HEADERS)
    if cookie:
        headers["cookie"] = cookie
    s.headers.update(headers)
    return s


def fetch_search_page(
    session: requests.Session,
    keyword: str,
    page: int,
    page_size: int = 30,
) -> Dict[str, Any]:

    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "from_source": "",
        "platform": "pc",
        "highlight": "1",
        "single_column": "0",
        "category_id": "",
        "dynamic_offset": 0,
        "preload": "true",
        "com2co": "true",
    }

    r = session.get(SEARCH_URL, params=params, timeout=(20, 60))
    return {"status_code": r.status_code, "json": safe_json(r)}


def safe_json(resp: requests.Response) -> Optional[Dict[str, Any]]:
    try:
        return resp.json()
    except:
        return None


def extract_rows(keyword: str, page: int, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for d in data_list:
        title = strip_html(d.get("title", ""))
        desc = strip_html(d.get("description", ""))

        # 作者字段
        author = d.get("author") or d.get("uname") or d.get("owner", "")

        # BVID / AID
        bvid = d.get("bvid")
        aid = d.get("aid")

        # 时间戳
        pub_ts = d.get("pubdate") or d.get("pub_date") or d.get("created")
        pub_dt = datetime.fromtimestamp(pub_ts) if isinstance(pub_ts, int) else None

        # 搜索结果有时给的是字符串计数
        view = cn_number_to_int(d.get("play"))
        danmaku = cn_number_to_int(d.get("video_review") or d.get("danmaku"))
        like = cn_number_to_int(d.get("like"))
        favorite = cn_number_to_int(d.get("favorites") or d.get("favorite"))

        # 分区与标签
        typename = d.get("typename") or d.get("type") or d.get("tname")
        tag = d.get("tag")

        duration = parse_duration(d.get("duration"))

        rows.append({
            "keyword": keyword,
            "page": page,
            "title": title,
            "author": author,
            "bvid": bvid,
            "aid": aid,
            "pub_ts": pub_ts,
            "pub_time": pub_dt.strftime("%Y-%m-%d %H:%M:%S") if pub_dt else None,
            "duration": duration,
            "danmaku": danmaku,
            "like": like,
            "view": view,
            "favorite": favorite,
            "type_name": typename,
            "tag": tag,
            "description": desc,
            "link": f"https://www.bilibili.com/video/{bvid}" if bvid else None,
        })
    return rows


def crawl_bilibili_search(
    keyword: str,
    pages: int = 3,
    page_size: int = 30,
    cookie: Optional[str] = None,
    proxies: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    session = build_session(cookie, proxies=proxies)

    all_rows = []
    for page in range(1, pages + 1):
        resp = fetch_search_page(session, keyword, page, page_size)

        code = resp["status_code"]
        j = resp["json"]

        # 412 常见反爬
        if code == 412:
            raise RuntimeError(
                "触发 HTTP 412（疑似反爬）。\n"
                "解决办法：\n"
                "1) 使用自己浏览器的 Cookie\n"
                "   - 方式A：命令行参数 --cookie \"...\"\n"
                "   - 方式B：环境变量 BILI_COOKIE\n"
                "   - 方式C：放到同目录 cookie.txt\n"
                "2) 降低 pages / 增加 sleep。\n"
            )
        if code != 200 or not j:
            raise RuntimeError(f"请求失败：status={code}, json解析={bool(j)}")

        if j.get("code") != 0:
            raise RuntimeError(f"接口返回非0 code：{j.get('code')}, msg={j.get('message')}")

        data_list = (j.get("data", {}) or {}).get("result", []) or []
        rows = extract_rows(keyword, page, data_list)
        all_rows.extend(rows)

        polite_sleep()

    df = pd.DataFrame(all_rows)

    # 基础去重：按 bvid
    if "bvid" in df.columns:
        df = df.drop_duplicates(subset=["bvid"], keep="first")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="B站搜索结果爬取"
    )
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--pages", type=int, default=3, help="爬取页数")
    parser.add_argument("--page_size", type=int, default=30, help="每页数量（默认30）")
    parser.add_argument("--out", default="bili_search.csv", help="输出CSV文件名")
    parser.add_argument("--cookie", default=None, help="B站Cookie")

    parser.add_argument("--proxy", default=None, help="HTTP代理，如 http://127.0.0.1:7897")

    args = parser.parse_args()

    cookie = load_cookie(args.cookie)

    proxies = None
    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}

    df = crawl_bilibili_search(
        keyword=args.keyword,
        pages=args.pages,
        page_size=args.page_size,
        cookie=cookie,
        proxies=proxies,
    )

    df.to_csv(args.out, index=False, encoding="utf_8_sig")
    print(f"[OK] 保存完成：{args.out}  行数={len(df)}")


if __name__ == "__main__":
    # ====== 手动修改搜索关键词 ======
    keyword = "六级"
    pages = 3
    out = "六级_搜索.csv"
    page_size = 30
    proxy = "http://127.0.0.1:7897"

    cookie = load_cookie(None)

    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    df = crawl_bilibili_search(
        keyword=keyword,
        pages=pages,
        page_size=page_size,
        cookie=cookie,
        proxies=proxies,
    )

    df.to_csv(out, index=False, encoding="utf_8_sig")
    print(f"[OK] 保存完成：{out}  行数={len(df)}")

