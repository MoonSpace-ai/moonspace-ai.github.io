# -*- coding: utf-8 -*-
"""Build MoonSpace's static site using Python's standard library only."""
import json
import re
from learn import render_learn
from testing import render_testing
from html import escape as e
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
D = json.loads((ROOT / 'content.json').read_text())
OUT = ROOT / 'docs'
ORIGIN = D['site_url'].rstrip('/')
PAGES = []

def external(url, label, cls=''):
    return f'<a href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer" class="{cls}">{label}</a>'


def button(url, label, secondary=False):
    return f'<a class="button{" secondary" if secondary else ""}" href="{e(url, quote=True)}">{label}</a>'


def eyebrow(text):
    if ' / ' in text and not re.search(r'[\u4e00-\u9fff]',text.split(' / ')[0]): text=text.split(' / ',1)[1]
    return f'<div class="section-label">{e(text)}</div>' if re.search(r'[\u4e00-\u9fff]',text) else ''

def tags(items): return '<div class="tags">'+''.join(f'<span class="tag">{e(t)}</span>' for t in items)+'</div>'

NAV = [('/cases/','合作案例'),('/people/','人与作品'),('/knowledge/','社区知识'),('/about/','关于我们')]

def header(active):
    links=''.join(f'<a href="{u}"'+(' aria-current="page"' if active==u else '')+f'>{label}</a>' for u,label in NAV)
    return f'''<a class="skip" href="#main">跳到正文</a><header class="header"><div class="container header-inner">
    <a class="brand" href="/" aria-label="MoonSpace 首页"><span class="brand-mark"><img src="/assets/moonspace-logo.png" alt="" width="1569" height="1003"></span><span class="brand-text">MoonSpace</span></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="main-navigation" type="button">菜单</button>
    <nav class="nav" id="main-navigation" aria-label="主导航">{links}<a class="nav-cta" href="/join/">一起聊聊</a></nav></div></header>'''


def footer():
    return f'''<footer class="footer"><div class="container"><div class="footer-main"><div class="footer-intro"><a class="footer-brand" href="/">MoonSpace</a><p>把工具还给工具，把人还给人。</p></div><div class="footer-links"><a href="/cases/">合作案例</a><a href="/people/">人与作品</a><a href="/knowledge/">社区知识</a></div><div class="footer-links"><a href="/join/">联系社区</a>{external(D['wiki'],'飞书知识库')}{external('https://github.com/MoonSpace-ai/moonspace-ai','GitHub')}<a href="/feed.xml">RSS 订阅</a></div></div><div class="footer-bottom"><span>© 2026 MoonSpace</span><a href="/about/">一个正在生长的 AI 创造者社区。</a></div></div></footer>'''


