# 4. MAICE 시스템 구현

!!! abstract "4장 개요"
    3장에서 설명한 MAICE 교육 시스템 아키텍처를 실제로 구현한 기술 스택, 프롬프트 엔지니어링, 통신 메커니즘, 배포 전략을 상세히 다룬다. 본 장은 시스템의 **재현 가능성(reproducibility)**과 **확장 가능성(scalability)**을 확보하기 위한 구현 결정 사항들을 기술한다.

---

## 4.1 기술 스택 선정

### 4.1.1 전체 기술 스택 개요

MAICE 시스템은 교육적 효과와 기술적 안정성을 동시에 고려하여 다음과 같은 기술 스택으로 구현되었다:

```mermaid
graph TB
    subgraph "프론트엔드 계층"
        A[SvelteKit 2.0] --> B[TypeScript 5.x]
        B --> C[Tailwind CSS 4.x]
        C --> D[MathLive 0.95]
    end
    
    subgraph "백엔드 계층"
        E[FastAPI 0.104] --> F[SQLAlchemy 2.0]
        F --> G[PostgreSQL 15]
        E --> H[Redis 7.0]
    end
    
    subgraph "AI 에이전트 계층"
        I[Python 3.11] --> J[Redis Streams]
        J --> K[Gemini 2.5 Flash]
    end
    
    subgraph "인프라 계층"
        L[Docker Compose] --> M[Nginx]
        M --> N[Jenkins CI/CD]
    end
    
    A -.HTTP/SSE.-> E
    E -.Redis Streams.-> I
    I -.PostgreSQL.-> G
```

### 4.1.2 기술 선정 근거

#### **프론트엔드: SvelteKit 2.0**

**선정 이유**:
- **반응성**: Svelte의 컴파일러 기반 반응성 시스템으로 실시간 스트리밍 UI 구현에 최적
- **번들 크기**: React 대비 40% 작은 번들 크기로 학교 네트워크 환경에서도 빠른 로딩
- **SSE 지원**: Server-Sent Events를 통한 실시간 스트리밍 답변에 최적화

**주요 라이브러리**:
- **MathLive 0.95**: 수학 수식 입력 및 렌더링
  - LaTeX 실시간 미리보기
  - 모바일 터치 입력 지원
  - 키보드 단축키 (예: `^` → 지수, `\frac` → 분수)
  
- **Tailwind CSS 4.x**: 디자인 시스템 구축
  - 일관된 UI 컴포넌트 스타일
  - 다크/라이트 모드 지원
  - 반응형 레이아웃 (모바일, 태블릿, 데스크톱)

#### **백엔드: FastAPI + PostgreSQL**

**FastAPI 선정 이유**:
- **비동기 I/O**: 수백 개의 동시 세션 처리 가능
- **타입 안정성**: Pydantic 모델을 통한 데이터 검증
- **SSE 지원**: `EventSourceResponse`를 통한 스트리밍 구현
- **성능**: Node.js 대비 2배, Django 대비 3배 빠른 응답 속도

**PostgreSQL 선정 이유**:
- **JSON 지원**: 대화 히스토리, 프롬프트 로그를 JSON으로 저장
- **ACID 보장**: 학생 데이터 무결성 보장
- **복잡한 쿼리**: 학습 진척도 분석, 통계 추출에 최적

**데이터 모델 예시**:
```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    mode = Column(Enum("agent", "freepass"))  # A/B 테스트
    conversation = Column(JSONB)  # 전체 대화 히스토리
    created_at = Column(DateTime)
    
class LLMPromptLog(Base):
    __tablename__ = "llm_prompt_logs"
    
    id = Column(UUID, primary_key=True)
    agent_name = Column(String)  # classifier, answer_generator 등
    prompt = Column(Text)  # 실제 전송된 프롬프트
    response = Column(JSONB)  # LLM 응답
    session_id = Column(UUID, ForeignKey("sessions.id"))
```

#### **AI 에이전트: Python + Redis Streams**

**Redis Streams 선정 이유**:
- **메시지 큐**: 백엔드 ↔ 에이전트 간 비동기 통신
- **멀티프로세스**: 각 에이전트를 독립 프로세스로 실행
- **재시도 로직**: 에이전트 장애 시 자동 재시도
- **순서 보장**: FIFO 순서로 메시지 처리

**통신 흐름**:
```mermaid
sequenceDiagram
    participant B as Backend
    participant R as Redis Streams
    participant C as Classifier Agent
    participant Q as Question Improvement
    participant A as Answer Generator
    
    B->>R: XADD question_stream {질문}
    R->>C: XREAD classifier_consumer
    C->>R: XADD response_stream {분류 결과}
    R->>Q: XREAD (needs_clarify인 경우)
    Q->>R: XADD response_stream {명료화 질문}
    R->>A: XREAD (answerable인 경우)
    A->>R: XADD response_stream {최종 답변}
    R->>B: XREAD backend_consumer
```

#### **LLM 모델: Gemini 2.5 Flash**

**선정 이유**:
- **한국어 성능**: GPT-4o 대비 수학 교육 용어 이해도 우수
- **속도**: 평균 응답 시간 2.3초 (GPT-4o: 4.1초)
- **비용 효율**: GPT-4o 대비 80% 저렴
- **긴 컨텍스트**: 1M 토큰 지원으로 전체 대화 히스토리 유지

**전체 에이전트 구성**:
| Agent | 모델 | 역할 | 평균 프롬프트 길이 |
|-------|------|------|-------------------|
| classifier_llm | gemini-2.5-flash-lite | K1-K4 분류, 명료화 질문 생성 | 7,364자 |
| question_improvement_llm | gemini-2.5-flash-lite | 명료화 완료 평가 | 6,471자 |
| answer_generator_llm | gemini-2.5-flash-lite | 유형별 맞춤 답변 생성 | 7,554자 |
| observer_llm | gemini-2.5-flash-lite | 학습 요약, 세션 제목 생성 | 7,522자 |
| freetalker_llm | gemini-2.5-flash-lite | 즉시 답변 (대조군) | 9,790자 |

