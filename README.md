# DARIMATI — Brand Page

쇼피파이에 올릴 브랜드 소개 페이지.
미리보기: **https://darimati.github.io/brand-page/**

---

# 사진 갈아끼우기 (제일 자주 하는 일)

## 딱 3단계

### 1. 두 개를 브라우저로 엽니다

| 파일 | 뭐가 보이나 |
|---|---|
| **`slots.html`** | 지금 페이지에 쓰인 사진 20장. 각 사진 아래 **슬롯 이름** (예: `c1`, `cover_img`) |
| **`library.html`** | 쓸 수 있는 사진 70장 전부. 각 사진 아래 **사진 이름** (예: `ls-08`, `kv-01`) |

> 파인더에서 파일을 더블클릭하면 브라우저로 열립니다.

### 2. 이름 두 개를 확인합니다

- `slots.html` 에서 → **바꾸고 싶은 자리**의 이름. 예: `c1`
- `library.html` 에서 → **새로 넣을 사진**의 이름. 예: `ls-08`

### 3. 터미널에 한 줄

```bash
python3 swap.py c1 ls-08
```

끝입니다. 바꾸고 다시 빌드까지 알아서 합니다.
`index.html` 을 브라우저로 열면(또는 새로고침) 바뀐 게 보입니다.

---

### 자주 나오는 상황

**이름을 잘못 쳤을 때** — 알아서 알려주고 고를 수 있는 목록을 보여줍니다.

```
$ python3 swap.py c1 ls-99
"ls-99" 이라는 사진을 library/ 와 assets/ 에서 못 찾았습니다.

고를 수 있는 것:
hero-01   hero-02   kk-01-crosswalk   kv-01   kv-02 ...
```

**슬롯 이름이 기억 안 날 때** — 그냥 이렇게 치면 목록이 나옵니다.

```bash
python3 swap.py
```

**새 사진을 추가하고 싶을 때** — JPG 파일을 `library/` 폴더에 넣기만 하면 됩니다.
그 다음 `python3 build.py` 하면 `library.html` 에 나타나고, 그때부터 `swap.py` 로 쓸 수 있습니다.
(파일 이름이 곧 사진 이름입니다. 크기는 알아서 줄여줍니다.)

**여러 장 한꺼번에** — `swap.py` 를 여러 번 치거나, `images.tsv` 를 직접 열어서
경로를 여러 줄 고치고 `python3 build.py` 한 번만 해도 됩니다.

---

# 문구 고치기

`template.html` 을 텍스트 편집기로 열고, `</style>` 아래쪽 영어 문장만 고치면 됩니다.
섹션마다 주석이 붙어 있습니다.

| 주석 | 섹션 |
|---|---|
| `<!-- COVER -->` | 표지 |
| `<!-- RIVER -->` | Many cities are shaped by a river |
| `<!-- BRIDGE MECHANICS -->` | 기술 설명 + 스펙 |
| `<!-- QUIET PERFORMANCE -->` | 브랜드 철학 |
| `<!-- MAGAZINE -->` | DARI 매거진 + 32개 다리 |
| `<!-- DARI CLUB -->` | Dari Class 세션 |

고친 뒤 `python3 build.py`.

문구 대부분은 darimati.us 에서 그대로 가져온 것이라 스토어와 톤이 맞습니다. 고칠 때 참고하세요.

---

# 쇼피파이로 옮기기

1. `python3 build.py`
2. `dist/shopify.html` 을 편집기로 엽니다
3. `<style>` 부터 파일 끝까지 전부 복사
   (맨 위 `<title>`, `<meta>`, `<link>` 폰트 두 줄은 빼세요 — 테마에 이미 있습니다)
4. 쇼피파이 관리자 → **온라인 스토어 → 페이지 → 페이지 추가** →
   내용 편집기에서 `<>` (HTML 보기) 누르고 붙여넣기

사진이 파일 안에 들어 있어서 따로 업로드할 게 없습니다.
페이지가 무겁게 느껴지면 `assets/` 사진들을 쇼피파이 **콘텐츠 → 파일** 에 올리고
`index.html` 의 `src` 를 쇼피파이 주소로 바꿔 쓰면 됩니다.

---

# 폴더 설명

```
template.html      문구와 레이아웃        ← 고치는 파일
images.tsv         슬롯 ↔ 사진 연결표      ← swap.py 가 대신 고쳐줌
library/           쓸 수 있는 사진 70장
assets/            지금 페이지에 쓰이는 사진

swap.py            사진 갈아끼우기
build.py           빌드

index.html         [자동] 미리보기 / GitHub Pages
slots.html         [자동] 지금 쓰인 사진 목록
library.html       [자동] 쓸 수 있는 사진 목록
dist/shopify.html  [자동] 쇼피파이 붙여넣기용
```

`[자동]` 표시된 건 `build.py` 가 다시 만드니까 직접 고치지 마세요.

폰트는 스토어 테마와 같은 **Bricolage Grotesque** + **Manrope** (구글 폰트) 입니다.
