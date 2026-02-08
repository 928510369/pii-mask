#!/bin/bash
# 阿里云SSL证书更新脚本

SYSTEM_SSL_DIR="/etc/nginx/ssl"
PROJECT_SSL_DIR="./ssl"

echo "开始更新阿里云SSL证书..."

# 检查是否提供了证书文件路径参数
if [ $# -ne 2 ]; then
    echo "使用方法: $0 <cert_file> <key_file>"
    echo "示例: $0 aliyun_cert.pem aliyun_key.key"
    exit 1
fi

CERT_FILE=$1
KEY_FILE=$2

# 检查证书文件是否存在
if [ ! -f "$CERT_FILE" ]; then
    echo "错误: 证书文件 $CERT_FILE 不存在"
    exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
    echo "错误: 私钥文件 $KEY_FILE 不存在"
    exit 1
fi

# 检查是否具有sudo权限
if [ ! -w "$SYSTEM_SSL_DIR" ]; then
    echo "需要sudo权限来更新系统SSL目录中的证书"
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# 备份现有证书
if [ -f "$SYSTEM_SSL_DIR/cert.pem" ] && [ -f "$SYSTEM_SSL_DIR/key.pem" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "备份现有证书..."
    $SUDO_CMD cp "$SYSTEM_SSL_DIR/cert.pem" "$SYSTEM_SSL_DIR/cert.pem.backup_$TIMESTAMP"
    $SUDO_CMD cp "$SYSTEM_SSL_DIR/key.pem" "$SYSTEM_SSL_DIR/key.pem.backup_$TIMESTAMP"
    echo "已备份到 $SYSTEM_SSL_DIR 目录中"
fi

# 复制新证书到系统目录
echo "更新系统SSL目录中的证书文件..."
$SUDO_CMD mkdir -p "$SYSTEM_SSL_DIR"
$SUDO_CMD cp "$CERT_FILE" "$SYSTEM_SSL_DIR/cert.pem"
$SUDO_CMD cp "$KEY_FILE" "$SYSTEM_SSL_DIR/key.pem"

# 设置适当的权限
$SUDO_CMD chmod 600 "$SYSTEM_SSL_DIR/key.pem"
$SUDO_CMD chmod 644 "$SYSTEM_SSL_DIR/cert.pem"

# 同时更新项目目录中的副本（如果需要）
if [ -d "$PROJECT_SSL_DIR" ]; then
    echo "同步证书到项目目录..."
    cp "$CERT_FILE" "$PROJECT_SSL_DIR/cert.pem"
    cp "$KEY_FILE" "$PROJECT_SSL_DIR/key.pem"
    chmod 600 "$PROJECT_SSL_DIR/key.pem"
    chmod 644 "$PROJECT_SSL_DIR/cert.pem"
fi

echo "SSL证书已更新完成"
echo "证书信息:"
$SUDO_CMD openssl x509 -in "$SYSTEM_SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Not After|DNS:)" || echo "无法读取证书信息"

echo "重启Docker服务以应用新证书..."
docker-compose down
sleep 5
docker-compose up -d

echo "SSL证书更新完成！"
echo "请注意：证书更新后可能需要几分钟生效"