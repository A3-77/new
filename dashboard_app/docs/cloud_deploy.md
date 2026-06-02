# 上云部署说明

## 1. 快照与云部署的区别

当前页面截图已保存为：

```text
C:\Users\A377\Desktop\new\dashboard_app\dashboard_snapshot.png
```

截图适合汇报留档，但不能交互。要在云端继续使用上传 Excel、切换 Sheet、筛选、导出等能力，需要部署 Streamlit 应用。

## 2. 推荐方式：Docker 部署

项目根目录已经提供 `Dockerfile`。构建时会复制：

- `dashboard_app/` 看板代码
- 根目录下的 Excel 数据源

在项目根目录运行：

```powershell
cd C:\Users\A377\Desktop\new
docker build -t liaoning-franchise-dashboard .
docker run -p 8501:8501 liaoning-franchise-dashboard
```

云服务器安全组放行端口后访问：

```text
http://服务器IP:8501
```

生产环境建议通过 Nginx/HTTPS 反向代理到容器的 `8501` 端口。

## 3. Streamlit Community Cloud

适合轻量共享：

1. 将 `dashboard_app`、根目录 Excel、`requirements.txt` 相关文件提交到 GitHub。
2. Streamlit Cloud 选择仓库。
3. Main file path 填：

```text
dashboard_app/app.py
```

4. 部署后即可访问云端 URL。

注意：如果 Excel 不提交到仓库，页面首次打开会提示缺少默认数据源，但仍可通过侧边栏上传 Excel 使用。

## 4. Railway / Render / Heroku 类平台

项目根目录已提供 `Procfile`：

```text
web: cd dashboard_app && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

部署步骤：

1. 上传项目根目录。
2. 安装命令：`pip install -r dashboard_app/requirements.txt`
3. 启动命令使用平台自动识别的 `Procfile`，或手动填入同一条命令。

## 5. 数据源放置规则

云端默认会按以下顺序查找 Excel：

1. `dashboard_app/辽宁区域_加盟商贡献表_202604（测试）.xlsx`
2. 项目根目录的 `辽宁区域_加盟商贡献表_202604（测试）.xlsx`

如果都不存在，用户仍可在侧边栏上传同结构 Excel。

