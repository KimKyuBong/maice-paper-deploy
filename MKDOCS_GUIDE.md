# MkDocs 배포 가이드

이 가이드는 MAICE 논문을 MkDocs를 사용하여 웹사이트로 배포하는 전체 과정을 안내합니다.

---

## 🎯 목차

1. [로컬 환경 설정](#1-로컬-환경-설정)
2. [미리보기 및 테스트](#2-미리보기-및-테스트)
3. [GitHub 저장소 설정](#3-github-저장소-설정)
4. [GitHub Pages 배포](#4-github-pages-배포)
5. [댓글 시스템 추가 (Giscus)](#5-댓글-시스템-추가-giscus)
6. [커스터마이징](#6-커스터마이징)
7. [문제 해결](#7-문제-해결)

---

## 1. 로컬 환경 설정

### 1.1 자동 설정 (추천)

```bash
# 실행 권한 부여
chmod +x setup_mkdocs.sh

# 스크립트 실행
./setup_mkdocs.sh
```

### 1.2 수동 설정

```bash
# 1. Python 가상환경 생성
python3 -m venv venv_mkdocs
source venv_mkdocs/bin/activate

# 2. 패키지 설치
pip install -r requirements_mkdocs.txt

# 또는 개별 설치
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-git-revision-date-localized-plugin
pip install mkdocs-print-site-plugin
pip install pymdown-extensions
```

---

## 2. 미리보기 및 테스트

### 2.1 로컬 서버 실행

```bash
# 가상환경 활성화 (필요시)
source venv_mkdocs/bin/activate

# MkDocs 서버 시작
mkdocs serve
```

브라우저에서 `http://127.0.0.1:8000` 접속

### 2.2 실시간 수정

- 파일을 수정하면 자동으로 새로고침됩니다
- `chapters/` 폴더의 마크다운 파일을 직접 수정하세요
- 변경사항이 즉시 브라우저에 반영됩니다

### 2.3 정적 사이트 빌드 테스트

```bash
# 빌드 실행
mkdocs build

# 빌드 결과 확인
ls site/
```

빌드된 파일은 `site/` 폴더에 생성됩니다.

---

## 3. GitHub 저장소 설정

### 3.1 GitHub 저장소 생성

1. GitHub에 로그인
2. 새 저장소 생성 (예: `maice-paper`)
3. 저장소 URL 복사 (예: `https://github.com/username/maice-paper`)

### 3.2 로컬 Git 설정

```bash
# Git 초기화 (처음만)
git init

# .gitignore 생성
cat > .gitignore << EOF
# MkDocs
site/
venv_mkdocs/

# Python
*.pyc
__pycache__/
*.log
.DS_Store

# 개인 정보
*.json
*.env
EOF

# GitHub 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/maice-paper.git

# 파일 커밋
git add .
git commit -m "Initial commit: MkDocs 프로젝트 설정"
git branch -M main
git push -u origin main
```

### 3.3 mkdocs.yml 설정 업데이트

`mkdocs.yml` 파일에서 다음 항목을 수정하세요:

```yaml
# Repository
repo_name: maice-paper
repo_url: https://github.com/YOUR_USERNAME/maice-paper  # 실제 URL로 변경
edit_uri: edit/main/docs/

# Extra
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/YOUR_USERNAME  # 실제 GitHub 프로필로 변경
```

---

## 4. GitHub Pages 배포

### 4.1 한 번에 배포 (가장 쉬움)

```bash
# GitHub Pages로 자동 배포
mkdocs gh-deploy
```

이 명령어는:
1. `site/` 폴더에 사이트를 빌드
2. `gh-pages` 브랜치를 자동 생성
3. 빌드된 파일을 푸시
4. GitHub Pages 활성화

### 4.2 GitHub Pages 설정 확인

1. GitHub 저장소 페이지로 이동
2. **Settings** → **Pages** 클릭
3. **Source**가 `gh-pages` 브랜치로 설정되어 있는지 확인
4. 배포 완료 후 URL 확인: `https://YOUR_USERNAME.github.io/maice-paper/`

### 4.3 GitHub Actions로 자동 배포 (선택사항)

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy MkDocs

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: |
          pip install mkdocs
          pip install mkdocs-material
          pip install mkdocs-git-revision-date-localized-plugin
          pip install mkdocs-print-site-plugin
          pip install pymdown-extensions
      
      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
```

이제 `main` 브랜치에 푸시할 때마다 자동으로 배포됩니다!

---

## 5. 댓글 시스템 추가 (Giscus)

### 5.1 Giscus 설정

1. **GitHub Discussions 활성화**
   - 저장소 → **Settings** → **Features** 
   - **Discussions** 체크박스 활성화

2. **Giscus 앱 설치**
   - https://giscus.app/ko 접속
   - 저장소 선택: `YOUR_USERNAME/maice-paper`
   - **Discussion 카테고리**: Announcements 선택
   - **Discussion 제목과 매핑**: pathname 선택

3. **설정 코드 복사**
   - 페이지 하단의 `<script>` 태그 코드 복사

### 5.2 MkDocs에 Giscus 추가

`docs/overrides/partials/comments.html` 파일 생성:

```bash
mkdir -p docs/overrides/partials
```

```html
<!-- docs/overrides/partials/comments.html -->
<h2 id="__comments">💬 댓글</h2>

<script src="https://giscus.app/client.js"
        data-repo="YOUR_USERNAME/maice-paper"
        data-repo-id="YOUR_REPO_ID"
        data-category="Announcements"
        data-category-id="YOUR_CATEGORY_ID"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="ko"
        crossorigin="anonymous"
        async>
</script>
```

`mkdocs.yml`에 추가:

```yaml
theme:
  custom_dir: docs/overrides
  features:
    - content.comments  # 댓글 기능 활성화
```

---

## 6. 커스터마이징

### 6.1 색상 테마 변경

`mkdocs.yml`:

```yaml
theme:
  palette:
    primary: blue  # indigo, blue, teal, green 등
    accent: blue
```

### 6.2 로고 추가

```yaml
theme:
  logo: assets/images/logo.png
  favicon: assets/images/favicon.ico
```

이미지는 `docs/assets/images/` 폴더에 저장하세요.

### 6.3 Google Analytics 추가

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX  # Google Analytics ID
```

---

## 7. 문제 해결

### 7.1 빌드 오류

**오류**: `Config file 'mkdocs.yml' does not exist`

```bash
# 현재 위치 확인
pwd

# 프로젝트 루트로 이동
cd /path/to/MAICE논문\ 작성/
```

### 7.2 한글 깨짐

`mkdocs.yml`에서 다음 확인:

```yaml
theme:
  language: ko
```

### 7.3 수식이 렌더링 안 됨

- `docs/javascripts/mathjax.js` 파일 확인
- `mkdocs.yml`의 `extra_javascript` 섹션 확인
- 수식은 `\( ... \)` (인라인) 또는 `\[ ... \]` (블록) 형식 사용

### 7.4 GitHub Pages 404 오류

```bash
# gh-pages 브랜치 확인
git branch -r

# 다시 배포
mkdocs gh-deploy --force
```

### 7.5 로컬 서버 포트 충돌

```bash
# 다른 포트 사용
mkdocs serve -a 127.0.0.1:8001
```

---

## 📝 일상적인 워크플로우

### 논문 수정 및 배포

```bash
# 1. 가상환경 활성화
source venv_mkdocs/bin/activate

# 2. 로컬 서버 시작 (미리보기)
mkdocs serve

# 3. chapters/ 폴더의 파일 수정

# 4. 변경사항 커밋
git add .
git commit -m "논문 수정: 3장 내용 보완"
git push

# 5. GitHub Pages 배포
mkdocs gh-deploy
```

### 빠른 배포 (스크립트)

`deploy.sh` 파일 생성:

```bash
#!/bin/bash
set -e

echo "🚀 배포 시작..."

# 변경사항 커밋
git add .
git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
git push

# GitHub Pages 배포
source venv_mkdocs/bin/activate
mkdocs gh-deploy

echo "✅ 배포 완료!"
echo "🌐 사이트: https://YOUR_USERNAME.github.io/maice-paper/"
```

실행:

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🎓 교수님께 공유하기

배포가 완료되면 다음 정보를 교수님께 전달하세요:

```
안녕하세요 교수님,

논문을 웹사이트로 배포하였습니다.

🌐 논문 사이트: https://YOUR_USERNAME.github.io/maice-paper/

- 각 챕터별로 페이지가 나뉘어 있어 편하게 읽으실 수 있습니다
- 우측 상단 검색창으로 특정 내용을 빠르게 찾으실 수 있습니다
- 각 페이지 하단의 댓글로 피드백을 남겨주실 수 있습니다
- PDF 출력도 가능합니다

피드백은 다음 방법으로 주시면 감사하겠습니다:
1. 각 페이지 하단 댓글
2. 피드백 페이지: https://YOUR_USERNAME.github.io/maice-paper/feedback/
3. 이메일: [이메일 주소]

감사합니다.
```

---

## 📚 추가 리소스

- [MkDocs 공식 문서](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Pages 가이드](https://docs.github.com/ko/pages)
- [Giscus 댓글 시스템](https://giscus.app/ko)

---

## ✅ 체크리스트

배포 전 확인사항:

- [ ] `mkdocs.yml`에서 GitHub 저장소 URL 수정
- [ ] `docs/index.md`에서 이메일 주소 추가
- [ ] `docs/feedback.md`에서 이메일 주소 추가
- [ ] 모든 챕터 파일이 `chapters/` 폴더에 있는지 확인
- [ ] 로컬에서 `mkdocs serve`로 미리보기 테스트
- [ ] GitHub 저장소 생성 및 푸시
- [ ] `mkdocs gh-deploy` 실행
- [ ] 배포된 사이트 정상 작동 확인
- [ ] Giscus 댓글 시스템 테스트
- [ ] 교수님께 URL 전달

---

궁금한 점이 있으시면 언제든 물어보세요! 🚀

