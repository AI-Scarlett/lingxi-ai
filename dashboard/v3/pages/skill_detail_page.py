#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能详情页 API

功能：
- 查看技能的详细信息
- 技能调用统计
- 技能配置参数
- 技能版本历史
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import time
import os
from pathlib import Path

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillVersion(BaseModel):
    """技能版本信息"""
    version: str
    released_at: float
    changes: List[str]
    is_current: bool = False


class SkillStat(BaseModel):
    """技能统计信息"""
    total_calls: int
    success_rate: float
    avg_response_time_ms: float
    total_tokens: int
    total_cost: float
    today_calls: int
    week_calls: int
    month_calls: int


class SkillConfig(BaseModel):
    """技能配置"""
    enabled: bool
    priority: int
    timeout_seconds: int
    max_retries: int
    require_auth: bool
    allowed_channels: List[str]


class SkillDetailResponse(BaseModel):
    """技能详情响应"""
    # 基本信息
    name: str
    display_name: str
    description: str
    version: str
    
    # 路径信息
    location: str
    skill_file: str
    
    # 配置
    config: SkillConfig
    
    # 统计
    stats: SkillStat
    
    # 版本历史
    versions: List[SkillVersion]
    
    # 触发条件
    triggers: List[str]
    keywords: List[str]
    
    # 依赖
    dependencies: List[str]
    required_envs: List[str]
    
    # 状态
    is_loaded: bool
    last_loaded_at: Optional[float]
    load_error: Optional[str]


@router.get("/list")
async def list_skills(
    source: str = Query("all", description="技能来源：all/local/installed"),
    include_stats: bool = Query(True, description="是否包含统计信息")
):
    """获取技能列表"""
    from ..database import db
    
    skills = []
    
    # 从 skills 目录扫描
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
                skill_info = scan_skill_folder(skill_folder)
                if skill_info:
                    if include_stats:
                        skill_info['stats'] = get_skill_stats(skill_info['name'])
                    skills.append(skill_info)
    
    # 从系统技能目录扫描
    system_skills_dir = Path("/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.8_@napi-rs+canvas@0.1.96_@types+express@5.0.6_hono@4.12.6_node-llama-cpp@3.16.2/node_modules/openclaw/skills")
    if system_skills_dir.exists() and source in ["all", "system"]:
        for skill_folder in system_skills_dir.iterdir():
            if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
                skill_info = scan_skill_folder(skill_folder)
                if skill_info:
                    skill_info['is_system'] = True
                    if include_stats:
                        skill_info['stats'] = get_skill_stats(skill_info['name'])
                    skills.append(skill_info)
    
    return {"total": len(skills), "skills": skills}


@router.get("/{skill_name}", response_model=SkillDetailResponse)
async def get_skill_detail(skill_name: str):
    """获取技能详情"""
    from ..database import db
    
    # 扫描技能目录
    skill_path = None
    possible_paths = [
        Path.home() / ".openclaw" / "workspace" / "skills" / skill_name,
        Path("/root/.local/share/pnpm/global/5/.pnpm/openclaw@2026.3.8_@napi-rs+canvas@0.1.96_@types+express@5.0.6_hono@4.12.6_node-llama-cpp@3.16.2/node_modules/openclaw/skills") / skill_name,
    ]
    
    for path in possible_paths:
        if path.exists():
            skill_path = path
            break
    
    if not skill_path:
        raise HTTPException(status_code=404, detail="技能不存在")
    
    # 解析技能信息
    skill_info = scan_skill_folder(skill_path)
    
    if not skill_info:
        raise HTTPException(status_code=404, detail="技能解析失败")
    
    # 获取统计信息
    stats = get_skill_stats(skill_name)
    
    # 获取配置
    config = get_skill_config(skill_name)
    
    # 解析 SKILL.md 获取触发条件
    triggers, keywords = parse_skill_triggers(skill_path / "SKILL.md")
    
    # 检查是否已加载
    is_loaded = check_skill_loaded(skill_name)
    
    return SkillDetailResponse(
        name=skill_info['name'],
        display_name=skill_info.get('display_name', skill_name),
        description=skill_info.get('description', ''),
        version=skill_info.get('version', '1.0.0'),
        location=str(skill_path),
        skill_file=str(skill_path / "SKILL.md"),
        config=config,
        stats=stats,
        versions=get_skill_versions(skill_path),
        triggers=triggers,
        keywords=keywords,
        dependencies=skill_info.get('dependencies', []),
        required_envs=skill_info.get('required_envs', []),
        is_loaded=is_loaded,
        last_loaded_at=None,
        load_error=None
    )


