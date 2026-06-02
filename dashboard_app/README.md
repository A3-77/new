# 辽宁区域加盟商运营看板

这是一个基于 `Python + Streamlit` 的可复用业务数据看板工程。默认读取项目根目录下的 `辽宁区域_加盟商贡献表_202604（测试）.xlsx`，也支持在侧边栏上传同结构 Excel 热替换数据源。

## 快速运行

```powershell
cd C:\Users\A377\Desktop\new\dashboard_app
python -m pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```

如本机没有 `python` 命令，请使用你自己的 Python 解释器路径运行。建议 Python 3.10+。

## 上云部署

已提供根目录 `Dockerfile` 和 `Procfile`。详细步骤见：

[cloud_deploy.md](docs/cloud_deploy.md)

Cloudflare 访问方式见：

[cloudflare.md](docs/cloudflare.md)

## 工程结构

```text
dashboard_app/
  app.py                 # 视图展示层：页面、图表、筛选、导出
  data_model.py          # 数据模型层：表头识别、清洗、指标、异常、质量校验
  analysis_config.py     # 业务语义配置：维度、指标、页面模块、行业关键词
  requirements.txt       # 运行依赖
  docs/
    architecture.md      # 架构设计
    page_layouts.md      # 全页面布局说明
    kpi_rules.md         # KPI 计算规则
    reuse_manual.md      # 后续复用手册
```

## 设计原则

- 每个有效 Sheet 自动生成一个页面，导航名称与 Sheet 名称完全一致。
- 每个页面只读取并分析当前 Sheet，不做跨 Sheet 混排。
- 数据源、数据模型、视图展示三层分离，替换同结构 Excel 后无需修改代码。
- 指标和维度基于物流快递加盟商运营通用关键词识别，新增同类 Sheet 可通过配置扩展。
