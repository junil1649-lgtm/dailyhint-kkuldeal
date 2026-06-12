# 데일리힌트 꿀딜 — GitHub Pages 배포 가이드

## 1단계: GitHub 저장소 생성

1. https://github.com/new 접속
2. Repository name: `dailyhint-kkuldeal` (정확히 이 이름 사용)
3. Public 선택
4. README 초기화 없이 생성

## 2단계: 로컬 저장소와 연결

PowerShell에서 실행:
```
cd D:\dailyhint-kkuldeal
git remote add origin https://github.com/[본인계정]/dailyhint-kkuldeal.git
git branch -M main
git push -u origin main
```

## 3단계: GitHub Pages 활성화

1. 저장소 → Settings → Pages
2. Source: **GitHub Actions** 선택
3. 저장

## 4단계: 자동 배포 확인

- push 후 Actions 탭에서 워크플로우 확인
- 완료 후: `https://[계정].github.io/dailyhint-kkuldeal/` 접속

## 5단계: Google Search Console 등록

1. https://search.google.com/search-console 접속
2. 속성 추가 → URL 접두사
3. URL: `https://[계정].github.io/dailyhint-kkuldeal`
4. HTML 태그 인증 (generate.py의 GA_ID 옆에 인증 코드 추가)
5. Sitemaps → `https://[계정].github.io/dailyhint-kkuldeal/sitemap.xml` 제출

## 매일 자동 업데이트

GitHub Actions가 매일 오전 10시(KST)에 자동으로:
1. generate.py 실행 → site/ 재생성
2. GitHub Pages에 자동 배포

## 수동으로 상품 추가하는 법

1. `D:\coupang-links` 앱에서 새 쿠팡파트너스 링크 추가
2. `python scripts/collect_products.py` 실행 → products.json 업데이트
3. `python generate.py` 실행 → site/ 재생성
4. `git add . && git commit -m "상품 추가" && git push`

## 파일 구조

```
dailyhint-kkuldeal/
├── generate.py          ← 사이트 생성기 (핵심)
├── products.json        ← 상품 데이터베이스
├── site/                ← 생성된 정적 사이트
│   ├── index.html       ← 메인 페이지
│   ├── categories/      ← 카테고리 페이지
│   ├── products/        ← 상품 상세 페이지
│   ├── compare/         ← 비교 페이지
│   ├── sitemap.xml
│   └── robots.txt
├── scripts/
│   ├── collect_products.py  ← 상품 자동 수집
│   └── submit_sitemap.py    ← 검색엔진 제출
└── .github/workflows/deploy.yml  ← GitHub Actions
```