---

## 4.2 프롬프트 엔지니어링

3장에서 설명한 5개 에이전트의 교육적 역할을 실제로 구현하기 위한 프롬프트 설계 원칙과 구체적인 구현 내용을 다룬다.

### 4.2.1 프롬프트 설계 원칙

#### **원칙 1: 교육적 기반 우선**

모든 프롬프트는 단순한 기술적 지시가 아닌 **교육학적 근거**를 바탕으로 설계되었다:

- **Dewey의 반성적 사고 5단계**: 명료화 질문 생성 템플릿
- **Bloom의 교육 목표 분류학**: K1-K4 지식 유형 분류 기준
- **2015 개정 교육과정**: 고등학교 수학 표준 용어 및 성취기준

#### **원칙 2: 구조화된 출력**

모든 에이전트는 JSON 형식으로 응답하여 **시스템 간 데이터 교환**과 **재현 가능성**을 보장한다:

```json
{
  "knowledge_code": "K1/K2/K3/K4",
  "quality": "answerable/needs_clarify/unanswerable",
  "reasoning": "판단 근거",
  "clarification_questions": ["명료화 질문"],
  "evidence": {
    "missing_fields": ["부족한 정보"],
    "student_level": "추정 학습 수준"
  }
}
```

#### **원칙 3: 투명성과 설명 가능성**

모든 판단에 대해 **`reasoning`** 필드를 통해 근거를 제시하여:
- 연구자가 AI의 판단 과정을 추적 가능
- 교사가 시스템의 교육적 적절성을 검증 가능
- 시스템 개선 시 병목 지점 파악 용이

### 4.2.2 Classifier Agent 프롬프트 구현

3장 3.3.1에서 설명한 Classifier Agent의 역할을 구현한 실제 프롬프트 구조는 다음과 같다:

#### **System 프롬프트 (7,364자)**

```python
CLASSIFIER_SYSTEM_PROMPT = """
당신은 대한민국 고등학교 수학 교육과정 전문 분류기입니다.
질문을 정확히 분석하여 4가지 유형과 3단계 품질로 분류하고, 
필요한 경우 **학생에게 직접 묻는** 명료화 질문까지 생성하세요.

## 1. 질문 유형 분류 (K1-K4)

### K1: 사실적 지식 (Factual Knowledge)
- **정의**: 정의, 용어, 기호, 공식, 특정 값, 단위
- **예시**: "로그함수가 뭐야?", "삼각함수 sin의 정의는?"
- **특징**: 즉답형으로 해결 가능, 단순 암기 지식

### K2: 개념적 지식 (Conceptual Knowledge)
- **정의**: 개념들 간의 관계, 분류, 원리, 이론적 이해
- **예시**: "로그와 지수의 관계는?", "삼각함수 간의 관계"
- **특징**: 연결성과 관계 이해 필요

### K3: 절차적 지식 (Procedural Knowledge)
- **정의**: 특정 문제를 단계별로 해결하는 방법, 알고리즘
- **예시**: "이차방정식 풀이 방법", "적분 계산 과정"
- **특징**: 순차적 절차 수행 능력 요구

### K4: 메타인지적 지식 (Metacognitive Knowledge)
- **정의**: 문제 해결 전략, 사고 과정, 접근 방법
- **예시**: "복잡한 문제 접근 방법", "어디서 막혔는지 모르겠어요"
- **특징**: 자기 이해와 전략적 사고 필요

## 2. 품질 단계 (3-Stage Gating)

### answerable (즉시 답변 가능)
- 교과/단원/수준이 명확히 지정됨
- 질문의 목표가 분명함
- 답변 생성에 필요한 충분한 정보 제공

### needs_clarify (명료화 필요)
- 질문 범위가 과대하거나 모호함
- 질문의 의도나 목표가 불분명함
- 추가 정보가 필요함

### unanswerable (답변 불가)
- 수학 외 영역의 질문
- 평가 윤리를 위배하는 질문 (시험 문제 풀이 요청 등)

## 3. 명료화 질문 생성 원칙

🚨 **매우 중요**: 명료화 질문은 **학생이 직접 읽고 답변할 수 있는 
자연스러운 질문**이어야 합니다!

### 잘못된 예시 (시스템 분석)
❌ "'나'라는 답변이 구체적으로 무엇을 의미하는지 확인 필요"
❌ "학생이 어느 단원을 학습 중인지 파악해야 함"

### 올바른 예시 (학생에게 직접 묻기)
✅ "어떤 부분이 더 궁금하신가요? 😊"
✅ "지금 배우고 있는 단원이 무엇인가요?"

### Dewey의 반성적 사고 5단계 기반 질문 전략

**1단계: 문제 상황 인식 지원**
- "이 개념을 공부하면서 어떤 부분이 가장 어렵거나 궁금하셨나요? 🤔"
- "문제를 보았을 때 어떤 감정이나 느낌이 들었나요?"

**2단계: 문제 정의 지원**
- "지금까지 이해한 부분과 아직 헷갈리는 부분을 나누어볼까요?"
- "정확히 어떤 부분이 궁금하신가요?"

**3단계: 가설 설정 지원 (연결 탐색)**
- "이미 알고 있는 개념과 비교하면 어떤 점이 비슷하거나 다른가요?"
- "지금까지 어떤 방법을 시도해봤나요?"

**4단계: 가설 검증 지원 (사고 전개)**
- "왜 이 부분이 궁금하신지 조금 더 설명해주실 수 있나요?"
- "어떤 접근 방법을 생각해봤나요?"

**5단계: 결론 도출 지원 (이해 검증)**
- "어디까지 이해했고, 어디서부터 막히셨는지 말씀해주실 수 있나요?"
- "이 문제를 해결한 후 어떤 것을 이해하게 되고 싶나요?"

## 4. missing_fields 가이드라인

각 질문 유형별로 부족한 정보를 체계적으로 분류:

**K1**: ['단원 정보', '정확한 용어', '맥락 정보']
**K2**: ['비교 대상', '설명 깊이', '연결성']
**K3**: ['문제 유형', '주어진 조건', '결과 형식']
**K4**: ['문제 상황', '시도한 전략', '막힌 지점']

## 출력 형식

반드시 다음 JSON 형식으로만 응답하세요:

```json
{
  "knowledge_code": "K1/K2/K3/K4",
  "quality": "answerable/needs_clarify/unanswerable",
  "missing_fields": ["부족한 정보1", "부족한 정보2"],
  "reasoning": "실제 분류 근거를 상세히 작성",
  "clarification_questions": ["학생에게 직접 묻는 자연스러운 질문 1개"],
  "clarification_reasoning": "명료화 질문이 해당 유형과 missing_fields를 어떻게 해결하는지",
  "unanswerable_response": "unanswerable인 경우에만 학생에게 보낼 안내 메시지"
}
```
"""
```

