#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀设备绑定认证系统 v1.0

功能：
1. 设备注册和审批
2. 设备指纹识别
3. Token 认证
4. 设备管理
5. 访问控制

作者：Scarlett
创建时间：2026-03-14
"""

import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


# ============ 配置 ============

WORKSPACE = Path.home() / ".openclaw" / "workspace"
DEVICES_FILE = WORKSPACE / "data" / "devices.json"
ADMIN_USERS = ["ou_7348fd3aa0650146ce65714ccacb902c"]  # 管理员列表


# ============ 数据模型 ============

@dataclass
class Device:
    """设备信息"""
    id: str
    name: str
    fingerprint: str
    ip_address: str
    user_agent: str
    status: str  # pending, approved, revoked
    created_at: str
    last_access: str
    access_count: int = 0
    created_by: Optional[str] = None  # 创建者 IP
    approved_by: Optional[str] = None  # 审批者
    approved_at: Optional[str] = None
    notes: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


# ============ 设备管理器 ============

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.load()
    
    def load(self):
        """加载设备数据"""
        if DEVICES_FILE.exists():
            try:
                data = json.loads(DEVICES_FILE.read_text(encoding='utf-8'))
                for device_id, device_data in data.items():
                    self.devices[device_id] = Device.from_dict(device_data)
                print(f"✅ 加载 {len(self.devices)} 个设备")
            except Exception as e:
                print(f"⚠️ 加载设备数据失败：{e}")
                self.devices = {}
    
    def save(self):
        """保存设备数据"""
        DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {did: dev.to_dict() for did, dev in self.devices.items()}
        DEVICES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def generate_fingerprint(self, user_agent: str, ip: str, screen: str = "") -> str:
        """生成设备指纹"""
        # 组合多个特征生成唯一指纹
        data = f"{user_agent}|{ip}|{screen}|{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def register_device(self, user_agent: str, ip: str, name: str = "", screen: str = "") -> Device:
        """注册新设备"""
        # 检查是否已存在相同指纹的设备
        fingerprint = self.generate_fingerprint(user_agent, ip, screen)
        
        for device in self.devices.values():
            if device.fingerprint == fingerprint:
                # 已存在，更新最后访问时间
                device.last_access = datetime.now().isoformat()
                device.access_count += 1
                self.save()
                return device
        
        # 新设备，创建记录
        device_id = f"dev_{secrets.token_hex(8)}"
        device = Device(
            id=device_id,
            name=name or f"未知设备-{device_id[:8]}",
            fingerprint=fingerprint,
            ip_address=ip,
            user_agent=user_agent,
            status="pending",  # 需要审批
            created_at=datetime.now().isoformat(),
            last_access=datetime.now().isoformat(),
            access_count=1,
            created_by=ip
        )
        
        self.devices[device_id] = device
        self.save()
        
        print(f"📱 新设备注册：{device.name} ({device_id})")
        return device
    
    def approve_device(self, device_id: str, approver: str) -> bool:
        """审批设备"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        device.status = "approved"
        device.approved_by = approver
        device.approved_at = datetime.now().isoformat()
        
        self.save()
        print(f"✅ 设备已审批：{device.name}")
        return True
    
    def revoke_device(self, device_id: str, reason: str = "") -> bool:
        """撤销设备"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        device.status = "revoked"
        device.notes = f"撤销原因：{reason}"
        
        self.save()
        print(f"❌ 设备已撤销：{device.name}")
        return True
    
    def verify_device(self, device_id: str, user_agent: str, ip: str) -> bool:
        """验证设备访问权限"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        
        # 检查设备状态
        if device.status == "revoked":
            print(f"⚠️ 设备已撤销：{device.name}")
            return False
        
        if device.status == "pending":
            print(f"⚠️ 设备待审批：{device.name}")
            return False
        
        # 验证指纹（宽松模式，允许 IP 变化）
        current_fingerprint = self.generate_fingerprint(user_agent, ip)
        if device.fingerprint[:16] != current_fingerprint[:16]:
            # 指纹不匹配，可能是不同设备
            print(f"⚠️ 设备指纹不匹配：{device.name}")
            return False
        
        # 更新访问记录
        device.last_access = datetime.now().isoformat()
        device.access_count += 1
        self.save()
        
        return True
    
    def get_pending_devices(self) -> List[Device]:
        """获取待审批设备"""
        return [d for d in self.devices.values() if d.status == "pending"]
    
    def get_approved_devices(self) -> List[Device]:
        """获取已审批设备"""
        return [d for d in self.devices.values() if d.status == "approved"]
    
    def get_device_stats(self) -> Dict:
        """获取设备统计"""
        return {
            "total": len(self.devices),
            "pending": len(self.get_pending_devices()),
            "approved": len(self.get_approved_devices()),
            "revoked": len([d for d in self.devices.values() if d.status == "revoked"]),
        }
    
    def generate_device_token(self, device_id: str) -> Optional[str]:
        """生成设备访问令牌"""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        if device.status != "approved":
            return None
        
        # 生成令牌（包含设备 ID 和过期时间）
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        token_data = f"{device_id}|{device.fingerprint}|{expires}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token
    
    def verify_token(self, token: str) -> Optional[Device]:
        """验证访问令牌"""
        for device in self.devices.values():
            if device.status != "approved":
                continue
            
            expected_token = self.generate_device_token(device.id)
            if expected_token == token:
                return device
        
        return None


