#!/bin/bash
# PII Shield 启动脚本
# 自动构建镜像并启动所有服务（包含GPU模式）

set -e  # 遇到错误时退出

echo "🚀 开始启动 Alta-Lex PII Shield 服务..."

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录执行此脚本"
    exit 1
fi

echo "🧹 清理旧的构建缓存..."
sudo docker builder prune -f

echo "🏗️  构建自定义服务镜像..."
sudo docker-compose build --no-cache backend frontend nginx

echo "📦 启动所有服务（包含GPU模式）..."
sudo docker-compose --profile gpu up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🔍 检查服务状态..."
sudo docker-compose ps

echo "📋 显示服务日志概览..."
sudo docker-compose logs --tail=10

echo "✅ 启动完成！"
echo "🌐 访问地址: https://47.236.69.6"
echo "🔧 管理命令:"
echo "   停止服务: ./stop.sh"
echo "   查看日志: sudo docker-compose logs"
echo "   服务状态: sudo docker-compose ps"