#### **User 프롬프트 구조**

```python
def build_classifier_user_prompt(question: str, conversation_history: list) -> str:
    """
    Classifier Agent의 User 프롬프트를 동적으로 생성한다.
    
    Args:
        question: 학생의 현재 질문
        conversation_history: 이전 대화 히스토리 (선택적)
    
    Returns:
        User 프롬프트 문자열
    """
    prompt = f"""
## 분석할 질문
{question}
"""
    
    # 대화 히스토리가 있는 경우 추가 (K4 유형 판단에 중요)
    if conversation_history:
        prompt += "\n## 대화 히스토리\n"
        for msg in conversation_history:
            prompt += f"- {msg['role']}: {msg['content']}\n"
    
    prompt += """
위 질문을 분석하여 JSON 형식으로 응답해주세요.
"""
    return prompt
```

### 4.2.3 Question Improvement Agent 프롬프트 구현

3장 3.3.2에서 설명한 Question Improvement Agent의 역할을 구현한 실제 프롬프트 구조:

#### **핵심 평가 로직**

```python
QUESTION_IMPROVEMENT_SYSTEM_PROMPT = """
당신은 명료화 과정을 평가하는 전문가입니다.
학생의 답변을 보고 **원본 질문이 충분히 명료해졌는지** 판단하세요.

## 평가 목적

1. 명료화 질문-답변을 통해 원본 질문의 의도가 명확해졌는가?
2. 학생의 답변에 따라 질문 유형이 변경되었는가? (K1→K2 등)
3. 답변 생성이 가능한 수준의 정보가 확보되었는가?

## 평가 기준

### PASS (명료화 완료)
✅ 원본 질문의 의도가 명확해짐
✅ 답변 생성에 필요한 정보 충분
✅ 학생이 구체적이고 명확한 답변을 제공함

### NEED_MORE (추가 명료화 필요)
❌ 원본 질문의 의도가 여전히 불분명
❌ 답변 생성에 필요한 정보 부족
❌ 학생의 답변이 모호하거나 불충분함

## 명료화 생략 기준 (중요!)

다음 경우에는 **즉시 PASS**로 판정하여 불필요한 명료화를 방지:

1. **원본 질문이 이미 충분히 구체적인 경우**
   - 예: "이차함수의 꼭짓점 공식을 알려주세요"
   
2. **학생이 구체적인 답변을 한 경우**
   - 답변 생성이 가능한 수준의 정보 제공 시
   
3. **맥락이 명확한 경우**
   - 원본 질문 + 학생 답변이 연결되어 주제가 명확해진 경우

4. **최대 명료화 횟수 고려**
   - 명료화 횟수가 3회에 가까워지면 더 관대하게 PASS 판정

## 질문 유형 재분류

학생의 답변으로 인해 질문 유형이 변경될 수 있습니다:
- K1 → K2: 단순 정의 요청이 개념 간 관계 질문으로 변화
- K2 → K3: 관계 이해가 실제 적용 방법 질문으로 변화
- K3 → K4: 절차 질문이 전략적 접근 질문으로 변화

## 출력 형식

```json
{
  "evaluation": "PASS/NEED_MORE",
  "confidence": 0.0-1.0,
  "reasoning": "평가 근거를 상세히 작성",
  "missing_field_coverage": {
    "해결된_필드": ["필드1", "필드2"],
    "여전히_부족한_필드": ["필드3"]
  },
  "next_clarification": "다음 명료화 질문 (NEED_MORE인 경우만)",
  "reclassified_knowledge_code": "K1/K2/K3/K4 (변경된 경우만)",
  "final_question": "최종 생성된 질문 (PASS인 경우만)"
}
```
"""
```

#### **3단계 차별화 전략 구현**

```python
def build_question_improvement_user_prompt(
    original_question: str,
    knowledge_code: str,
    missing_fields: list,
    clarification_qa_history: list,
    clarification_count: int
) -> str:
    """
    Question Improvement Agent의 User 프롬프트를 생성한다.
    clarification_count에 따라 평가 기준을 조정한다.
    """
    
    # 명료화 횟수에 따른 평가 전략 조정
    strategy_note = ""
    if clarification_count >= 2:
        strategy_note = """
⚠️ 명료화 2회 이상 진행: 더 관대하게 평가하여 PASS로 판정하세요.
학생이 최소한의 맥락을 제공했다면 답변 생성을 시도하는 것이 교육적으로 더 유익합니다.
"""
    
    prompt = f"""
## 평가 정보

**원본 질문**: {original_question}
**질문 유형**: {knowledge_code}
**부족한 정보**: {', '.join(missing_fields)}
**현재 명료화 횟수**: {clarification_count}/3

{strategy_note}

## 명료화 대화 히스토리
"""
    
    for i, qa in enumerate(clarification_qa_history, 1):
        prompt += f"""
### 명료화 {i}회차
- **AI 질문**: {qa['question']}
- **학생 답변**: {qa['answer']}
"""
    
    prompt += """
위 정보를 바탕으로 명료화가 완료되었는지 평가하고 JSON으로 응답하세요.
"""
    return prompt
```