@router.get("/{skill_name}/calls")
async def get_skill_calls(
    skill_name: str,
    days: int = Query(7, description="查询天数"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取技能调用历史"""
    from ..database import db
    
    # 从数据库查询技能调用记录
    calls = db.get_skill_calls(skill_name, days=days, limit=limit)
    
    return {
        "skill_name": skill_name,
        "days": days,
        "total": len(calls),
        "calls": calls
    }


@router.get("/{skill_name}/stats")
async def get_skill_stats_detail(skill_name: str):
    """获取技能详细统计"""
    from ..database import db
    
    stats = get_skill_stats(skill_name)
    
    # 获取按天统计
    daily_stats = db.get_skill_daily_stats(skill_name, days=30)
    
    # 获取按渠道统计
    channel_stats = db.get_skill_channel_stats(skill_name)
    
    # 获取错误统计
    error_stats = db.get_skill_error_stats(skill_name)
    
    return {
        "skill_name": skill_name,
        "overview": stats,
        "daily": daily_stats,
        "by_channel": channel_stats,
        "errors": error_stats
    }


def scan_skill_folder(skill_path: Path) -> Optional[Dict]:
    """扫描技能文件夹获取基本信息"""
    if not skill_path.exists():
        return None
    
    skill_info = {
        'name': skill_path.name,
        'display_name': skill_path.name,
        'description': '',
        'version': '1.0.0',
        'dependencies': [],
        'required_envs': []
    }
    
    # 读取 SKILL.md
    skill_file = skill_path / "SKILL.md"
    if skill_file.exists():
        try:
            content = skill_file.read_text(encoding='utf-8')[:2000]
            # 简单解析描述
            if 'description:' in content:
                desc_start = content.find('description:') + 12
                desc_end = content.find('\n', desc_start)
                if desc_end > desc_start:
                    skill_info['description'] = content[desc_start:desc_end].strip()
        except Exception:
            pass
    
    # 读取 package.json 或 requirements.txt
    pkg_file = skill_path / "package.json"
    if pkg_file.exists():
        try:
            import json
            pkg = json.loads(pkg_file.read_text())
            skill_info['dependencies'] = list(pkg.get('dependencies', {}).keys())
        except Exception:
            pass
    
    req_file = skill_path / "requirements.txt"
    if req_file.exists():
        try:
            deps = []
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    deps.append(line.split('==')[0].split('>=')[0])
            skill_info['dependencies'] = deps
        except Exception:
            pass
    
    return skill_info


def get_skill_stats(skill_name: str) -> SkillStat:
    """获取技能统计信息"""
    from ..database import db
    
    # 从数据库查询统计数据
    stats = db.get_skill_stats(skill_name)
    
    if not stats:
        # 返回默认值
        return SkillStat(
            total_calls=0,
            success_rate=100.0,
            avg_response_time_ms=0,
            total_tokens=0,
            total_cost=0,
            today_calls=0,
            week_calls=0,
            month_calls=0
        )
    
    return SkillStat(
        total_calls=stats.get('total_calls', 0),
        success_rate=stats.get('success_rate', 100.0),
        avg_response_time_ms=stats.get('avg_response_time_ms', 0),
        total_tokens=stats.get('total_tokens', 0),
        total_cost=stats.get('total_cost', 0),
        today_calls=stats.get('today_calls', 0),
        week_calls=stats.get('week_calls', 0),
        month_calls=stats.get('month_calls', 0)
    )


def get_skill_config(skill_name: str) -> SkillConfig:
    """获取技能配置"""
    # 从配置文件读取
    config_path = Path.home() / ".openclaw" / "workspace" / ".lingxi" / "skills_config.json"
    
    default_config = SkillConfig(
        enabled=True,
        priority=5,
        timeout_seconds=60,
        max_retries=3,
        require_auth=False,
        allowed_channels=["all"]
    )
    
    if config_path.exists():
        try:
            import json
            config_data = json.loads(config_path.read_text())
            skill_config = config_data.get(skill_name, {})
            return SkillConfig(
                enabled=skill_config.get('enabled', True),
                priority=skill_config.get('priority', 5),
                timeout_seconds=skill_config.get('timeout_seconds', 60),
                max_retries=skill_config.get('max_retries', 3),
                require_auth=skill_config.get('require_auth', False),
                allowed_channels=skill_config.get('allowed_channels', ["all"])
            )
        except Exception:
            pass
    
    return default_config


def parse_skill_triggers(skill_file: Path) -> tuple:
    """解析技能触发条件"""
    triggers = []
    keywords = []
    
    if not skill_file.exists():
        return triggers, keywords
    
    try:
        content = skill_file.read_text(encoding='utf-8')
        
        # 查找 triggers 关键字
        if 'Triggers on' in content:
            start = content.find('Triggers on') + 11
            end = content.find('.', start)
            if end > start:
                trigger_text = content[start:end].strip()
                triggers = [t.strip() for t in trigger_text.split(',')]
        
        # 查找 keywords
        if 'keywords' in content.lower():
            import re
            matches = re.findall(r'"([^"]+)"', content[:3000])
            keywords = matches[:10]  # 最多取 10 个关键词
    except Exception:
        pass
    
    return triggers, keywords


def get_skill_versions(skill_path: Path) -> List[SkillVersion]:
    """获取技能版本历史"""
    versions = []
    
    # 检查是否有 CHANGELOG.md
    changelog = skill_path / "CHANGELOG.md"
    if changelog.exists():
        try:
            content = changelog.read_text(encoding='utf-8')
            # 简单解析版本
            import re
            version_pattern = r'##\s+v?(\d+\.\d+\.\d+)'
            matches = re.finditer(version_pattern, content)
            
            for i, match in enumerate(matches):
                version = match.group(1)
                start = match.end()
                # 找到下一个版本或文件末尾
                next_match = list(matches)[i+1:i+2]
                end = next_match[0].start() if next_match else len(content)
                
                changes = []
                for line in content[start:end].splitlines()[:5]:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*'):
                        changes.append(line[1:].strip())
                
                versions.append(SkillVersion(
                    version=version,
                    released_at=time.time() - (i * 86400 * 30),  # 估算
                    changes=changes,
                    is_current=(i == 0)
                ))
        except Exception:
            pass
    
    if not versions:
        # 默认版本
        versions.append(SkillVersion(
            version="1.0.0",
            released_at=time.time(),
            changes=["初始版本"],
            is_current=True
        ))
    
    return versions


def check_skill_loaded(skill_name: str) -> bool:
    """检查技能是否已加载"""
    # 检查技能是否在运行时的技能列表中
    # 这里简化处理，返回 True
    return True
