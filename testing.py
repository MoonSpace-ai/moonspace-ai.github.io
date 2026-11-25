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


def activity_card(activity, external):
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
    return f'''<article class="testing-card">
  <span class="testing-status testing-status-{status}">{label}</span>
  <h3>{escape(activity['title'])}</h3>
  <p>{escape(activity['summary'])}</p>
  {facts}
  {action}
</article>'''


def render_testing(root, page, external):
    activities = json.loads((root / 'testing.json').read_text())
    if not isinstance(activities, list):
        raise ValueError('testing.json must contain an activity list.')

    groups = {status: [] for status in STATUSES}
    for activity in activities:
        status = activity.get('status')
        if status not in groups:
            raise ValueError(f'Unknown testing activity status: {status!r}')
        groups[status].append(activity_card(activity, external))

    current = groups['recruiting'] + groups['feedback']
    current_content = (
        '<div class="testing-grid">' + ''.join(current) + '</div>' if current else
        '<p class="testing-empty">当前暂无开放的产品体验活动。新的招募会在这里发布。</p>'
    )
    archive = (
        '<section class="testing-list"><h2>往期活动</h2><div class="testing-grid">'
        + ''.join(groups['closed']) + '</div></section>'
        if groups['closed'] else ''
    )
    description = '参与 MoonSpace 的产品体验活动，试用真实产品，把遇到的问题和建议反馈给团队。'
    body = f'''<div class="container testing">
<section class="testing-hero">
  <h1>产品体验招募</h1>
  <p>{description}</p>
</section>
<section class="testing-list">
  <h2>当前活动</h2>
  {current_content}
</section>
{archive}
</div>'''
    page('/testing/', '产品体验招募', description, body,
         extra_head='<link rel="stylesheet" href="/testing/testing.css">')
