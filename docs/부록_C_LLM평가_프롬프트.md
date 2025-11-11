# 부록 G. LLM 배치 채점 프롬프트 전문

본 연구에서 Gemini 2.5 Flash, Claude 4.5 Haiku, GPT-5 mini 3개 모델의 배치 채점에 사용된 프롬프트 전문입니다.

---

## 1. 평가 프롬프트 개요

**목적**: 학생-MAICE 간 수학 학습 세션의 질문 품질, 답변 품질, 대화 맥락을 체계적으로 평가

**평가 대상**:
- 학생이 세션 내에 남긴 모든 질문(유저 메시지)
- MAICE(assistant)가 남긴 모든 답변(assistant 메시지)
- 전체 대화 흐름(맥락)

**평가 방식**: 
- QAC 체크리스트 v4.3 (C1 제외, 8개 항목, 32개 체크리스트 요소)
- 40점 만점 (A영역 15점 + B영역 15점 + C영역 10점)
- 각 체크리스트 요소는 0(미충족) 또는 1(충족)로 평가
- 각 항목: 4개 체크리스트 × 1.25점 = 5점

---

## 2. 실제 프롬프트 전문

```
아래는 학생(유저)과 MAICE(assistant) 간 전체 수학 학습 세션 대화입니다.

- 학생이 세션 내에 남긴 모든 질문(유저 메시지)
- MAICE(assistant)가 남긴 모든 답변(assistant 메시지)
- 전체 대화 흐름(맥락)

을 통합적으로 고려해서 아래 루브릭 기준에 따라 채점하세요.

# 수학 학습 세션 평가 루브릭 (C1 제외 - 공정한 평가)

## 평가 개요
- **평가 대상**: 학생 질문(15점), AI 응답(15점), 대화 맥락(10점)
- **전체 총점**: 40점 만점 (C1 명료화 항목 제외)
- **척도**: 각 세부 항목 5점 만점 (1점: 매우 미흡, 5점: 매우 우수)

---

## A. 학생 질문 평가 (15점 만점)

### A1. 수학적 전문성 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- A1-1. ☐ **concept_accuracy** (수학적 개념/원리의 정확성): 수학 용어를 정확하게 사용했는가?
- A1-2. ☐ **curriculum_hierarchy** (교과과정 내 위계성 파악): 학년 수준에 맞는 개념인가?
- A1-3. ☐ **terminology_appropriateness** (수학적 용어 사용의 적절성): 전문 용어를 적절히 사용했는가?
- A1-4. ☐ **problem_direction_specificity** (문제해결 방향의 구체성): 해결하려는 문제가 구체적인가?

### A2. 질문 구조화 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- A2-1. ☐ **question_singularity** (핵심 질문의 단일성): 한 번에 하나의 명확한 질문을 하는가?
- A2-2. ☐ **condition_completeness** (조건 제시의 완결성): 필요한 조건/정보를 모두 제시했는가?
- A2-3. ☐ **sentence_logic** (문장 구조의 논리성): 문장이 논리적으로 구성되었는가?
- A2-4. ☐ **intent_clarity** (질문 의도의 명시성): 무엇을 알고 싶은지 명확한가?

### A3. 학습 맥락 적용 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- A3-1. ☐ **current_stage_description** (현재 학습 단계 설명): 학년/단원/진도를 언급했는가?
- A3-2. ☐ **prior_learning_mention** (선수학습 내용 언급): 이전에 배운 내용을 언급했는가?
- A3-3. ☐ **difficulty_specification** (구체적 어려움 명시): 어디서 막혔는지 구체적으로 말했는가?
- A3-4. ☐ **learning_goal_presentation** (학습 목표 제시): 무엇을 배우고 싶은지 목표를 제시했는가?

---

## B. AI 응답 평가 (15점 만점)

### B1. 학습자 맞춤도 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- B1-1. ☐ **level_based_approach** (학습자 수준별 접근): 학생 수준에 맞게 설명했는가?
- B1-2. ☐ **prior_knowledge_connection** (선수지식 연계성): 이미 배운 내용과 연결했는가?
- B1-3. ☐ **difficulty_adjustment** (학습 난이도 조절): 너무 어렵거나 쉽지 않은가?
- B1-4. ☐ **personalized_feedback** (개인화된 피드백): 학생 상황을 고려한 피드백인가?

### B2. 설명의 체계성 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- B2-1. ☐ **concept_hierarchy** (개념 설명의 위계화): 쉬운 것부터 어려운 것으로 단계적으로 설명했는가?
- B2-2. ☐ **stepwise_logic** (단계별 논리 전개): 각 단계가 논리적으로 연결되는가?
- B2-3. ☐ **key_emphasis** (핵심 요소 강조): 중요한 내용을 명확히 강조했는가?
- B2-4. ☐ **example_appropriateness** (예시 활용의 적절성): 이해를 돕는 적절한 예시를 제공했는가?

### B3. 학습 내용 확장성 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- B3-1. ☐ **advanced_direction** (심화학습 방향 제시): 더 깊이 공부할 방향을 제시했는가?
- B3-2. ☐ **application_connection** (응용문제 연계성): 관련된 응용 문제를 연결했는가?
- B3-3. ☐ **misconception_correction** (오개념 교정 전략): 잘못된 이해를 바로잡았는가?
- B3-4. ☐ **self_directed_induction** (자기주도 학습 유도): 스스로 탐구하도록 유도했는가?

---

## C. 대화 맥락 평가 (10점 만점)

### C1. 대화 일관성 및 연속성 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- C1-1. ☐ **goal_centered_consistency** (학습 목표 중심 일관성): 학습 목표를 벗어나지 않고 진행되는가?
- C1-2. ☐ **context_reference** (누적 맥락 참조): 전체 대화 이력을 기억하고 참조하는가? (멀리 떨어진 이전 대화 내용도 기억)
- C1-3. ☐ **topic_continuity** (주제 연속성): 주제가 자연스럽게 연결되는가?
- C1-4. ☐ **previous_turn_connection** (직전 턴 연결성): 각 발화가 바로 이전 턴과 유기적으로 연결되는가? (턴바이턴 흐름)

### C2. 학습 과정 지원성 (5점)

다음 **4가지 요소**를 체크하세요 (0=미충족, 1=충족):
- C2-1. ☐ **thinking_process_induction** (사고 과정 유도): 학생의 사고 과정을 유도하는가?
- C2-2. ☐ **understanding_check** (이해도 확인): 학생의 이해도를 확인하는가?
- C2-3. ☐ **metacognitive_promotion** (메타인지 촉진): 학생이 자신의 학습 과정을 돌아보게 하는가?
- C2-4. ☐ **deep_thinking_guidance** (깊이 있는 사고 유도): 단순 암기를 넘어 깊이 있는 사고를 유도하는가?

---

## 평가 지침

- 각 세부 요소는 **0 (미충족)** 또는 **1 (충족)**로만 체크
- 세션 전체에서 **가장 우수한 질문** 기준으로 A 영역 평가
- 점수 합산은 시스템이 자동으로 처리

**🚨 중요: B영역 최저점 규칙 (교사 평가 기준)**
- AI 답변이 **수학적 내용으로 이어지지 못한 경우** B1, B2, B3 모든 항목 **0개 충족** 처리
- 단순 격려("잘하고 있어요", "화이팅!"), 일반적 대화만 반복하고 수학 설명이 없는 경우
- 이 경우 B영역 총점은 3점(각 항목 1점씩)이 됨

---

## 3. 응답 형식

반드시 아래 JSON 형식으로만 응답 (각 요소에 value와 evidence 포함):

```json
{
  "A1_math_expertise": {
    "concept_accuracy": {
      "value": 1, 
      "evidence": "메시지[2]에서 '이차함수 y=x^2의 꼭짓점과 축의 방정식'이라고 표현하며 수학 용어를 정확히 사용"
    },
    "curriculum_hierarchy": {
      "value": 0, 
      "evidence": "전체 대화에서 중2, 고1 등 학년 정보나 '함수 단원', '이차함수 파트' 등 교육과정 위계 언급이 전혀 없음"
    },
    "terminology_appropriateness": {
      "value": 1, 
      "evidence": "메시지[2,4]에서 '꼭짓점', '축의 방정식', '표준형' 등 교과서 수준의 적절한 수학 용어 사용"
    },
    "problem_direction_specificity": {
      "value": 1, 
      "evidence": "메시지[0]에서 '이차함수 그래프를 그리고 싶어요'라고 구체적인 문제 해결 목표를 명시"
    }
  },
  "A2_question_structure": {
    "question_singularity": {
      "value": 1, 
      "evidence": "각 학생 메시지마다 '그래프 그리기', '꼭짓점 구하기' 등 하나의 명확한 질문에만 집중"
    },
    "condition_completeness": {
      "value": 1, 
      "evidence": "메시지[2]에서 함수식 y=x^2-4x+3을 제시하며 문제 해결에 필요한 조건을 완전히 제공"
    },
    "sentence_logic": {
      "value": 0, 
      "evidence": "메시지[4]에서 '그래프 어떻게... 꼭짓점도...' 식으로 문장이 완결되지 않고 단편적"
    },
    "intent_clarity": {
      "value": 1, 
      "evidence": "메시지[0,2,4] 모두에서 '~하고 싶어요', '~구하는 방법은?' 등 질문 의도가 명확하게 표현됨"
    }
  },
  "A3_learning_context": {
    "current_stage_description": {
      "value": 0, 
      "evidence": "전체 대화에서 현재 진도, 단원, 학년 등 학습 단계 정보가 전혀 언급되지 않음"
    },
    "prior_learning_mention": {
      "value": 0, 
      "evidence": "일차함수, 좌표평면 등 이미 배운 선수학습 내용에 대한 언급이 없음"
    },
    "difficulty_specification": {
      "value": 1, 
      "evidence": "메시지[4]에서 '꼭짓점 구하는 공식은 알겠는데 그래프 그리는 게 어려워요'라고 구체적 어려움 명시"
    },
    "learning_goal_presentation": {
      "value": 0, 
      "evidence": "'이차함수 완전 정복', '시험 대비' 등 명확한 학습 목표 제시가 없음"
    }
  },
  "B1_learner_customization": {
    "level_based_approach": {
      "value": 1, 
      "evidence": "메시지[3]에서 MAICE가 '먼저 일차 계수를 보고...'라며 학생이 이해할 수 있는 쉬운 단계부터 설명"
    },
    "prior_knowledge_connection": {
      "value": 1, 
      "evidence": "메시지[5]에서 'y=ax^2 그래프 형태는 이미 배웠죠?'라며 선수지식과 연결"
    },
    "difficulty_adjustment": {
      "value": 1, 
      "evidence": "메시지[3,5,7]에서 단계별로 난이도를 조절하며 너무 어렵지도 쉽지도 않게 설명"
    },
    "personalized_feedback": {
      "value": 0, 
      "evidence": "학생 개별 상황이나 실수 패턴을 고려한 맞춤형 피드백 없이 일반적 설명만 제공"
    }
  },
  "B2_explanation_systematicity": {
    "concept_hierarchy": {
      "value": 1, 
      "evidence": "메시지[3]에서 '1단계: 표준형 변환 → 2단계: 꼭짓점 찾기 → 3단계: 그래프 그리기' 순으로 체계적 설명"
    },
    "stepwise_logic": {
      "value": 1, 
      "evidence": "메시지[5,7,9]가 논리적으로 연결되며 각 단계가 다음 단계의 기반이 됨"
    },
    "key_emphasis": {
      "value": 1, 
      "evidence": "메시지[3]에서 '가장 중요한 건 꼭짓점입니다'라고 핵심 개념을 명시적으로 강조"
    },
    "example_appropriateness": {
      "value": 1, 
      "evidence": "메시지[7]에서 y=(x-2)^2-1 구체적 예시를 들어 꼭짓점(2,-1) 찾기 과정을 상세히 설명"
    }
  },
  "B3_learning_expandability": {
    "advanced_direction": {
      "value": 0, 
      "evidence": "이차함수 최댓값/최솟값 문제, 이차방정식 연계 등 심화 방향 제시 없음"
    },
    "application_connection": {
      "value": 0, 
      "evidence": "포물선 운동, 최적화 문제 등 실생활 응용이나 다른 단원 연계 없음"
    },
    "misconception_correction": {
      "value": 1, 
      "evidence": "메시지[9]에서 '축이 y축이 아니라 x=2입니다'라며 학생의 오개념을 명확히 교정"
    },
    "self_directed_induction": {
      "value": 0, 
      "evidence": "'스스로 해보세요', '다른 예제도 풀어볼까요?' 등 자기주도 탐구 유도 없음"
    }
  },
  "C1_dialogue_coherence": {
    "goal_centered_consistency": {
      "value": 1, 
      "evidence": "메시지[0]의 '그래프 그리기' 목표가 메시지[11]까지 일관되게 유지되며 주제 이탈 없음"
    },
    "context_reference": {
      "value": 1, 
      "evidence": "메시지[7]에서 '아까 말한 y=x^2-4x+3을 다시 보면'이라며 멀리 떨어진 이전 대화[2] 내용을 기억하고 참조 (누적 맥락 유지)"
    },
    "topic_continuity": {
      "value": 1, 
      "evidence": "그래프→꼭짓점→표준형→축 순으로 주제가 자연스럽게 확장되며 맥락 유지"
    },
    "previous_turn_connection": {
      "value": 0, 
      "evidence": "메시지[7]에서 바로 직전 학생 발화[6]의 '그래프 그리는 게 어려워요'라는 구체적 어려움을 직접 언급하지 않고 일반적 설명으로 넘어감 (턴바이턴 흐름 단절)"
    }
  },
  "C2_learning_support": {
    "thinking_process_induction": {
      "value": 1, 
      "evidence": "메시지[5]에서 '왜 표준형으로 바꿔야 할까요? 생각해봅시다'라며 학생의 사고 과정 유도"
    },
    "understanding_check": {
      "value": 0, 
      "evidence": "'이해했나요?', '직접 풀어볼까요?' 등 학생 이해도 확인 질문이 전혀 없음"
    },
    "metacognitive_promotion": {
      "value": 0, 
      "evidence": "'어떤 부분이 어려웠나요?', '어떻게 접근했나요?' 등 학습 과정 성찰 유도 없음"
    },
    "deep_thinking_guidance": {
      "value": 1, 
      "evidence": "메시지[9]에서 '왜 a값에 따라 그래프 모양이 달라질까?'라며 본질적 이해를 위한 깊이 있는 질문 제시"
    }
  }
}
```

**중요**: 
- 각 요소는 `{"value": 0 또는 1, "evidence": "구체적인 근거 문장"}` 형식
- evidence는 실제 대화에서 인용한 구체적 근거를 포함 (30-100자 권장)
- 근거 작성 방법:
  * value=1인 경우: 실제 대화 내용을 인용하여 충족 근거 제시 (예: "메시지[3]에서 '이차함수의 꼭짓점을 구하는 방법' 질문")
  * value=0인 경우: 왜 충족하지 못했는지 구체적 이유 (예: "전체 대화에서 학년/단원 정보 언급 없음")
- JSON 외 부가 텍스트 금지!

=== 세션 대화 내용 ===
[여기에 실제 세션 대화가 삽입됨]
```

