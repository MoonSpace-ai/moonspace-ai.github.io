"""Check generated routes, metadata, JSON-LD and local links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent/'docs'
class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.h1=0;self.ids=set();self.jsons=[];self.in_json=False;self.buf='';self.canonical=False;self.description=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag in ['a','link'] and a.get('href'):self.links.append(a['href'])
        if tag in ['script','img'] and a.get('src'):self.links.append(a['src'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical=True
        if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
        if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.buf=''
    def handle_data(self,d):
        if self.in_json:self.buf+=d
    def handle_endtag(self,t):
        if t=='script' and self.in_json:self.jsons.append(json.loads(self.buf));self.in_json=False

count=0
for f in ROOT.rglob('*.html'):
    p=Parser();text=f.read_text();p.feed(text)
    assert p.h1==1,(f,p.h1)
    assert p.canonical and p.description and p.jsons,f
    assert 'noindex' not in text,f
    assert not re.search(r'[\u2190-\u21ff\u2794\u27a1\u27f0-\u27ff]',text),f'Unexpected arrow in {f}'
    assert not any(label in text for label in ['BE SEEN','FIELD NOTES','OPEN NOTEBOOK','A COMMUNITY FOR PEOPLE']),f'Decorative label in {f}'
    assert '/assets/moonspace-logo.png' in text,f'Transparent logo missing in {f}'
    for href in p.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        if not u.path:
            if u.fragment:assert u.fragment in p.ids,(f,href)
            continue
        target=(ROOT/unquote(u.path).lstrip('/')) if u.path.startswith('/') else f.parent/unquote(u.path)
        if u.path.endswith('/'):target=target/'index.html'
        assert target.is_file(),(f,href,target)
    count+=1
for filename in ['sitemap.xml','feed.xml']:ET.parse(ROOT/filename)
print(f'PASS: {count} HTML pages; internal links, unique h1, metadata, JSON-LD, sitemap and RSS.')