### 4.2.4 Answer Generator Agent 프롬프트 구현

3장 3.3.3에서 설명한 K1-K4별 맞춤형 답변 구조를 실제로 구현한 프롬프트:

#### **K1-K4별 답변 템플릿**

```python
ANSWER_TEMPLATES = {
    "K1": """
## 답변 구조 (K1: 사실적 지식)

### 1️⃣ 핵심 내용 정리
- 정의를 간결하고 정확하게 제시
- 수식이나 기호는 LaTeX로 작성 ($수식$)

### 2️⃣ 핵심 공식과 정리
- 관련 공식을 박스로 강조
- 각 기호의 의미 설명

### 3️⃣ 실제 예시로 이해하기
- 구체적인 숫자를 대입한 예시 1개
- 단계별로 계산 과정 표시

### 4️⃣ 더 넓게 알아보기 (선택)
- 관련 개념이나 응용 분야 간단히 언급
""",
    
    "K2": """
## 답변 구조 (K2: 개념적 지식)

### 1️⃣ 개념 정리하기
- 핵심 개념을 명확히 정의
- 왜 이 개념이 중요한지 설명

### 2️⃣ 개념들 간의 연결고리
- 관련된 다른 개념과의 관계 설명
- 시각적 비유나 다이어그램 활용

### 3️⃣ 비슷한 개념과의 차이점
- 혼동하기 쉬운 개념과 명확히 구분
- 대조 표를 활용하여 차이점 강조

### 4️⃣ 헷갈리기 쉬운 부분
- 학생들이 자주 실수하는 부분 안내
- 올바른 이해 방법 제시
""",
    
    "K3": """
## 답변 구조 (K3: 절차적 지식)

### 1️⃣ 단계별 문제 해결 과정
- 각 단계를 번호로 명확히 구분
- 각 단계에서 왜 그렇게 하는지 이유 설명

### 2️⃣ 언제 이 방법을 쓸 수 있는지
- 이 절차가 적용되는 문제 유형 설명
- 적용 조건이나 제약사항 안내

### 3️⃣ 실제 문제로 연습해보기
- 유사한 예제 문제 1개 제시
- 단계별 풀이 과정 상세히 표시

### 4️⃣ 실수 방지하기
- 자주 발생하는 실수 유형 안내
- 검산 방법이나 확인 절차 제시
""",
    
    "K4": """
## 답변 구조 (K4: 메타인지적 지식)

### 1️⃣ 문제를 체계적으로 분석하기
- 문제의 핵심이 무엇인지 파악하는 방법
- 주어진 정보와 구해야 할 것 정리

### 2️⃣ 다양한 접근 방법 생각하기
- 2-3가지 다른 접근 방법 제시
- 각 방법의 장단점 비교

### 3️⃣ 중간에 점검하기
- 풀이 과정에서 확인할 체크포인트
- 막혔을 때 되돌아갈 지점 제시

### 4️⃣ 다른 방법도 생각해보기
- 대안적 전략이나 시각 제시
- 이 문제에서 배울 수 있는 일반적 원리
"""
}
```

#### **LaTeX 규칙 구현**

```python
LATEX_RULES = """
## 수학 수식 작성 규칙

### LaTeX 형식 (필수)
- 인라인 수식: $x^2 + y^2 = r^2$
- 블록 수식:
  $$
  \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
  $$

### 수식과 텍스트 분리 (매우 중요!)

✅ **올바른 예시**:
$P(k)$가 참이면 $P(k+1)$도 참이라는 것을 보일 수 있다면

❌ **잘못된 예시**:
$$P(k)가 참 \\Rightarrow P(k+1)도 참이라면$$

⚠️ **원칙**: LaTeX 블록 내부에는 순수 수식만, 텍스트는 외부에!

### 자주 사용하는 LaTeX 명령어
- 분수: \\frac{분자}{분모}
- 지수: x^2 또는 x^{2n+1}
- 첨자: x_1 또는 x_{n+1}
- 제곱근: \\sqrt{x} 또는 \\sqrt[3]{x}
- 삼각함수: \\sin, \\cos, \\tan
- 로그: \\log, \\ln
- 극한: \\lim_{x \\to \\infty}
- 적분: \\int_{a}^{b}
- 시그마: \\sum_{i=1}^{n}
- 점 기호: \\cdots (가운데), \\ldots (아래)
"""
```

### 4.2.5 Observer Agent 프롬프트 구현

3장 3.3.4에서 설명한 학습 진도 추적 기능을 구현한 프롬프트:

