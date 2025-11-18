# 5장 통계 근거 자료 (Chapter 5 Evidence)

이 디렉토리는 논문 5장의 모든 통계 수치를 Python 스크립트로 재현 가능하게 만든 계산 파일들을 포함합니다.

## 📊 표별 계산 스크립트

### 1절. 연구 실행 및 데이터 수집

#### 표Ⅴ-1: 수집 데이터 현황
- **스크립트**: `ch5_1_n_data_collection.py`
- **결과 파일**: `results/ch5_1_n_data_collection.json`
- **데이터**: `data/session_data/full_sessions_with_scores.csv`

#### 표Ⅴ-2: 명료화 수행 현황
- **스크립트**: `ch5_1_r_clarification_operation.py`
- **결과 파일**: `results/ch5_1_r_clarification_operation.json`
- **데이터**: 
  - `data/db_exports/public_llm_prompt_logs_full.csv` (PostgreSQL에서 추출)
  - `data/session_data/full_sessions_with_scores.csv`
- **방법**: DB 로그에서 `classifier_llm`/`question_improver_llm` 호출 여부로 판단

#### 사전 동질성 검증
- **스크립트**: `ch5_1_d_pre_homogeneity.py`
- **결과 파일**: `results/ch5_1_d_pre_homogeneity.json`
- **데이터**: 
  - `data/session_data/full_sessions_with_scores.csv`
  - `data/session_data/midterm_scores_with_quartile.csv`

### 2절. 명료화 효과: LLM-교사 이중 평가

#### 표Ⅴ-4: 세부 항목별 모드 비교 (LLM 평가)
- **스크립트**: `../04_effect_size/mode_quartile_analysis_perfect.py`
- **섹션**: 5장 2절 나항 (2) 전체 모드 효과

#### 표Ⅴ-5: Quartile별 C2(학습 지원) 비교 (LLM 평가)
- **스크립트**: `../04_effect_size/mode_quartile_analysis_perfect.py`
- **섹션**: 5장 2절 나항 (3) 성적 수준별 차별적 효과

#### 표Ⅴ-6: Quartile별 전체 점수 (LLM 평가)
- **스크립트**: `../04_effect_size/mode_quartile_analysis_perfect.py`
- **섹션**: 5장 2절 나항 (3) 성적 수준별 차별적 효과

#### 표Ⅴ-7: 세션 증가에 따른 항목별 점수 변화
- **스크립트**: `../04_effect_size/mode_quartile_analysis_perfect.py`
- **섹션**: 5장 2절 나항 (4) 반복 사용 효과

#### 표Ⅴ-9: 모드별 점수 비교 (교사 평가)
- **스크립트**: `../04_effect_size/teacher_mode_comparison_perfect.py`
- **섹션**: 5장 2절 다항 (2) 전체 모드 효과

#### 표Ⅴ-10: Quartile별 전체 점수 (교사 평가)
- **스크립트**: `../04_effect_size/teacher_mode_comparison_perfect.py`
- **섹션**: 5장 2절 다항 (3) 하위권 효과

#### 표Ⅴ-11: LLM-교사 평가 상관관계
- **스크립트**: `../03_correlation_analysis/llm_teacher_correlation_perfect.py`
- **섹션**: 5장 2절 라항 (1) 전체 점수 상관관계

#### 표Ⅴ-12: Q1(하위권) Agent 우위 폭 비교
- **스크립트**: `ch5_2_e_2_q1_convergence.py`
- **결과 파일**: `results/ch5_2_e_2_q1_convergence.json`
- **섹션**: 5장 2절 라항 (2) Q1 하위권 효과의 수렴

### 3절. 학습자 자기 평가 및 증거의 수렴

#### 표Ⅴ-14: 학습자 자기 평가 결과
- **스크립트**: `../05_student_survey/analyze_survey_47_by_mode_final.py`
- **데이터**: `data/MAICE 사용 설문조사 (2025학년도 2학년 수학)(1-47).csv`

#### 표Ⅴ-15: 명료화 방식 선호도
- **스크립트**: `../05_student_survey/analyze_survey_47_by_mode_final.py`
- **데이터**: `data/MAICE 사용 설문조사 (2025학년도 2학년 수학)(1-47).csv`

### 4절. 피드백 내용의 질적 분석

#### 표Ⅴ-23, Ⅴ-25, Ⅴ-26: Bloom-Dewey 이론 실증 분석
- **스크립트**: `ch5_4_bloom_dewey_from_db.py`
- **결과 파일**: 
  - `results/ch5_4_bloom_dewey_from_db.json`
  - `results/llm_prompt_logs_with_scores.csv`
