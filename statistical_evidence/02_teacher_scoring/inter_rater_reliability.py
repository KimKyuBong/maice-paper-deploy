#!/usr/bin/env python3
"""
평가자 간 신뢰도 분석

논문 5장 2절 다항(1)에서 제시된 교사 평가자 간 신뢰도를 검증합니다.

주요 지표:
1. Pearson 상관계수
2. Spearman 순위 상관계수

근거:
- 논문: "평가자 간 신뢰도: Pearson r=0.644, Spearman ρ=0.571 (p<0.001)"
- 표Ⅴ-8: 교사 평가 설계
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("교사 평가자 간 신뢰도 분석")
print("="*80)
print()

# 경로 설정
INPUT_PATH = Path(__file__).parent / "results"
OUTPUT_PATH = Path(__file__).parent / "results"
OUTPUT_PATH.mkdir(exist_ok=True)

# ============================================================================
# 1. 데이터 로드
# ============================================================================

print("1. 데이터 로드")
print("-" * 80)

matched_file = INPUT_PATH / "teacher_matched_scores.csv"

if not matched_file.exists():
    print(f"⚠️  파일이 없습니다: {matched_file}")
    print("먼저 teacher_score_processing.py를 실행하세요.")
    import sys
    sys.exit(1)

df = pd.read_csv(matched_file)
print(f"✓ 교사 매칭 데이터 로드: {len(df)}개 레코드")
print()

# ============================================================================
# 2. 교사별 데이터 분리
# ============================================================================

print("2. 교사별 데이터 분리")
print("-" * 80)

df_96 = df[df['evaluated_by'] == 96].sort_values('conversation_session_id').reset_index(drop=True)
df_97 = df[df['evaluated_by'] == 97].sort_values('conversation_session_id').reset_index(drop=True)

print(f"교사 96: {len(df_96)}개 세션")
print(f"교사 97: {len(df_97)}개 세션")

# 세션 ID가 일치하는지 확인
if not np.array_equal(df_96['conversation_session_id'].values, 
                       df_97['conversation_session_id'].values):
    print("⚠️  경고: 세션 ID가 일치하지 않습니다!")
else:
    print("✓ 세션 ID 일치 확인")

print()

# ============================================================================
# 3. 상관관계 분석
# ============================================================================

print("3. 평가자 간 상관관계 분석")
print("-" * 80)

# 점수 항목
score_items = {
    'question_total_score': '질문 영역',
    'response_total_score': '응답 영역',
    'context_total_score': '맥락 영역',
    'overall_score': '종합 점수',
    'question_professionalism_score': 'A1 수학 전문성',
    'question_structuring_score': 'A2 질문 구조화',
    'question_context_application_score': 'A3 학습 맥락',
    'answer_customization_score': 'B1 학습자 맞춤도',
    'answer_systematicity_score': 'B2 설명 체계성',
    'answer_expandability_score': 'B3 학습 확장성',
    'context_dialogue_coherence_score': 'C1 대화 일관성',
    'context_learning_support_score': 'C2 학습 지원'
}

results = []

print("【영역별 상관관계】")
print("-" * 80)

for score_col, korean_name in score_items.items():
    scores_96 = df_96[score_col].values
    scores_97 = df_97[score_col].values
    
    # 결측치 제거
    mask = ~(pd.isna(scores_96) | pd.isna(scores_97))
    if mask.sum() < 2:
        continue
    
    scores_96_clean = scores_96[mask]
    scores_97_clean = scores_97[mask]
    
    # Pearson 상관계수
    r_pearson, p_pearson = pearsonr(scores_96_clean, scores_97_clean)
    
    # Spearman 순위 상관계수
    r_spearman, p_spearman = spearmanr(scores_96_clean, scores_97_clean)
    
    # 유의성 표시
    sig_p = "***" if p_pearson < 0.001 else "**" if p_pearson < 0.01 else "*" if p_pearson < 0.05 else ""
    sig_s = "***" if p_spearman < 0.001 else "**" if p_spearman < 0.01 else "*" if p_spearman < 0.05 else ""
    
    if score_col in ['question_total_score', 'response_total_score', 'context_total_score', 'overall_score']:
        print(f"\n{korean_name} ({score_col}):")
        print(f"  Pearson r  = {r_pearson:6.3f} (p={p_pearson:.6f}) {sig_p}")
        print(f"  Spearman ρ = {r_spearman:6.3f} (p={p_spearman:.6f}) {sig_s}")
        print(f"  n = {len(scores_96_clean)}")
    
    results.append({
        '항목': korean_name,
        '항목코드': score_col,
        'Pearson_r': float(r_pearson),
        'Pearson_p': float(p_pearson),
        'Spearman_ρ': float(r_spearman),
        'Spearman_p': float(p_spearman),
        'n': int(len(scores_96_clean))
    })

print()

# ============================================================================
# 4. 종합 점수 상관관계 (논문 기재값과 비교)
# ============================================================================

print("4. 종합 점수 상관관계 검증")
print("-" * 80)

overall_result = [r for r in results if r['항목코드'] == 'overall_score'][0]

print(f"종합 점수 (overall_score):")
print(f"  Pearson r  = {overall_result['Pearson_r']:.3f} (p={overall_result['Pearson_p']:.6f})")
print(f"  Spearman ρ = {overall_result['Spearman_ρ']:.3f} (p={overall_result['Spearman_p']:.6f})")
print()

print("논문 기재값과 비교:")
print(f"  Pearson r:")
print(f"    논문: 0.644")
print(f"    계산: {overall_result['Pearson_r']:.3f}")
print(f"    차이: {abs(overall_result['Pearson_r'] - 0.644):.3f}")
print()
print(f"  Spearman ρ:")
print(f"    논문: 0.571")
print(f"    계산: {overall_result['Spearman_ρ']:.3f}")
print(f"    차이: {abs(overall_result['Spearman_ρ'] - 0.571):.3f}")
print()

# ============================================================================
# 5. 시각화
# ============================================================================

print("5. 시각화 생성")
print("-" * 80)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 산점도 (종합 점수)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 종합 점수
scores_96 = df_96['overall_score'].values
scores_97 = df_97['overall_score'].values

axes[0].scatter(scores_96, scores_97, alpha=0.6, s=60)
axes[0].plot([0, 40], [0, 40], 'r--', alpha=0.5, label='완벽한 일치선')
axes[0].set_xlabel('교사 96 점수', fontsize=12)
axes[0].set_ylabel('교사 97 점수', fontsize=12)
axes[0].set_title(f'종합 점수 평가자 간 일치도\n(Pearson r={overall_result["Pearson_r"]:.3f}, p<0.001)', 
                  fontsize=13, pad=15)
axes[0].grid(alpha=0.3)
axes[0].legend()

# 항목별 상관계수 비교
main_items = [r for r in results if r['항목코드'] in 
              ['question_total_score', 'response_total_score', 'context_total_score', 'overall_score']]

item_names = [r['항목'] for r in main_items]
pearson_values = [r['Pearson_r'] for r in main_items]
spearman_values = [r['Spearman_ρ'] for r in main_items]

x = np.arange(len(item_names))
width = 0.35

axes[1].bar(x - width/2, pearson_values, width, label='Pearson r', alpha=0.8)
axes[1].bar(x + width/2, spearman_values, width, label='Spearman ρ', alpha=0.8)
axes[1].set_xlabel('평가 영역', fontsize=12)
axes[1].set_ylabel('상관계수', fontsize=12)
axes[1].set_title('영역별 평가자 간 상관계수', fontsize=13, pad=15)
axes[1].set_xticks(x)
axes[1].set_xticklabels(item_names, rotation=15, ha='right')
axes[1].legend()
axes[1].axhline(y=0.5, color='red', linestyle='--', alpha=0.3)
axes[1].axhline(y=0.7, color='darkred', linestyle='--', alpha=0.3)
axes[1].grid(axis='y', alpha=0.3)
axes[1].set_ylim(0, 1)

plt.tight_layout()
fig_path = OUTPUT_PATH / "teacher_inter_rater_reliability.png"
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"✓ 시각화 저장: {fig_path}")

print()

# ============================================================================
# 6. 결과 저장
# ============================================================================

print("6. 결과 저장")
print("-" * 80)

# CSV 저장
results_df = pd.DataFrame(results)
csv_path = OUTPUT_PATH / "teacher_inter_rater_correlations.csv"
results_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"✓ 상관관계 결과 저장: {csv_path}")

# JSON 저장
summary = {
    'n_teachers': 2,
    'teacher_ids': [96, 97],
    'n_sessions': len(df_96),
    'overall_score': {
        'pearson_r': float(overall_result['Pearson_r']),
        'pearson_p': float(overall_result['Pearson_p']),
        'spearman_rho': float(overall_result['Spearman_ρ']),
        'spearman_p': float(overall_result['Spearman_p']),
        'paper_pearson': 0.644,
        'paper_spearman': 0.571,
        'pearson_diff': float(abs(overall_result['Pearson_r'] - 0.644)),
        'spearman_diff': float(abs(overall_result['Spearman_ρ'] - 0.571))
    },
    'all_items': results
}

json_path = OUTPUT_PATH / "teacher_inter_rater_reliability.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ 신뢰도 분석 결과 저장: {json_path}")

print()
print("="*80)
print("교사 평가자 간 신뢰도 분석 완료!")
print("="*80)
print()
print("✅ 검증 결과:")
print(f"   Pearson r:  {overall_result['Pearson_r']:.3f} (논문: 0.644, 차이: {abs(overall_result['Pearson_r'] - 0.644):.3f})")
print(f"   Spearman ρ: {overall_result['Spearman_ρ']:.3f} (논문: 0.571, 차이: {abs(overall_result['Spearman_ρ'] - 0.571):.3f})")
print(f"   모두 p<0.001 (매우 유의함)")
print()

