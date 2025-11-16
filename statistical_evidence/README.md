# 논문 통계분석 근거자료

## 📁 디렉토리 구조

```
statistical_evidence/
├── README.md                          # 이 파일
├── 01_llm_scoring/                    # LLM 채점점수 처리
│   ├── llm_score_processing.py
│   ├── llm_reliability_analysis.py
│   └── results/
├── 02_teacher_scoring/                # 교사 채점점수 처리
│   ├── teacher_score_processing.py
│   ├── inter_rater_reliability.py
│   └── results/
├── 03_correlation_analysis/           # 상관관계 분석
│   ├── pearson_spearman_analysis.py
│   ├── llm_teacher_correlation.py
│   └── results/
├── 04_effect_size/                    # 효과 크기 분석
│   ├── cohens_d_calculation.py
│   ├── quartile_analysis.py
│   └── results/
├── 05_chapter5_evidence/              # 5장 통계 종합
│   ├── chapter5_statistics_summary.md
│   ├── all_tests_verification.py
│   └── results/
└── verification_report.md             # 최종 검증 보고서
```

## 🎯 목적

본 디렉토리는 논문 5장에서 사용된 모든 통계분석의 **재현가능성(Reproducibility)**과 **검증가능성(Verifiability)**을 확보하기 위한 근거자료를 제공합니다.

## 📊 주요 통계 기법

### 1. LLM 채점점수 처리
- **3개 모델 평균**: Gemini 2.5 Flash, Claude 4.5 Haiku, GPT-5 mini
- **신뢰도 분석**: 
  - Cronbach's α = 0.868 (내적 일관성)
  - ICC (급내상관계수) = 0.642
  - Pearson r = 0.709 (모델 간 상관)

### 2. 교사 채점점수 처리
- **평가자**: 외부 수학 교사 2명 (ID: 96, 97)
- **평가 방식**: 동일 세션 독립 평가 (N=100)
- **평가자 간 신뢰도**:
  - Pearson r = 0.644*** (p<0.001)
  - Spearman ρ = 0.571*** (p<0.001)

### 3. 상관관계 분석
- **Pearson 상관계수**: 선형 관계 측정
- **Spearman 순위 상관**: 비선형 관계 측정
- **LLM-교사 일치도**: r = 0.743*** (N=100)

### 4. 독립표본 t-검정
- **가정 검증**: 정규성(Shapiro-Wilk), 등분산성(Levene)
- **효과 크기**: Cohen's d
  - 작은 효과: d = 0.2
  - 중간 효과: d = 0.5
  - 큰 효과: d = 0.8

### 5. Quartile 분석
- **중간고사 성적 기준** 4분위 분할
- **Q1 (하위 25%)** 특별 효과 검증
  - LLM 평가: +2.46점 (d=0.511, p=0.033*)
  - 교사 평가: +6.91점 (d=1.117, p=0.009**)

## 🔍 검증 전략

### 1단계: 개별 분석 검증
각 통계 기법별로 독립적인 Python 스크립트로 구현하고 검증합니다.

### 2단계: 5장 결과 재현
논문 5장의 모든 표와 수치를 재현하여 정확성을 확인합니다.

### 3단계: 가정 검증
통계적 가정(정규성, 등분산성 등)이 충족되는지 확인합니다.

### 4단계: 해석 타당성
통계적 유의성과 효과 크기를 종합하여 교육적 해석의 타당성을 검증합니다.

## 📝 주요 발견 요약

### 전체 모드 효과
| 항목 | LLM 평가 (N=284) | 교사 평가 (N=100) |
|------|-----------------|------------------|
| C2 학습 지원 | p=0.002**, d=0.376 | - |
| 전체 점수 | - | p=0.031*, d=0.307 |
| 응답 영역 | - | p=0.008**, d=0.380 |

### 하위권(Q1) 효과
| 평가 방법 | 차이 | Cohen's d | p-value |
|----------|------|-----------|---------|
| LLM 평가 | +2.46점 | 0.511 | 0.033* |
| 교사 평가 | +6.91점 | 1.117 | 0.009** |

### 평가자 간 일치도
| 비교 | 상관계수 | p-value |
|------|---------|---------|
| LLM 3개 모델 | r=0.709 | <0.001*** |
| 교사 2명 | r=0.644 | <0.001*** |
| LLM-교사 | r=0.743 | <0.001*** |

## ⚠️ 통계적 가정 및 제한점