- **데이터**: 
  - `data/db_exports/public_llm_prompt_logs_full.csv` (PostgreSQL에서 추출)
  - `data/db_exports/public_llm_response_logs_full.csv` (PostgreSQL에서 추출)
- **참고**: 질적 코딩 기반 분석. DB 로그를 수동으로 Bloom/Dewey 단계 코딩 필요

## 📁 DB 데이터 추출

### PostgreSQL 데이터베이스에서 데이터 추출
- **스크립트**: `export_db_data.py`
- **데이터베이스**: `maice_agent@192.168.1.110`
- **출력 디렉토리**: `../data/db_exports/`
- **추출된 파일**:
  - `public_llm_prompt_logs_full.csv` (1,671건)
  - `public_llm_response_logs_full.csv` (1,581건)
  - `export_metadata.json` (메타데이터)

## 🔄 재현 방법

### 1. DB 데이터 추출 (최초 1회)
```bash
cd statistical_evidence
python 05_chapter5_evidence/export_db_data.py
```

### 2. 각 표 계산
```bash
# 표Ⅴ-1
python 05_chapter5_evidence/ch5_1_n_data_collection.py

# 표Ⅴ-2
python 05_chapter5_evidence/ch5_1_r_clarification_operation.py

# 사전 동질성
python 05_chapter5_evidence/ch5_1_d_pre_homogeneity.py

# 표Ⅴ-12
python 05_chapter5_evidence/ch5_2_e_2_q1_convergence.py

# Bloom-Dewey 분석 데이터
python 05_chapter5_evidence/ch5_4_bloom_dewey_from_db.py
```

### 3. 다른 표들은 상위 디렉토리의 스크립트 사용
- LLM 평가: `04_effect_size/mode_quartile_analysis_perfect.py`
- 교사 평가: `04_effect_size/teacher_mode_comparison_perfect.py`
- 상관관계: `03_correlation_analysis/llm_teacher_correlation_perfect.py`
- 학생 설문: `05_student_survey/analyze_survey_47_by_mode_final.py`

## 📋 데이터 흐름

```
PostgreSQL (192.168.1.110)
    ↓ export_db_data.py
data/db_exports/
    ├── public_llm_prompt_logs_full.csv
    └── public_llm_response_logs_full.csv
    ↓ 각 계산 스크립트
results/
    ├── ch5_1_n_data_collection.json
    ├── ch5_1_r_clarification_operation.json
    ├── ch5_1_d_pre_homogeneity.json
    ├── ch5_2_e_2_q1_convergence.json
    └── ch5_4_bloom_dewey_from_db.json
```

## ✅ 검증 완료 항목

- [x] 표Ⅴ-1: 수집 데이터 현황
- [x] 표Ⅴ-2: 명료화 수행 현황 (DB 로그 기반)
- [x] 사전 동질성 검증
- [x] 표Ⅴ-4: 세부 항목별 모드 비교 (LLM)
- [x] 표Ⅴ-5: Quartile별 C2 비교 (LLM)
- [x] 표Ⅴ-6: Quartile별 전체 점수 (LLM)
- [x] 표Ⅴ-7: 세션 증가에 따른 점수 변화
- [x] 표Ⅴ-9: 모드별 점수 비교 (교사)
- [x] 표Ⅴ-10: Quartile별 전체 점수 (교사)
- [x] 표Ⅴ-11: LLM-교사 평가 상관관계
- [x] 표Ⅴ-12: Q1 하위권 Agent 우위 폭 비교
- [x] 표Ⅴ-14: 학습자 자기 평가 결과
- [x] 표Ⅴ-15: 명료화 방식 선호도
- [x] 표Ⅴ-23, Ⅴ-25, Ⅴ-26: Bloom-Dewey 분석 원본 데이터

## 📝 주의사항

1. **DB 데이터 추출**: PostgreSQL 데이터베이스에 직접 접근하여 원본 데이터를 추출합니다. 네트워크 연결이 필요합니다.
2. **명료화 수행 현황**: DB 로그에서 `classifier_llm` 또는 `question_improver_llm` 호출 여부로 판단합니다.
3. **Bloom/Dewey 분석**: 질적 코딩 기반 분석이므로, DB 로그를 수동으로 코딩하는 별도 프로세스가 필요합니다.
4. **교사 평가**: 평가자 96, 97만 사용합니다.
5. **학생 설문**: 불명확한 응답은 제외합니다.