---

## 4. 점수 산출 방식

각 항목(A1~A3, B1~B3, C1~C2)별로:

```
체크된 요소 개수 (0~4개)에 따라 점수 산출:
- 0개 충족 → 1점
- 1개 충족 → 2점
- 2개 충족 → 3점
- 3개 충족 → 4점
- 4개 충족 → 5점

공식: 점수 = (충족된 체크리스트 개수) + 1
```

**영역별 합산**:
- A영역 (15점): A1 (5점) + A2 (5점) + A3 (5점)
- B영역 (15점): B1 (5점) + B2 (5점) + B3 (5점)
- C영역 (10점): C1 (5점) + C2 (5점)
- **총점 (40점)**

---

## 5. 실제 적용 예시

**세션 예시**:
```
[0] 학생: 이차함수 그래프를 그리고 싶어요
[1] MAICE: 어떤 이차함수인가요?
[2] 학생: y=x^2-4x+3이요
[3] MAICE: 1단계로 표준형으로 바꿔봅시다. y=(x-2)^2-1입니다.
...
```

**A1 평가 예시**:
- concept_accuracy: 1 (메시지[2]에서 '이차함수 y=x^2' 정확한 표현)
- curriculum_hierarchy: 0 (학년/단원 언급 없음)
- terminology_appropriateness: 1 (메시지[2]에서 '꼭짓점', '축' 등 용어 사용)
- problem_direction_specificity: 1 (메시지[0]에서 '그래프 그리기' 명확한 목표)

