# 环境配置说明

## 1. 创建 .env 文件

在 `agent/src/demo/` 目录下创建 `.env` 文件，内容如下：

```env
# OpenAI API 配置
OPENAI_API_KEY=your-openai-api-key-here

# 代理配置（可选，如果需要通过代理访问）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# Opik 配置（可选）
OPIK_API_KEY=your-opik-api-key-here
OPIK_WORKSPACE=your-workspace-name
```

## 2. 获取 OpenAI API 密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. 登录你的账户
3. 点击 "Create new secret key"
4. 复制生成的密钥
5. 将密钥粘贴到 `.env` 文件的 `OPENAI_API_KEY` 字段

## 3. 代理配置（可选）

如果你在中国大陆或其他需要代理的地区：

1. 确保你有可用的代理服务器
2. 将代理地址填入 `HTTP_PROXY` 和 `HTTPS_PROXY`
3. 常见的代理地址格式：
   - `http://127.0.0.1:7890` (Clash)
   - `http://127.0.0.1:1080` (Shadowsocks)
   - `http://127.0.0.1:8080` (其他代理)

## 4. 运行测试

配置完成后，运行：

```bash
python test_evaluation.py
```

## 5. 常见问题

### API 密钥错误
- 确保 API 密钥正确且有效
- 检查账户余额是否充足

### 代理连接失败
- 确认代理服务器正在运行
- 检查代理地址和端口是否正确
- 尝试在浏览器中测试代理是否工作

### 网络超时
- 增加 `timeout` 参数值
- 检查网络连接
- 考虑使用更稳定的代理 