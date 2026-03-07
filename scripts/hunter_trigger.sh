#!/bin/bash
# Hunter Daily Report Trigger
# 通过 sessions_spawn 触发报告生成

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

echo "[$DATE $TIME] 触发 Hunter 报告生成..."

# 使用 openclaw sessions_spawn 触发任务
# 这会创建一个子代理来执行 feishu_doc 工具

cat << EOF
🎯 Hunter 每日商机报告 - $DATE

请执行以下任务：
1. 创建飞书文档，标题："🚀 Hunter 每日商机报告 - $DATE"
2. 填入报告内容（海外市场 + 国内市场机会）
3. 发送飞书消息给 ou_4192609eb71f18ae82f9163f02bef144，包含文档链接

报告内容模板：
- 海外：ContentRepurpose Pro ($19/mo), MeetingAction AI ($29/mo)
- 国内：公众号内容矩阵管家 (¥199/mo), 小红书爆款生成器 (¥99/mo)
- 推荐：公众号内容矩阵管家
EOF
