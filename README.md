# homiwiki

호미위키. 청라 지역 + AI + 생활정보를 다루는 한국어 위키.

## 📁 폴더 구조

```
homiwiki/
├── README.md              ← 이 파일
├── index.html             ← 프론트엔드 (정적 SPA)
├── docs/                  ← 모든 문서
│   ├── _index.json        ← 문서 인덱스 (메타 + 리다이렉트)
│   ├── _shared/           ← 여러 문서가 공유하는 이미지
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

### 4단계: `_index.json` 갱신
1. `docs/_index.json` 클릭
2. 우상단 연필 아이콘으로 편집
3. `docs` 객체에 새 항목 추가:
```json
"새-문서-id": {
  "title": "문서 제목",
  "subtitle": "Subtitle",
  "category": "카테고리",
  "parent": null,
  "children": [],
  "updated": "2026-05-08"
}
```
4. **Commit changes**

### 5단계: 자동 배포 대기
- Cloudflare Pages가 1~2분 안에 자동 배포
- `homiwiki.com/문서-이름`으로 확인

## 🔄 문서 분화 (긴 문서 → 여러 짧은 문서)

예: `청라-커낼웨이`가 너무 길어져서 `패들보트` 부분을 분리

1. **새 문서 생성**: `docs/청라-커낼웨이-패들보트/doc.json`
2. 원본 문서에서 해당 부분 잘라내서 새 문서로 이동
3. 관련 이미지도 새 폴더로 이동 (GitHub UI에서 파일 이동은 직접 못 하니까: 새 위치에 업로드 → 옛 위치에서 삭제)
4. 원본 문서에 링크 박기:
```html
자세한 내용은 <a data-link="청라-커낼웨이-패들보트">패들보트</a> 문서 참조.
```
5. `_index.json`에 새 문서 추가, 부모 항목의 `children` 배열에 새 ID 추가

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

## 📊 _index.json v2 스키마

```json
{
  "version": 2,
  "updated": "2026-05-08",
  "docs": {
    "문서-id": {
      "title": "문서 제목",
      "subtitle": "영문 부제 (옵션)",
      "category": "카테고리",
      "parent": "부모 문서 ID 또는 null",
      "children": ["자식 문서 ID 목록"],
      "updated": "YYYY-MM-DD"
    }
  },
  "redirects": {
    "옛-id": "새-id"
  }
}
```

`redirects`: 옛 ID로 들어온 요청을 새 ID로 자동 리다이렉트. 마이그레이션 후 외부 링크 호환성 유지용.

## 📝 라이선스 / 기여

- 콘텐츠: (TBD)
- 코드: (TBD)
- 기여 방법: 이슈 또는 PR

---

마지막 업데이트: 2026-05-08
