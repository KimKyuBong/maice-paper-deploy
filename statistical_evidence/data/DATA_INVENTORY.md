# 📦 논문 통계분석 원본 데이터 인벤토리

## 📁 디렉토리 구조

```
data/
├── DATA_INVENTORY.md              # 이 파일
├── llm_evaluations/                # LLM 평가 데이터
│   ├── gemini_results_20251105_174045.jsonl
│   ├── anthropic_haiku45_results_20251105.jsonl
│   └── openai_gpt5mini_results_20251105.jsonl
├── teacher_evaluations/            # 교사 평가 데이터
│   └── latest_evaluations.json
├── session_data/                   # 세션 메타데이터
│   ├── full_sessions_with_scores.csv
│   ├── session_metadata_full.csv
│   └── users_data.csv
└── analysis_results/               # 기존 분석 결과
    ├── teacher_correlation_results.json
    ├── three_teachers_correlation_results.json
    ├── three_teachers_items_results.json
    └── llm_teacher_correlation_results.json
```

---

## 1. LLM 평가 데이터

### 1.1 Gemini 2.5 Flash 평가 결과
**파일**: `llm_evaluations/gemini_results_20251105_174045.jsonl`

- **형식**: JSONL (JSON Lines)
- **생성일**: 2025-11-05 17:40:45
- **모델**: Gemini 2.5 Flash
- **예상 레코드 수**: ~284개 세션
- **용도**: 논문 표Ⅴ-4, 표Ⅴ-5, 표Ⅴ-6 (LLM 평가 3개 모델 평균)

