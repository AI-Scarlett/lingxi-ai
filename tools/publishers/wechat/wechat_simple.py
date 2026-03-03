#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号推送工具 - 简化 HTML 版本
微信只支持有限的 HTML 标签
"""

import requests
import json


class WeChatPublisherSimple:
    """微信公众号发布器 - 简化版"""
    
    def __init__(self, appid: str, appsecret: str):
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
    
    def get_access_token(self) -> str:
        """获取 access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        response = requests.get(url)
        result = response.json()
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            print(f"✅ 获取 access_token 成功")
            return self.access_token
        else:
            raise Exception(f"获取 access_token 失败：{result}")
    
    def upload_image(self, image_path: str) -> dict:
        """上传图片到素材库"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image"
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
        
        result = response.json()
        
        if "media_id" in result:
            print(f"✅ 图片上传成功：{result['media_id']}")
            return {
                "media_id": result["media_id"],
                "url": result.get("url", "")
            }
        else:
            print(f"❌ 图片上传失败：{result}")
            return None
    
    def add_to_draft(self, title: str, content: str, thumb_media_id: str, 
                     author: str = "", digest: str = "") -> dict:
        """添加到草稿箱"""
        if not self.access_token:
            self.get_access_token()
        
        url = "https://api.weixin.qq.com/cgi-bin/draft/add"
        params = {"access_token": self.access_token}
        
        # 微信支持的 HTML 标签非常有限
        data = {
            "article": {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 0
            }
        }
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(url, params=params, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
        result = response.json()
        
        return result
    
    def publish(self, title: str, content: str, cover_image: str,
                author: str = "", digest: str = "") -> dict:
        """完整发布流程"""
        print(f"📝 开始发布：{title}")
        
        # 上传封面图
        cover_result = self.upload_image(cover_image)
        if not cover_result:
            return {"success": False, "error": "封面图上传失败"}
        
        thumb_media_id = cover_result["media_id"]
        
        # 推送到草稿箱
        print("📤 推送到草稿箱...")
        result = self.add_to_draft(title, content, thumb_media_id, author, digest)
        
        if "errcode" in result:
            if result["errcode"] == 0:
                print(f"✅ 推送成功！media_id: {result.get('media_id')}")
                return {"success": True, "media_id": result.get("media_id")}
            else:
                print(f"❌ 推送失败：{result}")
                return {"success": False, "error": result}
        else:
            return {"success": False, "error": result}


if __name__ == "__main__":
    APPID = "wxd04bcd7faf50af4b"
    APPSECRET = "8d2d876ea7e1f6d07bd26653aac74697"
    
    # 创建发布器
    publisher = WeChatPublisherSimple(APPID, APPSECRET)
    
    # 简化的 HTML 内容（只用微信支持的标签）
    content = """
<p style="text-align: center; font-size: 16px;"><strong>🤖 灵犀 AI：一个人的公司如何靠 AI 调度系统实现高效运营</strong></p>
<p style="text-align: center; color: #888; font-size: 14px;">在 OpenClaw 生态中，用 AI 组建你的专属企业帝国 💋</p>
<hr>
<h2>开头：一个人的公司，真的是梦吗？</h2>
<p>2026 年，<strong>"一个人的公司"</strong>成了科技圈最火的话题。</p>
<p>不是自由职业，不是个体户，而是真正意义上——<strong>一个人，一家公司，一支团队</strong>。</p>
<blockquote><p>你可能听过这样的故事：</p><p>• 某独立开发者，靠着 AI 助手，一个人完成了所有工作</p><p>• 某内容创作者，用 AI 团队管理内容，月入 10 万+</p></blockquote>
<p>但现实往往是：</p>
<p>❌ 每个 AI 都是"单兵作战"，不会协作<br>❌ 任务分配靠手动<br>❌ 成本算不清<br>❌ 你还是累得像条狗</p>
<p>为什么？因为你缺的不是 AI 工具，而是一个<strong>智能调度中枢</strong>。</p>
<p><img src="__ORG_CHART_URL__" alt="组织架构图" style="max-width: 100%;"></p>
<h2>灵犀是什么？</h2>
<p><strong>灵犀 AI（Lingxi）</strong>，名字来自"心有灵犀一点通"。</p>
<p>它是 OpenClaw 生态系统中的<strong>智能调度中枢</strong>。</p>
<blockquote><p><strong>说人话就是：你说话，它办事，全程不用你操心。</strong></p></blockquote>
<h2>核心功能：四层架构</h2>
<p>灵犀最大的创新，是引入了<strong>企业组织架构系统</strong>。</p>
<p>✅ 明确的职责范围<br>✅ 独立的预算上限<br>✅ 清晰的汇报关系</p>
<h2>实际测评：用数据说话</h2>
<p>意图识别：<strong>0.003 ms</strong><br>任务调度：<strong>0.1 ms</strong><br>并发处理：<strong>86,600 任务/秒</strong><br>路由准确率：<strong>100%</strong></p>
<p><img src="__BUDGET_URL__" alt="预算仪表盘" style="max-width: 100%;"></p>
<h2>怎么用？3 步快速上手</h2>
<p><strong>第 1 步：</strong>克隆项目</p>
<p><code>git clone https://github.com/AI-Scarlett/lingxi-ai.git</code></p>
<p><strong>第 2 步：</strong>配置团队</p>
<p><strong>第 3 步：</strong>开始分配任务</p>
<h2>开源信息</h2>
<p><strong>项目名称：</strong>灵犀 AI (Lingxi)<br><strong>版本：</strong>v2.0.0<br><strong>许可证：</strong>MIT<br><strong>开源地址：</strong><a href="https://github.com/AI-Scarlett/lingxi-ai">github.com/AI-Scarlett/lingxi-ai</a></p>
<hr>
<p style="text-align: center; color: #888; font-size: 12px;">评测者：丝嘉丽 AI 实验室</p>
"""
    
    # 替换图片 URL（用素材库的）
    content = content.replace(
        "__ORG_CHART_URL__",
        "http://mmbiz.qpic.cn/mmbiz_png/z3ib9cMLKiaWGUDfssIs6nA8KyzibEt3HhbIGq2LUiayY4J42crtGL9xXNYVaHhm5pfcib5aoERQEZibUMrnBrnPRfpgyOGZJCZz2YuqhKQiaryzBs/0?wx_fmt=png"
    )
    content = content.replace(
        "__BUDGET_URL__",
        "http://mmbiz.qpic.cn/sz_mmbiz_png/z3ib9cMLKiaWEET3RNtKhsDD8ZA9uXDLefurkuN2D3nt8HsLVAaCDYfajfgghyY1WR7l4O8VvILvtU6FJiaSyGoTa8jQRB0jFdkMZzTNWINT0o/0?wx_fmt=png"
    )
    
    # 发布
    result = publisher.publish(
        title="灵犀 AI：一个人的公司如何靠 AI 调度系统实现高效运营",
        content=content,
        cover_image="/tmp/org_chart.png",
        author="丝嘉丽 AI 实验室",
        digest="在 OpenClaw 生态中，用 AI 组建你的专属企业帝国"
    )
    
    print(f"\n最终结果：{result}")