### 정규성 가정
- 표본 크기: N=284 (충분히 큼, 중심극한정리 적용 가능)
- Shapiro-Wilk 검정 결과 포함

### 등분산성 가정
- Levene's test 결과 포함
- 위반 시 Welch's t-test 사용

### Q1 표본 크기
- LLM 평가: n=75 (적정)
- **교사 평가: n=26 (작음) ⚠️**
- 해석 시 신중함 필요

## 📚 참고 문헌

### 통계 방법론
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.
- Cronbach, L. J. (1951). Coefficient alpha and the internal structure of tests. *Psychometrika*, 16(3), 297-334.
- McGraw, K. O., & Wong, S. P. (1996). Forming inferences about some intraclass correlation coefficients. *Psychological Methods*, 1(1), 30-46.

### 교육 연구
- Hattie, J., & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81-112.
- Schoenfeld, A. H. (1985). *Mathematical Problem Solving*. Academic Press.

## 🚀 사용 방법

### 재현 가능성 (Reproducibility)

**⚠️ 중요**: 재현 가능성을 위해 다음 단계를 따라주세요.

#### 1. 의존성 설치
```bash
cd statistical_evidence
pip install -r requirements.txt
```

#### 2. 데이터 준비
대부분의 스크립트는 `statistical_evidence/data/` 폴더의 데이터를 사용합니다.
- ✅ 이미 처리된 데이터: `data/llm_evaluations/`, `data/teacher_evaluations/` 등
- ⚠️ 원본 데이터가 필요한 경우: 상위 폴더의 `analysis/` 폴더 참조

#### 3. 실행 순서
```bash
# 1. LLM 평가 처리 (최종 CSV 파일 사용)
# ⚠️ 중요: llm_3models_284_PERFECT_FINAL.csv 파일이 필요합니다
python 01_llm_scoring/llm_score_processing.py  # 3개 모델 평균 계산
python 01_llm_scoring/llm_reliability_analysis.py  # 신뢰도 분석
# 또는 이미 처리된 결과 사용:
python 01_llm_scoring/process_perfect_final.py

# 2. 교사 평가 처리
python 02_teacher_scoring/process_teacher_perfect.py

# 3. 상관관계 분석
python 03_correlation_analysis/llm_teacher_correlation_perfect.py

# 4. 효과 크기 분석
python 04_effect_size/cohens_d_calculation.py
python 04_effect_size/mode_quartile_analysis_perfect.py

# 5. 학생 설문 분석
python 05_student_survey/analyze_survey_47_by_mode_final.py
```

**⚠️ 중요**: LLM 채점 자료는 **최종 생성된 CSV 파일(`llm_3models_284_PERFECT_FINAL.csv`)만 사용**합니다.
- 원본 JSONL 파일은 사용하지 않습니다.
- 3개 모델의 채점 결과가 모두 포함된 최종 CSV만 인용합니다.

#### 4. 전체 검증 실행
```bash
python 05_chapter5_evidence/all_tests_verification.py
```

**참고**: 재현 가능성 상세 검증 결과는 `REPRODUCIBILITY_CHECK.md`를 참조하세요.

### 개별 분석 실행 (레거시)
```bash
# LLM 점수 처리 (원본 JSONL 파일 필요)
python 01_llm_scoring/llm_score_processing.py

# 교사 점수 처리 (원본 JSON 파일 필요)
python 02_teacher_scoring/teacher_score_processing.py

# 상관관계 분석
python 03_correlation_analysis/llm_teacher_correlation.py

# 효과 크기 분석
python 04_effect_size/quartile_analysis.py
```

## 📋 재현 가능성 상태

**현재 상태**: ✅ **완전 재현 가능**

- ✅ 데이터 파일: 모두 존재 (`statistical_evidence/data/`)
- ✅ 스크립트: 모든 스크립트 실행 가능
- ✅ 경로 설정: 모든 스크립트가 `statistical_evidence/data/`만 참조
- ✅ 의존성: `requirements.txt` 제공
- ✅ analysis 폴더 참조: 완전 제거

**상세 검증 결과**: `REPRODUCIBILITY_CHECK.md` 참조

## 📧 문의

통계분석 관련 문의사항은 연구자에게 연락 바랍니다.

---

**최종 업데이트**: 2025-01-XX  
**작성자**: MAICE 연구팀  
**목적**: 논문 통계분석 재현성 확보

