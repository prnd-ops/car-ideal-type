# 중고차 이상형 월드컵

내 예산으로 만나는 진짜 사고 싶은 차를 찾는 30초 이상형 월드컵. 헤이딜러 B2C 고객 유입용 바이럴 웹 테스트입니다.

- **단일 파일**: `index.html` 하나에 CSS/JS/이미지(base64)가 모두 인라인 — 별도 빌드/서버 불필요
- **공유 썸네일**: `og.png` (1200×630)
- **진행 로그 DB**: `index.html#db` 에서 분석 대시보드 + CSV/JSON 내보내기

## 로컬 실행

정적 파일이라 브라우저로 열기만 하면 됩니다. (일부 브라우저는 `file://`에서 localStorage/공유가 제한되니 간단한 서버 권장)

```bash
python3 -m http.server 8000
# http://localhost:8000/index.html
```

## 배포 (GitHub Pages)

저장소: **`prnd-ops/car-ideal-type`** → 게시 주소: **https://prnd-ops.github.io/car-ideal-type/**

- 공개용 배포 파일은 **`deploy/`** 폴더에 있습니다 (`index.html` + `og.png` 만 — 내부 문서·소스 제외).
- **저장소를 Public** 으로 두고 **Settings → Pages → Source = Deploy from a branch → `main` / `(root)`** 로 설정하면 게시됩니다.
- 업데이트는 저장소에 최신 `index.html`·`og.png`(= `deploy/` 내용)를 커밋/업로드하면 자동 반영됩니다.

### 공유 썸네일(OG) 절대 URL

`index.html` `<head>`의 `og:image` / `twitter:image` / `og:url` 은 게시 주소 기준 절대 URL로 설정돼 있습니다.

```html
<meta property="og:image" content="https://prnd-ops.github.io/car-ideal-type/og.png"/>
```

> 도메인이 바뀌면 이 값들도 함께 바꿔야 합니다. 캐시 때문에 이전 썸네일이 보이면 [카카오 디버거](https://developers.kakao.com/tool/debugger/sharing) / [페이스북 셰어 디버거](https://developers.facebook.com/tools/debug/)에서 스크래핑을 초기화하세요.

## 진행 로그 / 데이터 분석

테스트 진행 중 모든 주요 이벤트가 상세히 기록됩니다.

| type | 시점 | 주요 필드 |
|---|---|---|
| `visit` | 페이지 진입 | ua, ref, w, h, lang |
| `test_start` | 예산 STEP 진입 | run |
| `budget_set` | 예산 확정 | bMin, bMax |
| `round` | 라운드 시작(16강/8강/준결승/결승) | phase, n |
| `match_shown` | 매치 노출 | phase, idx, a/b(슬러그), an/bn(이름) |
| `pick` | 선택 | win/lose, side, **ms(결정시간)**, **timeout**, combo, score |
| `result` | 결과 발표 | gold/silver/bronze, ms(총 소요) |
| `share` | 공유 버튼 | — |
| `cta_click` | 매물/앱 버튼 | car, dest |

각 이벤트에는 `vid`(고유 방문자 id), `run`(테스트 회차 id), `ts`/`iso`(시각)가 붙습니다.

### 분석 대시보드

`https://<배포주소>/index.html#db` (또는 주소 뒤 `#db`) 로 접속하면:

- 방문자/방문/테스트 시작/완료율, 평균 결정시간, 타임아웃율, 평균 소요시간
- 1위(금메달) 분포 TOP10, 예산대 분포
- 최근 이벤트 로그
- **CSV / JSON 내보내기**, 로그 삭제

### 여러 사용자 데이터 한 곳에 모으기 (원격 수집)

> ⚠️ GitHub Pages는 정적 호스팅이라 **기본적으로 로그는 각 방문자 브라우저(localStorage)에만** 저장됩니다. `#db`는 그 기기의 데이터만 보여줍니다. 전체 방문자 데이터를 중앙에서 모으려면 아래처럼 원격 엔드포인트를 설정하세요. **(선택된 방식: Google Sheets)**

`index.html` `<script>` 최상단의 이 줄에 Apps Script 웹앱 URL만 붙여넣으면, 모든 이벤트가 해당 URL로 자동 전송(`navigator.sendBeacon`)됩니다.

```js
window.WC_LOG_ENDPOINT="";   // ← 여기에 Apps Script 웹앱 URL 붙여넣기
```

**Google Sheets(Apps Script) 설정:**

1. 새 Google 스프레드시트 → 확장 프로그램 → Apps Script
2. [`집계_AppsScript_Code.gs`](집계_AppsScript_Code.gs) 내용을 붙여넣고 저장 → **배포 → 새 배포 → 웹 앱**, 실행 계정 "나", 액세스 권한 **"모든 사용자"**
3. 발급된 웹 앱 URL(`https://script.google.com/macros/s/.../exec`)을 위 `WC_LOG_ENDPOINT`에 입력 후 `deploy/` 재배포
4. **코드 수정 시**: 배포 → **배포 관리 → 편집(연필) → 버전 "새 버전" → 배포** (이렇게 해야 `/exec` URL이 유지됨. "새 배포"는 URL이 바뀜)

**시트 컬럼(한글 헤더, 이벤트당 1행):**

```
시각 · 이벤트 · 방문자 · 세션 · 라운드 · 매치 · 선택차 · 탈락차 ·
결정시간(초) · 타임아웃 · 금메달 · 은메달 · 동메달 · 예산대 · 유입경로 · User-Agent · URL
```

- 첫 행 헤더가 `시각`이 아니면(예전 테스트 데이터 등) 스크립트가 자동으로 시트를 비우고 위 헤더로 다시 시작합니다.
- **GA4**를 쓰려면 `gtag` 스니펫을 `<head>`에 추가하고 `WC_GA_ID`에 측정 ID를 넣으면 각 이벤트가 GA4 이벤트로도 전송됩니다.
- Supabase/Firebase/자체 API 등 어떤 POST 엔드포인트든 `WC_LOG_ENDPOINT`에 넣으면 됩니다(전송은 `text/plain`).

## 파일

- `index.html` — 앱 본체(자체 완결)
- `og.png` — 공유 썸네일
- `.github/workflows/deploy.yml` — Pages 자동 배포
- `.nojekyll` — Jekyll 가공 방지
- `assets/`, `fetch_images.py`, `*.csv`, `기획_핸드오프.md` — 제작용 소스(런타임 불필요)
