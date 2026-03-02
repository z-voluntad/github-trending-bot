# GitHub Trending Bot

每日自动抓取 GitHub 热榜 Top 10，用 AI 生成项目介绍，推送到 Telegram。

## 效果

每天 UTC 9:00 自动运行，推送格式：

```
🔥 GitHub 今日热榜 2026-03-02

1. owner/repo ⭐ 1,234 (+567 stars today)
💡 这是一个...（AI 生成的项目介绍）
```

## 部署

### 1. Fork 本仓库

### 2. 配置 Secrets

进入仓库 → Settings → Secrets and variables → Actions，添加：

| Secret | 说明 |
|--------|------|
| `ANTHROPIC_API_KEY` | Anthropic API Key |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（从 @BotFather 获取） |
| `TELEGRAM_CHAT_ID` | 你的 Telegram Chat ID |

### 3. 启用 Actions

进入 Actions 页面，启用 workflow。之后每天 UTC 9:00 自动运行。

手动触发：Actions → GitHub Trending Bot → Run workflow
