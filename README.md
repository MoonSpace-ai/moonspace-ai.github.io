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

`/learn/` 的期次、任务、示例课程、小测和作品都在 `learn.json`。在 `cohort` 中填写以下配置。未确定时保留 `null`，页面会显示待开放或待公布。精选作品仅渲染 `approved: true` 且有 HTTPS 作答链接的条目，移除该条可下架。更新后照常运行 `python3 build.py` 和 `python3 check.py`，提交源码及 `docs/` 产物。


| 配置项 | 填写内容 |
| --- | --- |
| `registration_url` | 可外部填写的飞书报名表 HTTPS 链接 |
| `full` | 设为 `true` 显示「首期已满员」，并用候补入口替换报名入口。默认 `false` |
| `waitlist_url` | 可公开展示的飞书候补群 HTTPS 链接。满员时启用，留空显示「候补群入口待开放」 |
| `submission_url` | 可外部填写的飞书作品提交表 HTTPS 链接 |
| `group_url` | 可公开展示的飞书共学群 HTTPS 链接 |
| `starts_on` | 开营日期，格式为 `YYYY-MM-DD` |
| `registration_deadline` | 可选的报名截止日期，格式为 `YYYY-MM-DD`（北京时间） |

填入真实链接后，用外部身份核对表单权限和群入口，再按上面的流程重新生成并发布。
