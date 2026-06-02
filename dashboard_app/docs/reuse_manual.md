# 后续复用操作手册

## 1. 替换 Excel 数据源

方式一：界面上传

1. 启动看板。
2. 在侧边栏点击“替换 Excel 数据源”。
3. 上传同结构的新 Excel。
4. 页面、KPI、图表、明细表自动刷新。

方式二：替换默认文件

1. 关闭 Streamlit 服务。
2. 将新的 Excel 文件放到项目根目录。
3. 如果文件名保持 `辽宁区域_加盟商贡献表_202604（测试）.xlsx`，无需修改任何代码。
4. 重新运行 `streamlit run app.py`。

如果希望更换默认文件名，只需要修改 `analysis_config.py` 中的 `DEFAULT_EXCEL_NAME`。

## 2. 新增页面

新增同类 Sheet 时：

1. 在 Excel 中新增 Sheet。
2. 保持表头语义清晰，例如包含加盟商、网点、月份、区域、费用、贡献等字段。
3. 上传或替换 Excel。
4. 看板自动生成同名页面。

如果要让新增页面进入固定优先级导航，可在 `analysis_config.py` 的 `PAGE_PRIORITY` 中追加 Sheet 名称。

## 3. 新增维度

如新增“管理片区”“直营网格”等维度：

1. 打开 `analysis_config.py`。
2. 在 `DIMENSION_KEYWORDS` 中新增维度名称和关键词。
3. 重启 Streamlit。

示例：

```python
"管理片区": ["管理片区", "片区", "直营网格"]
```

## 4. 新增 KPI 或调整优先级

打开 `analysis_config.py`，修改 `METRIC_PRIORITY` 的顺序即可。越靠前越优先显示为 KPI。

示例：

```python
METRIC_PRIORITY = [
    "贡献总额",
    "单票贡献",
    "单公斤贡献",
    "单量",
]
```

## 5. 新增页面专属模块

打开 `analysis_config.py`，在 `PAGE_MODULES` 中为 Sheet 配置模块名。

当前通用视图会根据可识别字段自动渲染：

- 排名分析
- 倒数分析
- 指标分布
- 经营结构
- 公斤段分析
- 状态分析
- 区域分析
- 异常预警
- 明细表

需要新增完全定制模块时，应在 `data_model.py` 增加模型函数，在 `app.py` 增加渲染函数，保持数据模型和视图展示分离。

## 6. 部署建议

本地运行：

```powershell
cd C:\Users\A377\Desktop\new\dashboard_app
streamlit run app.py
```

服务器部署：

1. 准备 Python 3.10+。
2. 安装依赖：`pip install -r requirements.txt`。
3. 将 Excel 和 `dashboard_app` 目录部署到同一业务目录。
4. 启动：`streamlit run app.py --server.port 8501 --server.address 0.0.0.0`。
5. 使用 Nginx 或内网网关做访问控制。

## 7. 运行限制说明

- Streamlit 原生表格支持排序、全屏、复制和下载；更复杂的列冻结、列宽拖拽、Excel 样式导出可后续接入 AgGrid。
- 当前异常阈值使用通用 P99 和零/负值规则；若公司有正式考核阈值，应将阈值配置化加入 `analysis_config.py`。
- 页面间遵循数据隔离，不跨 Sheet 补数。全局筛选只在当前 Sheet 存在同语义字段时生效。

