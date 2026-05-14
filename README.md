# homiwiki

호미위키. 청라 지역 + AI + 생활정보를 다루는 한국어 위키.

## 📁 폴더 구조

```
homiwiki/
├── README.md              ← 이 파일
├── index.html             ← 프론트엔드 (정적 SPA)
├── docs/                  ← 모든 문서
│   ├── _index.json        ← 문서 ID 목록 + 리다이렉트
│   ├── _categories.json   ← 분류 트리 정의
│   ├── _shared/           ← 여러 문서가 공유하는 이미지 (필요 시)
│   ├── 클로드/
│   │   └── doc.json
│   ├── 청라-커낼웨이/
│   │   ├── doc.json       ← 본문
│   │   ├── index.webp     ← 인포박스 대표 이미지
│   │   ├── overview.webp  ← 본문 figure
│   │   ├── ice.webp
│   │   └── paddleboat.webp
│   ├── 청라-유명인/
│   │   └── doc.json
│   └── 온라인-환불/
│       └── doc.json
├── gallery/               ← 갤러리 (별도 시스템)
│   ├── index.json
│   └── *.webp
└── scripts/               ← 자동화 스크립트
    └── verify.py          ← 무결성 검증
```

## 📐 컨벤션

### 폴더명 (= 문서 ID)
- **한글 + 하이픈** 사용. 예: `청라-커낼웨이`, `온라인-환불`
- 영문 ID도 가능 (`claude` 같은 고유명사). 단, 소문자.
- **공백 금지, 언더바(`_`) 금지**
- 분화 시: `{부모}-{하위}` 평면 구조. 예: `청라-커낼웨이-패들보트`

### 파일명
- **영문 통일**. 한글 파일명 금지.
- 본문 파일은 `doc.json` 으로 통일
- 이미지는 역할 명시. 예: `index.webp`(대표), `overview.webp`(개요), `ice.webp`(특정 주제)

### 이미지 위치
- 한 문서가 쓰는 이미지 → 그 문서 폴더 안
- 여러 문서가 공유하는 이미지 → `docs/_shared/`
- 본문 안에서는 **파일명만** 참조: `<img src="overview.webp">`
- 프론트엔드가 자동으로 `docs/{문서ID}/` 경로 보정함

### 이미지 태그 필수 속성
모든 `<img>` 태그에 width/height 명시 (레이아웃 점프 방지):
```html
<img src="overview.webp" alt="설명" loading="lazy" width="1200" height="675">
```

## 🧱 doc.json 필드 컨벤션

각 필드가 무엇을 위한 것인지 명확히 — **헷갈리지 말 것.**

### `title` — 그 문서의 고유한 이름
사람이 머릿속에서 그 대상을 부르는 자연스러운 이름. **줄이지 않는다.**
- ✅ `"청라 커낼웨이"` (사람이 그렇게 부름)
- ✅ `"서울 지하철 7호선 청라 연장사업"` (정식 명칭)
- ✅ `"온라인 환불하는 법"` (자연스러운 표현)
- ❌ `"커낼웨이"` (분류 경로에 청라가 있으니 빼자 = 잘못된 생각. 검색·SNS·외부 링크에선 컨텍스트 없음)

브레드크럼은 분류 경로를 보여주는 거고, title은 문서의 이름. **둘은 다른 차원이지 중복이 아님.**

### `subtitle` — 영문 부제 (옵션)
영문 표기나 부연. 없으면 생략.

### `categories` — 분류 트리의 leaf ID 배열
`_categories.json`에 정의된 ID만 사용. 자유 문자열 금지.

```json
"categories": ["청라"]              ✅
"categories": ["장보기", "가게"]    ✅ (여러 분류 가능)
"categories": ["인천광역시"]        ❌ (자유 문자열)
```

### `parent` — 분화 관계 (대부분 `null`)
**"이 문서는 부모 문서가 너무 길어져서 떼낸 것"** 일 때만 사용.
- 7호선 연장사업이 철도 문서에서 분리됨 → `parent: "청라-교통-철도"` ✓
- 자차는 그냥 교통 분류의 한 토픽 → `parent: null` ✓
- "같은 분류" ≠ "parent". 분류는 `categories`로만 표현.