def page(path,title,description,body,active='',schema_type='WebPage',author=None,extra_head=''):
    canonical=ORIGIN+path
    schema={'@context':'https://schema.org','@type':schema_type,'name':title,'description':description,'url':canonical,'inLanguage':'zh-CN','isPartOf':{'@type':'WebSite','name':'MoonSpace','url':ORIGIN+'/'}}
    if schema_type=='Article':
        schema.update(headline=title,datePublished=D['updated'],dateModified=D['updated'],author={'@type':'Person','name':author or '慢慢'},publisher={'@type':'Organization','name':'MoonSpace','url':ORIGIN+'/'})
    if path=='/': schema={'@context':'https://schema.org','@type':'Organization','name':'MoonSpace','alternateName':'MoonSpace.ai','url':canonical,'logo':ORIGIN+'/assets/moonspace-logo.png','description':description,'sameAs':['https://github.com/MoonSpace-ai/moonspace-ai']}
    schema_json=json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')
    html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · MoonSpace</title><meta name="description" content="{e(description,quote=True)}"><meta name="theme-color" content="#f6f6f2"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if schema_type=='Article' else 'website'}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="MoonSpace"><meta property="og:title" content="{e(title,quote=True)}"><meta property="og:description" content="{e(description,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/logo.jpg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/moonspace-logo.png" type="image/png"><link rel="alternate" type="application/rss+xml" title="MoonSpace 社区知识" href="/feed.xml"><link rel="stylesheet" href="/assets/site.css?v=20261115-journey"><script type="application/ld+json">{schema_json}</script><script defer src="/assets/site.js?v=20261115-journey"></script>{extra_head}</head><body>{header(active)}<main id="main">{body}</main>{footer()}<button class="sound-toggle" type="button" aria-pressed="false" aria-label="开启纯音乐"><span class="sound-bars" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span class="sound-label">开启音乐</span></button><span class="pointer-halo" aria-hidden="true"></span></body></html>'''
    dest=OUT/('index.html' if path=='/' else path.strip('/')+'/index.html')
    if path=='/404.html':dest=OUT/'404.html'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html)
    if path!='/404.html':PAGES.append((path,title,description))

def case_art(c,i):
    if i==0:
        return '<div class="case-visual event-photo"><img src="/assets/chengdu-event.jpg" alt="成都站活动中，高校参与者围坐体验与交流 AI 产品" loading="lazy"></div>'
    return '<div class="case-visual campus-cover"><span class="cover-title">校园里的问题，<br>一起找到新解法。</span><div class="campus-shapes" aria-hidden="true"><i></i><i></i><i></i></div></div>'


def case_cards():
    return '<div class="case-grid">'+''.join(f'<a class="case-card" href="/cases/{c["slug"]}/">{case_art(c,i)}<div class="case-body"><div class="small-label">{e(c["category"])}</div><h3>{e(c["name"])}</h3><p>{e(c["summary"])}</p><span class="read-link">阅读这次实践</span></div></a>' for i,c in enumerate(D['cases']))+'</div>'


def project_cards():
    covers=[('让感觉，<br>长出语言。','意译'),('想法与实现，<br>始终对得上。','共识'),('给自己的积累，<br>找一个家。','个人 Wiki')]
    return '<div class="project-grid">'+''.join(f'<article class="project-card"><a class="project-art project-{i}" href="{p["url"]}" target="_blank" rel="noopener noreferrer"><span class="project-cover-title">{covers[i][0]}</span><span class="project-cover-name">{covers[i][1]}</span></a><div class="project-body"><h3>{external(p["url"],e(p["name"]))}</h3><p>{e(p["description"])}</p><div class="project-bottom"><span>作者：{e(p["author"])}</span>{external(p["code"],"开源代码")}</div></div></article>' for i,p in enumerate(D['projects']))+'</div>'


def knowledge_list():
    return '<div class="knowledge-list">'+''.join(f'<a class="knowledge-row" href="/knowledge/{a["slug"]}/"><div><div class="small-label">{a["category"]} · 慢慢</div><h3 class="knowledge-title">{a["title"]}</h3><p>{a["description"]}</p></div><span class="read-link">读一读</span></a>' for a in D['articles'])+'</div>'


def page_head(eyebrow_text,title,description,breadcrumb=None):
    bc=f'<div class="breadcrumb"><a href="/">首页</a><span>/</span>{breadcrumb}</div>' if breadcrumb else ''
    return f'<div class="page-head">{bc}{eyebrow(eyebrow_text)}<h1>{title}</h1><p>{description}</p></div>'

FAQ=[('MoonSpace 是什么？','MoonSpace 是一个连接 AI 创造者、学生与产品团队的实践社区。我们关注真实作品、经验分享和项目共创，希望让一次交流能延续为实践与合作。'),('没有成熟作品，可以参与吗？','可以从一件正在做的事开始。整理自己的兴趣、尝试、问题与需要的帮助，也可以成为认识伙伴、获得反馈的起点。'),('产品团队可以怎样合作？','可以围绕产品体验、校园场景探索、内容或活动共创提出具体问题。合作前一起确认目标、交付、成员角色、报酬和成果使用方式。'),('知识库和官网有什么区别？','知识库承载原始记录、经验与协作内容；官网精选展示社区介绍、作品和公开实践。部分飞书原文可能需要相应访问权限。'),('成员能留下什么？','我们希望每次参与都能留下具体作品、贡献记录、可复用的经验和持续的连接。商业项目应提前约定合理报酬、署名和成果使用方式。')]

def faq():return '<div class="faq">'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in FAQ)+'</div>'

hero='''<section class="container hero" data-moon-scene="intro"><div class="hero-content"><h1 class="hero-title" aria-label="带着想法来，和有意思的人一起做！"><span class="hero-title-line"><span class="title-ink" data-title-text aria-hidden="true">带着想法来，</span></span><span class="hero-title-line title-second"><span class="title-ink" data-title-text aria-hidden="true">和有意思的人一起做<span class="title-bang">！</span></span></span></h1><p>在 MoonSpace，学生、AI 创造者和产品团队<br>分享作品，交换经验，也一起完成真实项目。</p><div class="actions">'''+button('#discover','看看大家在做什么')+button('/knowledge/introduce-yourself/','介绍一下你自己',True)+'''</div></div><div class="community-collage"><a class="collage-note" href="/knowledge/introduce-yourself/"><span class="note-sticker">从这里认识你</span><h2>最近，<br>你在做什么？</h2><p>一个作品、一段经历，<br>或是一个还没解开的问题。</p><span class="note-bottom">给下一次交流一个起点</span></a><a class="collage-photo" href="/cases/xiaohuanxiong-chengdu/"><div class="collage-photo-inner"><img src="/assets/chengdu-event.jpg" alt="MoonSpace 参与的成都站 AI 产品体验活动" fetchpriority="high"></div><span>有些好想法，是见面聊出来的。</span></a><a class="collage-work" href="https://vibe-design-labs.github.io/Vibe-UI-UX/" target="_blank" rel="noopener noreferrer"><span>来自社区的作品</span><h2>让感觉，<br>长出语言。</h2><p>意译 IntentKit</p><div class="work-swatch" aria-hidden="true"><i></i><i></i><i></i></div></a></div></section>'''

home=hero+'''<section class="section container discovery" id="discover"><div class="section-top"><h2>大家最近在做什么？</h2><div class="filters" role="group" aria-label="选择内容类型"><button type="button" data-filter="all" aria-pressed="true">全部</button><button type="button" data-filter="case" aria-pressed="false">合作</button><button type="button" data-filter="project" aria-pressed="false">作品</button><button type="button" data-filter="note" aria-pressed="false">经验</button></div></div><p class="sr-only" id="filter-status" role="status" aria-live="polite"></p><div class="discover-grid">'''
home+='<section class="discovery-chapter" data-moon-scene="cases" id="home-cases" aria-label="合作案例"><p class="chapter-label">合作案例</p><div class="chapter-grid">'
for i,c in enumerate(D['cases']):
    home+=f'<article class="discover-item" data-kind="case"><a class="discover-card" href="/cases/{c["slug"]}/">{case_art(c,i)}<div class="discover-body"><span class="small-label">{c["category"]}</span><h3>{c["name"]}</h3><p>{c["summary"]}</p><span class="read-link">阅读案例</span></div></a></article>'
home+='</div></section><section class="discovery-chapter" data-moon-scene="projects" id="home-projects" aria-label="社区作品"><p class="chapter-label">社区作品</p><div class="chapter-grid">'
for i,p in enumerate(D['projects'][:2]):
    cover=['让感觉，<br>长出语言。','想法与实现，<br>始终对得上。'][i]
    home+=f'<article class="discover-item" data-kind="project"><a class="discover-card" href="{p["url"]}" target="_blank" rel="noopener noreferrer"><div class="project-art project-{i}"><span class="project-cover-title">{cover}</span><span class="project-cover-name">{p["name"]}</span></div><div class="discover-body"><span class="small-label">作品 · 作者慢慢</span><h3>{p["name"]}</h3><p>{p["description"]}</p><span class="read-link">打开作品</span></div></a></article>'
home+='</div></section><section class="discovery-chapter" data-moon-scene="notes" id="home-notes" aria-label="社区知识"><p class="chapter-label">社区知识</p><div class="chapter-grid">'
for i,a in enumerate(D['articles'][:2]):
    home+=f'<article class="discover-item" data-kind="note"><a class="discover-card note-card note-{i}" href="/knowledge/{a["slug"]}/"><div class="note-cover"><h3>{a["title"]}</h3></div><div class="discover-body"><span class="small-label">{a["category"]} · 慢慢</span><p>{a["description"]}</p><span class="read-link">读这篇文章</span></div></a></article>'
home+='</div></section></div></section>'
home+='''<section class="section container" data-moon-scene="community"><div class="community-invite"><div><h2>先介绍自己，<br>再一起探索更大的世界。</h2><p>你正在做什么？能提供什么？想寻找什么？<br>一份具体的介绍，可以成为交流、调研和合作的开始。</p><div class="actions">'''+button('/knowledge/introduce-yourself/','一起整理个人介绍')+'''</div></div><div class="question-paper"><p>我正在做什么？</p><p>我做出过什么？</p><p>我能提供什么？</p><p>我正在寻找什么？</p><p>我想了解什么？</p></div></div></section>'''
home+='<section class="section container" data-moon-scene="notes"><div class="section-top"><h2>开始之前，你也许想问。</h2></div>'+faq()+'</section>'
home+='''<div class="moon-journey" aria-label="阅读进度" hidden><span class="moon-scene-label">初次相遇</span><div class="moon-track"><i></i><i></i><i></i><i></i><button class="journey-moon" type="button" aria-label="初次相遇，回到本节开头"><svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18" class="moon-shade"/><path class="moon-light" d="M25 2.7A18 18 0 1 0 35.5 29 18 18 0 0 1 25 2.7Z"/></svg></button></div></div>'''
page('/','带着想法来，和有意思的人一起做','MoonSpace 连接学生、AI 创造者与产品团队。发现作品、交流经验、参与真实项目，从具体的人和事开始认识彼此。',home)

