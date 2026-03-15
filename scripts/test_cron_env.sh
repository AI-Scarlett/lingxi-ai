#!/bin/bash
# 测试 cron 环境下的 PATH
echo "=== Cron 环境测试 ===" > /tmp/cron_env_test.log
echo "PATH: $PATH" >> /tmp/cron_env_test.log
echo "which node: $(which node 2>&1)" >> /tmp/cron_env_test.log
echo "which openclaw: $(which openclaw 2>&1)" >> /tmp/cron_env_test.log
echo "openclaw version: $(/root/.local/share/pnpm/openclaw --version 2>&1)" >> /tmp/cron_env_test.log
echo "测试时间: $(date)" >> /tmp/cron_env_test.log
