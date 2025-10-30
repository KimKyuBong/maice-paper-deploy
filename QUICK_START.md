# 🚀 빠른 시작 가이드

MAICE 논문을 웹사이트로 배포하는 가장 빠른 방법입니다.

---

## ⚡ 3단계로 시작하기

### 1️⃣ 설치 (1분)

```bash
# 실행 권한 부여
chmod +x setup_mkdocs.sh

# 자동 설치 실행
./setup_mkdocs.sh
```

### 2️⃣ 미리보기 (30초)

```bash
# 가상환경 활성화
source venv_mkdocs/bin/activate

# 로컬 서버 시작
mkdocs serve
```

브라우저에서 `http://127.0.0.1:8000` 접속 → 논문 확인

### 3️⃣ 배포 (2분)

#### 3-1. GitHub 저장소 생성

1. GitHub에서 새 저장소 생성 (예: `maice-paper`)
2. 저장소를 Public으로 설정

#### 3-2. 설정 파일 수정

`mkdocs.yml` 파일에서 다음 부분 수정:

```yaml
repo_url: https://github.com/YOUR_USERNAME/maice-paper  # 실제 URL로
```

`docs/index.md`와 `docs/feedback.md`에서 이메일 주소 추가

#### 3-3. Git 연결 및 배포

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit"

# GitHub 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/maice-paper.git
git branch -M main
git push -u origin main

# GitHub Pages 배포
mkdocs gh-deploy
```

#### 3-4. GitHub Pages 활성화 확인

1. GitHub 저장소 → **Settings** → **Pages**
2. Source가 `gh-pages` 브랜치인지 확인
3. 배포 URL 확인: `https://YOUR_USERNAME.github.io/maice-paper/`

---

## ✅ 완료!

이제 교수님께 URL을 공유하세요:

```
🌐 논문 사이트: https://YOUR_USERNAME.github.io/maice-paper/

- 각 챕터별 페이지로 읽기 편하게 구성
- 검색 기능으로 특정 내용 빠르게 찾기
- 각 페이지에서 댓글로 피드백 가능
- PDF 출력 지원
```

---

## 🔄 이후 수정 및 재배포

논문을 수정한 후 재배포하는 방법:

### 방법 1: 자동 스크립트 (가장 빠름)

```bash
# 실행 권한 부여 (처음만)
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

### 방법 2: 수동 명령어

```bash
# 1. chapters/ 폴더의 파일 수정

# 2. Git 커밋
git add .
git commit -m "논문 수정: 내용 보완"
git push

# 3. 배포
source venv_mkdocs/bin/activate
mkdocs gh-deploy
```

---

## 📱 댓글 시스템 추가 (선택사항)

교수님 피드백을 받기 위한 댓글 시스템:

1. **GitHub Discussions 활성화**
   - 저장소 → Settings → Features → Discussions 체크

2. **Giscus 설정**
   - https://giscus.app/ko 접속
   - 저장소 입력 후 설정 코드 복사

3. **댓글 컴포넌트 추가**
   ```bash
   mkdir -p docs/overrides/partials
   ```
   
   `docs/overrides/partials/comments.html` 생성 후 Giscus 코드 붙여넣기

4. **mkdocs.yml 수정**
   ```yaml
   theme:
     custom_dir: docs/overrides
     features:
       - content.comments
   ```

---

## 🆘 문제 해결

### "Config file not found" 오류

```bash
# 프로젝트 루트 디렉토리로 이동
cd "/Users/hwansi/Library/CloudStorage/SynologyDrive-MAC/Drive/6_PrivateFolder/common/obsidian/MAICE논문 작성"
```

### 포트가 이미 사용 중

```bash
# 다른 포트 사용
mkdocs serve -a 127.0.0.1:8001
```

### GitHub Pages가 404 오류

```bash
# 다시 배포
mkdocs gh-deploy --force
```

---

## 📚 더 자세한 가이드

- [MKDOCS_GUIDE.md](MKDOCS_GUIDE.md) - 전체 가이드
- [MkDocs 공식 문서](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

---

## 💡 팁

### 자동 배포 설정 (GitHub Actions)

`.github/workflows/deploy.yml` 파일이 이미 생성되어 있습니다!

이제 `main` 브랜치에 푸시할 때마다 자동으로 배포됩니다:

```bash
git add .
git commit -m "논문 수정"
git push  # 자동으로 배포됨!
```

### 로컬 미리보기 팁

```bash
# 특정 포트로 실행
mkdocs serve -a 0.0.0.0:8000  # 다른 기기에서도 접속 가능

# 자동 새로고침 끄기
mkdocs serve --no-livereload
```

---

궁금한 점이 있으면 언제든 물어보세요! 🎉