**데이터 구조**:
```json
{
  "metadata": {
    "key": "session_123"
  },
  "response": {
    "candidates": [
      {
        "content": {
          "parts": [
            {
              "text": "```json\n{\"question\": {...}, \"answer\": {...}, \"context\": {...}}\n```"
            }
          ]
        }
      }
    ]
  }
}
```

**평가 항목**:
- Question (질문): professionalism, structuring, context_application
- Answer (응답): customization, systematicity, expandability
- Context (맥락): dialogue_coherence, learning_support

---

### 1.2 Claude 4.5 Haiku 평가 결과
**파일**: `llm_evaluations/anthropic_haiku45_results_20251105.jsonl`

- **형식**: JSONL
- **생성일**: 2025-11-05
- **모델**: Claude 4.5 Haiku (Anthropic)
- **예상 레코드 수**: ~284개 세션
- **용도**: LLM 평가 3개 모델 평균

**데이터 구조**:
```json
{
  "custom_id": "session_123",
  "result": {
    "message": {
      "content": [
        {
          "text": "```json\n{\"question\": {...}, \"answer\": {...}, \"context\": {...}}\n```"
        }
      ]
    }
  }
}
```

---

### 1.3 GPT-5 mini 평가 결과
**파일**: `llm_evaluations/openai_gpt5mini_results_20251105.jsonl`

- **형식**: JSONL
- **생성일**: 2025-11-05
- **모델**: GPT-5 mini (OpenAI)
- **예상 레코드 수**: ~284개 세션
- **용도**: LLM 평가 3개 모델 평균

**데이터 구조**:
```json
{
  "custom_id": "session_123",
  "response": {
    "body": {
      "choices": [
        {
          "message": {
            "content": "{\"question\": {...}, \"answer\": {...}, \"context\": {...}}"
          }
        }
      ]
    }
  }
}
```

**통계 분석 용도**:
- 3개 모델 평균 계산
- Cronbach's α = 0.868
- ICC(2,1) = 0.642
- Pearson r = 0.709 (모델 간)

---

## 2. 교사 평가 데이터

### 2.1 교사 평가 결과 (외부 수학 교사 2명)
**파일**: `teacher_evaluations/latest_evaluations.json`

- **형식**: JSON Array
- **평가자**: 교사 96, 97 (외부 수학 교사)
- **평가 세션**: 100개
- **평가 방식**: 동일 세션 독립 평가 (완전한 대응 설계)
- **총 레코드**: 200개 (100 × 2)
- **용도**: 논문 표Ⅴ-8, 표Ⅴ-9, 표Ⅴ-10 (교사 평가)

**데이터 구조**:
```json
[
  {
    "conversation_session_id": 123,
    "evaluated_by": 96,
    "question_professionalism_score": 4,
    "question_structuring_score": 5,
    "question_context_application_score": 2,
    "question_total_score": 11,
    "answer_customization_score": 4,
    "answer_systematicity_score": 5,
    "answer_expandability_score": 2,
    "response_total_score": 11,
    "context_dialogue_coherence_score": 5,
    "context_learning_support_score": 3,
    "context_total_score": 8,
    "overall_score": 30
  }
]
```

**통계 분석 용도**:
- 교사 2명 평균 계산
- 평가자 간 신뢰도: Pearson r = 0.644, Spearman ρ = 0.571
- LLM-교사 상관관계: r = 0.743

---

## 3. 세션 메타데이터

### 3.1 전체 세션 점수 데이터
**파일**: `session_data/full_sessions_with_scores.csv`

- **형식**: CSV
- **레코드 수**: ~284개 세션
- **용도**: 모드별 비교, Quartile 분석
- **포함 정보**:
  - session_id: 세션 ID
  - user_id: 학생 ID
  - mode: Agent 또는 Freepass
  - midterm_score: 중간고사 점수
  - quartile: Q1, Q2, Q3, Q4
  - llm_scores: LLM 평가 점수 (3개 모델 평균)

**통계 분석 용도**:
- 표Ⅴ-4: 전체 모드 효과
- 표Ⅴ-5, Ⅴ-6: Quartile별 분석
- 독립표본 t-검정

---

### 3.2 세션 메타데이터
**파일**: `session_data/session_metadata_full.csv`

- **형식**: CSV
- **레코드 수**: ~346개 세션 (전체 수집 세션)
- **포함 정보**:
  - session_id
  - created_at: 세션 생성 시각
  - message_count: 메시지 수
  - clarification_count: 명료화 횟수
  - session_duration: 세션 지속 시간

**통계 분석 용도**:
- 표Ⅴ-2: 명료화 수행 현황
- 기술통계

---

### 3.3 사용자 데이터
**파일**: `session_data/users_data.csv`

- **형식**: CSV
- **레코드 수**: 58명 학생
- **포함 정보**:
  - user_id
  - assigned_mode: Agent 또는 Freepass
  - midterm_total: 중간고사 총점
  - midterm_quartile: Q1, Q2, Q3, Q4

**통계 분석 용도**:
- 표Ⅴ-1: 데이터 수집 현황
- 사전 동질성 검증
- Quartile 분류 기준

---

## 4. 기존 분석 결과

### 4.1 교사 4명 상관관계 분석 결과
**파일**: `analysis_results/teacher_correlation_results.json`

- **분석 내용**: 4명 교사(93, 94, 96, 97) 평가자 간 상관관계
- **용도**: 평가자 간 신뢰도 검증
- **포함 지표**: Pearson r, Spearman ρ (쌍별)

---

### 4.2 교사 3명 상관관계 분석 결과
**파일**: `analysis_results/three_teachers_correlation_results.json`

- **분석 내용**: 3명 교사(93, 96, 97) 100개 세션 상관관계
- **용도**: 교사 평가 신뢰도
- **포함 지표**: 쌍별 상관계수, 공통 세션 분석

---

### 4.3 교사 3명 세부 항목 분석 결과
**파일**: `analysis_results/three_teachers_items_results.json`

- **분석 내용**: 12개 루브릭 항목별 교사 간 상관관계
- **용도**: 항목별 평가자 일치도
- **포함 지표**: 영역별 상관계수, 카테고리별 평균

---

### 4.4 LLM-교사 상관관계 분석 결과
**파일**: `analysis_results/llm_teacher_correlation_results.json`

- **분석 내용**: LLM 3개 모델과 교사 2명 일치도
- **용도**: 논문 표Ⅴ-11, 표Ⅴ-12
- **포함 지표**: 
  - 전체 점수: r = 0.743
  - 항목별 상관계수
  - Q1 효과 수렴 분석

---

## 📊 데이터 통계 요약

### 전체 데이터셋
| 항목 | 수량 | 비고 |
|------|------|------|
| **전체 세션** | 346개 | 수집된 모든 세션 |
| **유효 세션** | 284개 | LLM 3개 모델 공통 평가 |
| **교사 평가 세션** | 100개 | 교사 2명 독립 평가 |
| **학생 수** | 58명 | Agent 28명, Freepass 30명 |

### 평가 분포
| 모드 | 세션 수 | 비율 |
|------|---------|------|
| **Agent** | 115개 | 40.5% |
| **Freepass** | 169개 | 59.5% |

### 성적 분위
| Quartile | 세션 수 (LLM) | 세션 수 (교사) |
|:--------:|:-------------:|:--------------:|
| Q1 (하위) | 75개 | 26개 |
| Q2 (중하위) | 71개 | 26개 |
| Q3 (중상위) | 72개 | 24개 |
| Q4 (상위) | 66개 | 24개 |

---

## 🔐 데이터 보안 및 윤리

### 개인정보 보호
- ✅ 모든 학생 ID는 익명화 (숫자 ID)
- ✅ 개인 식별 정보 제거
- ✅ 연구 윤리 승인 완료

### 데이터 사용 제한
- ⚠️ 본 데이터는 논문 검증 목적으로만 사용
- ⚠️ 외부 공개 금지
- ⚠️ 재배포 금지

---

## 📝 데이터 처리 파이프라인

```
원본 데이터 (analysis/)
    ↓