# ============ API 路由辅助 ============

def get_device_from_request(request) -> Optional[Device]:
    """从请求中获取设备信息"""
    # 获取设备 ID（从 header 或 cookie）
    device_id = request.headers.get("X-Device-ID")
    
    if not device_id:
        return None
    
    user_agent = request.headers.get("User-Agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    manager = DeviceManager()
    
    # 验证设备
    if manager.verify_device(device_id, user_agent, client_ip):
        return manager.devices[device_id]
    
    return None


# ============ 命令行接口 ============

if __name__ == "__main__":
    import sys
    
    manager = DeviceManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python device_auth.py list          # 列出所有设备")
        print("  python device_auth.py pending       # 待审批设备")
        print("  python device_auth.py approve <id>  # 审批设备")
        print("  python device_auth.py revoke <id>   # 撤销设备")
        print("  python device_auth.py stats         # 统计信息")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        print("📱 设备列表:")
        print("=" * 80)
        for device in manager.devices.values():
            status_icon = "✅" if device.status == "approved" else "⏳" if device.status == "pending" else "❌"
            print(f"{status_icon} {device.id}: {device.name}")
            print(f"   状态：{device.status} | IP: {device.ip_address} | 访问：{device.access_count}次")
            print(f"   最后访问：{device.last_access}")
            print()
    
    elif cmd == "pending":
        pending = manager.get_pending_devices()
        if not pending:
            print("✅ 无待审批设备")
        else:
            print("⏳ 待审批设备:")
            for device in pending:
                print(f"  {device.id}: {device.name}")
                print(f"     IP: {device.ip_address}")
                print(f"     UA: {device.user_agent[:100]}...")
    
    elif cmd == "approve":
        if len(sys.argv) < 3:
            print("用法：python device_auth.py approve <device_id>")
            sys.exit(1)
        device_id = sys.argv[2]
        if manager.approve_device(device_id, "admin"):
            print("✅ 设备已审批")
        else:
            print("❌ 设备不存在")
    
    elif cmd == "revoke":
        if len(sys.argv) < 3:
            print("用法：python device_auth.py revoke <device_id> [reason]")
            sys.exit(1)
        device_id = sys.argv[2]
        reason = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "未知原因"
        if manager.revoke_device(device_id, reason):
            print("✅ 设备已撤销")
        else:
            print("❌ 设备不存在")
    
    elif cmd == "stats":
        stats = manager.get_device_stats()
        print("📊 设备统计:")
        print(f"  总计：{stats['total']}")
        print(f"  待审批：{stats['pending']}")
        print(f"  已审批：{stats['approved']}")
        print(f"  已撤销：{stats['revoked']}")
