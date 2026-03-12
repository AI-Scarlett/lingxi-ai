#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档工具 - 集成到灵犀系统
将 Markdown 内容创建为飞书云文档
"""

import json
import os
import subprocess
from typing import Dict, Any, Optional


class FeishuDocTool:
    """飞书文档工具类"""
    
    def __init__(self):
        self.feishu_app_id = os.environ.get('FEISHU_APP_ID', 'cli_a92253b2e5789cb0')
        self.feishu_app_secret = os.environ.get('FEISHU_APP_SECRET', 'JXsMT5w6fMneUL4yaCTCgdWwICUbzHOK')
        self.access_token = None
    
    def get_tenant_token(self) -> Optional[str]:
        """获取 tenant_access_token"""
        if self.access_token:
            return self.access_token
        
        try:
            import requests
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            data = {
                "app_id": self.feishu_app_id,
                "app_secret": self.feishu_app_secret
            }
            resp = requests.post(url, json=data, timeout=10)
            result = resp.json()
            
            if result.get('code') == 0:
                self.access_token = result.get('tenant_access_token')
                return self.access_token
            else:
                print(f"获取 token 失败: {result}")
                return None
        except Exception as e:
            print(f"获取 token 异常: {e}")
            return None
    
    def create_doc_with_content(self, title: str, markdown_content: str) -> Dict[str, Any]:
        """
        创建飞书文档并写入内容
        
        Args:
            title: 文档标题
            markdown_content: Markdown 内容
            
        Returns:
            包含 doc_token 和 doc_url 的字典
        """
        token = self.get_tenant_token()
        if not token:
            return {"error": "无法获取飞书访问令牌"}
        
        try:
            import requests
            
            # 1. 创建空白文档
            create_url = "https://open.feishu.cn/open-apis/docx/v1/documents"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            create_data = {
                "node_type": "docx",
                "parent_node_token": "",
                "title": title
            }
            
            resp = requests.post(create_url, headers=headers, json=create_data, timeout=30)
            result = resp.json()
            
            if result.get('code') != 0:
                return {"error": f"创建文档失败: {result}"}
            
            doc_info = result['data']['document']
            doc_token = doc_info.get('token') or doc_info.get('document_id')
            doc_url = f"https://feishu.cn/docx/{doc_token}"
            
            # 2. 写入内容 - 使用批量操作
            blocks = self._markdown_to_blocks(markdown_content)
            
            if blocks:
                # 获取现有 blocks 找到插入点
                block_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks"
                block_resp = requests.get(block_url, headers=headers, timeout=10)
                block_result = block_resp.json()
                
                first_block_id = None
                if block_result.get('code') == 0:
                    items = block_result.get('data', {}).get('items', [])
                    if items:
                        first_block_id = items[0].get('block_id')
                
                # 逐个插入 blocks
                last_block_id = first_block_id
                for block in blocks:
                    insert_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks"
                    insert_data = {
                        "block": block
                    }
                    if last_block_id:
                        insert_data["insert_after_block_id"] = last_block_id
                    
                    insert_resp = requests.post(insert_url, headers=headers, json=insert_data, timeout=10)
                    insert_result = insert_resp.json()
                    
                    if insert_result.get('code') == 0:
                        last_block_id = insert_result.get('data', {}).get('block', {}).get('block_id')
                    else:
                        print(f"插入失败: {insert_result}")
            
            return {
                "success": True,
                "doc_token": doc_token,
                "doc_url": doc_url,
                "title": title
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _markdown_to_blocks(self, markdown: str) -> list:
        """将 Markdown 转换为飞书 block 数组"""
        import re
        
        blocks = []
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.rstrip()
            if not line.strip():
                continue
            
            # 标题
            if line.startswith('# '):
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": line[2:],
                        "hash": None
                    },
                    "style": {
                        "bold": True,
                        "font_size": "ultra_large"
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": line[3:],
                        "hash": None
                    },
                    "style": {
                        "bold": True,
                        "font_size": "large"
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": line[4:],
                        "hash": None
                    },
                    "style": {
                        "bold": True,
                        "font_size": "medium"
                    }
                })
            # 分隔线
            elif line == '---':
                blocks.append({"tag": "divider"})
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": "• " + content,
                        "hash": None
                    }
                })
            # 普通文本
            else:
                # 移除 markdown 格式
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                text = re.sub(r'~~(.+?)~~', r'\1', text)
                
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": text,
                        "hash": None
                    }
                })
        
        return blocks


def create_feishu_document(title: str, markdown: str) -> Dict[str, Any]:
    """创建飞书文档的便捷函数"""
    tool = FeishuDocTool()
    return tool.create_doc_with_content(title, markdown)


# 测试
if __name__ == "__main__":
    test_md = """# Hunter 每日商机报告

**日期**: 2026-03-12

## 今日最佳推荐

### 小红书爆款封面生成器 ⭐

- 可行性: 8/10
- 理由: 需求真实、痛点强烈
- 启动成本: ~500元

---

结论: 推荐小红书封面生成器
"""
    result = create_feishu_document("测试文档", test_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))