body='<div class="container">'+page_head('FIELD NOTES / 合作案例','我们一起，做过这些事。','从校园场景到产品现场，记录每一次连接怎样变成行动，以及行动之后留下了什么。')+'<section class="page-section">'+case_cards()+'<div class="project-feature"><h2>你有一个具体问题，想一起试试吗？</h2><p>产品体验、校园实践、内容与活动共创，都可以从一次具体的交流开始。</p>'+button('/join/','了解合作方式')+'</div></section></div>'
page('/cases/','合作案例','阅读 MoonSpace 的小浣熊成都站与 Coze 校园实践记录，了解高校连接、活动共创和 AI 应用场景探索。',body,'/cases/')

for c in D['cases']:
    acts=''.join(f'<li>{e(s)}</li>' for s in c['actions'])
    outputs=''.join(f'<li>{e(s)}</li>' for s in c['outputs'])
    sources=''.join(external(s['url'],s['label']) for s in c['evidence'])
    body='<div class="container">'+page_head(c['category'],c['title'],c['name'],'<a href="/cases/">合作案例</a> / 实践记录')+f'<div class="article-layout"><article class="prose"><h2>从什么问题出发</h2><p>{c["context"]}</p><h2>我们参与的部分</h2><ul>{acts}</ul><h2>留下的成果</h2><ul>{outputs}</ul><h2>从这次实践继续</h2><blockquote>{c["learning"]}</blockquote><div class="reading-note">本页根据 MoonSpace 项目记录整理，聚焦社区实际参与的工作。原始材料中的部分链接可能需要相应访问权限。</div><div class="actions">{button("/join/","交流类似项目",True)}</div></article><aside class="side-note"><strong>{c["name"]}</strong><span>MoonSpace 实践记录<br>页面整理：{D["updated"]}</span>{tags(c["tags"])}<strong style="margin-top:25px">资料与成果入口</strong>{sources}</aside></div></div>'
    page('/cases/'+c['slug']+'/',c['name'],c['summary'],body,'/cases/')

