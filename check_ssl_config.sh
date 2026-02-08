#!/bin/bash
# SSL配置检查脚本

SYSTEM_SSL_DIR="/etc/nginx/ssl"
PROJECT_SSL_DIR="./ssl"

echo "=== SSL配置检查 ==="

# 检查系统目录中的证书文件是否存在
if [ -f "$SYSTEM_SSL_DIR/cert.pem" ] && [ -f "$SYSTEM_SSL_DIR/key.pem" ]; then
    echo "✓ SSL证书文件存在于系统目录 $SYSTEM_SSL_DIR"
    CERT_PATH="$SYSTEM_SSL_DIR"
elif [ -f "$PROJECT_SSL_DIR/cert.pem" ] && [ -f "$PROJECT_SSL_DIR/key.pem" ]; then
    echo "! SSL证书文件存在于项目目录 $PROJECT_SSL_DIR，建议移动到系统目录"
    CERT_PATH="$PROJECT_SSL_DIR"
else
    echo "✗ SSL证书文件缺失"
    echo "请确保以下文件存在于 $SYSTEM_SSL_DIR 目录："
    echo "  - cert.pem (证书文件)"
    echo "  - key.pem (私钥文件)"
    exit 1
fi

# 检查证书有效性
echo ""
echo "证书信息："
echo "----------"
sudo openssl x509 -in "$CERT_PATH/cert.pem" -text -noout | grep -E "(Subject:|Issuer:|Not After|DNS:)" | head -10

echo ""
# 检查证书过期时间
EXPIRY_DATE=$(sudo openssl x509 -in "$CERT_PATH/cert.pem" -noout -enddate | cut -d= -f2)
echo "证书过期时间: $EXPIRY_DATE"

# 检查是否即将过期（30天内）
DAYS_LEFT=$(($(date -d "$EXPIRY_DATE" +%s) - $(date +%s)))
DAYS_LEFT=$((DAYS_LEFT / 86400))

if [ $DAYS_LEFT -lt 0 ]; then
    echo "✗ 证书已过期！"
elif [ $DAYS_LEFT -lt 30 ]; then
    echo "! 证书将在 $DAYS_LEFT 天内过期，请及时更新！"
else
    echo "✓ 证书有效期还有 $DAYS_LEFT 天"
fi

echo ""
# 检查证书和私钥是否匹配
echo "检查证书和私钥匹配性..."
CERT_MODULUS=$(sudo openssl x509 -in "$CERT_PATH/cert.pem" -noout -modulus | sudo openssl md5)
KEY_MODULUS=$(sudo openssl rsa -in "$CERT_PATH/key.pem" -noout -modulus | sudo openssl md5)

if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
    echo "✓ 证书和私钥匹配"
else
    echo "✗ 证书和私钥不匹配！"
    exit 1
fi

echo ""
# 检查Docker服务状态
echo "检查Docker服务状态..."
if command -v docker &> /dev/null; then
    if docker ps | grep -q nginx; then
        echo "✓ Nginx容器正在运行"
    else
        echo "! Nginx容器未运行，需要启动服务"
    fi
else
    echo "! Docker未安装或未运行"
fi

echo ""
echo "=== SSL配置检查完成 ==="