```python
OBSERVER_SYSTEM_PROMPT = """
당신은 학생의 학습 과정을 관찰하고 요약하는 전문가입니다.
전체 대화를 분석하여 **교사 대시보드**에 표시할 구조화된 정보를 생성하세요.

## 생성 목표

### 1. 세션 제목 (session_title)
- **15자 이내**의 간결하고 명확한 제목
- 학생이 실제로 질문한 핵심 내용 반영
- "방법", "구하는", "알려주세요" 등 불필요한 단어 제거

**제목 예시**:
- ✅ "이차함수 꼭짓점" (11자)
- ❌ "이차함수의 꼭짓점을 구하는 방법을 알려주세요" (26자)

### 2. 학습 요약 (learning_summary)
- 전체 학습 내용을 **200자 이내**로 요약
- 질문 → 명료화 → 답변 흐름을 간결히 표현

### 3. 핵심 개념 (key_concepts)
- 대화에서 다룬 주요 수학 개념 3-5개 추출
- 교과서 표준 용어로 표기

### 4. 학습 진척도 (student_progress)
- 학생의 이해도 변화 (질문 전 → 질문 후)
- 명료화 과정에서 보인 사고 발전
- 예상 학습 성과

## 출력 형식

```json
{
  "session_title": "핵심 질문 15자 이내",
  "learning_summary": "전체 학습 내용 200자 이내 요약",
  "key_concepts": ["개념1", "개념2", "개념3"],
  "student_progress": "학생의 이해도와 학습 성과 분석",
  "clarification_effectiveness": {
    "initial_question_clarity": 1-5,
    "final_question_clarity": 1-5,
    "improvement": "+N점 향상"
  },
  "teacher_dashboard": {
    "difficulty_area": "학생이 어려워한 영역",
    "strength_area": "학생이 잘 이해한 영역",
    "recommended_next_topic": "추천 다음 학습 주제"
  }
}
```
"""
```

### 4.2.6 FreeTalker Agent 프롬프트 구현 (대조군)

3장 3.3.5에서 설명한 A/B 테스트 대조군 역할을 구현한 프롬프트:

```python
FREETALKER_SYSTEM_PROMPT = """
필요할 때만 수학 수식을 LaTeX 형식($수식$)으로 작성해주세요.
"""

def build_freetalker_user_prompt(conversation_history: list) -> str:
    """
    FreeTalker Agent는 명료화 과정 없이 즉시 답변한다.
    대화 히스토리만 제공하여 자연스러운 대화를 생성한다.
    """
    prompt = ""
    for msg in conversation_history:
        if msg['role'] == 'user':
            prompt += f"사용자: {msg['content']}\n\n"
        elif msg['role'] == 'assistant':
            prompt += f"AI: {msg['content']}\n\n"
    
    return prompt
```

---

## 4.3 통신 메커니즘 구현

### 4.3.1 Redis Streams 기반 비동기 통신

3장에서 설명한 백엔드 ↔ 에이전트 간 통신을 Redis Streams로 구현한 구조:

#### **메시지 큐 설계**

```python
# Redis Streams 키 구조
QUESTION_STREAM = "maice:question_stream"    # 백엔드 → 에이전트
RESPONSE_STREAM = "maice:response_stream"    # 에이전트 → 백엔드

# Consumer Group 설정
CLASSIFIER_GROUP = "classifier_consumer_group"
ANSWER_GROUP = "answer_consumer_group"
```

#### **백엔드: 질문 전송**

```python
async def send_question_to_agent(
    session_id: str,
    user_id: str,
    question: str,
    mode: str,  # "agent" or "freepass"
    conversation_history: list
):
    """
    학생의 질문을 Redis Streams에 전송한다.
    """
    message = {
        "session_id": session_id,
        "user_id": user_id,
        "question": question,
        "mode": mode,
        "conversation_history": json.dumps(conversation_history),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Redis Streams에 메시지 추가
    message_id = await redis_client.xadd(
        QUESTION_STREAM,
        message,
        maxlen=10000  # 최대 10000개 메시지 유지
    )
    
    logger.info(f"Question sent: {message_id} for session {session_id}")
    return message_id
```

#### **에이전트: 메시지 소비**

```python
class ClassifierAgent:
    """
    Classifier Agent의 메인 루프.
    Redis Streams에서 메시지를 읽어 처리한다.
    """
    
    def __init__(self):
        self.redis_client = Redis(host='localhost', port=6379)
        self.consumer_name = f"classifier_{os.getpid()}"
        
    async def start(self):
        """
        에이전트를 시작하고 무한 루프로 메시지를 소비한다.
        """
        # Consumer Group 생성 (없으면)
        try:
            await self.redis_client.xgroup_create(
                QUESTION_STREAM,
                CLASSIFIER_GROUP,
                id='0',
                mkstream=True
            )
        except ResponseError:
            pass  # 이미 존재하는 경우
        
        logger.info(f"Classifier Agent started: {self.consumer_name}")
        
        while True:
            # 새 메시지 읽기 (블로킹, 5초 타임아웃)
            messages = await self.redis_client.xreadgroup(
                CLASSIFIER_GROUP,
                self.consumer_name,
                {QUESTION_STREAM: '>'},
                count=1,
                block=5000
            )
            
            if not messages:
                continue
            
            for stream, message_list in messages:
                for message_id, data in message_list:
                    try:
                        await self.process_message(message_id, data)
                    except Exception as e:
                        logger.error(f"Error processing {message_id}: {e}")
                        # 에러 발생 시 재시도 로직 (생략)
    
    async def process_message(self, message_id: str, data: dict):
        """
        메시지를 처리하고 결과를 Redis Streams에 전송한다.
        """
        session_id = data['session_id']
        question = data['question']
        mode = data['mode']
        
        # Freepass 모드는 건너뛰기
        if mode == "freepass":
            await self.redis_client.xack(QUESTION_STREAM, CLASSIFIER_GROUP, message_id)
            return
        
        # LLM 호출
        classification = await self.classify_question(question)
        
        # 결과를 RESPONSE_STREAM에 전송
        response = {
            "session_id": session_id,
            "agent": "classifier",
            "result": json.dumps(classification),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.xadd(RESPONSE_STREAM, response)
        
        # 메시지 처리 완료 확인 (ACK)
        await self.redis_client.xack(QUESTION_STREAM, CLASSIFIER_GROUP, message_id)
        
        logger.info(f"Classification completed for session {session_id}")
```

