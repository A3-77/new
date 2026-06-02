# Cloudflare 打开与上云方式

## 1. 以后本地怎么打开

最简单方式：双击项目根目录的：

```text
start_dashboard.bat
```

启动后浏览器打开：

```text
http://127.0.0.1:8501
```

如果脚本没有自动打开浏览器，手动复制这个地址即可。

## 2. 能不能直接上传到 Cloudflare Pages

不建议直接上传 Cloudflare Pages。

原因是这个看板是 Streamlit 应用，需要 Python 后端进程持续运行；Cloudflare Pages 更适合静态站点、前端应用或构建产物。它可以保存页面截图或静态 HTML，但不能完整承载 Streamlit 的上传 Excel、筛选、切换 Sheet、导出 CSV 等交互能力。

## 3. 推荐方案：Cloudflare Tunnel

Cloudflare Tunnel 可以把本地或云服务器上的 Streamlit 服务暴露成 HTTPS 地址。

本地先启动看板：

```powershell
.\start_dashboard.bat
```

然后安装并登录 `cloudflared` 后运行：

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

它会生成一个临时的 `trycloudflare.com` 地址，别人可以通过这个地址访问你的看板。

## 4. 正式域名方案

如果你有自己的域名，并且域名已经托管在 Cloudflare：

1. 在 Cloudflare Zero Trust 创建 Tunnel。
2. 安装 `cloudflared` 到运行看板的电脑或云服务器。
3. Public hostname 填你的域名，例如：

```text
dashboard.yourdomain.com
```

4. Service 填：

```text
http://127.0.0.1:8501
```

5. 启动 Tunnel 后，通过 `https://dashboard.yourdomain.com` 访问。

## 5. 更稳定的生产部署

如果要长期给团队用，建议：

- 用一台云服务器运行 Docker 版看板。
- 用 Cloudflare Tunnel 或 Cloudflare DNS + HTTPS 代理到这台服务器。
- 给看板加访问控制，避免 Excel 财务数据公开暴露。

