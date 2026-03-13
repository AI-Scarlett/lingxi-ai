#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer0 响应规则管理 API - 完整版
支持 191 条规则的实时管理
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import json
from pathlib import Path
import shutil
from datetime import datetime

# Token 验证
OPENCLAW_DIR = Path.home() / ".openclaw"
TOKEN_FILE = OPENCLAW_DIR / "workspace" / ".lingxi" / "dashboard_token.txt"

def verify_token(token: str = Query("", description="访问 Token")):
    """验证 Token"""
    if not TOKEN_FILE.exists():
        return True
    saved = TOKEN_FILE.read_text().strip()
    if not saved:
        return True
    if token != saved:
        raise HTTPException(status_code=401, detail="Token 无效")
    return True


# 规则文件路径
RULES_FILE = Path(__file__).parent / "layer0_all_rules.json"
BACKUP_FILE = Path(__file__).parent / "layer0_all_rules.backup.json"


def load_rules() -> Dict:
    """加载所有规则"""
    if not RULES_FILE.exists():
        raise HTTPException(status_code=404, detail="规则文件不存在，请先初始化")
    
    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_rules(data: Dict):
    """保存规则"""
    # 先备份
    if RULES_FILE.exists():
        shutil.copy(RULES_FILE, BACKUP_FILE)
    
    data['updated_at'] = datetime.now().isoformat()
    
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


layer0_router = APIRouter(prefix="/api/layer0", tags=["Layer0"])


class RuleInput(BaseModel):
    patterns: List[str]
    response: str
    category: str = "其他"
    priority: int = 8
    enabled: bool = True


@layer0_router.get("/stats")
async def get_stats(_: bool = Depends(verify_token)):
    """获取规则统计"""
    data = load_rules()
    rules = data['rules']
    
    # 按分类统计
    categories = {}
    for rule in rules:
        cat = rule.get('category', '其他')
        categories[cat] = categories.get(cat, 0) + 1
    
    # 按状态统计
    enabled = sum(1 for r in rules if r.get('enabled', True))
    disabled = len(rules) - enabled
    
    return {
        "total": len(rules),
        "enabled": enabled,
        "disabled": disabled,
        "categories": categories,
        "version": data.get('version', '3.3.6'),
        "updated_at": data.get('updated_at')
    }


@layer0_router.get("/rules")
async def get_rules(
    category: str = Query("", description="分类筛选"),
    search: str = Query("", description="搜索关键词"),
    enabled_only: bool = Query(False, description="只显示启用的规则"),
    disabled_only: bool = Query(False, description="只显示禁用的规则"),
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    _: bool = Depends(verify_token)
):
    """获取规则列表（支持分页和筛选）"""
    data = load_rules()
    rules = data['rules']
    
    # 筛选
    if category:
        rules = [r for r in rules if r.get('category') == category]
    
    if search:
        search_lower = search.lower()
        rules = [r for r in rules if 
                 search_lower in r.get('response', '').lower() or
                 any(search_lower in p for p in r.get('patterns', []))]
    
    if enabled_only:
        rules = [r for r in rules if r.get('enabled', True)]
    
    if disabled_only:
        rules = [r for r in rules if not r.get('enabled', True)]
    
    # 分页
    total = len(rules)
    paginated = rules[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "rules": paginated
    }


@layer0_router.get("/rules/{rule_id}")
async def get_rule(rule_id: str, _: bool = Depends(verify_token)):
    """获取规则详情"""
    data = load_rules()
    
    for rule in data['rules']:
        if rule['id'] == rule_id:
            return rule
    
    raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")


@layer0_router.post("/rules")
async def create_rule(rule: RuleInput, _: bool = Depends(verify_token)):
    """创建新规则"""
    data = load_rules()
    
    # 生成新 ID
    max_id = 0
    for r in data['rules']:
        try:
            num = int(r['id'].split('_')[1])
            max_id = max(max_id, num)
        except:
            pass
    
    new_rule = {
        "id": f"L0_{max_id + 1:04d}",
        "patterns": rule.patterns,
        "response": rule.response,
        "category": rule.category,
        "enabled": rule.enabled,
        "priority": rule.priority,
        "created_at": datetime.now().isoformat(),
        "source": "custom"
    }
    
    data['rules'].append(new_rule)
    data['total'] = len(data['rules'])
    save_rules(data)
    
    return {"success": True, "rule": new_rule, "message": f"规则已创建：{new_rule['id']}"}


@layer0_router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, rule: RuleInput, _: bool = Depends(verify_token)):
    """更新规则"""
    data = load_rules()
    
    for i, r in enumerate(data['rules']):
        if r['id'] == rule_id:
            data['rules'][i].update({
                "patterns": rule.patterns,
                "response": rule.response,
                "category": rule.category,
                "priority": rule.priority,
                "enabled": rule.enabled
            })
            data['rules'][i]['updated_at'] = datetime.now().isoformat()
            
            save_rules(data)
            
            return {"success": True, "rule": data['rules'][i], "message": f"规则已更新：{rule_id}"}
    
    raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")


@layer0_router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, _: bool = Depends(verify_token)):
    """删除规则"""
    data = load_rules()
    
    for i, r in enumerate(data['rules']):
        if r['id'] == rule_id:
            deleted = data['rules'].pop(i)
            data['total'] = len(data['rules'])
            save_rules(data)
            
            return {"success": True, "deleted": deleted, "message": f"规则已删除：{rule_id}"}
    
    raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")


@layer0_router.post("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, _: bool = Depends(verify_token)):
    """切换规则启用/禁用状态"""
    data = load_rules()
    
    for i, r in enumerate(data['rules']):
        if r['id'] == rule_id:
            data['rules'][i]['enabled'] = not r.get('enabled', True)
            data['rules'][i]['updated_at'] = datetime.now().isoformat()
            
            save_rules(data)
            
            status = "启用" if data['rules'][i]['enabled'] else "禁用"
            return {"success": True, "rule": data['rules'][i], "message": f"规则已{status}：{rule_id}"}
    
    raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")


@layer0_router.get("/categories")
async def get_categories(_: bool = Depends(verify_token)):
    """获取所有分类"""
    data = load_rules()
    
    categories = {}
    for rule in data['rules']:
        cat = rule.get('category', '其他')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {"categories": categories}


@layer0_router.post("/backup/restore")
async def restore_backup(_: bool = Depends(verify_token)):
    """恢复备份"""
    if not BACKUP_FILE.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")
    
    shutil.copy(BACKUP_FILE, RULES_FILE)
    
    return {"success": True, "message": "已从备份恢复规则"}
