# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🔐 WeChat Official Account (微信公众号)

**API Credentials:**
```bash
export WECHAT_APP_ID=wxd04bcd7faf50af4b
export WECHAT_APP_SECRET=8d2d876ea7e1f6d07bd26653aac74697
```

**IP Whitelist:** 确保运行机器的 IP 已添加到公众号后台白名单
- 服务器 IP: `106.52.101.202`
- 后台地址：https://mp.weixin.qq.com/

**如何获取凭证：**
- 登录微信公众号后台：https://mp.weixin.qq.com/
- 设置与开发 → 基本配置 → 开发者 ID(AppID) 和开发者密码 (AppSecret)
- 添加服务器 IP 到白名单：设置与开发 → 基本配置 → IP 白名单

---

Add whatever helps you do your job. This is your cheat sheet.
