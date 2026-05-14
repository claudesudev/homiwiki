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

### 문서 제목 (title) 컨벤션
**짧은 이름만** 사용. 상위 분류·부모 문서 이름은 빼고 짓는다. 브레드크럼이 경로를 보여주므로 제목에 중복할 필요 없다.

| ❌ 옛 방식 | ✅ 새 방식 |
|---|---|
| `"청라 커낼웨이"` | `"커낼웨이"` |
| `"청라/교통/철도"` | `"철도"` |
| `"온라인 환불하는 법"` | `"온라인 환불하는 법"` (생활 분류엔 같은 토픽 없으니 OK) |

### categories 컨벤션
`_categories.json`에 정의된 **leaf ID 문자열 배열**만 사용. 자유 문자열 금지.

```json
"categories": ["청라"]          ✅
"categories": ["장보기", "가게"] ✅ (한 문서가 여러 분류에 속해도 됨)
"categories": ["인천광역시"]    ❌ (자유 문자열)
```

### parent 컨벤션
**진짜 분화 관계일 때만** 사용. "같은 분류에 속한다"는 의미가 아님.
- 7호선 연장사업이 철도 문서에서 떨어져 나온 경우 → `parent: "청라-교통-철도"` ✓
- 자차가 그냥 교통 분류의 한 토픽 → `parent: null` (`categories: ["교통"]`만 있으면 됨)

## 🚀 새 문서 추가 워크플로우 (GitHub 웹UI)

### 1단계: Claude한테 요청
> "○○ 문서 만들어줘"

Claude가 `doc.json` 내용 + 필요한 이미지 알려줌.

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
새 분류가 필요하면 `_categories.json`도 같이 수정. 기존 분류만 쓰면 이 단계 건너뜀.

### 6단계: 자동 배포 대기
- Cloudflare Pages가 1~2분 안에 자동 배포
- `homiwiki.pages.dev/#/doc/문서-이름`으로 확인

## 🔄 문서 분화 (긴 문서 → 여러 짧은 문서)

예: `청라-커낼웨이`가 너무 길어져서 `패들보트` 부분을 분리

1. **새 문서 생성**: `docs/청라-커낼웨이-패들보트/doc.json`
   - `parent: "청라-커낼웨이"` 명시
   - `categories: [...]`도 적절히
2. 원본 문서에서 해당 부분 잘라내서 새 문서로 이동
3. 관련 이미지도 새 폴더로 이동 (GitHub UI에서 파일 이동은 직접 못 하니까: 새 위치에 업로드 → 옛 위치에서 삭제)
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
  "title": "커낼웨이",
  "subtitle": "Cheongna Canal Way",
  "updated": "2026-05-07",
  "categories": ["청라"],
  "parent": null,
  "contributors": [ ... ],
  "infobox": { ... },
  "toc": [ ... ],
  "content": "...",
  "related": [ ... ],
  "aliases": [ ... ]
}
```

문서의 진짜 source of truth. 모든 메타데이터가 여기 들어있다.

## 📝 라이선스 / 기여

- 콘텐츠: (TBD)
- 코드: (TBD)
- 기여 방법: 이슈 또는 PR

---

마지막 업데이트: 2026-05-14 (v3 데이터 모델 적용)
