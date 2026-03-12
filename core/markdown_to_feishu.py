#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转飞书文档工具
用于将 Markdown 内容转换为飞书云文档
"""

import re
import json
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from .utils import get_feishu_client
except ImportError:
    from utils import get_feishu_client


class MarkdownToFeishu:
    """Markdown 转飞书文档"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """获取飞书客户端"""
        if self.client is None:
            self.client = get_feishu_client()
        return self.client
    
    def markdown_to_blocks(self, markdown: str) -> list:
        """将 Markdown 转换为飞书文档块"""
        blocks = []
        lines = markdown.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # 跳过空行
            if not line.strip():
                i += 1
                continue
            
            # 标题处理
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
            # 列表处理
            elif line.startswith('- ') or line.startswith('* '):
                content = line[2:].strip()
                # 处理嵌套列表
                indent = len(line) - len(line.lstrip())
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": "• " + content,
                        "hash": None
                    }
                })
            # 数字列表
            elif re.match(r'^\d+\.\s', line):
                match = re.match(r'^(\d+)\.\s(.*)', line)
                if match:
                    content = match.group(2)
                    blocks.append({
                        "tag": "text",
                        "text": {
                            "tag": "plain_text",
                            "content": f"{match.group(1)}. {content}",
                            "hash": None
                        }
                    })
            # 表格处理（简化版）
            elif line.startswith('|') and '---' not in line:
                # 收集表格行
                table_lines = [line]
                while i + 1 < len(lines) and lines[i + 1].startswith('|'):
                    i += 1
                    table_lines.append(lines[i])
                
                if len(table_lines) > 1:
                    # 解析表格
                    table_content = self._parse_table(table_lines)
                    blocks.append({
                        "tag": "table",
                        "cells": table_content
                    })
                else:
                    blocks.append({
                        "tag": "text",
                        "text": {
                            "tag": "plain_text",
                            "content": line.strip('| '),
                            "hash": None
                        }
                    })
            # 分隔线
            elif line.startswith('---'):
                blocks.append({
                    "tag": "divider"
                })
            # 普通文本
            else:
                # 处理粗体、斜体
                text = line
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # 移除粗体标记
                text = re.sub(r'\*(.+?)\*', r'\1', text)    # 移除斜体标记
                
                blocks.append({
                    "tag": "text",
                    "text": {
                        "tag": "plain_text",
                        "content": text,
                        "hash": None
                    }
                })
            
            i += 1
        
        return blocks
    
    def _parse_table(self, lines: list) -> list:
        """解析表格行"""
        cells = []
        for line in lines:
            if '---' in line:
                continue
            # 移除首尾的 |
            row = line.strip('|').split('|')
            cells.append([cell.strip() for cell in row])
        return cells
    
    def create_document(self, title: str, markdown_content: str, folder_token: str = None) -> Dict[str, Any]:
        """创建飞书文档"""
        client = self._get_client()
        
        # 获取用户 ID
        try:
            user_info = client.users.get(user_id='me')
            user_id = user_info.data.id if hasattr(user_info, 'data') else user_info.get('data', {}).get('id')
        except:
            user_id = None
        
        # 创建文档
        doc_data = {
            "obj_type": "docx",
            "parent_node_token": folder_token,
            "title": title
        }
        
        if folder_token:
            result = client.docx.create_document(
                folder_token=folder_token,
                title=title
            )
        else:
            # 直接创建文档（需要在根目录）
            # 使用 drive API 创建
            result = client.drive.create_folder(name=title)
            if hasattr(result, 'data') and result.data:
                folder_token = result.data.get('token')
                result = client.docx.create_document(
                    folder_token=folder_token,
                    title=title
                )
        
        # 获取文档 token
        if hasattr(result, 'data') and result.data:
            doc_token = result.data.get('token')
        else:
            doc_token = result.get('data', {}).get('token')
        
        if not doc_token:
            return {"error": "无法创建文档", "detail": str(result)}
        
        # 获取文档中的 Block ID
        blocks_result = client.docx.list_blocks(doc_token=doc_token)
        
        if hasattr(blocks_result, 'data') and blocks_result.data:
            block_items = blocks_result.data.get('items', [])
            if block_items:
                first_block_id = block_items[0].get('block_id')
            else:
                first_block_id = None
        else:
            first_block_id = None
        
        # 追加内容
        blocks = self.markdown_to_blocks(markdown_content)
        
        for block in blocks:
            try:
                if first_block_id:
                    client.docx.insert(
                        doc_token=doc_token,
                        after_block_id=first_block_id,
                        block=block
                    )
                else:
                    client.docx.append(
                        doc_token=doc_token,
                        block=block
                    )
            except Exception as e:
                print(f"添加块失败: {e}")
        
        # 获取文档 URL
        doc_url = f"https://feishu.cn/docx/{doc_token}"
        
        return {
            "success": True,
            "doc_token": doc_token,
            "doc_url": doc_url,
            "title": title
        }
    
    def update_document(self, doc_token: str, markdown_content: str) -> Dict[str, Any]:
        """更新飞书文档内容"""
        client = self._get_client()
        
        # 清空现有内容并重新写入
        # 获取所有块
        blocks_result = client.docx.list_blocks(doc_token=doc_token)
        
        if hasattr(blocks_result, 'data') and blocks_result.data:
            block_items = blocks_result.data.get('items', [])
            # 删除现有块（除了第一个）
            for block in block_items[1:]:
                try:
                    client.docx.delete_block(
                        doc_token=doc_token,
                        block_id=block.get('block_id')
                    )
                except:
                    pass
        
        # 添加新内容
        blocks = self.markdown_to_blocks(markdown_content)
        
        if block_items:
            first_block_id = block_items[0].get('block_id')
            for block in blocks:
                try:
                    client.docx.insert(
                        doc_token=doc_token,
                        after_block_id=first_block_id,
                        block=block
                    )
                except Exception as e:
                    print(f"添加块失败: {e}")
        
        return {"success": True, "doc_token": doc_token}


# 快捷函数
def create_feishu_doc(title: str, markdown: str, folder_token: str = None) -> Dict[str, Any]:
    """创建飞书文档的快捷函数"""
    converter = MarkdownToFeishu()
    return converter.create_document(title, markdown, folder_token)


# 测试
if __name__ == "__main__":
    test_md = """# 测试文档

## 第一部分

- 项目 1
- 项目 2

## 第二部分

| 列1 | 列2 |
|-----|-----|
| 内容1 | 内容2 |
"""
    
    result = create_feishu_doc("测试文档", test_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))