→ A1 점수 = 3개 충족 + 1 = **4점**

---

## 6. 채점 구현 코드

본 프롬프트는 다음 스크립트에서 사용됩니다:

**배치 채점 생성**: `analysis/newtest/Gemini_배치채점_3모델.py`
```python
RUBRIC_TEXT = """
[위 프롬프트 전문]
"""

def create_prompt(session):
    convo = build_conversation(session)
    return f"{RUBRIC_TEXT}\n\n=== 세션 대화 내용 ===\n{convo}"
```

**결과 파싱 및 분석**: `analysis/newtest/최종_3모델_통합분석.py`
```python
# 정규표현식으로 value만 추출 (LaTeX 수식 이스케이프 에러 방지)
for item_key, full_name in item_mapping:
    item_text = text[start_pos:next_pos]
    values = re.findall(r'"value"\s*:\s*(\d+)', item_text)
    checked_count = sum(int(v) for v in values[:4])
    score = checked_count + 1  # 0~4개 → 1~5점
```

---

## 7. 주요 설계 결정 사항

### 7.1. C1 항목 제외 이유

**초기 버전 (v4.0)**: C1. 명료화 효과성 항목 포함 (45점 만점, 9개 항목)

**문제점**:
- C1은 Agent 모드만 명료화를 수행하므로 Freepass 모드에 불리
- 공정한 비교를 위해 "대화의 질"을 측정하는 항목만 포함해야 함

