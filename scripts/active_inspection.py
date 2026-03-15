#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀主动巡察系统 v2.0 - 增强版

功能：
1. 每 30 分钟巡察任务执行情况
2. 验证是否按规则汇报
3. 识别任务归属 agent
4. 执行奖惩
5. 服务健康检查（新增）

作者：Scarlett
创建时间：2026-03-14
更新时间：2026-03-14 13:20
"""

import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加路径
CORE_DIR = Path.home() / ".openclaw" / "workspace" / "core"
sys.path.insert(0, str(CORE_DIR))
from agent_credit import AgentCreditManager, CREDIT_RULES

# ============ 配置 ============

WORKSPACE = Path.home() / ".openclaw" / "workspace"
DASHBOARD_TOKEN_FILE = WORKSPACE / ".lingxi" / "dashboard_token.txt"
DASHBOARD_HOST = "http://localhost:8765"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# 巡察配置
INSPECTION_INTERVAL_MINUTES = 30
REPORT_DELAY_THRESHOLD_MINUTES = 10  # 汇报延迟阈值


# ============ 巡察器 ============

class ActiveInspector:
    """主动巡察器"""
    
    def __init__(self):
        self.token = self._load_token()
        self.credit_manager = AgentCreditManager()
        self.inspection_log = []
        self.service_status = {}
    
    def _load_token(self) -> str:
        """加载 Dashboard Token"""
        if DASHBOARD_TOKEN_FILE.exists():
            return DASHBOARD_TOKEN_FILE.read_text().strip()
        return ""
    
    def inspect(self):
        """执行巡察"""
        print("=" * 60)
        print("🔍 灵犀主动巡察系统")
        print(f"巡察时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 0. 检查服务健康状态
        print("\n🏥 服务健康检查")
        self._check_services()
        
        # 1. 获取过去 30 分钟的任务
        tasks = self._get_recent_tasks()
        print(f"\n📋 发现 {len(tasks)} 个任务")
        
        # 2. 检查每个任务的汇报情况
        for task in tasks:
            self._inspect_task(task)
        
        # 3. 生成巡察报告
        report = self._generate_report()
        
        # 4. 保存报告
        self._save_report(report)
        
        # 5. 发送飞书通知
        self._send_feishu_notification(report)
        
        print("\n" + "=" * 60)
        print("✅ 巡察完成")
        print("=" * 60)
        
        return report
    
    def _check_services(self):
        """检查各服务是否正常运行"""
        services = [
            ("Dashboard 服务", self._check_dashboard),
            ("每小时汇报", self._check_hourly_report),
            ("定时任务 Cron", self._check_cron),
            ("OpenClaw Gateway", self._check_openclaw),
        ]
        
        all_normal = True
        for name, check_func in services:
            try:
                status = check_func()
                self.service_status[name] = status
                icon = "✅" if status["status"] == "normal" else "⚠️" if status["status"] == "warning" else "❌"
                print(f"  {icon} {name}: {status['message']}")
                if status["status"] != "normal":
                    all_normal = False
            except Exception as e:
                self.service_status[name] = {"status": "error", "message": str(e)}
                print(f"  ❌ {name}: {e}")
                all_normal = False
        
        # 如果有服务异常，记录处罚
        if not all_normal:
            self.inspection_log.append({
                "type": "service_issue",
                "time": datetime.now().isoformat(),
                "details": {k: v for k, v in self.service_status.items() if v.get("status") != "normal"}
            })
        
        # 安全检查（新增）
        print("\n🔒 安全检查")
        self._check_security()
    
    def _check_dashboard(self) -> Dict:
        """检查 Dashboard 服务"""
        try:
            response = requests.get(
                f"{DASHBOARD_HOST}/api/stats?token={self.token}",
                timeout=5
            )
            if response.status_code == 200:
                return {"status": "normal", "message": "正常运行"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"无法访问：{e}"}
    
    def _check_hourly_report(self) -> Dict:
        """检查每小时汇报"""
        try:
            log_file = Path("/tmp/hourly_report.log")
            if not log_file.exists():
                return {"status": "warning", "message": "日志文件不存在"}
            
            content = log_file.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            # 检查最近一次汇报时间
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            
            # 查找最近一次成功汇报
            for line in reversed(lines[-50:]):
                if '✅ 汇报完成' in line:
                    return {"status": "normal", "message": "最近有成功汇报"}
            
            return {"status": "warning", "message": "未找到最近成功汇报"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_cron(self) -> Dict:
        """检查定时任务"""
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                cron_lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('#')]
                return {"status": "normal", "message": f"{len(cron_lines)} 个定时任务"}
            else:
                return {"status": "warning", "message": "无法读取 crontab"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_openclaw(self) -> Dict:
        """检查 OpenClaw Gateway"""
        try:
            result = subprocess.run(
                ["/root/.local/share/pnpm/openclaw", "status"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {"status": "normal", "message": "Gateway 正常运行"}
            else:
                return {"status": "warning", "message": "Gateway 可能未运行"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_security(self):
        """安全检查"""
        security_issues = []
        
        # 1. 检查敏感信息泄露
        leak_check = self._check_sensitive_info_leak()
        if leak_check["issues"]:
            security_issues.extend(leak_check["issues"])
            print(f"  ⚠️ 敏感信息：{len(leak_check['issues'])} 个风险")
        else:
            print(f"  ✅ 敏感信息：未发现泄露")
        
        # 2. 检查外网 IP 暴露
        ip_check = self._check_public_ip_exposure()
        if ip_check["issues"]:
            security_issues.extend(ip_check["issues"])
            print(f"  ⚠️ 外网暴露：{len(ip_check['issues'])} 个风险")
        else:
            print(f"  ✅ 外网暴露：未发现风险")
        
        # 3. 检查 API 密钥安全
        key_check = self._check_api_keys_security()
        if key_check["issues"]:
            security_issues.extend(key_check["issues"])
            print(f"  ⚠️ API 密钥：{len(key_check['issues'])} 个风险")
        else:
            print(f"  ✅ API 密钥：配置安全")
        
        # 4. 检查文件权限
        perm_check = self._check_file_permissions()
        if perm_check["issues"]:
            security_issues.extend(perm_check["issues"])
            print(f"  ⚠️ 文件权限：{len(perm_check['issues'])} 个风险")
        else:
            print(f"  ✅ 文件权限：配置正确")
        
        # 记录安全问题
        if security_issues:
            self.inspection_log.append({
                "type": "security_issue",
                "time": datetime.now().isoformat(),
                "severity": "high" if len(security_issues) > 3 else "medium",
                "issues": security_issues
            })
            
            # 发送安全告警
            self._send_security_alert(security_issues)
    
    def _check_sensitive_info_leak(self) -> Dict:
        """检查敏感信息泄露"""
        issues = []
        
        # 检查工作区文件
        workspace = Path.home() / ".openclaw" / "workspace"
        
        # 检查 CREDENTIALS.md 权限
        creds_file = workspace / "CREDENTIALS.md"
        if creds_file.exists():
            mode = creds_file.stat().st_mode
            if mode & 0o044:  # 其他人可读
                issues.append({
                    "type": "sensitive_file_permission",
                    "file": str(creds_file),
                    "risk": "CREDENTIALS.md 权限过于开放",
                    "suggestion": "运行 chmod 600 CREDENTIALS.md"
                })
        
        # 检查是否有硬编码密钥
        sensitive_patterns = [
            (r'sk-[a-f0-9]{32}', '阿里云百炼 API Key'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Token'),
            (r'wxd[a-f0-9]{16}', '微信公众号 AppID'),
        ]
        
        # 扫描 Python 文件
        for py_file in workspace.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern, name in sensitive_patterns:
                    import re
                    matches = re.findall(pattern, content)
                    if matches:
                        issues.append({
                            "type": "hardcoded_secret",
                            "file": str(py_file),
                            "risk": f"发现硬编码的{name}",
                            "suggestion": "使用环境变量或加密存储"
                        })
            except:
                continue
        
        # 检查日志文件
        log_files = [
            Path("/tmp/hourly_report.log"),
            Path("/tmp/inspection.log"),
            Path("/tmp/dashboard.log"),
        ]
        
        for log_file in log_files:
            if log_file.exists():
                try:
                    content = log_file.read_text(encoding='utf-8')[-10000:]  # 只看最后 10KB
                    for pattern, name in sensitive_patterns:
                        import re
                        matches = re.findall(pattern, content)
                        if matches:
                            issues.append({
                                "type": "log_secret_leak",
                                "file": str(log_file),
                                "risk": f"日志中泄露{name}",
                                "suggestion": "清理日志并添加脱敏"
                            })
                except:
                    continue
        
        return {"issues": issues}
    
    def _check_public_ip_exposure(self) -> Dict:
        """检查外网 IP 暴露"""
        issues = []
        
        try:
            import socket
            # 获取本机外网 IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # 检查 Dashboard 是否绑定到 0.0.0.0
            dashboard_log = Path("/tmp/dashboard.log")
            if dashboard_log.exists():
                content = dashboard_log.read_text(encoding='utf-8')
                if "0.0.0.0:8765" in content:
                    issues.append({
                        "type": "dashboard_exposed",
                        "risk": f"Dashboard 绑定到 0.0.0.0，外网可访问",
                        "suggestion": "改为绑定 127.0.0.1 或使用防火墙限制",
                        "ip": local_ip
                    })
            
            # 检查防火墙状态
            try:
                result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
                if "inactive" in result.stdout.lower() or "disabled" in result.stdout.lower():
                    issues.append({
                        "type": "firewall_disabled",
                        "risk": "防火墙未启用",
                        "suggestion": "运行 ufw enable 启用防火墙"
                    })
            except:
                pass  # 可能没有 ufw
            
            # 检查是否有端口暴露
            try:
                result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=5)
                exposed_ports = []
                for line in result.stdout.split('\n'):
                    if '0.0.0.0:' in line or '*:' in line:
                        if '127.0.0.1' not in line:
                            exposed_ports.append(line.strip())
                
                if exposed_ports:
                    issues.append({
                        "type": "ports_exposed",
                        "risk": f"{len(exposed_ports)} 个端口对外暴露",
                        "suggestion": "检查不必要的端口暴露",
                        "details": exposed_ports[:5]
                    })
            except:
                pass
        
        except Exception as e:
            issues.append({
                "type": "check_error",
                "risk": f"外网检查失败：{e}",
                "suggestion": "手动检查网络配置"
            })
        
        return {"issues": issues}
    
    def _check_api_keys_security(self) -> Dict:
        """检查 API 密钥安全"""
        issues = []
        
        workspace = Path.home() / ".openclaw" / "workspace"
        
        # 检查 .env 文件
        env_file = workspace / ".env"
        if env_file.exists():
            mode = env_file.stat().st_mode
            if mode & 0o044:  # 其他人可读
                issues.append({
                    "type": "env_permission",
                    "file": str(env_file),
                    "risk": ".env 文件权限过于开放",
                    "suggestion": "运行 chmod 600 .env"
                })
            
            # 检查 .env 内容是否有明文密钥
            try:
                content = env_file.read_text(encoding='utf-8')
                if 'API_KEY=' in content or 'SECRET=' in content or 'TOKEN=' in content:
                    # 检查是否有注释说明
                    lines = content.split('\n')
                    for line in lines:
                        if any(k in line for k in ['API_KEY', 'SECRET', 'TOKEN']):
                            if '=' in line and not line.strip().startswith('#'):
                                # 检查值是否像真实密钥
                                if len(line.split('=')[1].strip()) > 20:
                                    issues.append({
                                        "type": "plaintext_key",
                                        "file": str(env_file),
                                        "risk": ".env 中包含可能的明文密钥",
                                        "suggestion": "使用密钥管理服务或加密"
                                    })
                                    break
            except:
                pass
        
        # 检查 git 历史是否有密钥泄露
        git_dir = workspace / ".git"
        if git_dir.exists():
            try:
                result = subprocess.run(
                    ["git", "log", "-p", "--all", "-S", "sk-", "--oneline"],
                    capture_output=True, text=True, timeout=10, cwd=str(workspace)
                )
                if result.stdout.strip():
                    issues.append({
                        "type": "git_secret_history",
                        "risk": "Git 历史中可能包含密钥",
                        "suggestion": "使用 git filter-branch 或 BFG 清理历史"
                    })
            except:
                pass
        
        return {"issues": issues}
    
    def _check_file_permissions(self) -> Dict:
        """检查文件权限"""
        issues = []
        
        workspace = Path.home() / ".openclaw" / "workspace"
        
        # 关键文件列表
        critical_files = [
            ("CREDENTIALS.md", 0o600),
            (".env", 0o600),
            ("core/agent_credit.py", 0o644),
            ("core/evomind.py", 0o644),
        ]
        
        for filename, expected_mode in critical_files:
            filepath = workspace / filename
            if filepath.exists():
                mode = filepath.stat().st_mode & 0o777
                if mode != expected_mode:
                    issues.append({
                        "type": "file_permission",
                        "file": str(filepath),
                        "risk": f"权限 {oct(mode)} 不符合预期 {oct(expected_mode)}",
                        "suggestion": f"运行 chmod {oct(expected_mode)[-3:]} {filename}"
                    })
        
        # 检查脚本文件是否可执行
        scripts = [
            "scripts/active_inspection.py",
            "scripts/hourly_progress_report.py",
        ]
        
        for script in scripts:
            filepath = workspace / script
            if filepath.exists():
                mode = filepath.stat().st_mode
                if not (mode & 0o111):  # 无可执行权限
                    issues.append({
                        "type": "script_not_executable",
                        "file": str(filepath),
                        "risk": "脚本文件无可执行权限",
                        "suggestion": f"运行 chmod +x {script}"
                    })
        
        return {"issues": issues}
    
    def _send_security_alert(self, issues: List[Dict]):
        """发送安全告警"""
        try:
            high_severity = [i for i in issues if i.get('type') in ['hardcoded_secret', 'log_secret_leak', 'git_secret_history']]
            
            if high_severity:
                title = "🚨 安全告警"
                content = [
                    f"巡察时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"",
                    f"发现 {len(high_severity)} 个高风险安全问题:",
                    ""
                ]
                for i, issue in enumerate(high_severity, 1):
                    content.append(f"{i}. {issue.get('risk', '未知风险')}")
                    content.append(f"   📁 文件：{issue.get('file', 'N/A')}")
                    content.append(f"   💡 建议：{issue.get('suggestion', '手动检查')}")
                    content.append("")
            else:
                title = "🔒 安全报告"
                content = [
                    f"巡察时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"",
                    f"发现 {len(issues)} 个安全问题需要关注:",
                    ""
                ]
                for i, issue in enumerate(issues[:5], 1):
                    content.append(f"{i}. {issue.get('risk', '未知风险')}")
                if len(issues) > 5:
                    content.append(f"... 还有 {len(issues) - 5} 个问题")
            
            content.append("---")
            content.append("*灵犀安全巡察系统*")
            
            message = "\n".join(content)
            
            cmd = [
                "/root/.local/share/pnpm/openclaw", "message", "send",
                "--channel", "feishu",
                "--message", f"{title}\n\n{message}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("  ✅ 安全告警已发送")
            else:
                print(f"  ⚠️ 告警发送失败：{result.stderr}")
        except Exception as e:
            print(f"  ⚠️ 发送安全告警异常：{e}")
    
    def _get_recent_tasks(self) -> List[Dict]:
        """获取最近 30 分钟的任务"""
        try:
            # 从 Dashboard API 获取任务
            response = requests.get(
                f"{DASHBOARD_HOST}/api/tasks",
                params={"limit": 100, "token": self.token},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                
                # 过滤最近 30 分钟的任务
                cutoff = (datetime.now() - timedelta(minutes=INSPECTION_INTERVAL_MINUTES)).timestamp() * 1000
                recent_tasks = [t for t in tasks if t.get("created_at", 0) >= cutoff]
                
                return recent_tasks
        except Exception as e:
            print(f"⚠️ 获取任务失败：{e}")
        
        # 降级：从会话文件读取
        return self._get_tasks_from_sessions()
    
    def _get_tasks_from_sessions(self) -> List[Dict]:
        """从会话文件读取任务"""
        tasks = []
        
        if not SESSIONS_DIR.exists():
            return tasks
        
        cutoff = datetime.now() - timedelta(minutes=INSPECTION_INTERVAL_MINUTES)
        
        for session_file in SESSIONS_DIR.glob("*.jsonl"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    for line in lines[-50:]:  # 只看最后 50 条
                        try:
                            msg = json.loads(line)
                            if msg.get('type') == 'message':
                                role = msg.get('message', {}).get('role')
                                if role == 'user':
                                    # 提取任务
                                    content = msg.get('message', {}).get('content', [])
                                    for item in content:
                                        if item.get('type') == 'text':
                                            text = item.get('text', '')
                                            if len(text) > 10:  # 有效任务
                                                tasks.append({
                                                    "id": f"session_{session_file.stem}_{len(tasks)}",
                                                    "user_input": text[:200],
                                                    "channel": "feishu",
                                                    "created_at": cutoff.timestamp() * 1000,
                                                    "status": "completed",
                                                })
                        except:
                            continue
            except Exception as e:
                print(f"⚠️ 读取会话文件失败：{e}")
        
        return tasks
    
    def _inspect_task(self, task: Dict):
        """检查单个任务"""
        task_id = task.get("id", "unknown")
        user_input = task.get("user_input", "")[:50]
        status = task.get("status", "unknown")
        created_at = task.get("created_at", 0)
        completed_at = task.get("completed_at", 0)
        
        print(f"\n📌 检查任务：{task_id}")
        print(f"   内容：{user_input}...")
        
        # 1. 检查任务状态
        if status == "failed":
            print(f"   ❌ 任务失败")
            self._penalize_task(task_id, "task_failed", "任务执行失败")
            return
        
        # 2. 检查汇报情况
        has_report = self._check_report(task)
        
        if not has_report:
            print(f"   ❌ 未找到汇报")
            self._penalize_task(task_id, "late_report", "未按时汇报")
        else:
            print(f"   ✅ 汇报正常")
            self._reward_task(task_id, "on_time_task", "按时完成任务")
    
    def _check_report(self, task: Dict) -> bool:
        """检查任务是否有汇报"""
        # 检查是否有 completed_at
        if task.get("completed_at"):
            created_at = task.get("created_at", 0)
            completed_at = task.get("completed_at", 0)
            
            # 检查是否延迟
            delay_minutes = (completed_at - created_at) / 60000
            if delay_minutes > REPORT_DELAY_THRESHOLD_MINUTES:
                print(f"   ⚠️ 汇报延迟 {delay_minutes:.1f} 分钟")
                self._penalize_task(task.get("id"), "late_report", f"汇报延迟{delay_minutes:.0f}分钟")
                return False
            
            return True
        
        return False
    
    def _reward_task(self, task_id: str, action: str, reason: str):
        """奖励任务"""
        # 默认奖励 main agent（实际应该根据任务归属）
        agent_id = "main"
        points = CREDIT_RULES.get(action, 1)
        self.credit_manager.add_points(agent_id, points, action, f"{reason} - {task_id}", task_id)
    
    def _penalize_task(self, task_id: str, action: str, reason: str):
        """处罚任务"""
        agent_id = "main"
        points = CREDIT_RULES.get(action, -1)
        self.credit_manager.add_points(agent_id, points, action, f"{reason} - {task_id}", task_id)
    
    def _generate_report(self) -> Dict:
        """生成巡察报告"""
        stats = self.credit_manager.get_stats()
        ranking = self.credit_manager.get_ranking(5)
        
        report = {
            "inspection_time": datetime.now().isoformat(),
            "interval_minutes": INSPECTION_INTERVAL_MINUTES,
            "service_status": self.service_status,
            "statistics": stats,
            "top_agents": [
                {
                    "agent_id": a.agent_id,
                    "score": a.score,
                    "level": a.level,
                }
                for a in ranking
            ],
            "log": self.inspection_log,
        }
        
        return report
    
    def _save_report(self, report: Dict):
        """保存巡察报告"""
        report_dir = WORKSPACE / "data" / "inspections"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"inspection_{timestamp}.json"
        
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\n💾 报告已保存：{report_file}")
    
    def _send_feishu_notification(self, report: Dict):
        """发送飞书通知"""
        try:
            stats = report.get("statistics", {})
            service_status = report.get("service_status", {})
            top_agents = report.get("top_agents", [])
            
            # 检查是否有服务异常
            issues = [k for k, v in service_status.items() if v.get("status") != "normal"]
            
            # 构建消息
            if issues:
                title = "⚠️ 灵犀巡察告警"
                content = [f"发现 {len(issues)} 个服务异常:", ""]
                for issue in issues:
                    status = service_status[issue]
                    content.append(f"❌ {issue}: {status.get('message', '未知错误')}")
            else:
                title = "🔍 灵犀主动巡察报告"
                content = [
                    f"巡察时间：{report.get('inspection_time', '')[:19]}",
                    f"",
                    f"📊 统计信息:",
                    f"  • Agent 总数：{stats.get('total_agents', 0)}",
                    f"  • 平均积分：{stats.get('average_score', 0):.1f}",
                    f"  • 最高积分：{stats.get('highest_score', 0)}",
                    f"",
                    f"🏆 排行榜 TOP 3:",
                ]
                
                for i, agent in enumerate(top_agents[:3], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                    content.append(f"  {medal} {agent['agent_id']}: {agent['score']}分 ({agent['level']})")
            
            message = "\n".join(content)
            
            # 使用 openclaw 命令发送
            cmd = [
                "/root/.local/share/pnpm/openclaw", "message", "send",
                "--channel", "feishu",
                "--message", f"{title}\n\n{message}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ 飞书通知已发送")
            else:
                print(f"⚠️ 飞书发送失败：{result.stderr}")
        except Exception as e:
            print(f"⚠️ 发送飞书通知失败：{e}")


# ============ 主入口 ============

def main():
    """主函数"""
    inspector = ActiveInspector()
    report = inspector.inspect()
    
    # 输出摘要
    print("\n📋 巡察摘要:")
    stats = report.get("statistics", {})
    print(f"  Agent 总数：{stats.get('total_agents', 0)}")
    print(f"  平均积分：{stats.get('average_score', 0):.1f}")
    
    # 服务状态
    service_status = report.get("service_status", {})
    issues = [k for k, v in service_status.items() if v.get("status") != "normal"]
    if issues:
        print(f"  ⚠️ 异常服务：{', '.join(issues)}")
    else:
        print(f"  ✅ 所有服务正常")
    
    top_agents = report.get("top_agents", [])
    if top_agents:
        print(f"  🏆 冠军：{top_agents[0]['agent_id']} ({top_agents[0]['score']}分)")


if __name__ == "__main__":
    main()
