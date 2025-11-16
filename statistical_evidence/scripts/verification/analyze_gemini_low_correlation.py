#!/usr/bin/env python3
"""
Gemini 낮은 상관계수 원인 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

문제: Gemini r=0.301~0.317 vs Anthropic r=0.672~0.743

분석:
  1. 점수 분포 비교 (평균, 표준편차, 범위)
  2. 항목별 상관계수
  3. 과대/과소평가 패턴
  4. Bland-Altman 플롯
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("🔍 Gemini 낮은 상관계수 원인 분석")
print("=" * 80)

# LLM 데이터
df_llm = pd.read_csv(DATA_DIR / 'llm_evaluations' / 'llm_284sessions_complete.csv')

# 각 모델 Total
for model in ['gemini', 'anthropic', 'openai']:
    cols = [f'{model}_{item}' for item in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']]
    df_llm[f'{model}_total'] = df_llm[cols].sum(axis=1)

# 교사 데이터
df_teacher_raw = pd.read_csv(DATA_DIR / 'analysis_results' / 'three_teachers_100_sessions.csv')
df_teacher = df_teacher_raw[df_teacher_raw['evaluator'].isin([96, 97])]

# 교사 평균
teacher_avg = df_teacher.groupby('session_id')['overall'].mean().reset_index()
teacher_avg.columns = ['session_id', 'teacher_avg']

# 병합
df_merged = pd.merge(df_llm, teacher_avg, on='session_id', how='inner')

print(f"\n✓ 병합 완료: {len(df_merged)} 세션")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 기술통계 비교
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 점수 분포 비교")
print("=" * 80)

stats_table = []

for model_name, col in [('Gemini', 'gemini_total'), 
                        ('Anthropic', 'anthropic_total'),
                        ('OpenAI', 'openai_total'),
                        ('교사 평균', 'teacher_avg')]:
    data = df_merged[col]
    
    stats_table.append({
        '평가자': model_name,
        '평균': round(data.mean(), 2),
        '표준편차': round(data.std(), 2),
        '최소': round(data.min(), 2),
        '최대': round(data.max(), 2),
        '범위': round(data.max() - data.min(), 2)
    })
    
    print(f"\n{model_name}:")
    print(f"  평균: {data.mean():.2f}")
    print(f"  표준편차: {data.std():.2f}")
    print(f"  범위: {data.min():.2f} ~ {data.max():.2f}")

df_stats = pd.DataFrame(stats_table)
print("\n" + df_stats.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 3. 항목별 상관계수
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 항목별 상관계수 (교사 평균과)")
print("=" * 80)

# 교사 개별 항목
teacher_items = df_teacher.groupby('session_id').agg({
    'q1': 'mean', 'q2': 'mean', 'q3': 'mean',
    'r1': 'mean', 'r2': 'mean', 'r3': 'mean',
    'c1': 'mean', 'c2': 'mean'
}).reset_index()

df_full = pd.merge(df_merged, teacher_items, on='session_id', how='inner')

items = [
    ('A1', 'q1'),
    ('A2', 'q2'),
    ('A3', 'q3'),
    ('B1', 'r1'),
    ('B2', 'r2'),
    ('B3', 'r3'),
    ('C1', 'c1'),
    ('C2', 'c2')
]

item_corr = []

for item_code, teacher_col in items:
    gemini_r, _ = stats.pearsonr(df_full[f'gemini_{item_code}'], df_full[teacher_col])
    anthropic_r, _ = stats.pearsonr(df_full[f'anthropic_{item_code}'], df_full[teacher_col])
    openai_r, _ = stats.pearsonr(df_full[f'openai_{item_code}'], df_full[teacher_col])
    
    item_corr.append({
        '항목': item_code,
        'Gemini': round(gemini_r, 3),
        'Anthropic': round(anthropic_r, 3),
        'OpenAI': round(openai_r, 3),
        'Gemini-Anthropic 차이': round(gemini_r - anthropic_r, 3)
    })
    
    print(f"{item_code}: Gemini={gemini_r:.3f}, Anthropic={anthropic_r:.3f}, 차이={gemini_r-anthropic_r:+.3f}")

df_item_corr = pd.DataFrame(item_corr)
print("\n" + df_item_corr.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 4. Bland-Altman 분석 (과대/과소평가 패턴)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 Bland-Altman 분석 (평균 vs 차이)")
print("=" * 80)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (model_name, col) in enumerate([('Gemini', 'gemini_total'),
                                          ('Anthropic', 'anthropic_total'),
                                          ('OpenAI', 'openai_total')]):
    ax = axes[idx]
    
    # 평균과 차이
    mean_val = (df_merged[col] + df_merged['teacher_avg']) / 2
    diff_val = df_merged[col] - df_merged['teacher_avg']
    
    # 산점도
    ax.scatter(mean_val, diff_val, alpha=0.5, s=30)
    
    # 평균선, ±1.96 SD
    mean_diff = diff_val.mean()
    std_diff = diff_val.std()
    
    ax.axhline(mean_diff, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_diff:.2f}')
    ax.axhline(mean_diff + 1.96*std_diff, color='gray', linestyle=':', label=f'+1.96 SD')
    ax.axhline(mean_diff - 1.96*std_diff, color='gray', linestyle=':', label=f'-1.96 SD')
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    
    ax.set_xlabel('평균 [(LLM + 교사) / 2]', fontsize=11)
    ax.set_ylabel('차이 (LLM - 교사)', fontsize=11)
    ax.set_title(f'{model_name}\nBias={mean_diff:.2f}, r={stats.pearsonr(df_merged[col], df_merged["teacher_avg"])[0]:.3f}',
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    print(f"\n{model_name}:")
    print(f"  평균 차이 (Bias): {mean_diff:.2f}")
    print(f"  표준편차: {std_diff:.2f}")
    print(f"  과대평가(+) 비율: {(diff_val > 0).sum() / len(diff_val) * 100:.1f}%")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'bland_altman_llm_vs_teacher.png', dpi=300, bbox_inches='tight')
print(f"\n✓ 저장: bland_altman_llm_vs_teacher.png")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 점수 분산 패턴 분석
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 점수 분산 패턴 (교사와의 차이)")
print("=" * 80)

for model_name, col in [('Gemini', 'gemini_total'),
                        ('Anthropic', 'anthropic_total'),
                        ('OpenAI', 'openai_total')]:
    
    # 교사보다 높게/낮게 평가한 세션 수
    diff = df_merged[col] - df_merged['teacher_avg']
    
    overrated = (diff > 5).sum()  # 5점 이상 높게
    underrated = (diff < -5).sum()  # 5점 이상 낮게
    similar = ((diff >= -5) & (diff <= 5)).sum()
    
    print(f"\n{model_name}:")
    print(f"  과대평가 (>+5점): {overrated}개 ({overrated/len(diff)*100:.1f}%)")
    print(f"  유사 (±5점):     {similar}개 ({similar/len(diff)*100:.1f}%)")
    print(f"  과소평가 (<-5점): {underrated}개 ({underrated/len(diff)*100:.1f}%)")

# ═══════════════════════════════════════════════════════════════════════════
# 6. 결과 저장
# ═══════════════════════════════════════════════════════════════════════════

df_stats.to_csv(OUTPUT_DIR / 'GEMINI_ANALYSIS_STATS.csv', index=False, encoding='utf-8-sig')
df_item_corr.to_csv(OUTPUT_DIR / 'GEMINI_ANALYSIS_ITEMS.csv', index=False, encoding='utf-8-sig')

print("\n" + "=" * 80)
print("✅ 분석 완료!")
print("=" * 80)

