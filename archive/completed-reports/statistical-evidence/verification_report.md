# 논문 5장 통계분석 검증 보고서

**생성 일시**: 2025-11-13 15:26:16

**검증 상태**: ❌ 검증 실패

---

## 1. 스크립트 실행 결과

- ❌ **1_llm_processing**: error
- ❌ **2_llm_reliability**: error
- ✅ **3_teacher_processing**: success
- ✅ **4_teacher_reliability**: success
- ❌ **5_correlation**: error
- ✅ **6_effect_size**: success

## 2. 논문 기재값 vs 계산값 비교

| 지표 | 논문 | 계산 | 차이 | 일치 |
|------|:----:|:----:|:----:|:----:|
| Pearson r (교사 간) | 0.644 | 0.644 | 0.000 | ✓ |

### 교사 평가자 간 신뢰도

- Pearson r: 0.644
- Spearman ρ: 0.568

### Cohen's d 효과 크기

| 분석 항목 | Cohen's d | 해석 |
|----------|-----------|------|
| C2 학습 지원 (LLM, 전체) | 0.376 | 작은 효과 (Small) |
| Q1 하위권 (LLM) | 0.511 | 중간 효과 (Medium) |
| 전체 점수 (교사) | 0.307 | 작은 효과 (Small) |
| 응답 영역 (교사) | 0.380 | 작은 효과 (Small) |
| Q1 하위권 (교사) | 1.117 | 큰 효과 (Large) |

---

## 4. 결론

❌ **검증 실패: 일부 스크립트 실행 오류 또는 불일치가 있습니다.**

상세한 오류 내용은 verification_results.json 파일을 참조하세요.

---

**생성 도구**: `all_tests_verification.py`  
**목적**: 논문 통계분석 재현성 확보