body='<div class="container">'+page_head('PEOPLE & PROJECTS / 人与作品','先认识一个人，<br>再一起做一件事。','作品让想法变得具体，记录让经历有迹可循。这里从社区运营者的实践开始，认识正在做事的人。')+'''<section class="page-section"><div class="person"><div class="avatar" aria-hidden="true">慢</div><div><div class="small-label">社区运营 · AI 产品与开发者连接</div><h2>慢慢 🌙</h2><p>商科出身，正在把 AI 产品实践、开发者关系与校园社区连接在一起。喜欢从一个真实卡点出发，做出能上手、能反馈，也能继续维护的小作品。</p><div class="person-links">'''+external('https://moonspaceai.feishu.cn/wiki/QnwSwDygIiG7PUkklyicAjcQncg','个人说明书')+external('https://virtue192.github.io/zhishiku-blog-pages/','个人博客')+external('https://github.com/virtue192','GitHub')+'''</div></div></div><div class="section-top" style="margin-top:55px"><div>'''+eyebrow('A FEW THINGS IN THE MAKING')+'''<h2 class="section-title">从具体的作品认识彼此。</h2></div></div>'''+project_cards()+'''<div class="project-feature"><h2>你的作品，也值得被认识。</h2><p>带上一份自我介绍、一项可以体验的作品，或者一个希望获得反馈的问题。一起把它整理成别人看得懂的介绍。</p>'''+button('/join/','分享你正在做的事')+'''</div></section></div>'''
page('/people/','人与作品','认识 MoonSpace 的实践者，探索 IntentKit、Accord 与 Life Ledger OS，交流正在做的作品与合作意愿。',body,'/people/')

