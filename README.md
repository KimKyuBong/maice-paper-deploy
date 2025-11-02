# MAICE 논문 웹사이트

**수학 학습에서 질문 명료화를 지원하는 AI Agent 설계 및 개발**

고등학교 2학년 수학적 귀납법 단원 중심으로

---

## 🌐 웹사이트 주소

- **메인 사이트**: https://kimkyubong.github.io/maice-paper-deploy/
- **GitHub 저장소**: https://github.com/KimKyuBong/maice-paper-deploy.git

---

## 📚 프로젝트 구조

```
maice-paper-deploy/
├── mkdocs.yml                 # MkDocs 설정 파일
├── docs/                      # 웹사이트 소스
│   ├── index.md              # 홈페이지
│   ├── chapters/             # 논문 장별 파일
│   │   ├── 01-introduction.md                    # 서론
│   │   ├── 02-theoretical-background.md          # 이론적 배경
│   │   ├── 03-system-design.md                   # MAICE 교육 시스템 아키텍처
│   │   ├── 04-system-implementation.md           # MAICE 시스템 구현 ⭐ NEW
│   │   ├── 05-mathematical-induction-application.md  # 수학적 귀납법 적용
│   │   ├── 06-research-methods.md                # 연구 방법
│   │   ├── 07-results.md                         # 결과
│   │   ├── 08-discussion-conclusion.md           # 논의 및 결론
│   │   └── 09-references.md                      # 참고문헌
│   ├── prompts/              # AI 에이전트 프롬프트 분석
│   │   ├── README.md                             # 프롬프트 상세 설명 (500줄)
│   │   ├── PROMPT_ANALYSIS_SUMMARY.md            # 프롬프트 분석 요약
│   │   ├── RUBRIC_PROMPT_CORRELATION.md          # 루브릭-프롬프트 상관관계
│   │   ├── KEY_FINDINGS_AB_TEST.md               # A/B 테스트 핵심 발견
│   │   └── agent_prompts_summary.json            # 에이전트 프롬프트 JSON
│   ├── 부록_A_루브릭_상세설명서.md      # 평가 기준 상세
│   ├── 부록_B_AI채점_결과_샘플.md       # 실제 채점 사례
│   ├── 부록_C_통계분석_상세표.md         # 통계 검정 결과
│   ├── 부록_D_연구_신뢰성_체크리스트.md  # 연구 품질 검증
│   ├── javascripts/          # JavaScript 파일
│   │   ├── mathjax.js       # 수식 렌더링
│   │   └── mermaid-init.js  # 다이어그램 초기화
│   ├── stylesheets/          # CSS 파일
│   │   └── extra.css        # 커스텀 스타일
│   └── assets/               # 이미지, 템플릿
├── analysis/                  # 통계 분석 스크립트
│   ├── Gemini_병렬_채점.py              # AI 루브릭 채점 시스템
│   ├── compare_agent_freepass_current.py # Agent vs Freepass 비교
│   └── *.json                # 채점 결과 데이터
├── .github/workflows/         # GitHub Actions
│   └── deploy.yml            # 자동 배포 워크플로우
├── setup_mkdocs.sh           # 설치 스크립트
├── deploy.sh                 # 배포 스크립트
├── requirements_mkdocs.txt   # Python 패키지
├── QUICK_START.md            # 빠른 시작 가이드
├── MKDOCS_GUIDE.md           # 상세 가이드
├── 논문_설계도.md              # 논문 전체 구조 설계
└── README.md                 # 이 파일
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

## 📖 논문 개요

### 연구 주제
**수학 학습에서 질문 명료화를 지원하는 AI Agent 설계 및 개발: 고등학교 2학년 수학적 귀납법 단원 중심으로**

### 핵심 기여
- ✅ **교육 아키텍처 우선 설계**: Dewey의 반성적 사고 + Bloom의 교육 목표 분류학 기반
- ✅ **5개 AI 에이전트 시스템**: Classifier, Question Improvement, Answer Generator, Observer, FreeTalker
- ✅ **A/B 테스트 실증**: Agent 모드 vs Freepass 모드 (59명 학생, 177개 세션)
- ✅ **통계적 유의성**: 하위권 학생 학습 효과 +0.83점 (Cohen's d=1.04, p=0.002)

### 논문 구성 (9장)
1. **서론**: Freepass 방식의 한계 → MAICE 필요성
2. **이론적 배경**: Dewey, Bloom, 멀티 에이전트 시스템
3. **교육 시스템 아키텍처**: 설계 철학, 5개 에이전트 역할
4. **시스템 구현** ⭐ **NEW**: 기술 스택, 프롬프트 엔지니어링, Redis Streams, Docker
5. **수학적 귀납법 적용**: 도메인 특화 설계
6. **연구 방법**: A/B 테스트 설계, 루브릭 개발
7. **결과**: 통계 분석, 효과성 입증
8. **논의 및 결론**: 교육적 시사점
9. **참고문헌**

---

## ✨ 웹사이트 주요 기능

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

### 📊 다이어그램 지원

- Mermaid 통합
- 시스템 아키텍처 다이어그램
- 시퀀스 다이어그램, 플로우차트

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

### 논문 웹사이트

- **정적 사이트 생성기**: [MkDocs](https://www.mkdocs.org/)
- **테마**: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- **수식 렌더링**: [MathJax](https://www.mathjax.org/)
- **다이어그램**: [Mermaid](https://mermaid.js.org/)
- **댓글 시스템**: [Giscus](https://giscus.app/)
- **호스팅**: [GitHub Pages](https://pages.github.com/)
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)

### MAICE 시스템 (4장에서 상세)

- **프론트엔드**: SvelteKit 2.0, TypeScript, Tailwind CSS 4.x, MathLive 0.95
- **백엔드**: FastAPI 0.104, SQLAlchemy 2.0, PostgreSQL 15, Redis 7.0
- **AI 에이전트**: Python 3.11, Gemini 2.5 Flash, Redis Streams
- **인프라**: Docker Compose, Nginx, Jenkins CI/CD
- **성능**: 평균 응답 2.3초, 동시 120 세션, 99.2% 가용성

### 통계 분석

- **Python**: pandas, numpy, scipy
- **AI 채점**: Gemini 2.5 Flash (루브릭 기반 자동 채점)
- **통계 검정**: Welch's t-test, Cohen's d, 천장효과 보정

### Python 패키지 (웹사이트)

- `mkdocs` - 핵심 프레임워크
- `mkdocs-material` - Material Design 테마
- `mkdocs-git-revision-date-localized-plugin` - 수정 날짜 표시
- `mkdocs-print-site-plugin` - PDF 출력 지원
- `pymdown-extensions` - 마크다운 확장 기능 (Mermaid 포함)

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

### 2025-11-02
- 🎉 **4장 "시스템 구현" 신설** (21,000자)
  - 기술 스택 선정 및 근거
  - 5개 에이전트 프롬프트 엔지니어링 상세
  - Redis Streams 통신 메커니즘
  - Docker 기반 배포 및 인프라
  - 성능 최적화 및 모니터링
- ✅ 논문 구조 재편 (8장 → 9장)
- ✅ 프롬프트 분석 문서 5개 추가 (2,600줄)
- ✅ README 개선 (논문 개요, MAICE 시스템 기술 스택)

### 2025-11-01
- ✅ 3장 "교육 시스템 아키텍처" 몰입형 구조로 재작성
  - 설계 철학 신설
  - 5개 에이전트 역할 재구성
  - Mermaid 다이어그램 5개 추가
- ✅ 통계 분석 완료 (Agent vs Freepass)
  - A/B 테스트 결과 분석
  - 하위권 학생 효과성 입증 (d=1.04, p=0.002)
  - 루브릭 기반 AI 자동 채점

### 2025-10-30
- ✅ MkDocs 프로젝트 초기 설정
- ✅ Material 테마 적용
- ✅ 한글 최적화
- ✅ 수식 렌더링 설정 (MathJax)
- ✅ 다이어그램 지원 (Mermaid)
- ✅ 자동 배포 워크플로우 구성
- ✅ 문서화 완료

---

## 🎯 연구 성과 요약

### 논문 기여도
- ✅ **교육학적 근거**: Dewey + Bloom 기반 명료화 프로세스 설계
- ✅ **기술적 구현**: 5개 AI 에이전트 멀티 시스템 (재현 가능, 확장 가능)
- ✅ **실증 검증**: A/B 테스트 (59명, 177 세션, 통계적 유의성)
- ✅ **교육적 효과**: 하위권 학생 학습 효과 입증 (Cohen's d=1.04)

### 시스템 성능
- ⚡ 평균 응답 시간: **2.3초**
- 🔄 동시 처리: **최대 120 세션**
- 📊 시스템 가용성: **99.2%** (12일간 운영)
- 🤖 AI 에이전트: **5개 독립 프로세스**

---

더 궁금한 점이 있으시면 [MKDOCS_GUIDE.md](MKDOCS_GUIDE.md)를 참조하거나 문의해주세요! 🚀