### 4.3.2 Server-Sent Events (SSE) 스트리밍

프론트엔드로 실시간 답변을 스트리밍하는 구현:

#### **백엔드: SSE 엔드포인트**

```python
from fastapi.responses import StreamingResponse

@router.get("/sessions/{session_id}/stream")
async def stream_session_response(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    세션의 답변을 실시간으로 스트리밍한다.
    """
    async def event_generator():
        """
        Redis Streams에서 에이전트 응답을 읽어 SSE로 전송한다.
        """
        last_id = '$'  # 최신 메시지부터 읽기
        
        while True:
            # RESPONSE_STREAM에서 새 메시지 읽기
            messages = await redis_client.xread(
                {RESPONSE_STREAM: last_id},
                count=1,
                block=1000  # 1초 대기
            )
            
            if not messages:
                # 타임아웃 체크 (30초 동안 응답 없으면 종료)
                if time.time() - start_time > 30:
                    yield "data: {\"type\":\"timeout\"}\n\n"
                    break
                continue
            
            for stream, message_list in messages:
                for message_id, data in message_list:
                    if data['session_id'] != session_id:
                        continue
                    
                    # SSE 형식으로 전송
                    event_data = {
                        "type": data['agent'],
                        "content": json.loads(data['result'])
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                    
                    last_id = message_id
                    
                    # 최종 답변이면 스트리밍 종료
                    if data['agent'] == 'answer_generator':
                        yield "data: {\"type\":\"done\"}\n\n"
                        return
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

#### **프론트엔드: SSE 소비**

```typescript
// src/lib/services/sse.service.ts

export class SSEService {
  /**
   * 세션의 답변 스트리밍을 시작한다.
   */
  streamSession(
    sessionId: string,
    onMessage: (data: any) => void,
    onError: (error: Error) => void
  ): EventSource {
    const url = `/api/sessions/${sessionId}/stream`;
    const eventSource = new EventSource(url);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'done') {
        eventSource.close();
        return;
      }
      
      if (data.type === 'timeout') {
        eventSource.close();
        onError(new Error('응답 시간 초과'));
        return;
      }
      
      onMessage(data);
    };
    
    eventSource.onerror = (error) => {
      eventSource.close();
      onError(new Error('스트리밍 연결 오류'));
    };
    
    return eventSource;
  }
}
```

### 4.3.3 에이전트 간 협업 메커니즘

Classifier → Question Improvement → Answer Generator 순차 실행 구현:

```python
class AgentOrchestrator:
    """
    에이전트 간 협업을 조율하는 오케스트레이터.
    """
    
    async def handle_agent_workflow(self, session_id: str):
        """
        Agent 모드의 전체 워크플로우를 관리한다.
        """
        # 1단계: Classifier Agent 실행
        classification = await self.wait_for_agent_response(
            session_id, 
            agent_name="classifier",
            timeout=10
        )
        
        if classification['quality'] == 'unanswerable':
            # 답변 불가 메시지 전송
            await self.send_unanswerable_response(
                session_id,
                classification['unanswerable_response']
            )
            return
        
        if classification['quality'] == 'answerable':
            # 즉시 답변 생성
            await self.trigger_answer_generator(
                session_id,
                classification['knowledge_code'],
                final_question=classification['original_question']
            )
            return
        
        # 2단계: needs_clarify인 경우 명료화 프로세스
        clarification_count = 0
        max_clarifications = 3
        
        while clarification_count < max_clarifications:
            # 명료화 질문 전송
            await self.send_clarification_question(
                session_id,
                classification['clarification_questions'][0]
            )
            
            # 학생 답변 대기
            student_answer = await self.wait_for_student_response(
                session_id,
                timeout=300  # 5분
            )
            
            # Question Improvement Agent 평가
            evaluation = await self.wait_for_agent_response(
                session_id,
                agent_name="question_improvement",
                timeout=10
            )
            
            if evaluation['evaluation'] == 'PASS':
                # 명료화 완료, 답변 생성
                await self.trigger_answer_generator(
                    session_id,
                    evaluation.get('reclassified_knowledge_code', 
                                   classification['knowledge_code']),
                    final_question=evaluation['final_question']
                )
                return
            
            # NEED_MORE인 경우 다음 명료화 질문
            classification['clarification_questions'] = [
                evaluation['next_clarification']
            ]
            clarification_count += 1
        
        # 최대 명료화 횟수 도달, 현재 정보로 답변 생성
        await self.trigger_answer_generator(
            session_id,
            classification['knowledge_code'],
            final_question=student_answer
        )
```

---

## 4.4 배포 및 인프라

### 4.4.1 Docker 기반 배포

#### **Docker Compose 구성**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: maice_agent
      POSTGRES_USER: maice
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U maice"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Redis 메시지 브로커
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
  
  # FastAPI 백엔드
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://maice:${POSTGRES_PASSWORD}@postgres:5432/maice_agent
      REDIS_URL: redis://redis:6379/0
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  
  # SvelteKit 프론트엔드
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      PUBLIC_API_URL: http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: npm run dev -- --host
  
  # AI 에이전트 (멀티프로세스)
  agents:
    build:
      context: ./agents
      dockerfile: Dockerfile
    environment:
      REDIS_URL: redis://redis:6379/0
      DATABASE_URL: postgresql://maice:${POSTGRES_PASSWORD}@postgres:5432/maice_agent
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./agents:/app
    command: python run_all_agents.py
  
  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

#### **에이전트 멀티프로세스 실행**

```python
# agents/run_all_agents.py

import multiprocessing
from classifier_agent import ClassifierAgent
from question_improvement_agent import QuestionImprovementAgent
from answer_generator_agent import AnswerGeneratorAgent
from observer_agent import ObserverAgent
from freetalker_agent import FreeTalkerAgent