**최종 버전 (v4.3)**: C1 제외 → C1(대화 일관성), C2(학습 지원)로 재구성 (40점 만점, 8개 항목)

### 7.2. 체크리스트 방식 채택

**장점**:
- 이진 판단(0/1)으로 평가자 간 일치도 향상
- 각 요소별 구체적인 근거(evidence) 제시로 평가 투명성 확보
- 자동 점수 계산으로 일관성 보장

**실제 효과**:
- 3개 AI 모델 간 ICC(2,1) = 0.642, Cronbach's α = 0.868
- AI-교사 간 일치도 Pearson r = 0.771

### 7.3. B영역 최저점 규칙

**목적**: AI가 수학적 내용을 제공하지 못한 경우 명확히 구분

**적용 조건**:
- 단순 격려만 반복 ("화이팅!", "잘하고 있어요")
- 일반적 대화만 있고 수학 설명 부재
- 기술적 오류로 답변 미생성

**처리 방식**:
- B1, B2, B3 모든 체크리스트 → 0개 충족
- B영역 총점 = 3점 (각 항목 1점씩 최저점)

---

## 8. 재현 가능성

**입력 데이터**: `analysis/newtest/학생세션_수집_20251105_154459.json` (284개 세션)

**배치 작업 생성**:
```bash
cd analysis/newtest
python3 Gemini_배치채점_3모델.py --models gemini openai anthropic
```

**결과 다운로드 및 분석**:
```bash
python3 최종_3모델_통합분석.py
```

**출력**:
- `최종_3모델_점수비교.csv`: 284개 세션별 3개 모델 점수
- `최종_3모델_요약통계.csv`: 모드별, 수준별 통계 요약
- `284개_전체_재분석_최종보고서.txt`: 상세 분석 결과

---

**작성일**: 2025년 11월 11일  
**버전**: 2.0 (284개 전체 분석)  
**출처**: `analysis/newtest/Gemini_배치채점_3모델.py` 내 `RUBRIC_TEXT` 변수

