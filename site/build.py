#!/usr/bin/env python3
"""Build portable static support/privacy pages. No external dependencies."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlsplit
from content import SUPPORT, POLICY

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'publication-config.json').read_text())
DIST = ROOT.parent / 'docs'
DIST.mkdir(exist_ok=True)


def h(text):
    return html.escape(str(text), quote=True)


def problems(config):
    errors = []
    if not config.get('operator_name', '').strip(): errors.append('operator_name: 운영자명 필요')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', config.get('support_email', '')): errors.append('support_email: 실제 지원 이메일 필요')
    privacy = config.get('privacy_contact_email') or config.get('support_email', '')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', privacy): errors.append('privacy_contact_email: 실제 개인정보 문의 이메일 필요')
    period = config.get('support_retention_days')
    text = config.get('support_retention_text', {})
    if not (type(period) is int and period >= 1) and not all(text.get(lang, '').strip() for lang in ('ko', 'en')):
        errors.append('support_retention_days / support_retention_text: 문의 보관 기준 필요')
    try: date.fromisoformat(config.get('effective_date', ''))
    except ValueError: errors.append('effective_date: 실제 시행일 YYYY-MM-DD 필요')
    origin = urlsplit(config.get('site_origin', ''))
    if origin.scheme != 'https' or not origin.netloc or origin.path not in ('', '/'): errors.append('site_origin: HTTPS 사이트 원점 필요')
    if config.get('privacy_reviewed') is not True: errors.append('privacy_reviewed: 최종 SDK·호스팅·법적 고지 검토 필요')
    return errors


READY = CONFIG.get('publication_mode') == 'release' and not problems(CONFIG)
SITE_BASE = CONFIG['site_origin'].rstrip('/') + CONFIG.get('base_path', '').rstrip('/')
if CONFIG.get('publication_mode') == 'release' and not READY:
    raise SystemExit('공개용 빌드 차단 / Release blocked:\n' + '\n'.join(problems(CONFIG)))


def route(lang, kind):
    return f'{lang}/{kind}/'


def url_from(lang, kind, to_lang=None, to_kind=None):
    return '../../' + route(to_lang or lang, to_kind or kind)


def document(lang, kind, title, description, body, hero=True):
    other = 'en' if lang == 'ko' else 'ko'
    label_support, label_privacy = ('지원', '개인정보처리방침') if lang == 'ko' else ('Support', 'Privacy')
    switch = 'English' if lang == 'ko' else '한국어'
    banner = '' if READY else '<div class="banner" role="note">' + ('게시 준비용 초안 · 운영자 정보와 문의처, 정책 검토가 완료되면 공개합니다.' if lang == 'ko' else 'Publication draft · Publisher details, contact information and policy review are pending.') + '</div>'
    links = f'<nav class="nav" aria-label="{"주요 메뉴" if lang == "ko" else "Main navigation"}"><a href="{url_from(lang,kind,to_kind="support")}" {"aria-current=page" if kind == "support" else ""}>{label_support}</a><a href="{url_from(lang,kind,to_kind="privacy")}" {"aria-current=page" if kind == "privacy" else ""}>{label_privacy}</a><a class="language" href="{url_from(lang,kind,to_lang=other)}" lang="{other}" hreflang="{other}">{switch}</a></nav>'
    canonical = SITE_BASE + '/' + route(lang, kind)
    meta = '<meta name="robots" content="noindex,nofollow">' if not READY else f'<link rel="canonical" href="{h(canonical)}">'
    alternates = ''.join(f'<link rel="alternate" hreflang="{code}" href="{h(SITE_BASE + "/" + route(code,kind))}">' for code in ('ko','en')) if READY else ''
    head = f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)} · 1891: Life Out West</title><meta name="description" content="{h(description)}">{meta}{alternates}<link rel="icon" href="../../assets/icon.png"><link rel="stylesheet" href="../../assets/site.css"><script src="../../assets/site.js" defer></script></head><body>'
    skip = '본문으로 건너뛰기' if lang == 'ko' else 'Skip to content'
    header = f'<a class="skip" href="#main">{skip}</a><header><div class="topbar"><a class="brand" href="../../index.html"><img src="../../assets/icon.png" alt="" width="42" height="42">1891: LIFE OUT WEST</a>{links}</div></header>{banner}'
    footer_text = ('1891: 서부에서 살아가기 · 지원과 개인정보' if lang == 'ko' else '1891: Life Out West · Support & privacy')
    operator = h(CONFIG['operator_name']) if CONFIG['operator_name'] else ('운영자 정보 입력 대기' if lang == 'ko' else 'Publisher details pending')
    footer = f'<footer><div class="foot"><span>{footer_text}<br>{operator}</span><span><a href="{url_from(lang,kind,to_kind="support")}">{label_support}</a><a href="{url_from(lang,kind,to_kind="privacy")}">{label_privacy}</a></span></div></footer></body></html>'
    return head + header + body + footer


def hero(eyebrow, title, intro):
    return f'<div class="hero"><div class="hero-inner"><span class="eyebrow">{h(eyebrow)}</span><h1>{h(title)}</h1><p>{h(intro)}</p></div></div>'


def toc(entries, lang):
    return '<aside class="toc" aria-label="' + ('페이지 목차' if lang == 'ko' else 'On this page') + '"><strong>' + ('ON THIS PAGE' if lang == 'en' else '이 페이지에서') + '</strong>' + ''.join(f'<a href="#{ident}">{h(label)}</a>' for ident, label in entries) + '</aside>'


def email_link(email):
    return 'mailto:' + quote(email, safe='@.+-')


for lang, copy in SUPPORT.items():
    entries = [('questions', copy['faq_title']), ('contact', copy['contact']), ('privacy', POLICY[lang]['title'])]
    faq = ''.join(f'<details><summary>{h(q)}</summary><p>{h(a)}</p></details>' for q, a in copy['faqs'])
    email = CONFIG['support_email']
    contact = f'<a href="{h(email_link(email))}">{h(email)}</a>' if email else f'<span class="empty">{h(copy["no_email"])}</span>'
    contact_button = f'<a class="button secondary" href="{h(email_link(email))}?subject={quote("1891 Support")}">{h(copy["email_button"])}</a>' if email else ''
    if CONFIG.get('issues_url'):
        contact_button += f'<p class="small"><a href="{h(CONFIG["issues_url"])}">' + ('공개 버그 제보 · GitHub Issues' if lang == 'ko' else 'Public bug reports · GitHub Issues') + '</a><br>' + ('GitHub 계정이 필요합니다. 공개 글에는 이메일 주소, 영수증, 저장 파일 등 개인정보를 올리지 마세요. 비공개 문의는 지원 이메일을 이용하세요.' if lang == 'ko' else 'A GitHub account is required. Do not post email addresses, receipts, save files or other personal information publicly. Use the support email for private requests.') + '</p>'
    main = f'''{hero(copy['eyebrow'],copy['title'],copy['intro'])}<div class="wrap">{toc(entries,lang)}<main id="main">
    <section id="questions"><h2>{h(copy['faq_title'])}</h2><div class="faq">{faq}</div></section>
    <section id="contact" class="contact"><h2>{h(copy['contact'])}</h2><p>{h(copy['contact_intro'])}</p><span class="contact-label">{h(copy['email_label'])}</span><div class="contact-address">{contact}</div>{contact_button}
    <label class="template-label" for="request-template">{h(copy['template_label'])}</label><textarea id="request-template" rows="9" readonly>{h(copy['template'])}</textarea><button type="button" data-copy="request-template" data-success="{h(copy['copied'])}" data-fallback="{h(copy['copy_fallback'])}">{h(copy['copy'])}</button><p class="status" role="status" aria-live="polite" id="copy-status"></p><p class="small">{h(copy['sensitive'])}</p></section>
    <section class="callout" id="privacy"><h3>{h(POLICY[lang]['title'])}</h3><p>{h(copy['privacy_cta'])}</p><a href="{url_from(lang,'support',to_kind='privacy')}">{h(copy['privacy_link'])} →</a></section></main></div>'''
    out = DIST / route(lang, 'support'); out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(document(lang, 'support', copy['title'], copy['intro'], main))

for lang, copy in POLICY.items():
    pending = '게시 전 입력 필요' if lang == 'ko' else 'Required before publication'
    effective = CONFIG['effective_date'] or pending
    publisher = CONFIG['operator_name'] or pending
    address = CONFIG['privacy_contact_email'] or CONFIG['support_email']
    contact = f'<a href="{h(email_link(address))}">{h(address)}</a>' if address else h(pending)
    days = CONFIG.get('support_retention_days')
    retention = (f'문의 처리 완료 후 {days}일' if lang == 'ko' else f'{days} days after resolution') if days else CONFIG.get('support_retention_text', {}).get(lang, pending)
    facts = f'<dl class="facts"><div><dt>{h(copy["operator"])}</dt><dd>{h(publisher)}</dd></div><div><dt>{h(copy["contact"])}</dt><dd>{contact}</dd></div><div><dt>{h(copy["effective"])}</dt><dd>{h(effective)}</dd></div><div><dt>{h(copy["retention"])}</dt><dd>{h(retention)}</dd></div></dl>'
    sections = ''.join(f'<section id="{ident}"><h2>{h(title)}</h2>' + ''.join(f'<p>{h(p)}</p>' for p in paragraphs) + '</section>' for ident, title, paragraphs in copy['sections'])
    refs = '<section id="references"><h2>' + h(copy['refs']) + '</h2><div class="refs">' + ''.join(f'<a href="{u}" rel="noreferrer">{h(label)}</a>' for label,u in [
        ('Apple Privacy','https://www.apple.com/legal/privacy/'),('Unity Privacy','https://unity.com/legal/game-player-and-app-user-privacy-policy'),('Unity IAP Privacy','https://docs.unity.com/en-us/iap/privacy-and-consent/overview'),('GitHub Privacy','https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement')]) + '</div></section>'
    entries = [(ident,title.split('. ',1)[-1]) for ident,title,_ in copy['sections']]
    main = hero(copy['eyebrow'],copy['title'],copy['intro']) + '<div class="wrap">' + toc(entries,lang) + '<main class="policy" id="main">' + facts + sections + refs + f'<p><a href="{url_from(lang,"privacy",to_kind="support")}">{h(copy["support_link"])} →</a></p></main></div>'
    out = DIST / route(lang, 'privacy'); out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(document(lang,'privacy',copy['title'],copy['intro'],main))

banner = '' if READY else '<div class="banner">게시 준비용 초안 · Publication draft</div>'
(DIST/'index.html').write_text(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1891: Life Out West · 지원 / Support</title><meta name="description" content="1891: Life Out West 한국어·영어 지원 및 개인정보처리방침. Support and privacy in Korean and English.">{'<meta name="robots" content="noindex,nofollow">' if not READY else ''}<link rel="icon" href="assets/icon.png"><link rel="stylesheet" href="assets/site.css"></head><body>{banner}<main id="main" class="home"><span class="eyebrow home-eyebrow">1891 · LIFE OUT WEST</span><h1>당신의 여정을 위한 안내<br><span lang="en">Help for your journey</span></h1><p>게임 지원과 개인정보처리방침을 확인하세요.<br><span lang="en">Support and privacy information for 1891: Life Out West.</span></p><section class="callout"><h2>1891: 서부에서 살아가기</h2><p>사금 채취, 광산 탐험과 말을 타는 여행. 집과 목장을 마련하며 일곱 지도 조각을 따라 엘도라도로 향하는 1인용 서부 탐험 게임입니다. 한국어·영어와 iPhone·iPad·Mac을 지원합니다.</p><p lang="en">Pan for gold, explore mines and ride the frontier. Build a home and ranch as you follow seven map fragments toward El Dorado in this single-player western adventure for iPhone, iPad and Mac, in Korean and English.</p><p>일반 여정의 게임 내 첫 3일 무료 · 이후 일회성 정식판 구매<br><span lang="en">First 3 in-game days free · One-time Full Version purchase thereafter</span></p></section><div class="languages"><section class="language-panel"><h2>한국어</h2><div class="actions"><a class="button" href="ko/support/">지원 페이지</a><a class="button secondary" href="ko/privacy/">개인정보처리방침</a></div></section><section class="language-panel" lang="en"><h2>English</h2><div class="actions"><a class="button" href="en/support/">Support</a><a class="button secondary" href="en/privacy/">Privacy Policy</a></div></section></div><p><a href="mailto:support@supracore.co.kr">support@supracore.co.kr</a> · <a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">Apple 표준 이용약관 · Standard EULA</a></p></main></body></html>''')
assets = DIST/'assets';assets.mkdir(exist_ok=True)
for name in ('site.css','site.js','icon.png','frontier.png'):shutil.copyfile(ROOT/'assets'/name,assets/name)
(DIST/'robots.txt').write_text('User-agent: *\n' + ('Allow: /\nSitemap: '+SITE_BASE+'/sitemap.xml\n' if READY else 'Disallow: /\n'))
urls = [SITE_BASE+'/'+route(lang,kind) for lang in ('ko','en') for kind in ('support','privacy')]
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + (''.join('<url><loc>'+h(u)+'</loc></url>' for u in urls) if READY else '')+'</urlset>')
(DIST/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n  Content-Security-Policy: default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; connect-src 'none'\n" + ('' if READY else '  X-Robots-Tag: noindex, nofollow\n'))
expected = {lang: {'support_url':SITE_BASE+'/'+route(lang,'support'),'privacy_policy_url':SITE_BASE+'/'+route(lang,'privacy')} for lang in ('ko','en')}
(ROOT/'publication-status.json').write_text(json.dumps({'ready_to_publish':READY,'state':'release' if READY else 'draft','deployed':False,'missing':problems(CONFIG),'proposed_urls_not_live':expected},ensure_ascii=False,indent=2)+'\n')
(ROOT/'PublicationLinks.proposed.json').write_text(json.dumps({'privacyPolicyUrl':expected['ko']['privacy_policy_url'],'supportUrl':expected['ko']['support_url']},ensure_ascii=False,indent=2)+'\n')
print(f'Built 4 localized pages and language index; publication_ready={READY}')

(DIST/'.nojekyll').write_text('')
shutil.copyfile(ROOT.parent/'app-store-links.json', DIST/'app-store-links.json')
