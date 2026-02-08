#!/bin/bash
# PII Shield 停止脚本

echo "🛑 开始停止 Alta-Lex PII Shield 服务..."

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录执行此脚本"
    exit 1
fi

echo "⏹️  停止所有服务..."
sudo docker compose --profile gpu down

echo "🧹 清理未使用的资源..."
sudo docker system prune -f

echo "📊 当前运行的容器:"
sudo docker compose ps

echo "✅ 服务已停止"
echo "🔧 如需重新启动，请运行: ./start.sh"