### `aliases` — 검색 키워드 변형 배열
호미위키 내 검색 자동완성에 잡힐 키워드들. 사람들이 같은 대상을 다르게 부르는 변형 + 약칭 + 표기 차이.

**3-10개 정도 채우는 게 정상. 빈 배열은 잘못된 디폴트.**

| 종류 | 예시 (커낼웨이) | 예시 (클로드) |
|---|---|---|
| 흔한 변형/오기 | 커낼, 커널, 캐널 | 클로드 4, 클로드 AI |
| 약칭/줄임말 | 청라 수로 | Claude |
| 영문 표기 | Canal Way, canalway | Anthropic Claude |
| 공식 명칭 | 청라국제도시 문화공원 | (해당 없음) |
| 별명/SEO 키워드 | 청라 베네치아 | 클로드 코드 |
| 합성 | 청라 커낼웨이 | 클로드 옵서스 |

**무엇을 안 넣을지:**
- title이랑 완전 똑같은 것 (이미 매치됨)
- 너무 일반적인 단어 ("문서", "공원" 단독) — 노이즈
- 동명이인 (예: 클로드 섀넌 — 검색 노이즈)

### `related` — 강조용 관련 문서 (대부분 비어있어도 됨)
본문에서 언급한 다른 호미위키 문서 중 **특별히 강조**하고 싶은 것 2~6개. 비워두는 게 일반적.

```json
"related": [
  { "id": "anthropic", "desc": "Claude의 본진. 안전성 집착파" },
  { "id": "chatgpt", "desc": "수능 경쟁자. 항상 비교당하는 사이" }
]
```

본문에서 `data-link`로 연결된 문서가 이미 있으면 굳이 related에 또 넣을 필요 없음. **관련 없으면 빈 배열이 정상.**

### `infobox`, `toc`, `content`, `contributors`
기존대로 유지. 자세한 건 기존 문서 참고.

## 🚀 새 문서 추가 워크플로우 (GitHub 웹UI)

### 1단계: Claude한테 요청
> "○○ 문서 만들어줘"

Claude가 `doc.json` 내용 + 필요한 이미지 알려줌. 이때 위 컨벤션 따라야 함:
- title은 자연스러운 이름 그대로
- categories는 `_categories.json` leaf ID
- parent는 분화가 아니면 null
- aliases는 3-10개 채우기

### 2단계: 폴더 + doc.json 생성
1. GitHub 저장소 → 우상단 **Add file** → **Create new file**
2. 파일명 입력란에: `docs/문서-이름/doc.json`
   - 슬래시(`/`) 입력 순간 폴더 자동 생성됨
3. Claude가 준 JSON 내용 붙여넣기
4. 하단 **Commit changes** 클릭

### 3단계: 이미지 업로드
1. 방금 만든 `docs/문서-이름/` 폴더 클릭해서 진입
2. **Add file** → **Upload files**
3. 다운로드 폴더에서 이미지 드래그 앤 드롭
4. **Commit changes** 클릭

### 4단계: `_index.json` 에 ID 추가
1. `docs/_index.json` 클릭
2. 우상단 연필 아이콘으로 편집
3. `docs` 배열에 새 ID 한 줄 추가:
```json
{
  "version": 3,
  "docs": [
    "클로드",
    "청라-커낼웨이",
    "새-문서-id"
  ],
  ...
}
```
4. **Commit changes**

> **메타데이터(title, categories 등)는 `_index.json`에 안 적습니다.** 각 문서의 `doc.json`이 source of truth.

### 5단계: 분류 트리 갱신 (필요 시)
새 분류가 필요하면 `_categories.json`도 같이 수정. 기존 분류만 쓰면 건너뜀.

### 6단계: 자동 배포 대기
- Cloudflare Pages가 1~2분 안에 자동 배포
- `homiwiki.pages.dev/#/doc/문서-이름`으로 확인

## 🔄 문서 분화 (긴 문서 → 여러 짧은 문서)

예: `청라-커낼웨이`가 너무 길어져서 `패들보트` 부분을 분리

1. **새 문서 생성**: `docs/청라-커낼웨이-패들보트/doc.json`
   - `parent: "청라-커낼웨이"` 명시
   - `categories: [...]`도 적절히
