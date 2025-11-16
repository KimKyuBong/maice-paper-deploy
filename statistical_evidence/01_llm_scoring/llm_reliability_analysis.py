#!/usr/bin/env python3
"""
LLM 평가 신뢰도 분석

논문 5장 2절 나항(1)에서 제시된 신뢰도 지표들을 검증합니다.

⚠️ 중요: 최종 생성된 CSV 파일만 사용합니다.
- 입력: llm_3models_284_PERFECT_FINAL.csv (3개 모델 채점 결과)

주요 지표:
1. Cronbach's α (내적 일관성)
2. ICC (Intraclass Correlation Coefficient, 급내상관계수)
3. Pearson 상관계수 (모델 간)

근거:
- 논문: "신뢰도: Cronbach's α=0.868, ICC=0.642, Pearson r=0.709"
- Cohen (1988), Cronbach (1951), McGraw & Wong (1996)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("LLM 평가 신뢰도 분석")
print("="*80)
print()
print("⚠️  최종 CSV 파일만 사용합니다: llm_3models_284_PERFECT_FINAL.csv")
print()

# 경로 설정
BASE_PATH = Path(__file__).parent.parent / "data"
OUTPUT_PATH = Path(__file__).parent / "results"
OUTPUT_PATH.mkdir(exist_ok=True)

# ============================================================================
# 1. Cronbach's Alpha 계산
# ============================================================================

def cronbach_alpha(data):
    """
    Cronbach's Alpha 계산
    
    α = (k / (k-1)) * (1 - (Σvar_items / var_total))
    
    where:
        k = 항목 수
        var_items = 각 항목의 분산
        var_total = 전체 점수의 분산
    
    참고: Cronbach, L. J. (1951). Coefficient alpha and the internal 
          structure of tests. Psychometrika, 16(3), 297-334.
    """
    # data: DataFrame (행=세션, 열=평가자/모델)
    n_items = data.shape[1]
    
    # 각 항목(모델)의 분산
    var_items = data.var(axis=0, ddof=1).sum()
    
    # 전체 점수의 분산 (각 행의 합)
    total_scores = data.sum(axis=1)
    var_total = total_scores.var(ddof=1)
    
    # Cronbach's Alpha
    alpha = (n_items / (n_items - 1)) * (1 - (var_items / var_total))
    
    return alpha

# ============================================================================
# 2. ICC 계산 (Two-way random effects, absolute agreement)
# ============================================================================

def calculate_icc(data):
    """
    ICC(2,1) 계산: Two-way random effects, absolute agreement
    
    참고: McGraw, K. O., & Wong, S. P. (1996). Forming inferences about 
          some intraclass correlation coefficients. Psychological Methods, 
          1(1), 30-46.
    """
    # data: DataFrame (행=세션, 열=평가자/모델)
    n_subjects = data.shape[0]  # 세션 수
    n_raters = data.shape[1]    # 모델 수
    
    # 전체 평균
    grand_mean = data.values.mean()
    
    # 세션별 평균
    subject_means = data.mean(axis=1).values
    
    # 평가자별 평균
    rater_means = data.mean(axis=0).values
    
    # Sum of Squares
    SS_total = ((data.values - grand_mean) ** 2).sum()
    SS_subjects = n_raters * ((subject_means - grand_mean) ** 2).sum()
    SS_raters = n_subjects * ((rater_means - grand_mean) ** 2).sum()
    SS_error = SS_total - SS_subjects - SS_raters
    
    # Mean Squares
    MS_subjects = SS_subjects / (n_subjects - 1)
    MS_raters = SS_raters / (n_raters - 1)
    MS_error = SS_error / ((n_subjects - 1) * (n_raters - 1))
    
    # ICC(2,1)
    icc = (MS_subjects - MS_error) / (MS_subjects + (n_raters - 1) * MS_error + n_raters * (MS_raters - MS_error) / n_subjects)
    
    return max(0, icc)  # 음수 방지

# ============================================================================
# 3. 최종 CSV 파일 로드
# ============================================================================

print("1. 최종 CSV 파일 로드")
print("-" * 80)

SOURCE_FILE = BASE_PATH / "llm_evaluations" / "llm_3models_284_PERFECT_FINAL.csv"

if not SOURCE_FILE.exists():
    print(f"❌ 파일이 없습니다: {SOURCE_FILE}")
    print("최종 생성된 CSV 파일이 필요합니다: llm_3models_284_PERFECT_FINAL.csv")
    import sys
    sys.exit(1)

df = pd.read_csv(SOURCE_FILE)
print(f"✓ 파일 로드 완료: {len(df)}개 세션, {len(df.columns)}개 컬럼")
print()

# ============================================================================
# 4. 3개 모델의 overall 점수 추출
# ============================================================================

print("2. 3개 모델 overall 점수 추출")
print("-" * 80)

models = ['gemini', 'anthropic', 'openai']
reliability_data = pd.DataFrame({'session_id': df['session_id']})

for model in models:
    col = f"{model}_overall"
    if col in df.columns:
        reliability_data[model] = df[col].values
        print(f"✓ {model.upper()}: {len(df[df[col].notna()])}개 세션")
    else:
        print(f"✗ {model.upper()}: 컬럼 없음 ({col})")
        import sys
        sys.exit(1)

# 결측치 제거
reliability_data = reliability_data.dropna()
print(f"\n✓ 공통 세션: {len(reliability_data)}개")
print()

# 세션 ID를 인덱스로 설정
reliability_data = reliability_data.set_index('session_id')

# 모델별 점수만 추출
reliability_scores = reliability_data[models]

print(f"분석 데이터: {len(reliability_scores)}개 세션 × 3개 모델")
print()

# ============================================================================
# 5. 신뢰도 분석
# ============================================================================

print("3. 신뢰도 분석")
print("-" * 80)

# 5-1. Cronbach's Alpha
print("\n📊 (1) Cronbach's Alpha (내적 일관성)")
print("-" * 80)

alpha = cronbach_alpha(reliability_scores)
print(f"Cronbach's α = {alpha:.3f}")
print()
print("해석:")
if alpha >= 0.9:
    print("  ✓ 매우 높음 (Excellent, α ≥ 0.9)")
elif alpha >= 0.8:
    print("  ✓ 높음 (Good, 0.8 ≤ α < 0.9)")
elif alpha >= 0.7:
    print("  ✓ 수용 가능 (Acceptable, 0.7 ≤ α < 0.8)")
else:
    print("  ⚠️  낮음 (Poor, α < 0.7)")

print()
print(f"논문 기재값: α = 0.868")
print(f"계산 결과:   α = {alpha:.3f}")
print(f"차이:       Δα = {abs(alpha - 0.868):.3f}")
print()

# 5-2. ICC
print("📊 (2) ICC (급내상관계수)")
print("-" * 80)

icc = calculate_icc(reliability_scores)
print(f"ICC(2,1) = {icc:.3f}")
print()
print("해석:")
if icc >= 0.75:
    print("  ✓ 높음 (Excellent, ICC ≥ 0.75)")
elif icc >= 0.60:
    print("  ✓ 중간-높음 (Good, 0.60 ≤ ICC < 0.75)")
elif icc >= 0.40:
    print("  ⚠️  중간 (Fair, 0.40 ≤ ICC < 0.60)")
else:
    print("  ⚠️  낮음 (Poor, ICC < 0.40)")

print()
print(f"논문 기재값: ICC = 0.642")
print(f"계산 결과:   ICC = {icc:.3f}")
print(f"차이:       ΔICC = {abs(icc - 0.642):.3f}")
print()

# 5-3. Pearson 상관계수
print("📊 (3) Pearson 상관계수 (모델 간)")
print("-" * 80)

correlations = {}
pairs = [
    ('gemini', 'anthropic'),
    ('gemini', 'openai'),
    ('anthropic', 'openai')
]

for m1, m2 in pairs:
    r, p = stats.pearsonr(reliability_scores[m1], reliability_scores[m2])
    correlations[f"{m1}_{m2}"] = {
        'r': float(r),
        'p': float(p)
    }
    print(f"{m1.upper():8s} - {m2.upper():8s}: r = {r:.3f} (p = {p:.4f})")

avg_r = np.mean([corr['r'] for corr in correlations.values()])
print()
print(f"평균 상관계수: r = {avg_r:.3f}")
print()
print(f"논문 기재값: r = 0.709")
print(f"계산 결과:   r = {avg_r:.3f}")
print(f"차이:       Δr = {abs(avg_r - 0.709):.3f}")
print()

# ============================================================================
# 6. 결과 저장
# ============================================================================

print("4. 결과 저장")
print("-" * 80)

reliability_summary = {
    'n_sessions': len(reliability_scores),
    'n_models': 3,
    'cronbach_alpha': {
        'value': float(alpha),
        'interpretation': 'Good' if alpha >= 0.8 else 'Acceptable' if alpha >= 0.7 else 'Poor',
        'paper_value': 0.868,
        'difference': float(abs(alpha - 0.868))
    },
    'icc': {
        'value': float(icc),
        'interpretation': 'Excellent' if icc >= 0.75 else 'Good' if icc >= 0.60 else 'Fair',
        'paper_value': 0.642,
        'difference': float(abs(icc - 0.642))
    },
    'pearson_average': {
        'value': float(avg_r),
        'interpretation': 'Strong' if avg_r >= 0.7 else 'Moderate',
        'paper_value': 0.709,
        'difference': float(abs(avg_r - 0.709))
    },
    'pairwise_correlations': correlations
}

output_json = OUTPUT_PATH / "llm_reliability_results.json"
import json
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(reliability_summary, f, ensure_ascii=False, indent=2)
print(f"✓ 신뢰도 분석 결과 저장: {output_json}")

# 상관계수 행렬 CSV
corr_matrix = reliability_scores.corr()
corr_csv = OUTPUT_PATH / "llm_correlation_matrix.csv"
corr_matrix.to_csv(corr_csv, encoding='utf-8-sig')
print(f"✓ 상관계수 행렬 저장: {corr_csv}")

print()
print("="*80)
print("LLM 평가 신뢰도 분석 완료!")
print("="*80)
print()
print("✅ 검증 결과:")
print(f"   Cronbach's α: {alpha:.3f} (논문: 0.868, 차이: {abs(alpha - 0.868):.3f})")
print(f"   ICC(2,1):     {icc:.3f} (논문: 0.642, 차이: {abs(icc - 0.642):.3f})")
print(f"   Pearson r:    {avg_r:.3f} (논문: 0.709, 차이: {abs(avg_r - 0.709):.3f})")
print()
print("⚠️  참고: 이 스크립트는 최종 CSV 파일만 사용합니다.")
print("   원본 JSONL 파일은 사용하지 않습니다.")
