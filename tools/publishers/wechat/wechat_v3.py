#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号推送工具 v3 - 使用微信原生 HTML 格式
"""

import requests
import json


def get_token():
    APPID = "wxd04bcd7faf50af4b"
    APPSECRET = "8d2d876ea7e1f6d07bd26653aac74697"
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    resp = requests.get(url)
    data = resp.json()
    return data.get("access_token")


def upload_image(image_path, access_token):
    """上传图片并返回微信 CDN URL"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        resp = requests.post(url, files=files)
    
    result = resp.json()
    
    if "url" in result:
        # 返回微信 CDN URL（用于 HTML 中的 img src）
        cdn_url = result["url"].replace("http://", "https://")
        media_id = result["media_id"]
        print(f"✅ 图片上传成功：{media_id}")
        print(f"   CDN URL: {cdn_url}")
        return {"media_id": media_id, "cdn_url": cdn_url}
    else:
        print(f"❌ 上传失败：{result}")
        return None


def create_wechat_html(org_chart_url, budget_url):
    """创建微信原生 HTML 格式"""
    
    html = f'''<section>
<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<h1 style="font-weight: bold;margin: 0px;padding: 4px;font-size: 32px;">
<span style="font-size: 16px;"><strong>🤖 灵犀 AI：一个人的公司如何靠 AI 调度系统实现高效运营</strong></span>
</h1>
</blockquote>

<p style="text-align: center; color: #888; font-size: 14px;">
<span style="font-size: 14px;">在 OpenClaw 生态中，用 AI 组建你的专属企业帝国 💋</span>
</p>

<hr>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>开头：一个人的公司，真的是梦吗？</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">2026 年，<strong>"一个人的公司"</strong>成了科技圈最火的话题。</span></p>

<p><span style="font-size: 16px;">不是自由职业，不是个体户，而是真正意义上——<strong>一个人，一家公司，一支团队</strong>。</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;">你可能听过这样的故事：</span></p>
<p><span style="font-size: 16px;">• 某独立开发者，靠着 AI 助手，一个人完成了所有工作</span></p>
<p><span style="font-size: 16px;">• 某内容创作者，用 AI 团队管理内容，月入 10 万+</span></p>
</blockquote>

<p><span style="font-size: 16px;">但现实往往是：</span></p>

<p><span style="font-size: 16px;">❌ 每个 AI 都是"单兵作战"，不会协作<br/>
❌ 任务分配靠手动<br/>
❌ 成本算不清<br/>
❌ 你还是累得像条狗</span></p>

<p><span style="font-size: 16px;">为什么？因为你缺的不是 AI 工具，而是一个<strong>智能调度中枢</strong>。</span></p>

<section style="text-align: center;">
<img class="rich_pages wxw-img" data-aistatus="1" data-ratio="1" data-src="{org_chart_url}" data-type="png" data-w="1024" type="block" src="{org_chart_url}">
<p style="text-align: center; color: #888; font-size: 12px;">[灵犀 AI 企业组织架构图]</p>
</section>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>灵犀是什么？</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;"><strong>灵犀 AI（Lingxi）</strong>，名字来自"心有灵犀一点通"。</span></p>

<p><span style="font-size: 16px;">它是 OpenClaw 生态系统中的<strong>智能调度中枢</strong>。</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>说人话就是：你说话，它办事，全程不用你操心。</strong></span></p>
</blockquote>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>核心功能：四层架构</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">灵犀最大的创新，是引入了<strong>企业组织架构系统</strong>。</span></p>

<p><span style="font-size: 16px;">✅ 明确的职责范围<br/>
✅ 独立的预算上限<br/>
✅ 清晰的汇报关系</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>实际测评：用数据说话</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">意图识别：<strong>0.003 ms</strong>（比你眨眼快 10 万倍）<br/>
任务调度：<strong>0.1 ms</strong>（百万分之一秒）<br/>
并发处理：<strong>86,600 任务/秒</strong><br/>
路由准确率：<strong>100%</strong></span></p>

<section style="text-align: center;">
<img class="rich_pages wxw-img" data-aistatus="1" data-ratio="0.3" data-src="{budget_url}" data-type="png" data-w="1024" type="block" src="{budget_url}">
<p style="text-align: center; color: #888; font-size: 12px;">[灵犀预算控制仪表盘]</p>
</section>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>预算测试</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">写文案：¥0.50<br/>
SEO 分析：¥0.30<br/>
发社交媒体：¥0.80<br/>
开发功能：¥1.20<br/>
CEO 决策：¥2.50</span></p>

<p><span style="font-size: 16px;"><strong>总计：¥5.30（一杯咖啡的钱）</strong></span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>使用场景</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">✅ 强烈推荐：<br/>
• 中小企业老板<br/>
• "一个人的公司"践行者<br/>
• AI 中台团队<br/>
• 内容创作者</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>与 OpenClaw 的关系</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">• OpenClaw = AI 助手的"操作系统"<br/>
• 灵犀 = AI 团队的"CEO"</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>3 步快速上手</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;"><strong>第 1 步：</strong>克隆项目<br/>
<code style="background: #f6f8fa; padding: 3px 6px;">git clone https://github.com/AI-Scarlett/lingxi-ai.git</code></span></p>

<p><span style="font-size: 16px;"><strong>第 2 步：</strong>配置团队<br/>
<strong>第 3 步：</strong>开始分配任务</span></p>

<blockquote style="margin: 16px 0px;border-left: 3px solid rgb(219, 219, 219);padding-left: 10px;color: rgba(0, 0, 0, 0.55);padding-top: 4px;text-indent: 0px;font-size: 15px;">
<p><span style="font-size: 16px;"><strong>📦 开源信息</strong></span></p>
</blockquote>

<p><span style="font-size: 16px;">项目名称：灵犀 AI (Lingxi)<br/>
版本：v2.0.0<br/>
许可证：MIT<br/>
<strong>开源地址：</strong><a href="https://github.com/AI-Scarlett/lingxi-ai">github.com/AI-Scarlett/lingxi-ai</a></span></p>

<hr>

<p style="text-align: center; color: #888; font-size: 12px;">
<span style="font-size: 12px;">评测者：丝嘉丽 AI 实验室</span>
</p>

<p style="display: none;"><mp-style-type data-value="3"></mp-style-type></p>
</section>'''
    
    return html


