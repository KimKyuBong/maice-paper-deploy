# MAICE 논문 웹사이트

**수학 학습에서 질문 명료화를 지원하는 AI Agent 설계 및 개발**

고등학교 2학년 수학적 귀납법 단원 중심으로

---

## 🌐 웹사이트 주소

- **메인 사이트**: [여기에 배포 후 URL 입력]
- **GitHub 저장소**: [여기에 저장소 URL 입력]

---

## 📚 프로젝트 구조

```
MAICE논문 작성/
├── mkdocs.yml                 # MkDocs 설정 파일
├── docs/                      # 웹사이트 소스
│   ├── index.md              # 홈페이지
│   ├── feedback.md           # 피드백 페이지
│   ├── javascripts/          # JavaScript 파일
│   │   └── mathjax.js       # 수식 렌더링
│   ├── stylesheets/          # CSS 파일
│   │   └── extra.css        # 커스텀 스타일
│   └── assets/               # 이미지, 템플릿
├── chapters/                  # 논문 챕터 (원본)
│   ├── 01-introduction.md
│   ├── 02-theoretical-background.md
│   ├── 03-system-design.md
│   ├── 04-mathematical-induction-application.md
│   ├── 05-research-methods.md
│   ├── 06-results.md
│   ├── 07-discussion-conclusion.md
│   └── 08-references.md
├── .github/workflows/         # GitHub Actions
│   └── deploy.yml            # 자동 배포 워크플로우
├── setup_mkdocs.sh           # 설치 스크립트
├── deploy.sh                 # 배포 스크립트
├── requirements_mkdocs.txt   # Python 패키지
├── QUICK_START.md            # 빠른 시작 가이드
├── MKDOCS_GUIDE.md           # 상세 가이드
└── README_MKDOCS.md          # 이 파일
```

---

## 🚀 빠른 시작

### 1. 설치

```bash
chmod +x setup_mkdocs.sh
./setup_mkdocs.sh
```

### 2. 로컬 미리보기

```bash
source venv_mkdocs/bin/activate
mkdocs serve
```

http://127.0.0.1:8000 에서 확인

### 3. GitHub Pages 배포

```bash
# GitHub 저장소 생성 후
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/maice-paper.git
git push -u origin main

# 배포
mkdocs gh-deploy
```

더 자세한 내용은 [QUICK_START.md](QUICK_START.md)를 참조하세요.

---

## 📖 문서

- **[QUICK_START.md](QUICK_START.md)** - 3단계 빠른 시작
- **[MKDOCS_GUIDE.md](MKDOCS_GUIDE.md)** - 전체 가이드 (설치, 배포, 댓글 시스템)
- **[MkDocs 공식 문서](https://www.mkdocs.org/)** - MkDocs 공식 가이드
- **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** - 테마 문서

---

## ✨ 주요 기능

### 📱 사용자 친화적

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모두 지원
- **다크 모드**: 라이트/다크 테마 자동 전환
- **한글 최적화**: Noto Sans KR 폰트 사용

### 🔍 강력한 검색

- 한글 검색 지원
- 자동완성 기능
- 검색 결과 하이라이트

### 📝 수식 지원

- MathJax 통합
- LaTeX 수식 렌더링
- 인라인 및 블록 수식 지원

### 💬 댓글 시스템

- Giscus 통합 (GitHub Discussions 기반)
- 각 페이지별 댓글
- 교수님 피드백 수집용

### 📄 PDF 출력

- 전체 논문 PDF로 출력
- 페이지별 출력도 가능
- 인쇄 최적화

### 🚀 자동 배포

- GitHub Actions 자동 배포
- `main` 브랜치에 푸시하면 자동 배포
- 빌드 실패 시 알림

---

## 🔧 커스터마이징

### 색상 테마 변경

`mkdocs.yml`:

```yaml
theme:
  palette:
    primary: blue  # 원하는 색상으로 변경
    accent: blue
```

### 로고 추가

```yaml
theme:
  logo: assets/images/logo.png
  favicon: assets/images/favicon.ico
```

### Google Analytics 추가

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

---

## 📝 논문 수정 워크플로우

### 일반적인 작업 흐름

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

# 5. 배포 (자동 또는 수동)
```

### 빠른 배포

```bash
chmod +x deploy.sh
./deploy.sh "커밋 메시지"
```

---

## 🛠️ 기술 스택

- **정적 사이트 생성기**: [MkDocs](https://www.mkdocs.org/)
- **테마**: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- **수식 렌더링**: [MathJax](https://www.mathjax.org/)
- **댓글 시스템**: [Giscus](https://giscus.app/)
- **호스팅**: [GitHub Pages](https://pages.github.com/)
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)

### Python 패키지

- `mkdocs` - 핵심 프레임워크
- `mkdocs-material` - Material Design 테마
- `mkdocs-git-revision-date-localized-plugin` - 수정 날짜 표시
- `mkdocs-print-site-plugin` - PDF 출력 지원
- `pymdown-extensions` - 마크다운 확장 기능

---

## 🐛 문제 해결

### 빌드 오류

```bash
# 의존성 재설치
pip install -r requirements_mkdocs.txt --force-reinstall

# 캐시 삭제 후 빌드
mkdocs build --clean
```

### 한글 깨짐

- `mkdocs.yml`에서 `language: ko` 확인
- 파일 인코딩이 UTF-8인지 확인

### GitHub Pages 404

```bash
# gh-pages 브랜치 확인
git branch -r

# 강제 재배포
mkdocs gh-deploy --force
```

### 포트 충돌

```bash
# 다른 포트 사용
mkdocs serve -a 127.0.0.1:8001
```

---

## 📊 배포 체크리스트

배포 전 확인사항:

- [ ] `mkdocs.yml`의 `repo_url` 수정
- [ ] `docs/index.md`의 이메일 주소 추가
- [ ] `docs/feedback.md`의 이메일 주소 추가
- [ ] 모든 챕터 파일 확인
- [ ] 로컬 미리보기 테스트
- [ ] GitHub 저장소 Public 설정
- [ ] GitHub Pages 활성화 확인
- [ ] 배포 후 사이트 정상 작동 확인
- [ ] 댓글 시스템 테스트
- [ ] 교수님께 URL 전달

---

## 🤝 기여

논문 피드백은 다음 방법으로 가능합니다:

- 웹사이트의 댓글 시스템
- [피드백 페이지](feedback.md)
- GitHub Issues
- 이메일: [이메일 주소]

---

## 📞 연락처

- **저자**: 김규봉
- **소속**: 부산대학교 AI융합교육전공
- **학번**: 202373389
- **이메일**: [이메일 주소를 입력하세요]
- **GitHub**: [GitHub 프로필 링크]

---

## 📄 라이선스

이 프로젝트는 학술 논문으로, 저작권은 저자에게 있습니다.

---

## 🙏 감사

- MkDocs 개발팀
- Material for MkDocs 개발자
- 피드백을 주신 교수님과 동료 연구자들

---

## 📅 업데이트 로그

### 2025-10-30
- ✅ MkDocs 프로젝트 초기 설정
- ✅ Material 테마 적용
- ✅ 한글 최적화
- ✅ 수식 렌더링 설정
- ✅ 자동 배포 워크플로우 구성
- ✅ 문서화 완료

---

더 궁금한 점이 있으시면 [MKDOCS_GUIDE.md](MKDOCS_GUIDE.md)를 참조하거나 문의해주세요! 🚀

