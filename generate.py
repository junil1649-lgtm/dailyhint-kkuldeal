"""
generate.py — 데일리힌트 꿀딜 정적 사이트 생성기

실행: python generate.py
출력: site/ 폴더에 완전한 정적 HTML 사이트 생성
"""
import json, re, shutil
from pathlib import Path
from datetime import datetime, timezone

# ── 설정 ──────────────────────────────────────────────────────────────────────
SITE_NAME      = '데일리힌트 꿀딜'
SITE_URL       = 'https://junil1649-lgtm.github.io/dailyhint-kkuldeal'
SITE_TAGLINE   = '생활용품·주방용품 가성비 비교 추천'
SITE_DESC      = '생활용품과 주방용품의 실제 사용 후기와 가성비 비교 정보를 제공합니다. 쿠팡 인기상품 실시간 추천.'
AUTHOR         = '데일리힌트'
GA_ID          = ''   # Google Analytics ID (예: G-XXXXXXXXXX)
COUPANG_NOTICE = '이 포스팅은 쿠팡파트너스 활동의 일환으로 일정액의 수수료를 제공받습니다.'

ROOT     = Path(__file__).parent
SITE_DIR = ROOT / 'site'
DATA_DIR = ROOT

# ── 공통 CSS ──────────────────────────────────────────────────────────────────
COMMON_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Apple SD Gothic Neo','Noto Sans KR',sans-serif;background:#f7f8fa;color:#222;line-height:1.65}
a{color:inherit;text-decoration:none}
img{max-width:100%}

