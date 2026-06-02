# Git 回滚工具说明

根目录新增了 `git_rollback.bat`，用于在改坏页面或线上部署异常时安全回滚。

## 使用方式

1. 双击根目录的 `git_rollback.bat`。
2. 脚本会显示最近 8 次提交。
3. 直接按回车会回滚最近一次提交。
4. 也可以输入指定 commit hash，例如 `1b77f00`。
5. 输入 `Y` 确认后，会执行 `git revert`。
6. 回滚成功后，可以选择是否立即推送到 GitHub。

## 为什么不用 reset

脚本使用的是 `git revert`，它会新增一个反向提交，不会删除历史记录。

这比 `git reset --hard` 更适合当前项目，因为 GitHub 和 Streamlit Cloud 都能清楚看到每一次修改和回滚记录。

## 注意事项

- 如果当前有未提交改动，脚本会停止，避免误覆盖。
- 如果回滚时出现冲突，需要手动处理冲突后再提交。
- 如果 GitHub 网络连接失败，可以稍后手动执行：

```bash
git push origin main
```