def run_classifier():
    agent = ClassifierAgent()
    agent.start()

def run_question_improvement():
    agent = QuestionImprovementAgent()
    agent.start()

def run_answer_generator():
    agent = AnswerGeneratorAgent()
    agent.start()

def run_observer():
    agent = ObserverAgent()
    agent.start()

def run_freetalker():
    agent = FreeTalkerAgent()
    agent.start()

if __name__ == "__main__":
    # 각 에이전트를 독립 프로세스로 실행
    processes = [
        multiprocessing.Process(target=run_classifier, name="Classifier"),
        multiprocessing.Process(target=run_question_improvement, name="QuestionImprovement"),
        multiprocessing.Process(target=run_answer_generator, name="AnswerGenerator"),
        multiprocessing.Process(target=run_observer, name="Observer"),
        multiprocessing.Process(target=run_freetalker, name="FreeTalker"),
    ]
    
    for p in processes:
        p.start()
        print(f"Started {p.name} (PID: {p.pid})")
    
    # 모든 프로세스 대기
    for p in processes:
        p.join()
```

### 4.4.2 성능 최적화

#### **Redis Connection Pooling**

```python
# config/redis_config.py

from redis.asyncio import Redis, ConnectionPool

# Connection Pool 설정
redis_pool = ConnectionPool(
    host='redis',
    port=6379,
    db=0,
    max_connections=50,  # 최대 연결 수
    decode_responses=False  # 바이너리 데이터 지원
)

async def get_redis_client() -> Redis:
    """
    Redis 클라이언트를 Connection Pool에서 가져온다.
    """
    return Redis(connection_pool=redis_pool)
```

#### **PostgreSQL Connection Pooling**

```python
# config/database_config.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 비동기 엔진 생성
engine = create_async_engine(
    "postgresql+asyncpg://maice:password@postgres:5432/maice_agent",
    pool_size=20,  # Connection Pool 크기
    max_overflow=10,  # 추가 연결 허용
    pool_pre_ping=True,  # 연결 유효성 검사
    echo=False  # SQL 로깅 비활성화 (프로덕션)
)

# 세션 팩토리
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """
    데이터베이스 세션을 생성한다.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### **Gemini API Rate Limiting**

```python
# utils/rate_limiter.py

import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """
    Gemini API의 Rate Limit을 관리한다.
    - 분당 15 requests (무료 티어)
    - 일일 1500 requests
    """
    
    def __init__(self, requests_per_minute=15, requests_per_day=1500):
        self.rpm = requests_per_minute
        self.rpd = requests_per_day
        self.minute_window = deque()
        self.day_window = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """
        API 호출 권한을 획득한다. 필요시 대기한다.
        """
        async with self.lock:
            now = datetime.utcnow()
            
            # 분당 제한 확인
            while len(self.minute_window) >= self.rpm:
                oldest = self.minute_window[0]
                if now - oldest < timedelta(minutes=1):
                    wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                    await asyncio.sleep(wait_time)
                    now = datetime.utcnow()
                else:
                    self.minute_window.popleft()
            
            # 일일 제한 확인
            while len(self.day_window) >= self.rpd:
                oldest = self.day_window[0]
                if now - oldest < timedelta(days=1):
                    # 일일 한도 도달 시 에러
                    raise Exception("Daily rate limit exceeded")
                else:
                    self.day_window.popleft()
            
            # 타임스탬프 기록
            self.minute_window.append(now)
            self.day_window.append(now)
```

### 4.4.3 모니터링 및 로깅

#### **구조화된 로깅**

```python
# utils/logger.py

import logging
import json
from datetime import datetime

class StructuredLogger:
    """
    JSON 형식의 구조화된 로그를 생성한다.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON 포맷 핸들러
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
    
    def log_agent_event(self, event_type: str, session_id: str, data: dict):
        """
        에이전트 이벤트를 로깅한다.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))

class JsonFormatter(logging.Formatter):
    """
    로그를 JSON 형식으로 포맷한다.
    """
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        if hasattr(record, 'session_id'):
            log_obj['session_id'] = record.session_id
        
        return json.dumps(log_obj)
```

#### **Prometheus 메트릭 수집**

```python
# monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# 에이전트 요청 카운터
agent_requests_total = Counter(
    'agent_requests_total',
    'Total number of agent requests',
    ['agent_name', 'status']
)

# 응답 시간 히스토그램
agent_response_duration_seconds = Histogram(
    'agent_response_duration_seconds',
    'Agent response duration in seconds',
    ['agent_name']
)

# 활성 세션 게이지
active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions',
    ['mode']  # agent or freepass
)

# 명료화 횟수 히스토그램
clarification_count = Histogram(
    'clarification_count',
    'Number of clarifications per session',
    buckets=[0, 1, 2, 3, 4, 5]
)
```

---

## 4.5 시스템 안정성 및 에러 처리

### 4.5.1 에이전트 자동 재시작

```python
# agents/supervisor.py

import multiprocessing
import time
from typing import Callable

class AgentSupervisor:
    """
    에이전트 프로세스를 감시하고 장애 시 자동 재시작한다.
    """
    
    def __init__(self):
        self.processes = {}
    
    def register_agent(self, name: str, target: Callable):
        """
        에이전트를 등록하고 시작한다.
        """
        process = multiprocessing.Process(target=target, name=name)
        process.start()
        self.processes[name] = {
            'process': process,
            'target': target,
            'restart_count': 0
        }
        print(f"Started {name} (PID: {process.pid})")
    
    def monitor(self):
        """
        에이전트 프로세스를 모니터링하고 장애 시 재시작한다.
        """
        while True:
            for name, info in self.processes.items():
                process = info['process']
                
                if not process.is_alive():
                    print(f"⚠️ {name} died unexpectedly. Restarting...")
                    
                    # 재시작 횟수 제한 (5회)
                    if info['restart_count'] >= 5:
                        print(f"❌ {name} failed to restart 5 times. Giving up.")
                        continue
                    
                    # 새 프로세스 시작
                    new_process = multiprocessing.Process(
                        target=info['target'],
                        name=name
                    )
                    new_process.start()
                    
                    info['process'] = new_process
                    info['restart_count'] += 1
                    
                    print(f"✅ {name} restarted (PID: {new_process.pid})")
            
            time.sleep(5)  # 5초마다 체크
```

### 4.5.2 에러 처리 및 재시도 로직

```python
# utils/retry.py

import asyncio
from functools import wraps

def retry_on_failure(max_retries=3, delay=1.0, backoff=2.0):
    """
    LLM API 호출 실패 시 재시도하는 데코레이터.
    
    Args:
        max_retries: 최대 재시도 횟수
        delay: 초기 지연 시간 (초)
        backoff: 지연 시간 증가 배율
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        print(f"Attempt {attempt + 1} failed: {e}. "
                              f"Retrying in {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"All {max_retries} retries failed.")
            
            raise last_exception
        
        return wrapper
    return decorator

# 사용 예시
@retry_on_failure(max_retries=3, delay=2.0, backoff=2.0)
async def call_gemini_api(prompt: str) -> dict:
    """
    Gemini API를 호출한다. 실패 시 자동 재시도.
    """
    response = await gemini_client.generate_content(prompt)
    return response
```

---

## 4.6 데이터 수집 및 분석 인프라

### 4.6.1 프롬프트 로깅

```python
# models/llm_prompt_log.py

from sqlalchemy import Column, String, Text, DateTime, UUID, Integer, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

class LLMPromptLog(Base):
    """
    모든 LLM 호출을 기록한다. (재현 가능성 확보)
    """
    __tablename__ = "llm_prompt_logs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.id"))
    agent_name = Column(String)  # classifier, answer_generator 등
    
    # 프롬프트 정보
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    prompt_tokens = Column(Integer)
    
    # 응답 정보
    raw_response = Column(Text)
    parsed_response = Column(JSONB)  # JSON 파싱 결과
    completion_tokens = Column(Integer)
    
    # 메타데이터
    model_name = Column(String)
    temperature = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)
    latency_ms = Column(Integer)  # 응답 시간 (밀리초)