def publish_to_draft(access_token, title, content, thumb_media_id, author="丝嘉丽 AI 实验室", digest="在 OpenClaw 生态中，用 AI 组建你的专属企业帝国"):
    """推送到草稿箱"""
    
    url = "https://api.weixin.qq.com/cgi-bin/draft/add"
    params = {"access_token": access_token}
    
    data = {
        "article": {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
    }
    
    headers = {"Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, params=params, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
    result = resp.json()
    
    return result


if __name__ == "__main__":
    print("="*70)
    print("📤 微信公众号推送 v3 - 微信原生格式")
    print("="*70)
    
    # 获取 token
    access_token = get_token()
    print(f"✅ Access Token: {access_token[:30]}...")
    
    # 上传图片
    print("\n📤 上传封面图...")
    cover_result = upload_image('/tmp/org_chart.png', access_token)
    
    if not cover_result:
        print("❌ 封面图上传失败")
        exit(1)
    
    thumb_media_id = cover_result["media_id"]
    org_chart_url = cover_result["cdn_url"]
    
    print("\n📤 上传预算图...")
    budget_result = upload_image('/tmp/budget_dashboard.png', access_token)
    
    if not budget_result:
        print("❌ 预算图上传失败")
        exit(1)
    
    budget_url = budget_result["cdn_url"]
    
    # 创建 HTML
    print("\n📝 创建微信原生 HTML...")
    content = create_wechat_html(org_chart_url, budget_url)
    print(f"✅ HTML 长度：{len(content)} 字节")
    
    # 推送
    print("\n📤 推送到草稿箱...")
    result = publish_to_draft(
        access_token=access_token,
        title="灵犀 AI：一个人的公司如何靠 AI 调度系统实现高效运营",
        content=content,
        thumb_media_id=thumb_media_id,
        author="丝嘉丽 AI 实验室",
        digest="在 OpenClaw 生态中，用 AI 组建你的专属企业帝国 💋"
    )
    
    print(f"\n📊 推送结果：{result}")
    
    if result.get("errcode") == 0:
        print("\n" + "="*70)
        print("✅✅✅ 推送成功！！！")
        print("="*70)
        print(f"草稿箱 media_id: {result.get('media_id')}")
    else:
        print(f"\n❌ 推送失败：{result.get('errmsg')}")
        print(f"错误码：{result.get('errcode')}")
