# sing-box Base64 订阅发布器

从本机 sing-box 分片配置中提取 VLESS 和 Hysteria2 节点，生成供 v2rayN、Shadowrocket 使用的 Base64 订阅，并发布到 CloudCone 的现有 HTTPS Nginx 服务。

## 输出范围

- 读取 `/root/application/toumingdaili/sing-box/config`。
- 导出 VLESS 和 Hysteria2 出站。
- 排除占位节点 `empty-for-hold-reality`。
- 节点数量自动计算，允许日后直接添加或删除节点。
- 至少必须存在 1 个节点，并检查节点名称不重复。
- Hysteria2 端口范围同时输出主端口与 `mport` 参数。

## 配置

部署配置保存在未纳入 Git 的 `deploy.env`：

```bash
cp deploy.env.example deploy.env
chmod 600 deploy.env
```

`SUBSCRIPTION_FILENAME` 必须使用不可预测的随机值：

```bash
printf 'all-%s.txt\n' "$(openssl rand -hex 24)"
```

## 发布

```bash
./publish.sh
```

脚本会依次：

1. 运行单元测试；
2. 通过 `sudo sing-box merge` 合并本地配置；
3. 生成 Base64 订阅并自动验证节点数量、格式和名称唯一性；
4. 通过 SSH 上传到 `72.18.82.91:/var/www/sing-box-subscribe/`；
5. 为远程 Nginx 安装受管理的精确路径配置；
6. 执行 `nginx -t`、reload；
7. 分别直连源站和通过 Cloudflare 公网地址验证，并确保内容与本地生成结果完全一致。

远程 Nginx 的现有 sing-box 订阅路径不会被修改。

## 安全说明

订阅内容包含节点凭据。不要提交 `deploy.env`、生成结果或解码后的节点链接。若订阅 URL 泄漏，请更换 `SUBSCRIPTION_FILENAME` 后重新发布。