복사 및 정리 (statistical_evidence/data/)
    ↓
파싱 및 처리 (01_llm_scoring/, 02_teacher_scoring/)
    ↓
통계 분석 (03_correlation_analysis/, 04_effect_size/)
    ↓
검증 및 보고서 (05_chapter5_evidence/)
```

---

## 🔄 데이터 업데이트

### 원본 위치
모든 데이터의 원본은 다음 위치에 있습니다:
```
/Users/hwansi/Library/CloudStorage/SynologyDrive-MAC/Drive/6_PrivateFolder/common/obsidian/MyReport/maice-paper-deploy/analysis/
```

### 업데이트 방법
원본 데이터가 변경되면 다음 명령으로 업데이트:
```bash
cd statistical_evidence
rm -rf data/
mkdir -p data/{llm_evaluations,teacher_evaluations,session_data,analysis_results}

# LLM 평가 데이터
cp ../analysis/threemodel/*.jsonl data/llm_evaluations/

# 교사 평가 데이터
cp ../analysis/latest_evaluations.json data/teacher_evaluations/

# 세션 데이터
cp ../analysis/full_sessions_with_scores.csv data/session_data/
cp ../analysis/session_metadata_full.csv data/session_data/
cp ../analysis/users_data.csv data/session_data/

# 기존 분석 결과
cp ../analysis/*_results.json data/analysis_results/
```

---

## ✅ 데이터 무결성 체크리스트

### LLM 평가 데이터
- [ ] 3개 파일 모두 존재
- [ ] 각 파일 크기 > 100KB
- [ ] JSONL 형식 유효
- [ ] session_id 중복 없음
- [ ] 284개 공통 세션 확인

### 교사 평가 데이터
- [ ] 파일 존재
- [ ] 200개 레코드 (100 × 2)
- [ ] 교사 96, 97만 포함
- [ ] 완전한 대응 설계 확인

### 세션 메타데이터
- [ ] 3개 파일 모두 존재
- [ ] CSV 형식 유효
- [ ] 세션 ID 일치
- [ ] 결측치 처리 확인

---

## 📚 관련 문서

1. **README.md**: 전체 개요
2. **QUICK_START.md**: 빠른 시작 가이드
3. **05_chapter5_evidence/chapter5_statistics_summary.md**: 통계기법 정리
4. **VERIFICATION_CHECKLIST.md**: 검증 체크리스트

---

**최종 업데이트**: 2025-11-13  
**데이터 수집 기간**: 2025-10-27 ~ 2025-11-11 (16일)  
**작성자**: MAICE 연구팀  
**목적**: 논문 통계분석 재현성 확보

