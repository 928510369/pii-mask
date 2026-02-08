# HTTPS 部署指南

## 概述
本文档介绍如何配置 Alta-Lex PII Shield 以使用 HTTPS 提供安全连接。

## 配置要求

### SSL 证书
您有两种选择：

1. **自签名证书**（仅用于测试）
2. **正式SSL证书**（生产环境推荐）

## 自签名证书设置（测试环境）

1. 生成SSL证书：
   ```bash
   chmod +x generate_ssl_cert.sh
   ./generate_ssl_cert.sh
   ```

2. 这将创建以下文件：
   - `ssl/cert.pem` - SSL证书
   - `ssl/key.pem` - 私钥

## 正式SSL证书设置（生产环境）

### 阿里云SSL证书配置

1. 登录阿里云控制台，访问SSL证书服务
2. 申请或购买SSL证书
3. 完成域名验证（DNS验证或文件验证）
4. 审核通过后，下载证书文件（选择Nginx格式）
5. 将下载的证书文件重命名并放入系统SSL目录：
   - 将 `[证书名称].pem` 重命名为 `cert.pem`
   - 将 `[证书名称].key` 重命名为 `key.pem`
   - 将证书文件复制到 `/etc/nginx/ssl/` 目录：
     - `/etc/nginx/ssl/cert.pem` - 证书文件
     - `/etc/nginx/ssl/key.pem` - 私钥文件
   
   在Linux系统上使用以下命令：
   ```bash
   # 创建目录（如果不存在）
   sudo mkdir -p /etc/nginx/ssl
   
   # 复制证书文件（替换为实际的证书文件名）
   sudo cp [证书名称].pem /etc/nginx/ssl/cert.pem
   sudo cp [证书名称].key /etc/nginx/ssl/key.pem
   
   # 设置适当的权限
   sudo chmod 600 /etc/nginx/ssl/key.pem
   sudo chmod 644 /etc/nginx/ssl/cert.pem
   ```

## 部署服务

### 使用Docker Compose部署
```bash
# 构建并启动服务
docker-compose up -d

# 或启用GPU模式
docker-compose --profile gpu up -d
```

### 证书更新

当SSL证书即将到期时，使用以下脚本更新证书：

```bash
# 给脚本添加执行权限
chmod +x update_ssl_cert.sh

# 更新证书（将新的证书文件放在项目根目录）
./update_ssl_cert.sh new_cert.pem new_key.key
```

### 证书配置检查

使用以下脚本检查SSL配置状态：

```bash
# 给脚本添加执行权限
chmod +x check_ssl_config.sh

# 检查SSL配置（可能需要sudo权限）
sudo ./check_ssl_config.sh
```

### 服务端口
- HTTPS: `:443`

## 安全配置说明

### Nginx 配置
- 强制HTTP重定向到HTTPS
- 支持TLS 1.2和1.3
- 使用强加密套件
- 设置请求体大小限制（10MB）

### CORS 配置
- 仅允许HTTPS来源
- 允许本地开发环境（localhost和127.0.0.1）

## 生产环境注意事项

1. **使用正式SSL证书** - 避免浏览器安全警告
2. **定期更新证书** - 确保证书不过期
3. **备份私钥** - 确保私钥安全存储
4. **监控SSL配置** - 使用SSL测试工具验证配置
5. **设置HSTS** - 考虑添加HTTP Strict Transport Security头

## 故障排除

### 证书问题
- 检查证书路径是否正确映射到容器
- 验证证书和私钥是否匹配
- 确认证书格式正确

### 连接问题
- 确保防火墙允许443端口
- 检查证书是否过期
- 验证Nginx配置语法

### Docker权限
- 确保Docker服务正在运行
- 检查用户是否在docker组中