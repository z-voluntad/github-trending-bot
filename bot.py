import os
import base64
import requests
from datetime import datetime
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_trending():
    r = requests.get(
        "https://github.com/trending?since=daily",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    repos = []
    for article in soup.select("article.Box-row")[:10]:
        a = article.select_one("h2 a")
        if not a:
            continue
        parts = a["href"].strip("/").split("/")
        if len(parts) != 2:
            continue
        owner, repo = parts
        desc_el = article.select_one("p")
        desc = desc_el.get_text(strip=True) if desc_el else ""
        stars_today_el = article.select_one("span.float-sm-right")
        stars_today = stars_today_el.get_text(strip=True) if stars_today_el else ""
        total_stars = ""
        for a_el in article.select("a.Link--muted"):
            if "stargazers" in a_el.get("href", ""):
                total_stars = a_el.get_text(strip=True)
                break
        repos.append({
            "full_name": f"{owner}/{repo}",
            "owner": owner,
            "repo": repo,
            "desc": desc,
            "stars": total_stars,
            "stars_today": stars_today,
        })
    return repos


def get_readme(owner, repo):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {token}"
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/readme", headers=headers)
    if r.status_code != 200:
        return ""
    try:
        return base64.b64decode(r.json().get("content", "")).decode("utf-8", errors="ignore")[:500]
    except Exception:
        return ""


def summarize(repo):
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    readme = get_readme(repo["owner"], repo["repo"])
    r = requests.post(
        f"{base_url}/v1/messages",
        headers={
            "x-api-key": api_key,
            "Authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            "max_tokens": 300,
            "messages": [{"role": "user", "content": (
                f"项目: {repo['full_name']}\n描述: {repo['desc']}\nREADME:\n{readme}\n\n"
                "用3-5句中文详细介绍这个项目是做什么的、解决什么问题、有哪些核心功能或特点。不要介绍安装和使用方法。"
            )}],
        },
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"].strip()


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
    ).raise_for_status()


def main():
    repos = fetch_trending()
    today = datetime.now().strftime("%Y-%m-%d")
    parts = [f"🔥 <b>GitHub 今日热榜 {today}</b>\n"]

    for i, repo in enumerate(repos, 1):
        summary = summarize(repo)
        stars_info = f"⭐ {repo['stars']}" if repo["stars"] else ""
        if repo["stars_today"]:
            stars_info += f" ({repo['stars_today']})"
        parts.append(
            f"{i}. <b><a href=\"https://github.com/{repo['full_name']}\">{repo['full_name']}</a></b> {stars_info}\n"
            f"💡 {summary}\n"
        )

    message = "\n".join(parts)
    if len(message) <= 4096:
        send_telegram(message)
    else:
        send_telegram(parts[0])
        for part in parts[1:]:
            send_telegram(part)

    print(f"Sent {len(repos)} repos")


if __name__ == "__main__":
    main()
