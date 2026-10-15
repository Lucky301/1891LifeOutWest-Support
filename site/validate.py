#!/usr/bin/env python3
"""Validate the rendered static site. --release refuses incomplete publication."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
DIST = ROOT.parent/'docs'


class Document(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.links=[];self.resources=[];self.lang=None;self.h1=0;self.noindex=False;self.forms=0;self.errors=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:self.errors.append('duplicate id '+a['id'])
            self.ids.add(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='form':self.forms+=1
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='link' and a.get('rel') in ('stylesheet','icon'):self.resources.append(a['href'])
        if tag in ('img','script') and a.get('src'):self.resources.append(a['src'])
        if tag=='meta' and a.get('name')=='robots':self.noindex='noindex' in a.get('content','')


def validate(release=False):
    status=json.loads((ROOT/'publication-status.json').read_text())
    pages=list(DIST.rglob('*.html'));assert len(pages)==5,'Expected four localized pages and one language index'
    parsed={p:Document() for p in pages};errors=[]
    for p,doc in parsed.items():
        doc.feed(p.read_text());errors.extend(f'{p.name}: {e}' for e in doc.errors)
        if doc.lang not in ('ko','en'):errors.append(f'{p}: missing language')
        if doc.h1!=1:errors.append(f'{p}: expected one H1')
        if doc.forms:errors.append(f'{p}: unexpected data submission form')
        if not status['ready_to_publish'] and not doc.noindex:errors.append(f'{p}: draft must be noindex')
    for p,doc in parsed.items():
        for value in doc.links+doc.resources:
            u=urlsplit(value)
            if u.scheme:
                if value in doc.resources:errors.append(f'{p}: external executable/media dependency')
                continue
            target=(DIST/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else (p.parent/unquote(u.path))
            target=target.resolve()
            if not target.is_relative_to(DIST.resolve()):errors.append(f'{p}: link escapes dist: {value}');continue
            if target.is_dir():target=target/'index.html'
            if not target.exists():errors.append(f'{p}: missing link: {value}')
            elif u.fragment and target in parsed and u.fragment not in parsed[target].ids:errors.append(f'{p}: missing fragment: {value}')
    assert not errors,'\n'.join(errors)
    result={'static_checks_passed':True,'html_pages':len(pages),'local_links_valid':True,'external_asset_dependencies':0,'ready_to_publish':status['ready_to_publish'],'publication_blockers':status['missing']}
    (ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if release and not status['ready_to_publish']:raise SystemExit('Publication blocked: fill publisher/contact/retention/date, review privacy, set publication_mode=release and rebuild.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');args=parser.parse_args();validate(args.release)