/* 헤더 */
header{background:#e8f4fd;border-bottom:3px solid #2196f3;padding:0 20px}
.header-inner{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;flex-wrap:wrap;gap:8px}
.logo{font-size:22px;font-weight:900;color:#1565c0}
.logo span{color:#f44336}
nav a{margin-left:20px;font-size:14px;color:#555;font-weight:600}
nav a:hover{color:#2196f3}

/* 히어로 배너 */
.hero{background:linear-gradient(135deg,#1565c0 0%,#1976d2 60%,#42a5f5 100%);color:#fff;padding:52px 20px;text-align:center}
.hero h1{font-size:32px;font-weight:900;margin-bottom:12px}
.hero p{font-size:16px;opacity:.9;max-width:600px;margin:0 auto 24px}
.hero-badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.badge{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);padding:6px 16px;border-radius:20px;font-size:13px}

/* 컨테이너 */
.container{max-width:1100px;margin:0 auto;padding:32px 20px}

/* 섹션 제목 */
.section-title{font-size:22px;font-weight:800;color:#1565c0;border-left:4px solid #2196f3;padding-left:14px;margin-bottom:20px}
.section-subtitle{font-size:14px;color:#777;margin-top:4px;font-weight:400}

/* 상품 카드 그리드 */
.product-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px;margin-bottom:40px}
.product-card{background:#fff;border-radius:12px;border:1px solid #e8ecf0;padding:20px;position:relative;transition:box-shadow .2s}
.product-card:hover{box-shadow:0 6px 20px rgba(0,0,0,.1)}
.card-badge{position:absolute;top:14px;right:14px;background:#f44336;color:#fff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:10px}
.card-badge.green{background:#43a047}
.card-badge.blue{background:#1976d2}
.card-badge.orange{background:#fb8c00}
.card-category{font-size:11px;color:#2196f3;font-weight:700;margin-bottom:6px;text-transform:uppercase}
.card-name{font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:8px;line-height:1.45}
.card-price{font-size:18px;font-weight:900;color:#f44336;margin-bottom:8px}
.card-rating{display:flex;align-items:center;gap:6px;font-size:13px;color:#666;margin-bottom:12px}
.stars{color:#ffc107}
.card-features{list-style:none;margin-bottom:14px}
.card-features li{font-size:13px;color:#555;padding:2px 0;padding-left:14px;position:relative}
.card-features li::before{content:"✓";position:absolute;left:0;color:#43a047;font-weight:700}
.btn-buy{display:block;width:100%;background:#e8140c;color:#fff;text-align:center;padding:11px;border-radius:8px;font-size:14px;font-weight:700;transition:background .15s}
.btn-buy:hover{background:#c0110a}
.btn-compare{display:block;width:100%;background:#fff;color:#1565c0;border:2px solid #1565c0;text-align:center;padding:9px;border-radius:8px;font-size:13px;font-weight:700;margin-top:8px;transition:all .15s}
.btn-compare:hover{background:#e3f2fd}

/* 비교표 */
.compare-section{background:#fff;border-radius:12px;border:1px solid #e8ecf0;padding:28px;margin-bottom:32px}
.compare-title{font-size:20px;font-weight:800;color:#1565c0;margin-bottom:20px}
.compare-table{width:100%;border-collapse:collapse;font-size:14px}
.compare-table th{background:#1565c0;color:#fff;padding:12px 16px;text-align:left;font-weight:700}
.compare-table td{padding:11px 16px;border-bottom:1px solid #f0f0f0;vertical-align:top}
.compare-table tr:hover td{background:#f8f9ff}
.compare-table .highlight{font-weight:700;color:#f44336}
.pros-cons{display:flex;gap:12px;margin-top:8px}
.pros,.cons{flex:1;padding:10px;border-radius:6px;font-size:13px}
.pros{background:#f1f8e9;border-left:3px solid #66bb6a}
.cons{background:#fff3e0;border-left:3px solid #ffa726}
.pros li,.cons li{list-style:none;padding:2px 0;padding-left:16px;position:relative}
.pros li::before{content:"👍";position:absolute;left:0;font-size:11px}
.cons li::before{content:"⚠️";position:absolute;left:0;font-size:11px}

/* 카테고리 카드 */
.cat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;margin-bottom:40px}
.cat-card{background:#fff;border-radius:12px;border:2px solid #e8ecf0;padding:24px 20px;text-align:center;transition:all .2s;cursor:pointer}
.cat-card:hover{border-color:#2196f3;transform:translateY(-2px)}
.cat-icon{font-size:36px;margin-bottom:10px}
.cat-name{font-size:16px;font-weight:700;color:#333;margin-bottom:4px}
.cat-count{font-size:13px;color:#999}

/* 공정위 배너 */
.notice{background:#fff3cd;border:1px solid #ffc107;padding:10px 16px;border-radius:8px;font-size:12px;color:#856404;margin-bottom:20px}

/* 상품 상세 */
.product-detail{background:#fff;border-radius:12px;border:1px solid #e8ecf0;padding:32px;margin-bottom:24px}
.detail-header{margin-bottom:20px}
.detail-name{font-size:24px;font-weight:900;color:#1a1a1a;margin-bottom:10px}
.detail-price{font-size:28px;font-weight:900;color:#f44336;margin-bottom:12px}
.detail-desc{font-size:15px;color:#444;line-height:1.7;margin-bottom:20px}
.detail-keywords{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.keyword-chip{background:#e3f2fd;color:#1565c0;padding:4px 12px;border-radius:14px;font-size:12px;font-weight:600}
.btn-buy-large{display:inline-block;background:#e8140c;color:#fff;padding:16px 40px;border-radius:10px;font-size:17px;font-weight:800;transition:background .15s}
.btn-buy-large:hover{background:#c0110a}

/* 검색 바 */
.search-bar{display:flex;gap:0;max-width:480px;margin:0 auto 32px}
.search-bar input{flex:1;border:2px solid #2196f3;border-right:none;padding:12px 16px;font-size:15px;border-radius:8px 0 0 8px;outline:none}
.search-bar button{background:#2196f3;color:#fff;border:none;padding:12px 20px;font-size:15px;border-radius:0 8px 8px 0;cursor:pointer;font-weight:700}

/* 푸터 */
footer{background:#1a1a2e;color:#aaa;padding:32px 20px;margin-top:48px}
.footer-inner{max-width:1100px;margin:0 auto}
.footer-inner p{font-size:13px;line-height:1.8;margin-bottom:6px}
.footer-links{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap}
.footer-links a{color:#90caf9;font-size:13px}

/* 브레드크럼 */
.breadcrumb{font-size:13px;color:#999;margin-bottom:20px}
.breadcrumb a{color:#2196f3}
.breadcrumb span{margin:0 6px}

/* 반응형 */
@media(max-width:640px){
  .hero h1{font-size:22px}
  .product-grid{grid-template-columns:1fr}
  .compare-table{font-size:13px}
  .detail-name{font-size:18px}
  header .logo{font-size:18px}
  nav a{margin-left:10px;font-size:13px}
}
"""

# ── 유틸 함수 ─────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    text = re.sub(r'[^\w가-힣\s-]', '', text).strip()
    return re.sub(r'[\s_]+', '-', text).lower()


def stars_html(rating: float) -> str:
    full  = int(rating)
    empty = 5 - round(rating)
    return '★' * full + ('½' if rating % 1 >= 0.5 else '') + '☆' * empty


def badge_class(badge: str) -> str:
    if '베스트' in badge or '스테디' in badge: return 'green'
    if '인기' in badge or '폭발' in badge:     return 'orange'
    return ''


def ga_snippet() -> str:
    if not GA_ID:
        return ''
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
            f'gtag("js",new Date());gtag("config","{GA_ID}");</script>')


def head(title: str, desc: str, canonical: str, extra_meta: str = '') -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {SITE_NAME}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title} | {SITE_NAME}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}/{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title} | {SITE_NAME}">
<meta name="twitter:description" content="{desc}">
{extra_meta}
{ga_snippet()}
<style>{COMMON_CSS}</style>
</head>"""


def header_html(active: str = '') -> str:
    def a(href, label):
        style = ' style="color:#2196f3"' if active == label else ''
        return f'<a href="{href}"{style}>{label}</a>'
    return f"""<header>
<div class="header-inner">
  <a class="logo" href="/">{SITE_NAME.replace('꿀딜','<span>꿀딜</span>')}</a>
  <nav>
    {a('/','홈')}
    {a('/categories/생활용품.html','생활용품')}
    {a('/categories/주방용품.html','주방용품')}
    {a('/compare/','비교 추천')}
  </nav>
</div>
</header>"""


def footer_html() -> str:
    year = datetime.now().year
    return f"""<footer>
<div class="footer-inner">
  <div class="footer-links">
    <a href="/">홈</a>
    <a href="/sitemap.xml">사이트맵</a>
    <a href="/categories/생활용품.html">생활용품</a>
    <a href="/categories/주방용품.html">주방용품</a>
  </div>
  <p>⚠️ {COUPANG_NOTICE}</p>
  <p>쿠팡파트너스 수수료율: 카테고리별 1~7% (구매 금액의 일정 비율)</p>
  <p>© {year} {SITE_NAME} | 상품 가격·재고는 쿠팡 사이트에서 최종 확인 바랍니다.</p>
</div>
</footer>"""


def product_card_html(p: dict, show_compare: bool = True) -> str:
    bc = badge_class(p.get('badge', ''))
    bc_cls = f' {bc}' if bc else ''
    features_li = ''.join(f'<li>{f}</li>' for f in p.get('features', [])[:3])
    compare_btn = (f'<a class="btn-compare" href="/compare/{slugify(p["compare_group"])}.html">'
                   f'🔍 비교하기</a>') if show_compare else ''
    return f"""<div class="product-card">
  <span class="card-badge{bc_cls}">{p.get('badge','추천')}</span>
  <div class="card-category">{p['category']} · {p.get('subcategory','')}</div>
  <div class="card-name">{p['short_name']}</div>
  <div class="card-price">₩{p.get('price','')}</div>
  <div class="card-rating"><span class="stars">{stars_html(p.get('rating',0))}</span>
    {p.get('rating',0)} ({p.get('review_count',0):,}개 리뷰)</div>
  <ul class="card-features">{features_li}</ul>
  <a class="btn-buy" href="{p['url']}" target="_blank" rel="nofollow noopener">
    🛒 쿠팡에서 보기</a>
  {compare_btn}
</div>"""


def schema_product(p: dict, canonical: str) -> str:
    return f"""<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"Product",
  "name":"{p['name']}",
  "description":"{p['description']}",
  "brand":{{"@type":"Brand","name":"{SITE_NAME}"}},
  "offers":{{
    "@type":"Offer",
    "priceCurrency":"KRW",
    "price":"{p.get('price','0').replace(',','')}",
    "availability":"https://schema.org/InStock",
    "url":"{p['url']}"
  }},
  "aggregateRating":{{
    "@type":"AggregateRating",
    "ratingValue":"{p.get('rating',4.0)}",
    "reviewCount":"{p.get('review_count',0)}"
  }}
}}
</script>"""


# ── 페이지 생성 함수 ───────────────────────────────────────────────────────────

def build_index(products: list):
    """메인 페이지 (index.html)"""
    # 카테고리별 카운트
    cat_counts = {}
    for p in products:
        cat_counts[p['category']] = cat_counts.get(p['category'], 0) + 1

    # 카테고리 카드
    cat_icons = {'생활용품': '🏠', '주방용품': '🍳', '주방가전': '⚡', '반려동물': '🐾'}
    cat_cards = ''
    for cat, cnt in sorted(cat_counts.items()):
        icon = cat_icons.get(cat, '📦')
        slug = slugify(cat)
        cat_cards += f"""<a class="cat-card" href="/categories/{cat}.html">
  <div class="cat-icon">{icon}</div>
  <div class="cat-name">{cat}</div>
  <div class="cat-count">{cnt}개 상품</div>
</a>"""

    # 추천 상품 (전체)
    cards = ''.join(product_card_html(p) for p in products[:6])

    # 비교 그룹 목록
    groups = {}
    for p in products:
        g = p.get('compare_group', '')
        if g:
            groups.setdefault(g, []).append(p)

    compare_links = ''
    for g, items in groups.items():
        compare_links += (f'<a class="btn-compare" style="margin:4px;display:inline-block;" '
                          f'href="/compare/{slugify(g)}.html">🔍 {g} 비교 ({len(items)}개)</a>')

    schema_site = f"""<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"WebSite",
  "name":"{SITE_NAME}",
  "url":"{SITE_URL}",
  "description":"{SITE_DESC}",
  "potentialAction":{{"@type":"SearchAction","target":"{SITE_URL}/search?q={{search_term_string}}","query-input":"required name=search_term_string"}}
}}
</script>"""

    html = f"""{head(SITE_TAGLINE, SITE_DESC, '', schema_site)}
<body>
{header_html('홈')}
<div class="hero">
  <h1>💰 {SITE_NAME}</h1>
  <p>{SITE_TAGLINE}<br>진짜 써본 사람이 비교해드립니다</p>
  <div class="hero-badges">
    <span class="badge">✅ 쿠팡파트너스 공식 링크</span>
    <span class="badge">📊 실사용 후기 기반</span>
    <span class="badge">🏷️ 가성비 TOP 상품만</span>
  </div>
</div>
<div class="container">
  <div class="notice">⚠️ {COUPANG_NOTICE}</div>

  <div class="section-title">📂 카테고리별 상품 보기
    <div class="section-subtitle">원하는 카테고리를 선택하세요</div>
  </div>
  <div class="cat-grid">{cat_cards}</div>

  <div class="section-title">🔥 지금 인기 상품
    <div class="section-subtitle">실구매 리뷰 기반 추천 상품</div>
  </div>
  <div class="product-grid">{cards}</div>

  <div class="section-title">🔍 상품 비교 추천</div>
  <div class="compare-section">
    <div class="compare-title">카테고리별 상품 비교</div>
    {compare_links}
  </div>
</div>
{footer_html()}
</body></html>"""

    (SITE_DIR / 'index.html').write_text(html, encoding='utf-8')
    print('[OK] index.html')


def build_category_pages(products: list):
    """카테고리 페이지"""
    cats = {}
    for p in products:
        cats.setdefault(p['category'], []).append(p)

    for cat, items in cats.items():
        cards = ''.join(product_card_html(p) for p in items)
        desc  = f'{cat} 가성비 추천 상품 {len(items)}개. 실구매 리뷰와 비교 정보 제공.'
        keywords_str = ', '.join(set(kw for p in items for kw in p.get('keywords', [])[:2]))

        schema_list = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{cat} 추천 상품",
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i+1, "name": p['name'], "url": f"{SITE_URL}/products/{p['id']}.html"}
                for i, p in enumerate(items)
            ]
        }

        html = f"""{head(f'{cat} 추천 상품 비교', desc, f'categories/{cat}.html',
                         f'<meta name="keywords" content="{keywords_str}">'
                         f'<script type="application/ld+json">{json.dumps(schema_list,ensure_ascii=False)}</script>')}
<body>
{header_html(cat)}
<div class="container">
  <div class="breadcrumb"><a href="/">홈</a><span>›</span>{cat}</div>
  <div class="notice">⚠️ {COUPANG_NOTICE}</div>
  <div class="section-title">🏠 {cat} 추천 상품 ({len(items)}개)
    <div class="section-subtitle">실구매 리뷰 기반 가성비 추천</div>
  </div>
  <div class="product-grid">{cards}</div>
</div>
{footer_html()}
</body></html>"""

        (SITE_DIR / 'categories' / f'{cat}.html').write_text(html, encoding='utf-8')
        print(f'[OK] categories/{cat}.html')


def build_product_pages(products: list):
    """상품 상세 페이지"""
    for p in products:
        pros_li  = ''.join(f'<li>{x}</li>' for x in p.get('pros', []))
        cons_li  = ''.join(f'<li>{x}</li>' for x in p.get('cons', []))
        kw_chips = ''.join(f'<span class="keyword-chip">{k}</span>' for k in p.get('keywords', []))
        tags     = ' '.join(f'#{t}' for t in p.get('tags', []))
        desc     = p.get('description', '')
        keywords_meta = ', '.join(p.get('keywords', []))

        compare_btn = (f'<a class="btn-compare" style="margin-top:12px;display:inline-block;" '
                       f'href="/compare/{slugify(p["compare_group"])}.html">'
                       f'🔍 {p["compare_group"]} 전체 비교 보기</a>')

        html = f"""{head(p['short_name'] + ' 추천', desc,
                         f'products/{p["id"]}.html',
                         f'<meta name="keywords" content="{keywords_meta}">'
                         + schema_product(p, f'products/{p["id"]}.html'))}
<body>
{header_html()}
<div class="container">
  <div class="breadcrumb">
    <a href="/">홈</a><span>›</span>
    <a href="/categories/{p['category']}.html">{p['category']}</a><span>›</span>
    {p['short_name']}
  </div>
  <div class="notice">⚠️ {COUPANG_NOTICE}</div>
  <div class="product-detail">
    <div class="detail-header">
      <div class="card-category">{p['category']} · {p.get('subcategory','')}</div>
      <div class="detail-name">{p['name']}</div>
      <div class="card-rating"><span class="stars">{stars_html(p.get('rating',0))}</span>
        {p.get('rating',0)}점 ({p.get('review_count',0):,}개 리뷰)</div>
      <div class="detail-price">₩{p.get('price','')}</div>
    </div>
    <div class="detail-desc">{desc}</div>
    <div class="detail-keywords">{kw_chips}</div>
    <div class="pros-cons">
      <div class="pros"><strong style="display:block;margin-bottom:6px;color:#388e3c">👍 장점</strong><ul>{pros_li}</ul></div>
      <div class="cons"><strong style="display:block;margin-bottom:6px;color:#e65100">⚠️ 단점</strong><ul>{cons_li}</ul></div>
    </div>
    <br>
    <a class="btn-buy-large" href="{p['url']}" target="_blank" rel="nofollow noopener">
      🛒 쿠팡에서 최저가 확인하기</a>
    {compare_btn}
    <br><br>
    <div style="font-size:13px;color:#999">{tags}</div>
  </div>
</div>
{footer_html()}
</body></html>"""

        (SITE_DIR / 'products' / f'{p["id"]}.html').write_text(html, encoding='utf-8')
    print(f'[OK] products/ - {len(products)}개')


def build_compare_pages(products: list):
    """비교 페이지"""
    groups = {}
    for p in products:
        g = p.get('compare_group', '')
        if g:
            groups.setdefault(g, []).append(p)

    for group_name, items in groups.items():
        if len(items) < 1:
            continue

        # 비교표 헤더/행
        headers = '<th>상품명</th><th>가격</th><th>평점</th><th>리뷰수</th><th>주요 특징</th><th>구매 링크</th>'
        rows = ''
        for p in items:
            feats = ' / '.join(p.get('features', [])[:2])
            rows += f"""<tr>
  <td><strong>{p['short_name']}</strong></td>
  <td class="highlight">₩{p.get('price','')}</td>
  <td><span class="stars">{stars_html(p.get('rating',0))}</span> {p.get('rating',0)}</td>
  <td>{p.get('review_count',0):,}개</td>
  <td style="font-size:13px">{feats}</td>
  <td><a class="btn-buy" href="{p['url']}" target="_blank" rel="nofollow noopener" style="padding:7px;font-size:13px">쿠팡 보기</a></td>
</tr>"""

        # 개별 카드
        cards = ''.join(product_card_html(p, show_compare=False) for p in items)

        desc = f'{group_name} 가성비 비교 추천 {len(items)}개 상품. 가격·평점·특징을 한눈에 비교하세요.'
        slug = slugify(group_name)
        keywords_meta = f'{group_name} 비교, {group_name} 추천, {group_name} 가성비'

        html = f"""{head(f'{group_name} 비교 추천', desc, f'compare/{slug}.html',
                         f'<meta name="keywords" content="{keywords_meta}">')}
<body>
{header_html('비교 추천')}
<div class="container">
  <div class="breadcrumb"><a href="/">홈</a><span>›</span>비교 추천<span>›</span>{group_name}</div>
  <div class="notice">⚠️ {COUPANG_NOTICE}</div>
  <div class="section-title">🔍 {group_name} 비교 추천
    <div class="section-subtitle">{len(items)}개 상품 가격·특징 한눈에 비교</div>
  </div>
  <div class="compare-section">
    <div class="compare-title">📊 {group_name} 비교표</div>
    <div style="overflow-x:auto">
    <table class="compare-table">
      <thead><tr>{headers}</tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
  </div>
  <div class="section-title">📦 상품 상세 보기</div>
  <div class="product-grid">{cards}</div>
</div>
{footer_html()}
</body></html>"""

        (SITE_DIR / 'compare' / f'{slug}.html').write_text(html, encoding='utf-8')

    # 비교 인덱스
    group_links = ''.join(
        f'<a class="cat-card" href="/compare/{slugify(g)}.html">'
        f'<div class="cat-icon">🔍</div>'
        f'<div class="cat-name">{g}</div>'
        f'<div class="cat-count">{len(v)}개 상품 비교</div></a>'
        for g, v in groups.items()
    )
    index_html = f"""{head('상품 비교 추천', '생활용품·주방용품 카테고리별 가성비 비교 추천', 'compare/')}
<body>
{header_html('비교 추천')}
<div class="container">
  <div class="breadcrumb"><a href="/">홈</a><span>›</span>비교 추천</div>
  <div class="section-title">🔍 카테고리별 비교 추천</div>
  <div class="cat-grid">{group_links}</div>
</div>
{footer_html()}
</body></html>"""
    (SITE_DIR / 'compare' / 'index.html').write_text(index_html, encoding='utf-8')
    print(f'[OK] compare/ - {len(groups)}개 그룹')


def build_sitemap(products: list):
    """sitemap.xml 생성"""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    urls  = [
        f'<url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority><lastmod>{today}</lastmod></url>',
        f'<url><loc>{SITE_URL}/categories/생활용품.html</loc><changefreq>daily</changefreq><priority>0.9</priority><lastmod>{today}</lastmod></url>',
        f'<url><loc>{SITE_URL}/categories/주방용품.html</loc><changefreq>daily</changefreq><priority>0.9</priority><lastmod>{today}</lastmod></url>',
        f'<url><loc>{SITE_URL}/compare/</loc><changefreq>weekly</changefreq><priority>0.8</priority><lastmod>{today}</lastmod></url>',
    ]
    for p in products:
        urls.append(f'<url><loc>{SITE_URL}/products/{p["id"]}.html</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{today}</lastmod></url>')

    groups = set(p.get('compare_group', '') for p in products if p.get('compare_group'))
    for g in groups:
        urls.append(f'<url><loc>{SITE_URL}/compare/{slugify(g)}.html</loc><changefreq>weekly</changefreq><priority>0.8</priority><lastmod>{today}</lastmod></url>')

    cats = set(p['category'] for p in products)
    for cat in cats:
        urls.append(f'<url><loc>{SITE_URL}/categories/{cat}.html</loc><changefreq>daily</changefreq><priority>0.9</priority><lastmod>{today}</lastmod></url>')

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'
    (SITE_DIR / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    print('[OK] sitemap.xml')


def build_robots(products: list):
    """robots.txt 생성"""
    txt = f"""User-agent: *
Allow: /
Disallow:

Sitemap: {SITE_URL}/sitemap.xml
"""
    (SITE_DIR / 'robots.txt').write_text(txt, encoding='utf-8')
    print('[OK] robots.txt')


def build_404():
    html = f"""{head('페이지를 찾을 수 없습니다', '요청하신 페이지가 없습니다.', '404.html')}
<body>
{header_html()}
<div class="container" style="text-align:center;padding:80px 20px">
  <div style="font-size:72px;margin-bottom:20px">😅</div>
  <h1 style="font-size:28px;margin-bottom:12px">페이지를 찾을 수 없어요</h1>
  <p style="color:#666;margin-bottom:28px">요청하신 페이지가 없거나 이동되었습니다.</p>
  <a href="/" class="btn-buy-large">🏠 홈으로 돌아가기</a>
</div>
{footer_html()}
</body></html>"""
    (SITE_DIR / '404.html').write_text(html, encoding='utf-8')
    print('[OK] 404.html')


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    # links.json에서 신규 상품 병합
    links_file = Path(r'D:\coupang-links\dist\links.json')
    products = json.loads((DATA_DIR / 'products.json').read_text(encoding='utf-8'))

    if links_file.exists():
        links = json.loads(links_file.read_text(encoding='utf-8'))
        existing_urls = {p['url'] for p in products}
        added = 0
        for lk in links:
            if lk.get('url','').startswith('https://link.coupang.com') and lk['url'] not in existing_urls:
                cat_map = {'주방': '주방용품', '생활용품': '생활용품', '건강': '생활용품', '기타': '생활용품'}
                cat = cat_map.get(lk.get('category',''), '생활용품')
                products.append({
                    'id': lk['id'][:8],
                    'name': lk['name'],
                    'short_name': lk['name'][:20],
                    'url': lk['url'],
                    'category': cat,
                    'subcategory': lk.get('category',''),
                    'price': '가격 확인',
                    'rating': 4.3,
                    'review_count': 0,
                    'features': [lk.get('memo', lk['name'][:30])],
                    'pros': ['쿠팡 판매 상품'],
                    'cons': ['쿠팡에서 상세 확인'],
                    'description': f'{lk["name"]} — 쿠팡 최저가 확인',
                    'keywords': [lk['name'][:15]+' 추천', lk['name'][:15]+' 가성비'],
                    'tags': [cat],
                    'compare_group': cat,
                    'rank': 99,
                    'badge': '신규'
                })
                existing_urls.add(lk['url'])
                added += 1
        if added:
            print(f'[INFO] links.json에서 {added}개 상품 추가')

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / 'categories').mkdir(exist_ok=True)
    (SITE_DIR / 'products').mkdir(exist_ok=True)
    (SITE_DIR / 'compare').mkdir(exist_ok=True)

    print(f'\n[START] {SITE_NAME} 사이트 생성 시작 - 상품 {len(products)}개\n')
    build_index(products)
    build_category_pages(products)
    build_product_pages(products)
    build_compare_pages(products)
    build_sitemap(products)
    build_robots(products)
    build_404()

    # 생성된 파일 수
    html_count = len(list(SITE_DIR.rglob('*.html')))
    print(f'\n[DONE] HTML {html_count}개 | sitemap.xml | robots.txt 생성 완료')
    print(f'[PATH] {SITE_DIR}')
    print(f'[URL]  {SITE_URL}')


if __name__ == '__main__':
    main()
