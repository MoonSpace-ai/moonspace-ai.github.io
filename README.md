# MoonSpace 官网

公开网址：https://moonspace-ai.github.io/

## 更新内容

修改 content.json 与 build.py，在仓库根目录执行：

```sh
python3 build.py
python3 check.py
```

将源码与 docs/ 产物一起提交至 main。GitHub Pages 使用 main 分支的 /docs 目录。

网页为完整静态内容，无需后端。包含合作案例、成员与作品、社区知识和联系入口。

标志使用 MoonSpace 原有图案的透明底版本；标题字体许可见 docs/assets/FONT-LICENSE.txt。

## 项目共学社区

`/learn/` 的期次、任务、示例课程、小测和作品都在 `learn.json`。待确定的日期和飞书链接用 `null`，日期使用 `YYYY-MM-DD`（报名截止当天以北京时间为准）。配置前请从外部身份试开报名和提交表。精选作品仅渲染 `approved: true` 且有 HTTPS 作答链接的条目，移除该条可下架。更新后照常运行 `python3 build.py` 和 `python3 check.py`，提交源码及 `docs/` 产物。
