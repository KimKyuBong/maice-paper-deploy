# 📊 MAICE 논문용 다이어그램

이 폴더에는 MAICE 시스템 설계 장(3장)의 머메이드 다이어그램이 논문용으로 준비되어 있습니다.

## 📋 다이어그램 목록

| 파일명 | 설명 | 논문 포함 권장도 | 유형 |
|--------|------|----------------|------|
| `figure3-1-pipeline.mmd` | 질문 → 분류 → 명료화 → 답변 파이프라인 | ⭐⭐⭐ 필수 | Flowchart |
| `figure3-2-architecture.mmd` | 3계층 시스템 아키텍처 | ⭐⭐⭐ 필수 | Flowchart |
| `figure3-3-sequence.mmd` | 질문 처리 시퀀스 다이어그램 | ⭐⭐⭐ 필수 | Sequence |
| `figure3-4-gating.mmd` | 3단계 게이팅 (answerable/needs_clarify/unanswerable) | ⭐⭐⭐ 필수 | Flowchart |
| `figure3-5-clarification.mmd` | 명료화 완료 판단 프로세스 | ⭐⭐ 권장 | Flowchart |
| `figure3-6-ocr.mmd` | 이미지 OCR 수식 변환 시스템 | ⭐⭐ 권장 | Sequence |

## 🚀 빠른 시작

### 1️⃣ 필수 도구 설치

```bash
# Mermaid CLI 설치
npm install -g @mermaid-js/mermaid-cli
```

### 2️⃣ 이미지 변환

```bash
# 변환 스크립트 실행 권한 부여
chmod +x convert-to-images.sh

# 모든 다이어그램을 SVG/PNG로 변환
./convert-to-images.sh
```

### 3️⃣ 출력 확인

변환된 이미지는 다음 위치에 저장됩니다:

```
docs/diagrams/
├── output/
│   ├── svg/          # SVG 파일 (벡터, 권장)
│   │   ├── figure3-1-pipeline.svg
│   │   ├── figure3-2-architecture.svg
│   │   └── ...
│   └── png/          # PNG 파일 (래스터, 고해상도)
│       ├── figure3-1-pipeline.png
│       ├── figure3-2-architecture.png
│       └── ...
```

## 🎨 다이어그램 특징

### 논문용 최적화

모든 다이어그램은 논문 출판을 위해 다음과 같이 최적화되었습니다:

- ✅ **중립 테마**: 흑백 인쇄에 적합한 neutral 테마
- ✅ **큰 폰트**: 최소 16px (인쇄 시 가독성 확보)
- ✅ **한글 지원**: Noto Sans KR 폰트 우선 사용
- ✅ **고해상도**: PNG는 3000px 너비 (300 DPI 기준)
- ✅ **투명 배경**: SVG는 투명 배경 (논문 배경에 맞춤)

### 이모지 제거

원본 마크다운 문서의 이모지는 논문용으로 모두 제거되었습니다.

## 📝 논문에 삽입하기

### LaTeX 사용 시

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{diagrams/output/svg/figure3-1-pipeline.svg}
    \caption{MAICE 시스템의 질문 처리 파이프라인. 
             학생 질문은 Classifier를 거쳐 분류되고, 
             needs\_clarify 판정 시 명료화 과정을 거친 후 답변이 생성된다.}
    \label{fig:pipeline}
\end{figure}
```

### Microsoft Word 사용 시

1. **삽입** → **그림** → PNG 파일 선택
2. 그림 우클릭 → **캡션 삽입**
3. 캡션 입력: "그림 3.1 MAICE 시스템의 질문 처리 파이프라인"

### 캡션 예시

```markdown
**그림 3.1** MAICE 시스템의 질문 처리 파이프라인

학생의 질문은 Classifier Agent를 거쳐 K1-K4 유형과 answerable/needs_clarify/unanswerable 
품질로 분류된다. needs_clarify 판정을 받은 질문은 Question Improvement Agent의 명료화 
과정을 거쳐 개선된 후, Answer Generator Agent가 맞춤형 답변을 생성한다.
```

## 🔧 개별 변환

특정 다이어그램만 변환하고 싶다면:

```bash
# SVG로 변환 (벡터, 권장)
mmdc -i figure3-1-pipeline.mmd -o figure3-1-pipeline.svg -t neutral -b transparent

# PNG로 변환 (고해상도)
mmdc -i figure3-1-pipeline.mmd -o figure3-1-pipeline.png -t neutral -b white -w 3000

# PDF로 변환 (일부 저널 요구)
mmdc -i figure3-1-pipeline.mmd -o figure3-1-pipeline.pdf -t neutral -b white
```

## 💡 추가 최적화

### 색상 커스터마이징

필요 시 `.mmd` 파일 상단의 테마 설정을 수정하세요:

```javascript
%%{init: {'theme':'neutral', 'themeVariables': {
  'primaryColor':'#ffffff',
  'primaryTextColor':'#000000',
  'primaryBorderColor':'#000000',
  'lineColor':'#000000',
  'fontSize':'18px',          // 폰트 크기 조정
  'fontFamily':'Noto Sans KR, Arial'
}}}%%
```

### 해상도 조정

더 높은 해상도가 필요하다면:

```bash
# 4K 해상도 (3840px)
mmdc -i diagram.mmd -o diagram.png -w 3840

# 8K 해상도 (7680px, 매우 큰 포스터용)
mmdc -i diagram.mmd -o diagram.png -w 7680
```

## 🎯 권장 사항

### 논문 유형별 권장 형식

| 논문 유형 | 권장 형식 | 이유 |
|----------|----------|------|
| **LaTeX** | SVG | 벡터 그래픽, 확대해도 깨지지 않음 |
| **Word** | PNG | 호환성 우수, 고해상도면 충분 |
| **웹 발표** | SVG | 파일 크기 작고 품질 우수 |
| **포스터** | PNG (8K) | 대형 인쇄물에 적합 |

### 품질 체크리스트

- [ ] 텍스트가 명확하게 읽히는가?
- [ ] 한글이 깨지지 않고 표시되는가?
- [ ] 흑백 인쇄 시에도 구분이 되는가?
- [ ] 화살표와 선이 명확한가?
- [ ] 배경이 깔끔한가?

## 🐛 문제 해결

### 한글 폰트가 깨질 때

```bash
# 시스템에 Noto Sans KR 폰트 설치 필요
# macOS
brew install font-noto-sans-cjk-kr

# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk
```

### mmdc 명령어가 없을 때

```bash
# Node.js가 설치되어 있는지 확인
node --version

# Node.js 설치 (없는 경우)
brew install node  # macOS
# 또는 https://nodejs.org/ 에서 다운로드

# mermaid-cli 재설치
npm install -g @mermaid-js/mermaid-cli
```

### 변환이 실패할 때

```bash
# 권한 문제
chmod +x convert-to-images.sh

# 파일 경로 확인
ls -la *.mmd

# 수동으로 한 파일씩 테스트
mmdc -i figure3-1-pipeline.mmd -o test.svg -t neutral
```

## 📚 참고 자료

- [Mermaid 공식 문서](https://mermaid.js.org/)
- [Mermaid CLI GitHub](https://github.com/mermaid-js/mermaid-cli)
- [Mermaid Live Editor](https://mermaid.live/) - 온라인 편집기

---

**작성일**: 2025년 11월  
**버전**: 1.0  
**작성자**: 김규봉


