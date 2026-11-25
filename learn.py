"""Render the project-learning pilot using the MoonSpace site template."""
from datetime import date
from html import escape as e
import json
from urllib.parse import urlsplit


def https_url(value):
    if value is None:
        return None
    url = urlsplit(value)
    if url.scheme != 'https' or not url.hostname or url.username or url.password:
        raise ValueError('Use a public HTTPS URL for each configured entry.')
    return value


def list_items(items):
    return ''.join(f'<li>{e(item)}</li>' for item in items)


def render_learn(root, page, button, external):
    data = json.loads((root / 'learn.json').read_text())
    cohort, task, quiz = (data[key] for key in ('cohort', 'task', 'quiz'))
    deadline = cohort['registration_deadline']
    if deadline:
        date.fromisoformat(deadline)
    starts = cohort['starts_on']
    start_display = (
        f'<time datetime="{date.fromisoformat(starts).isoformat()}">{e(starts)}</time>'
        if starts else '待公布'
    )

    register_url = https_url(cohort['registration_url'])
    submit_url = https_url(cohort['submission_url'])
    group_url = https_url(cohort['group_url'])
    register_status = (
        f'<p>报名截止日为 <time datetime="{deadline}">{deadline}</time>（北京时间）。</p>'
        if deadline else '<p>报名截止日期待公布。</p>'
    )
    register_action = (
        external(register_url, '打开飞书报名表', 'button')
        if register_url else '<strong>报名表待开放</strong>'
    )
    if register_url and deadline:
        register_action = (
            f'<div data-registration-deadline="{deadline}"><span>{register_action}</span>'
            '<strong hidden>报名已截止</strong></div>'
        )
    banner_link = (
        external(register_url, '打开飞书报名表', 'learn-banner-link')
        if register_url else '<a class="learn-banner-link" href="#register">查看报名安排</a>'
    )
    banner_title = '首期报名已开放' if register_url else '首期报名即将开启'
    banner_content = f'<strong>{banner_title}</strong>{banner_link}'
    if register_url and deadline:
        banner_content = (
            f'<div class="learn-banner-content" data-registration-deadline="{deadline}">'
            f'<span>{banner_content}</span><strong hidden>首期报名已截止</strong></div>'
        )
    submit_action = (
        external(submit_url, '打开飞书作品提交表', 'button')
        if submit_url else '<strong>提交表待开放</strong>'
    )
    group_action = (
        external(group_url, '打开飞书共学群', 'button secondary')
        if group_url else '<strong>群入口待开放</strong>'
    )
    heading = e(task['title'])
    course = e(quiz['course'])
    topic = e(quiz['topic'])
    quiz_title = e(quiz['title'])
    steps = ''.join(
        f'<li><span>{e(day)}</span><div><h3>{e(title)}</h3><p>{e(body)}</p></div></li>'
        for day, title, body in task['steps']
    )
    resources = ''.join(
        f'<h3>{e(label)}</h3><p>{e(body)}</p>' for label, body in task['resources']
    )
    works = ''.join(
        f'<article class="learn-panel"><h3>{e(work["title"])}</h3>'
        f'<p>{e(work["author"])} · {e(work["description"])}</p>'
        f'{external(https_url(work["url"]), "打开试做", "text-link")}</article>'
        for work in data['works'] if work['approved'] is True and work['url']
    )
    if not works:
        works = ('<div class="learn-empty"><h3>首期作品将在这里展出</h3>'
                 '<p>目前还没有获得作者公开授权的作品。你可以先试做官方示例。</p>'
                 f'{button("/learn/quiz/", "试做示例", True)}</div>')

    body = f'''<div class="container learn">
<aside class="learn-banner" aria-label="首期报名通知">{banner_content}</aside>
<nav class="learn-nav" aria-label="共学导航">
  <a href="#task">当期任务</a><a href="/learn/quiz/">小测示例</a>
  <a href="#showcase">精选作品</a><a href="#register">报名与入群</a><a href="#submit">提交作品</a>
</nav>
<section class="learn-hero">
  <div class="learn-intro">
    <p class="section-label">MoonSpace 项目共学社区 · {e(cohort['name'])}</p>
    <h1>{heading}</h1>
    <p class="learn-lede">{e(cohort['audience'])}{e(task['summary'])}</p>
    <div class="actions">{button('#register', '选这项任务')}{button('#task', '查看任务卡', True)}</div>
  </div>
  <a class="learn-preview" href="/learn/quiz/">
    <div class="learn-preview-top"><span>成品示例</span><span>{len(quiz['questions'])} 道单选题</span></div>
    <span class="learn-preview-course">{course} · {topic}</span>
    <strong>哪个数更能代表典型水平？</strong>
    <span class="learn-numbers" aria-hidden="true"><i>2</i><i>3</i><i>4</i><i>5</i><i>100</i></span>
    <span class="learn-preview-cta">试做 5 题小测</span>
  </a>
</section>
<dl class="learn-facts">
  <div><dt>共学周期</dt><dd>{e(cohort['duration'])}</dd></div>
  <div><dt>首期名额</dt><dd>{e(cohort['capacity'])}</dd></div>
  <div><dt>预计总投入</dt><dd>{e(cohort['effort'])}</dd></div>
  <div><dt>开营日期</dt><dd>{start_display}</dd></div>
</dl>
<section id="task" class="learn-section">
  <h2>首期任务卡</h2>
  <div class="learn-columns">
    <div>
      <ol class="learn-steps">{steps}</ol>
      <div class="learn-panel learn-prompt">
        <h3>第一题提示词</h3><p id="learn-prompt">{e(task['prompt'])}</p>
        <button type="button" class="button secondary" id="learn-copy-button">复制提示词</button>
        <span id="learn-copy" role="status"></span>
      </div>
    </div>
    <aside class="learn-panel learn-standard">
      <h3>怎样算完成</h3><ul>{list_items(task['criteria'])}</ul>
      <p>预计用时：出题和校对约 40 分钟，搭建约 50 分钟，试用、修改和提交约 30–60 分钟。</p>
      {button('/learn/quiz/', '查看成品示例', True)}
    </aside>
  </div>
  <details class="learn-panel learn-help"><summary>工具与群内求助</summary>{resources}<p><a class="text-link" href="/learn/quiz/template.html" download="moonspace-quiz.html">下载单文件小测模板</a>。下载后可在浏览器离线试做，修改题目、答案和解析后可发布为自己的作答链接。</p><a class="text-link" href="#group">查看共学群入口</a></details>
</section>
<section class="learn-section learn-entry" aria-label="报名、入群与作品提交">
  <article class="learn-panel" id="register"><h2>报名首期</h2>{register_status}
    <p>录取后会收到报名编号和共学群入口。现在就可以阅读任务卡、试做示例。</p>{register_action}
  </article>
  <article class="learn-panel" id="group"><h2>加入共学群</h2>
    <p>入营后在群里发「课程＋章节」开工，遇到卡点也可以在群里求助。</p>{group_action}
  </article>
  <article class="learn-panel" id="submit"><h2>提交作品</h2>
    <p>准备好报名编号、作答链接、题数、核查说明和同学试做记录。补交时使用原报名编号。</p>{submit_action}
  </article>
</section>
<section id="showcase" class="learn-section">
  <h2>精选作品</h2>{works}
</section>
</div>'''
    assets = '<link rel="stylesheet" href="/learn/learn.css"><script defer src="/learn/learn.js"></script>'
    page('/learn/', '项目共学社区', task['summary'], body, extra_head=assets)

    quiz_questions = []
    for number, item in enumerate(quiz['questions'], 1):
        options = ''.join(
            f'<label><input type="radio" name="q{number}" value="{index}" required>'
            f'<span>{e(option)}</span></label>'
            for index, option in enumerate(item['options'])
        )
        answer = item['answer']
        quiz_questions.append(
            f'<fieldset data-answer="{answer}"><legend>{number}. {e(item["question"])}</legend>'
            f'<div class="learn-options">{options}</div><div class="learn-explanation" hidden>'
            f'<strong></strong><p>正确答案：{e(item["options"][answer])}</p>'
            f'<p>{e(item["explanation"])}</p></div></fieldset>'
        )
    quiz_body = f'''<div class="container learn learn-quiz">
<nav class="learn-nav" aria-label="共学导航"><a href="/learn/">共学首页</a><a href="/learn/#task">当期任务</a></nav>
<header class="learn-quiz-head">
  <p class="section-label">首期成品示例 · {course}</p>
  <h1>{quiz_title}</h1>
  <p>每题选一个答案。交卷后会显示分数、正确答案和解析。答题记录只保留在当前页面。</p>
</header>
<noscript><p>请启用 JavaScript 后作答并查看解析。</p></noscript>
<form id="learn-quiz">
  <p id="learn-result" class="learn-result" tabindex="-1" role="status" hidden></p>
  {''.join(quiz_questions)}
  <div class="learn-quiz-actions" hidden><p id="learn-progress">已答 0 / {len(quiz_questions)} 题</p>
    <button class="button" type="submit">交卷并查看解析</button>
    <button class="button secondary" type="reset" hidden>再做一次</button>
  </div>
</form>
</div>'''
    page('/learn/quiz/', quiz['title'], '试做统计学期末五道单选题，交卷后查看分数和逐题解析。', quiz_body, extra_head=assets)

    # Reuse the quiz markup and behavior in an offline, editable HTML download.
    quiz_form = quiz_body[quiz_body.index('<noscript>'):quiz_body.index('</form>') + len('</form>')]
    style = (root / 'docs/learn/learn.css').read_text()
    script = (root / 'docs/learn/learn.js').read_text()
    template_url = 'https://moonspace-ai.github.io/learn/quiz/template.html'
    template_schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'LearningResource', 'url': template_url,
        'name': quiz['title'], 'inLanguage': 'zh-CN'
    }, ensure_ascii=False).replace('<', chr(92) + 'u003c')
    (root / 'docs/learn/quiz/template.html').write_text(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{quiz_title}</title><meta name="description" content="可离线试做和修改的 MoonSpace 小测模板。">
<link rel="canonical" href="{template_url}"><link rel="icon" href="/assets/moonspace-logo.png">
<script type="application/ld+json">{template_schema}</script>
<style>{style}
:root {{ --line: #dbe3d8; --paper: #f8f8f4; }}
* {{ box-sizing: border-box; }}
body {{ margin: 20px; font: 1rem/1.6 system-ui, sans-serif; color: #25352f; background: var(--paper); }}
.learn {{ margin: auto; }}
[hidden] {{ display: none !important; }}
.button {{ min-height: 44px; padding: 7px 18px; font: inherit; background: #173c35; color: white; border: 0; border-radius: 24px; cursor: pointer; }}
</style></head><body><main class="learn learn-quiz"><h1>{quiz_title}</h1>
<p>每题选一个答案，交卷后查看分数与解析。</p>
<!-- 修改每组 fieldset 的题干、选项和解析。data-answer 填正确选项的 value（0 到 3）。 -->
{quiz_form}
</main><script>{script}</script></body></html>''')
