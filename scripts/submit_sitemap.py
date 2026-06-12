"""
submit_sitemap.py — Google Search Console에 사이트맵 제출

사용:
  python scripts/submit_sitemap.py

필요: Google Search Console에서 사이트 소유권 인증 완료 후 실행
"""
import urllib.request, json, sys

SITE_URL    = 'https://dailyhint-kkuldeal.github.io'
SITEMAP_URL = f'{SITE_URL}/sitemap.xml'

def ping_google():
    """Google에 사이트맵 핑 전송 (인증 불필요)"""
    url = f'https://www.google.com/ping?sitemap={SITEMAP_URL}'
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            print(f'[Google 핑] {r.status} — {SITEMAP_URL}')
    except Exception as e:
        print(f'[Google 핑 오류] {e}')

def ping_bing():
    """Bing에 사이트맵 핑 전송"""
    url = f'https://www.bing.com/ping?sitemap={SITEMAP_URL}'
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            print(f'[Bing 핑] {r.status} — {SITEMAP_URL}')
    except Exception as e:
        print(f'[Bing 핑 오류] {e}')

if __name__ == '__main__':
    print('🔍 사이트맵 검색엔진 제출 중...')
    ping_google()
    ping_bing()
    print('\n✅ 완료!')
    print(f'\n📌 Google Search Console 수동 등록 방법:')
    print(f'   1. https://search.google.com/search-console 접속')
    print(f'   2. 속성 추가 → URL 접두사 → {SITE_URL}')
    print(f'   3. HTML 태그 인증 (index.html의 <head>에 meta 태그 추가)')
    print(f'   4. Sitemaps 메뉴 → {SITEMAP_URL} 제출')
