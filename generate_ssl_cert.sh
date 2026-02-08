#!/bin/bash
# 生成自签名SSL证书脚本

# 创建SSL目录
mkdir -p ssl

# 生成私钥
openssl genrsa -out ssl/key.pem 2048

# 生成证书签名请求
openssl req -new -key ssl/key.pem -out ssl/csr.pem -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"

# 生成自签名证书
openssl x509 -req -days 365 -in ssl/csr.pem -signkey ssl/key.pem -out ssl/cert.pem

# 设置适当权限
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "SSL证书已生成在ssl/目录中"
echo "注意：自签名证书会在浏览器中显示安全警告，在生产环境中请使用正式的CA签发证书"