body='<div class="container">'+page_head('OPEN NOTEBOOK / 社区知识','记录走过的路，<br>也给新的探索留一点光。','从具体经历出发，分享做事的方法、遇到的卡点与自己的判断。经验提供线索，选择仍然属于每个人。')+'<section class="page-section">'+knowledge_list()+'<div class="project-feature"><h2>带着上下文，分享一段真实经历。</h2><p>当时有什么条件？试过哪些方法？留下了什么结果？比起一个万能答案，我们更想读到这些具体的过程。</p>'+external(D['wiki'],'进入飞书社区项目','text-link')+'</div></section></div>'
page('/knowledge/','社区知识','阅读 MoonSpace 关于个人记录、公开学习与行业连接的经验文章，把真实实践变成可以继续使用的知识。',body,'/knowledge/')

for a in D['articles']:
    sections=''.join(f'<h2>{s["title"]}</h2><p>{s["text"]}</p>' for s in a['sections'])
    body='<div class="container">'+page_head(a['category'],a['title'],a['description'],'<a href="/knowledge/">社区知识</a> / 阅读')+f'<div class="article-layout"><article class="prose"><p>{a["intro"]}</p>{sections}<div class="reading-note">作者：慢慢。本页根据作者飞书原文整理为网站阅读版，原文保留更完整的个人经历与表达。<br>网站版发布：{D["updated"]}。</div><div class="actions">{external(a["source"],"阅读飞书原文","button secondary")}</div></article><aside class="side-note"><strong>关于这份记录</strong><span>来自真实的经历与持续探索。<br>阅读时，也请保留自己的处境与判断。</span><a href="/people/">认识作者</a><a href="/knowledge/">继续翻阅社区知识</a><a href="/join/">分享你的实践</a></aside></div></div>'
    page('/knowledge/'+a['slug']+'/',a['title'],a['description'],body,'/knowledge/',schema_type='Article')

body='<div class="container">'+page_head('ABOUT MOONSPACE / 关于我们','把工具还给工具，<br>把人还给人。','我们相信，AI 时代值得持续积累的，还有一个个具体的人、真实的作品，以及一起做事建立的信任。')+'''<div class="article-layout"><article class="prose"><h2>我们为什么相聚</h2><p>高校青年有想法、有创造力，也希望接触课程与比赛之外的真实问题。产品团队希望找到愿意理解产品、使用产品并提出具体反馈的伙伴。MoonSpace 希望为双方创造一起实践的入口。</p><blockquote>让一次机会，变成作品、能力、关系与信任。</blockquote><h2>我们正在做的事情</h2><p>从高校青年出发，连接 AI 创造者、开发者、设计师与产品团队。通过个人介绍与作品展示发现彼此，通过产品体验、活动和项目共创一起行动，再把成果与经验沉淀下来。</p><h2>我们如何一起做事</h2><ul><li>从一个真实、边界明确的问题开始，确认角色、时间与交付。</li><li>提前说清成员回报、署名与成果使用方式。</li><li>保留过程与证据，让个人贡献和项目成果能够被理解。</li><li>经作者与相关参与者同意，再分享可以公开的成果与经验。</li></ul><h2>一个可以继续生长的社区</h2><p>MoonSpace 正在建设中。我们希望这里逐渐成为一张创造者关系网络：有人带着作品来，有人带着问题来，也有人在一次合作之后，把经验留给后来的人。</p><div class="actions">'''+button('/join/','从一次交流开始')+'''</div></article><aside class="side-note"><strong>MoonSpace.ai</strong><span>AI 创造者实践社区<br>发现人 · 发现作品 · 发现新的可能</span>'''+external('https://github.com/MoonSpace-ai/moonspace-ai','GitHub 社区入口')+external(D['source'],'阅读社区 brief')+'''</aside></div><section class="page-section"><h2 class="section-title">关于参与和合作。</h2>'''+faq()+'''</section></div>'''
page('/about/','关于 MoonSpace','了解 MoonSpace 的社区理念：连接 AI 创造者、学生与产品团队，通过真实项目积累作品、经验与信任。',body,'/about/')

