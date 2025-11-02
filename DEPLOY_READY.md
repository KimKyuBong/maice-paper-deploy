# 🚀 MAICE 논문 배포용 폴더

이 폴더는 GitHub Pages 배포를 위해 준비된 깨끗한 버전입니다.

---

## 📦 포함된 내용

### ✅ 핵심 파일
- `mkdocs.yml` - MkDocs 설정
- `requirements_mkdocs.txt` - Python 패키지
- `.gitignore` - Git 무시 파일
- `README.md` - 프로젝트 메인 README

### ✅ 논문 콘텐츠
- `chapters/` - 논문 8개 챕터 (01~08)
- `부록_A~D.md` - 4개 부록 파일
- `docs/` - 웹사이트 소스 (index.md, feedback.md 등)

### ✅ 설문 자료
- `MAICE_사후설문지.md`
- `학생_설문조사지.md`
- `설문지_개선사항_요약.md`

### ✅ 시스템 문서
- `docs/architecture/` - 시스템 아키텍처
- `docs/api/` - API 문서
- `docs/experiments/` - 실험 자료
- `docs/deployment/` - 배포 가이드

### ✅ 스크립트 & 가이드
- `setup_mkdocs.sh` - 자동 설치 스크립트
- `deploy.sh` - 빠른 배포 스크립트
- `QUICK_START.md` - 빠른 시작 가이드
- `MKDOCS_GUIDE.md` - 상세 가이드

### ✅ GitHub Actions
- `.github/workflows/deploy.yml` - 자동 배포 워크플로우

---

## 🚀 배포 3단계

### 1️⃣ 로컬 테스트 (2분)

```bash
# 이 폴더로 이동
cd maice-paper-deploy

# 설치
./setup_mkdocs.sh

# 미리보기
source venv_mkdocs/bin/activate
mkdocs serve
```

브라우저에서 http://127.0.0.1:8000 확인

### 2️⃣ GitHub 저장소 생성 (2분)

1. https://github.com 에서 새 저장소 생성
2. 저장소 이름: `maice-paper` (또는 원하는 이름)
3. **Public**으로 설정 (GitHub Pages 무료)
4. README 추가 안 함 (이미 있음)

### 3️⃣ 배포 (3분)

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: MAICE 논문 웹사이트"

# GitHub 연결 (YOUR_USERNAME을 실제 이름으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/maice-paper.git
git branch -M main
git push -u origin main

# GitHub Pages 배포
mkdocs gh-deploy
```

**배포 완료!** 🎉

웹사이트: `https://YOUR_USERNAME.github.io/maice-paper/`

---

## 📝 배포 전 체크리스트

배포하기 전에 확인하세요:

- [ ] `mkdocs.yml`에서 GitHub 저장소 URL 수정
- [ ] `docs/index.md`에서 이메일 주소 추가
- [ ] `docs/feedback.md`에서 이메일 주소 추가
- [ ] 로컬 테스트 완료 (`mkdocs serve`)
- [ ] GitHub 저장소 생성 완료
- [ ] 저장소가 Public인지 확인

---

## 🔄 이후 수정 및 재배포

```bash
# 1. chapters/ 또는 docs/ 폴더의 파일 수정

# 2. 빠른 배포
./deploy.sh

# 또는 수동으로
git add .
git commit -m "논문 내용 수정"
git push
mkdocs gh-deploy
```

---

## 📊 폴더 통계

- **총 용량**: 약 850KB (가볍습니다!)
- **마크다운 파일**: 60+ 개
- **챕터**: 8개
- **부록**: 4개
- **시스템 문서**: 20+ 페이지

---

## 💡 팁

### 자동 배포 활성화

이 폴더에는 `.github/workflows/deploy.yml`이 포함되어 있습니다.

GitHub에 푸시하면 **자동으로 배포**됩니다!

```bash
git add .
git commit -m "Update"
git push  # 자동 배포됨!
```

### 댓글 시스템 추가

교수님 피드백을 위해 Giscus 댓글 시스템을 추가하려면:

`MKDOCS_GUIDE.md` 파일의 5장 참조

---

## 🆘 문제 해결

### Python 버전

Python 3.8 이상 필요합니다.

```bash
python3 --version
```

### 빌드 에러

```bash
# 의존성 재설치
pip install -r requirements_mkdocs.txt --force-reinstall
```

### GitHub Pages 404

```bash
# 다시 배포
mkdocs gh-deploy --force
```

---

## 📞 연락처

- **저자**: 김규봉
- **소속**: 부산대학교 AI융합교육전공
- **학번**: 202373389

---

## 📚 더 알아보기

- [QUICK_START.md](QUICK_START.md) - 3단계 빠른 시작
- [MKDOCS_GUIDE.md](MKDOCS_GUIDE.md) - 전체 가이드
- [README.md](README.md) - 프로젝트 정보

---

이제 배포할 준비가 완료되었습니다! 🚀

질문이 있으시면 위 가이드 문서를 참조하세요.



