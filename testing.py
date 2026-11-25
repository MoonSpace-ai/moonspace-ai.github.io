"""Render public product-testing opportunities from repository data."""
from datetime import date
from html import escape
import json

from learn import https_url


STATUSES = {
    'recruiting': ('招募中', 'registration_url', '报名体验', '报名入口待开放'),
    'feedback': ('收集反馈', 'feedback_url', '提交反馈', '反馈入口待开放'),
    'closed': ('已结束', 'recap_url', '查看活动回顾', ''),
}


def activity_card(activity, tags, external):
    status = activity['status']
    label, url_field, action_label, pending_label = STATUSES[status]
    details = []
    for key, name in (
        ('audience', '招募对象'),
        ('effort', '预计用时'),
        ('feedback_focus', '希望收到的反馈'),
    ):
        if activity.get(key):
            details.append(f'<div><dt>{name}</dt><dd>{escape(activity[key])}</dd></div>')

    deadline = activity.get('registration_deadline')
    if status == 'recruiting' and deadline:
        deadline = date.fromisoformat(deadline).isoformat()
        details.append(f'<div><dt>报名截止</dt><dd><time datetime="{deadline}">{deadline}</time>（北京时间）</dd></div>')

    url = https_url(activity.get(url_field))
    action = ''
    if url:
        action = external(url, action_label, 'button secondary' if status == 'closed' else 'button')
    elif pending_label:
        action = f'<p class="testing-pending">{pending_label}</p>'
    facts = '<dl class="testing-facts">' + ''.join(details) + '</dl>' if details else ''
    tag_labels = ''.join(f'<li>{escape(tag)}</li>' for tag in tags)
    product_types = f'<ul class="testing-tags" aria-label="产品类型">{tag_labels}</ul>' if tags else ''
    tag_data = escape(json.dumps(tags, ensure_ascii=False), quote=True)
    return f'''<article class="testing-card" data-testing-tags="{tag_data}">
  <span class="testing-status testing-status-{status}">{label}</span>
  <h3>{escape(activity['title'])}</h3>
  <p>{escape(activity['summary'])}</p>
  {product_types}
  {facts}
  {action}
</article>'''


def render_testing(root, page, external):
    activities = json.loads((root / 'testing.json').read_text())
    if not isinstance(activities, list):
        raise ValueError('testing.json must contain an activity list.')

    groups = {status: [] for status in STATUSES}
    all_tags = {}
    for activity in activities:
        status = activity.get('status')
        if status not in groups:
            raise ValueError(f'Unknown testing activity status: {status!r}')
        raw_tags = activity.get('tags', [])
        if not isinstance(raw_tags, list) or any(not isinstance(tag, str) or not tag.strip() for tag in raw_tags):
            raise ValueError(f'Testing activity {activity["title"]!r} must use a list of nonempty tag names.')
        tags = list(dict.fromkeys(tag.strip() for tag in raw_tags))
        all_tags.update(dict.fromkeys(tags))
        groups[status].append(activity_card(activity, tags, external))

    filters = ''
    if all_tags:
        tag_buttons = ''.join(
            f'<button type="button" data-testing-filter="{escape(tag, quote=True)}" aria-pressed="false">{escape(tag)}</button>'
            for tag in all_tags
        )
        filters = (
            '<div class="testing-filters" role="group" aria-label="按产品类型筛选" hidden>'
            '<button type="button" data-testing-filter="" aria-pressed="true">全部</button>'
            f'{tag_buttons}</div><p class="sr-only" id="testing-filter-status" role="status"></p>'
        )

    current = groups['recruiting'] + groups['feedback']
    current_content = (
        '<div class="testing-grid">' + ''.join(current) + '</div>'
        '<p class="testing-empty" id="testing-no-matches" hidden>该类型暂无开放的体验活动。</p>'
        if current else
        '<p class="testing-empty">当前暂无开放的产品体验活动。新的招募会在这里发布。</p>'
    )
    archive = (
        '<section class="testing-list" id="testing-archive"><h2>往期活动</h2><div class="testing-grid">'
        + ''.join(groups['closed']) + '</div></section>'
        if groups['closed'] else ''
    )
    description = '参与 MoonSpace 的产品体验活动，试用真实产品，把遇到的问题和建议反馈给团队。'
    body = f'''<div class="container testing">
<section class="testing-hero">
  <h1>产品体验招募</h1>
  <p>{description}</p>
</section>
{filters}
<section class="testing-list" id="testing-current">
  <h2>当前活动</h2>
  {current_content}
</section>
{archive}
</div>'''
    page('/testing/', '产品体验招募', description, body,
         extra_head='<link rel="stylesheet" href="/testing/testing.css">'
                    '<script defer src="/testing/testing.js"></script>')
