#!/usr/bin/env python3
"""
질문점수(Q_총합)와 답변점수(A_총합) 간의 상관관계 분석
"""
import json
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# JSON 파일 읽기
with open('evaluation_statistics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Q_A_총합_상관관계 데이터 추출
qa_correlation_data = data['Q_A_총합_상관관계']
existing_correlation = qa_correlation_data['상관계수']
items_data = qa_correlation_data['문항별_총합']

# Q_총합과 A_총합 추출
q_scores = []
a_scores = []

for item in items_data:
    q_scores.append(item['Q_총합'])
    a_scores.append(item['A_총합'])

q_scores = np.array(q_scores)
a_scores = np.array(a_scores)

# 기본 통계
print("=" * 70)
print("질문점수(Q_총합)와 답변점수(A_총합) 상관관계 분석")
print("=" * 70)
print(f"\n📌 데이터에 기록된 상관계수: {existing_correlation:.4f}")
print()

print("📊 기술 통계량")
print("-" * 70)
print(f"질문점수(Q_총합):")
print(f"  - 평균: {np.mean(q_scores):.4f}")
print(f"  - 표준편차: {np.std(q_scores, ddof=1):.4f}")
print(f"  - 최소값: {np.min(q_scores):.4f}")
print(f"  - 최대값: {np.max(q_scores):.4f}")
print(f"  - 중앙값: {np.median(q_scores):.4f}")
print()

print(f"답변점수(A_총합):")
print(f"  - 평균: {np.mean(a_scores):.4f}")
print(f"  - 표준편차: {np.std(a_scores, ddof=1):.4f}")
print(f"  - 최소값: {np.min(a_scores):.4f}")
print(f"  - 최대값: {np.max(a_scores):.4f}")
print(f"  - 중앙값: {np.median(a_scores):.4f}")
print()

# Pearson 상관계수
pearson_r, pearson_p = stats.pearsonr(q_scores, a_scores)

print("📈 상관관계 분석")
print("-" * 70)
print(f"Pearson 상관계수 (r): {pearson_r:.4f}")
print(f"p-value: {pearson_p:.6f}")
print(f"결정계수 (R²): {pearson_r**2:.4f}")

# 효과 크기 해석
if abs(pearson_r) >= 0.7:
    effect_size = "매우 강함"
elif abs(pearson_r) >= 0.5:
    effect_size = "강함"
elif abs(pearson_r) >= 0.3:
    effect_size = "중간"
elif abs(pearson_r) >= 0.1:
    effect_size = "약함"
else:
    effect_size = "매우 약함"

print(f"상관 강도: {effect_size}")

# 통계적 유의성
if pearson_p < 0.001:
    significance = "매우 유의함 (p < 0.001) ***"
elif pearson_p < 0.01:
    significance = "유의함 (p < 0.01) **"
elif pearson_p < 0.05:
    significance = "유의함 (p < 0.05) *"
else:
    significance = "유의하지 않음 (p >= 0.05)"

print(f"통계적 유의성: {significance}")
print()

# Spearman 상관계수 (비모수)
spearman_r, spearman_p = stats.spearmanr(q_scores, a_scores)
print(f"Spearman 상관계수 (ρ): {spearman_r:.4f}")
print(f"p-value: {spearman_p:.6f}")
print()

# 선형 회귀 분석
slope, intercept, r_value, p_value, std_err = stats.linregress(q_scores, a_scores)
print("📉 선형 회귀 분석")
print("-" * 70)
print(f"회귀식: A_총합 = {intercept:.4f} + {slope:.4f} × Q_총합")
print(f"기울기 (slope): {slope:.4f}")
print(f"절편 (intercept): {intercept:.4f}")
print(f"표준오차: {std_err:.4f}")
print()

# 해석
print("💡 결과 해석")
print("-" * 70)
print(f"1. 질문점수와 답변점수 간에는 {pearson_r:.4f}의 상관관계가 있습니다.")
print(f"2. 이는 {effect_size} 관계로 해석됩니다.")
print(f"3. 결정계수(R²)는 {pearson_r**2:.4f}로, 질문점수가 답변점수 변동의 약 {pearson_r**2*100:.1f}%를 설명합니다.")
print(f"4. 통계적으로 {significance}")
print(f"5. 질문점수가 1점 증가할 때, 답변점수는 평균적으로 약 {slope:.4f}점 증가합니다.")
print()

# 데이터 개수
print(f"📌 분석 데이터 수: {len(q_scores)}개")
print("=" * 70)

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. 산점도 + 회귀선
ax1 = axes[0, 0]
ax1.scatter(q_scores, a_scores, alpha=0.6, s=50, edgecolors='black', linewidths=0.5)
x_line = np.array([q_scores.min(), q_scores.max()])
y_line = intercept + slope * x_line
ax1.plot(x_line, y_line, 'r--', linewidth=2, label=f'회귀선: y = {intercept:.2f} + {slope:.2f}x')
ax1.set_xlabel('질문점수 (Q_총합)', fontsize=12, fontweight='bold')
ax1.set_ylabel('답변점수 (A_총합)', fontsize=12, fontweight='bold')
ax1.set_title(f'질문점수 vs 답변점수 상관관계\n(r = {pearson_r:.4f}, p = {pearson_p:.4f})', 
              fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. 잔차 플롯
ax2 = axes[0, 1]
predicted = intercept + slope * q_scores
residuals = a_scores - predicted
ax2.scatter(predicted, residuals, alpha=0.6, s=50, edgecolors='black', linewidths=0.5)
ax2.axhline(y=0, color='r', linestyle='--', linewidth=2)
ax2.set_xlabel('예측값', fontsize=12, fontweight='bold')
ax2.set_ylabel('잔차', fontsize=12, fontweight='bold')
ax2.set_title('잔차 플롯 (Residual Plot)', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. 질문점수 분포
ax3 = axes[1, 0]
ax3.hist(q_scores, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
ax3.axvline(np.mean(q_scores), color='red', linestyle='--', linewidth=2, label=f'평균: {np.mean(q_scores):.2f}')
ax3.axvline(np.median(q_scores), color='green', linestyle='--', linewidth=2, label=f'중앙값: {np.median(q_scores):.2f}')
ax3.set_xlabel('질문점수 (Q_총합)', fontsize=12, fontweight='bold')
ax3.set_ylabel('빈도', fontsize=12, fontweight='bold')
ax3.set_title('질문점수 분포', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# 4. 답변점수 분포
ax4 = axes[1, 1]
ax4.hist(a_scores, bins=30, edgecolor='black', alpha=0.7, color='lightcoral')
ax4.axvline(np.mean(a_scores), color='red', linestyle='--', linewidth=2, label=f'평균: {np.mean(a_scores):.2f}')
ax4.axvline(np.median(a_scores), color='green', linestyle='--', linewidth=2, label=f'중앙값: {np.median(a_scores):.2f}')
ax4.set_xlabel('답변점수 (A_총합)', fontsize=12, fontweight='bold')
ax4.set_ylabel('빈도', fontsize=12, fontweight='bold')
ax4.set_title('답변점수 분포', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('correlation_analysis.png', dpi=300, bbox_inches='tight')
print("\n✅ 시각화 결과를 'correlation_analysis.png' 파일로 저장했습니다.")

# 추가 분석: 사분위수별 비교
print("\n📊 사분위수 분석")
print("-" * 70)
q1, q2, q3 = np.percentile(q_scores, [25, 50, 75])
print(f"질문점수 사분위수:")
print(f"  Q1 (25%): {q1:.4f}")
print(f"  Q2 (50%, 중앙값): {q2:.4f}")
print(f"  Q3 (75%): {q3:.4f}")
print()

# 질문점수 사분위별 답변점수 평균
low_q = a_scores[q_scores <= q1]
mid_low_q = a_scores[(q_scores > q1) & (q_scores <= q2)]
mid_high_q = a_scores[(q_scores > q2) & (q_scores <= q3)]
high_q = a_scores[q_scores > q3]

print(f"질문점수 사분위별 답변점수 평균:")
print(f"  Q1 이하 (낮음): {np.mean(low_q):.4f} (n={len(low_q)})")
print(f"  Q1-Q2 (중하): {np.mean(mid_low_q):.4f} (n={len(mid_low_q)})")
print(f"  Q2-Q3 (중상): {np.mean(mid_high_q):.4f} (n={len(mid_high_q)})")
print(f"  Q3 이상 (높음): {np.mean(high_q):.4f} (n={len(high_q)})")
print("=" * 70)

plt.show()