body='<div class="container">'+page_head('LET’S MAKE SOMETHING / 参与与合作','从你正在做的事，<br>开始聊起。','一项作品、一个具体问题，或是一段值得分享的经历，都可以成为我们认识彼此的起点。')+'''<section class="page-section"><div class="join-grid"><article class="join-card">'''+eyebrow('FOR CREATORS / 给创造者')+'''<h2>带着你的实践来。</h2><p>你可以先告诉我们：</p><ul><li>最近主要在做什么，具体负责哪一部分？</li><li>有没有一项可以查看或体验的作品？</li><li>想获得什么反馈，或者寻找什么伙伴？</li></ul><p>还没有成熟作品，也可以从一份个人介绍和一个真实问题开始。</p>'''+external(D['wiki'],'了解个人介绍共建项目','text-link')+'''</article><article class="join-card">'''+eyebrow('FOR PRODUCT TEAMS / 给产品团队')+'''<h2>带着一个真实问题来。</h2><p>可以一起讨论：</p><ul><li>产品体验与校园使用场景探索</li><li>创作者内容、案例与活动共创</li><li>有明确目标、成员分工与成果的实践项目</li></ul><p>合作前共同确认交付、时间、预算、成员报酬与成果使用方式。</p><a href="/cases/" class="text-link">先看看历史实践 </a></article></div><div class="contact"><div><div class="small-label">联系 MoonSpace · 慢慢</div><h2>给下一次合作，一个具体的开头。</h2><p>添加时备注「MoonSpace」，也欢迎附上你的作品或问题。</p><span class="contact-id">'''+e(D['wechat'])+'''</span></div><div><div class="actions"><button class="button" data-copy="'''+e(D['wechat'])+'''" data-status="copy-status" type="button">复制微信号 <span aria-hidden="true"></span></button><a class="button secondary" href="mailto:'''+e(D['email'])+'''?subject=MoonSpace%20%E4%BA%A4%E6%B5%81%E4%B8%8E%E5%90%88%E4%BD%9C">发一封邮件 </a></div><span class="copy-status" id="copy-status" role="status" aria-live="polite"></span></div></div></section></div>'''
page('/join/','参与与合作','通过微信或邮件联系 MoonSpace，分享你的作品、个人介绍或产品合作问题。一起讨论项目目标、交付与成员回报。',body)

page('/404.html','这个页面还没有抵达','回到 MoonSpace，继续认识人、发现作品与探索真实实践。','<section class="container empty404"><h1>404</h1><h2>这个页面，还没有抵达。</h2><p>换一个入口，继续逛逛这个小宇宙。</p>'+button('/','回到首页')+'</section>')

render_learn(ROOT, page, button, external)
render_testing(ROOT, page, external)

PAGES.append(('/intro/','个人说明书工坊','整理实践、作品和合作意向，本地保存并导出个人说明书。'))
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{xml_escape(ORIGIN+path)}</loc><lastmod>{D["updated"]}</lastmod></url>' for path,_,_ in PAGES)+'</urlset>')
(OUT/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>MoonSpace 社区知识</title><link>'+ORIGIN+'/knowledge/</link><description>真实经历、公开学习与共同创造。</description><language>zh-CN</language>'+''.join(f'<item><title>{xml_escape(a["title"])}</title><link>{ORIGIN}/knowledge/{a["slug"]}/</link><guid>{ORIGIN}/knowledge/{a["slug"]}/</guid><description>{xml_escape(a["description"])}</description></item>' for a in D['articles'])+'</channel></rss>')
(OUT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#173d33"/><path d="M43 13a23 23 0 1 0 9 38A24 24 0 0 1 43 13Z" fill="#efd4a3"/></svg>')
print(f'Built {len(PAGES)} indexable pages + 404, sitemap, RSS and static assets.')
