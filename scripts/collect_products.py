"""
collect_products.py — 쿠팡파트너스 링크에서 상품 자동 수집 & products.json 업데이트

사용:
  python scripts/collect_products.py

동작:
  1. D:\coupang-links\dist\links.json 읽기
  2. 기존 products.json과 병합 (중복 제거)
  3. Claude API로 상품 설명·키워드·장단점 자동 생성
  4. products.json 업데이트
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

ROOT        = Path(__file__).parent.parent
LINKS_FILE  = Path(r'D:\coupang-links\dist\links.json')
PRODUCTS_FILE = ROOT / 'products.json'

sys.path.insert(0, str(ROOT))

def enrich_product_with_claude(name: str, category: str) -> dict:
    """Claude API로 상품 메타데이터 자동 생성"""
    try:
        from dotenv import load_dotenv
        load_dotenv(str(ROOT.parent / 'blog-automation' / '.env'))
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))

        prompt = f"""상품명: {name}
카테고리: {category}

아래 JSON 형식으로 정확히 반환하세요 (설명 없이):
{{
  "short_name": "20자 이내 짧은 상품명",
  "description": "100자 이내 상품 설명 (구매 유도 포함)",
  "features": ["특징1", "특징2", "특징3"],
  "pros": ["장점1", "장점2"],
  "cons": ["단점1"],
  "keywords": ["롱테일 키워드1 (상품명+추천)", "롱테일 키워드2 (상품명+비교)", "롱테일 키워드3"],
  "tags": ["태그1", "태그2", "태그3"],
  "badge": "베스트셀러|인기폭발|가성비|신제품 중 하나",
  "compare_group": "카테고리 내 비교 그룹명 (예: 에어프라이어)"
}}"""

        resp = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=512,
            messages=[{'role': 'user', 'content': prompt}],
        )
        text = resp.content[0].text.strip()
        # JSON 추출
        start = text.find('{')
        end   = text.rfind('}') + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f'  [Claude 오류] {e}')
        return {}


def collect():
    if not LINKS_FILE.exists():
        print(f'[오류] links.json 없음: {LINKS_FILE}')
        return

    links    = json.loads(LINKS_FILE.read_text(encoding='utf-8'))
    products = json.loads(PRODUCTS_FILE.read_text(encoding='utf-8')) if PRODUCTS_FILE.exists() else []

    existing_urls = {p['url'] for p in products}
    cat_map = {
        '주방':     '주방용품',
        '주방가전':  '주방용품',
        '생활용품':  '생활용품',
        '건강':     '생활용품',
        '반려동물':  '생활용품',
        '기타':     '생활용품',
    }

    added = 0
    for lk in links:
        if not lk.get('url', '').startswith('https://link.coupang.com'):
            continue
        if lk['url'] in existing_urls:
            continue

        cat = cat_map.get(lk.get('category', '기타'), '생활용품')
        print(f'[새 상품] {lk["name"][:40]}')

        enriched = enrich_product_with_claude(lk['name'], cat)

        product = {
            'id':            lk['id'][:8],
            'name':          lk['name'],
            'short_name':    enriched.get('short_name', lk['name'][:20]),
            'url':           lk['url'],
            'category':      cat,
            'subcategory':   lk.get('category', ''),
            'price':         '가격 확인',
            'rating':        4.3,
            'review_count':  0,
            'features':      enriched.get('features', [lk['name'][:30]]),
            'pros':          enriched.get('pros', ['쿠팡 판매 상품']),
            'cons':          enriched.get('cons', ['쿠팡에서 상세 확인']),
            'description':   enriched.get('description', f'{lk["name"]} 쿠팡 최저가'),
            'keywords':      enriched.get('keywords', [lk['name'][:15]+' 추천']),
            'tags':          enriched.get('tags', [cat]),
            'compare_group': enriched.get('compare_group', cat),
            'rank':          99,
            'badge':         enriched.get('badge', '신규'),
            'memo':          lk.get('memo', ''),
            'created_at':    lk.get('created_at', datetime.now().isoformat()),
        }
        products.append(product)
        existing_urls.add(lk['url'])
        added += 1

    if added:
        PRODUCTS_FILE.write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\n✅ {added}개 상품 추가 완료 → products.json 업데이트')
    else:
        print('신규 상품 없음')


if __name__ == '__main__':
    collect()