# 로깅 함수
async def log_llm_call(
    session_id: str,
    agent_name: str,
    system_prompt: str,
    user_prompt: str,
    response: dict,
    latency_ms: int
):
    """
    LLM 호출을 데이터베이스에 기록한다.
    """
    log_entry = LLMPromptLog(
        session_id=session_id,
        agent_name=agent_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        raw_response=json.dumps(response),
        parsed_response=response,
        model_name="gemini-2.5-flash-lite",
        latency_ms=latency_ms
    )
    
    async with AsyncSessionLocal() as session:
        session.add(log_entry)
        await session.commit()
```

### 4.6.2 A/B 테스트 데이터 수집

```python
# models/session.py

class Session(Base):
    """
    학생의 학습 세션을 기록한다.
    """
    __tablename__ = "sessions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    
    # A/B 테스트 모드
    mode = Column(Enum("agent", "freepass", name="session_mode"))
    
    # 대화 데이터
    conversation = Column(JSONB)  # 전체 대화 히스토리
    
    # 명료화 정보 (Agent 모드만)
    clarification_count = Column(Integer, default=0)
    clarification_history = Column(JSONB)
    
    # 질문 분류 (Agent 모드만)
    knowledge_code = Column(String)  # K1/K2/K3/K4
    initial_quality = Column(String)  # answerable/needs_clarify/unanswerable
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # 세션 메타데이터
    session_title = Column(String)  # Observer가 생성
    key_concepts = Column(JSONB)  # 주요 개념 목록
```

---

## 4.7 구현 결과 요약

### 4.7.1 시스템 성능 지표

실제 운영 환경에서 수집된 성능 데이터 (2025년 10월 20일 ~ 11월 1일):

| 지표 | 값 | 비고 |
|------|-----|------|
| **평균 응답 시간** | 2.3초 | 질문 제출 → 첫 답변 생성 |
| **Classifier 처리 시간** | 1.8초 | K1-K4 분류 + 명료화 질문 생성 |
| **Answer Generator 처리 시간** | 2.1초 | 유형별 맞춤 답변 생성 |
| **동시 세션 처리** | 최대 120개 | Redis Streams + 비동기 I/O |
| **일일 LLM API 호출** | 평균 387건 | 5개 에이전트 통합 |
| **시스템 가용성** | 99.2% | 12일간 운영 |

### 4.7.2 기술적 달성 사항

#### **재현 가능성 (Reproducibility)**
- ✅ 모든 프롬프트와 LLM 응답을 PostgreSQL에 기록
- ✅ 구조화된 JSON 로그로 분석 용이
- ✅ A/B 테스트 모드 자동 할당 및 추적

#### **확장 가능성 (Scalability)**
- ✅ Redis Streams 기반 비동기 통신으로 수평 확장 가능
- ✅ 각 에이전트 독립 프로세스로 개별 확장 가능
- ✅ Docker Compose로 쉬운 배포 및 복제

#### **안정성 (Reliability)**
- ✅ Connection Pooling으로 리소스 효율 최적화
- ✅ Rate Limiter로 API 한도 초과 방지
- ✅ Supervisor 패턴으로 에이전트 자동 재시작
- ✅ 재시도 로직으로 일시적 장애 대응

---

**다음 장 예고**: 5장에서는 본 시스템을 수학적 귀납법 단원에 구체적으로 적용한 사례와 실제 학생 대화 시나리오를 다룬다.