2. 원본 문서에서 해당 부분 잘라내서 새 문서로 이동
3. 관련 이미지도 새 폴더로 이동
4. 원본 문서에 링크 박기:
```html
자세한 내용은 <a data-link="청라-커낼웨이-패들보트">패들보트</a> 문서 참조.
```
5. `_index.json`의 `docs` 배열에 새 ID 추가

## 🛡️ 인코딩 안전 규칙

호미위키는 **NFC 인코딩만 허용**합니다 (Mac/Windows 충돌 방지).

- ✅ **항상 GitHub 웹UI에서 폴더 생성**: 서버가 NFC로 만들어주므로 안전
- ❌ Windows 탐색기에서 만든 폴더를 깃에 푸시 (인코딩 섞임 위험)
- ❌ 옛날 Mac (HFS+) 에서 만든 폴더 직접 푸시
- 만약 직접 푸시해야 한다면 Mac에서 1회만 다음 설정:
  ```bash
  git config --global core.precomposeunicode true
  ```

## 🔍 무결성 검증

```bash
python3 scripts/verify.py
```

검증 항목:
- 모든 폴더에 `doc.json` 존재
- `_index.json`의 모든 ID와 폴더 일치
- `doc.json`이 참조하는 이미지가 실제 존재
- 사용 안 되는 고아 이미지 검출
- 깨진 위키링크 (`data-link`) 검출
- NFD 인코딩 파일/폴더 검출

## 📊 데이터 스키마

### `_index.json` (v3, 슬림)
```json
{
  "version": 3,
  "updated": "2026-05-14",
  "docs": ["문서-id-1", "문서-id-2", ...],
  "redirects": {
    "옛-id": "새-id"
  }
}
```

문서 ID 목록 + 옛 URL 호환용 리다이렉트만 담는다. 메타데이터는 각 `doc.json`에 있음.

### `_categories.json`
분류 트리 정의. 호미위키의 모든 분류는 여기 등록된 ID만 사용.

```json
{
  "version": 1,
  "tree": {
    "인천": {
      "label": "인천",
      "hidden_in_breadcrumb": true,
      "children": {
        "청라": {
          "label": "청라",
          "children": {
            "교통": { "label": "교통" },
            "편의시설": { "label": "편의시설" }
          }
        }
      }
    },
    "AI": { "label": "AI" }
  }
}
```

- `label`: 브레드크럼 등에 표시될 한글 라벨
- `hidden_in_breadcrumb`: `true`면 그 단계는 브레드크럼에 표시 안 함 (현재 `인천` 노드가 이 상태 — 추후 다른 지역 추가될 때 노출 예정)
- `children`: 하위 분류 (선택)

### `doc.json` (각 문서)
```json
{
  "title": "청라 커낼웨이",
  "subtitle": "Cheongna Canal Way",
  "updated": "2026-05-07",
  "categories": ["청라"],
  "parent": null,
  "contributors": [ ... ],
  "infobox": { ... },
  "toc": [ ... ],
  "content": "...",
  "related": [ ... ],
  "aliases": [ "커낼웨이", "커낼", "청라 수로", ... ]
}
```

문서의 진짜 source of truth. 모든 메타데이터가 여기 들어있다.

## 🧠 다음 세션 Claude에게 — 컨벤션 위반 주의

새 문서 만들 때 다음 실수를 하지 말 것:

1. **title을 줄이지 말 것.** "청라 커낼웨이"를 "커낼웨이"로 줄이는 등의 행위 금지. 자연스러운 이름 그대로.
2. **aliases를 빈 배열로 두지 말 것.** 기존 문서가 비어 있어도 그게 의도된 디폴트가 아니다. 3-10개 채워라.
3. **related는 비워둬도 된다.** 무리해서 채우지 말 것. 본문에서 진짜 언급한 강조 대상만.
4. **categories는 `_categories.json` leaf ID만.** 자유 문자열 금지.
5. **parent는 분화일 때만.** "같은 분류" 의미로 쓰지 말 것.

## 📝 라이선스 / 기여

- 콘텐츠: (TBD)
- 코드: (TBD)
- 기여 방법: 이슈 또는 PR

---

마지막 업데이트: 2026-05-14 (v3 데이터 모델 + aliases·related 컨벤션 정합)
