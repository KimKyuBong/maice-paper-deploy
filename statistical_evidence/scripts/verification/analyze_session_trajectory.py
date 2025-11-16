#!/usr/bin/env python3
"""
세션 변화 추이 분석 (Trajectory Analysis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목적:
  첫/마지막 세션만이 아니라 전체 세션의 변화 추이를 분석

분석 방법:
  1. 세션 순서별 평균 점수 추이
  2. 학생별 선형 회귀 기울기 (개인별 학습 곡선)
  3. 상관분석: 세션 번호 vs 점수
  4. 시각화: 스파게티 플롯 + 평균 추세선

통계 기법:
  - Linear Regression (학생별)
  - Pearson Correlation
  - 시각화
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# ═══════════════════════════════════════════════════════════════════════════
# 1. 데이터 로드
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'llm_evaluations'
OUTPUT_DIR = BASE_DIR / 'scripts' / 'verification'

print("=" * 80)
print("📈 세션 변화 추이 분석 (Trajectory Analysis)")
print("=" * 80)

df = pd.read_csv(DATA_DIR / 'llm_284sessions_complete.csv')

# Total 점수 계산
item_cols = ['avg_A1', 'avg_A2', 'avg_A3', 'avg_B1', 'avg_B2', 'avg_B3', 'avg_C1', 'avg_C2']
df['Total'] = df[item_cols].sum(axis=1)

# 시간순 정렬
df = df.sort_values(['student_name', 'session_id'])

# 복수 세션 학생 필터링
student_sessions = df.groupby('student_name').agg({
    'session_id': 'count',
    'assigned_mode': 'first'
}).rename(columns={'session_id': 'n_sessions'})

multi_session_students = student_sessions[student_sessions['n_sessions'] >= 2]

print(f"\n✓ 복수 세션 참여 학생: {len(multi_session_students)}명")
print(f"  Agent: {(multi_session_students['assigned_mode'] == 'agent').sum()}명")
print(f"  Freepass: {(multi_session_students['assigned_mode'] == 'freepass').sum()}명")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 세션 순서 번호 부여
# ═══════════════════════════════════════════════════════════════════════════

# 각 학생의 세션에 1, 2, 3... 순서 번호 부여
df['session_order'] = df.groupby('student_name').cumcount() + 1

# 복수 세션 학생만 필터링
multi_df = df[df['student_name'].isin(multi_session_students.index)].copy()

print(f"\n✓ 분석 대상 세션 수: {len(multi_df)}")
print(f"  최대 세션 수: {multi_df['session_order'].max()}")

# ═══════════════════════════════════════════════════════════════════════════
# 3. 방법 1: 세션 순서별 평균 점수 추이
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 방법 1: 세션 순서별 평균 점수")
print("=" * 80)

# 모드별, 세션 순서별 평균
session_means = multi_df.groupby(['assigned_mode', 'session_order']).agg({
    'avg_C2': ['mean', 'std', 'count'],
    'Total': ['mean', 'std', 'count']
}).round(2)

print("\n[C2 학습 지원]")
print(session_means['avg_C2'])

print("\n[전체 점수]")
print(session_means['Total'])

# ═══════════════════════════════════════════════════════════════════════════
# 4. 방법 2: 학생별 선형 회귀 기울기 (개인별 학습 곡선)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📈 방법 2: 학생별 선형 회귀 기울기 분석")
print("=" * 80)

def calculate_slope(student_data, score_col='avg_C2'):
    """
    한 학생의 세션 순서에 따른 점수 변화의 기울기 계산
    
    Returns:
    --------
    float : 선형 회귀 기울기 (세션당 점수 증가량)
    """
    if len(student_data) < 2:
        return np.nan
    
    x = student_data['session_order'].values
    y = student_data[score_col].values
    
    # 선형 회귀
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    return slope

# 각 학생의 기울기 계산
student_slopes = []

for mode in ['agent', 'freepass']:
    mode_students = multi_session_students[multi_session_students['assigned_mode'] == mode].index
    
    for student in mode_students:
        student_data = multi_df[multi_df['student_name'] == student]
        
        if len(student_data) >= 2:
            slope_c2 = calculate_slope(student_data, 'avg_C2')
            slope_total = calculate_slope(student_data, 'Total')
            
            student_slopes.append({
                'student': student,
                'mode': mode,
                'n_sessions': len(student_data),
                'slope_C2': slope_c2,
                'slope_Total': slope_total
            })

df_slopes = pd.DataFrame(student_slopes)

# 모드별 평균 기울기
print("\n[학생별 기울기의 평균]")
for mode in ['agent', 'freepass']:
    mode_data = df_slopes[df_slopes['mode'] == mode]
    
    mean_slope_c2 = mode_data['slope_C2'].mean()
    mean_slope_total = mode_data['slope_Total'].mean()
    
    # t-test: 기울기가 0과 유의하게 다른지
    t_c2, p_c2 = stats.ttest_1samp(mode_data['slope_C2'].dropna(), 0)
    t_total, p_total = stats.ttest_1samp(mode_data['slope_Total'].dropna(), 0)
    
    print(f"\n{mode.capitalize()}:")
    print(f"  C2 기울기:    {mean_slope_c2:+.3f} (세션당 변화량, t={t_c2:.2f}, p={p_c2:.3f})")
    print(f"  Total 기울기: {mean_slope_total:+.3f} (세션당 변화량, t={t_total:.2f}, p={p_total:.3f})")

# 두 모드 간 기울기 차이 검정
agent_slopes_c2 = df_slopes[df_slopes['mode'] == 'agent']['slope_C2'].dropna()
free_slopes_c2 = df_slopes[df_slopes['mode'] == 'freepass']['slope_C2'].dropna()

agent_slopes_total = df_slopes[df_slopes['mode'] == 'agent']['slope_Total'].dropna()
free_slopes_total = df_slopes[df_slopes['mode'] == 'freepass']['slope_Total'].dropna()

t_c2_diff, p_c2_diff = stats.ttest_ind(agent_slopes_c2, free_slopes_c2)
t_total_diff, p_total_diff = stats.ttest_ind(agent_slopes_total, free_slopes_total)

print(f"\n[Agent vs Freepass 기울기 차이]")
print(f"  C2: t={t_c2_diff:.2f}, p={p_c2_diff:.3f}")
print(f"  Total: t={t_total_diff:.2f}, p={p_total_diff:.3f}")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 방법 3: 상관분석 (세션 순서 vs 점수)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 방법 3: 상관분석 (세션 순서 vs 점수)")
print("=" * 80)

for mode in ['agent', 'freepass']:
    mode_data = multi_df[multi_df['assigned_mode'] == mode]
    
    # Pearson 상관계수
    r_c2, p_c2 = stats.pearsonr(mode_data['session_order'], mode_data['avg_C2'])
    r_total, p_total = stats.pearsonr(mode_data['session_order'], mode_data['Total'])
    
    print(f"\n{mode.capitalize()}:")
    print(f"  세션 순서 vs C2:    r={r_c2:+.3f}, p={p_c2:.3f}")
    print(f"  세션 순서 vs Total: r={r_total:+.3f}, p={p_total:.3f}")

# ═══════════════════════════════════════════════════════════════════════════
# 6. 시각화
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 시각화 생성")
print("=" * 80)

# 6-1. 스파게티 플롯 (개별 학생 추이)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, (mode, score_col, score_name) in enumerate([
    ('agent', 'avg_C2', 'C2 학습 지원'),
    ('agent', 'Total', '전체 점수'),
    ('freepass', 'avg_C2', 'C2 학습 지원'),
    ('freepass', 'Total', '전체 점수')
]):
    ax = axes[idx // 2, idx % 2]
    
    mode_data = multi_df[multi_df['assigned_mode'] == mode]
    
    # 각 학생별 선
    for student in mode_data['student_name'].unique():
        student_data = mode_data[mode_data['student_name'] == student].sort_values('session_order')
        ax.plot(student_data['session_order'], student_data[score_col], 
                alpha=0.3, color='gray', linewidth=0.5)
    
    # 평균 추세선
    session_avg = mode_data.groupby('session_order')[score_col].mean()
    ax.plot(session_avg.index, session_avg.values, 
            color='red', linewidth=2.5, marker='o', markersize=8, label='평균')
    
    ax.set_xlabel('세션 순서', fontsize=11)
    ax.set_ylabel('점수', fontsize=11)
    ax.set_title(f'{mode.capitalize()} - {score_name}', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_spaghetti.png', dpi=300, bbox_inches='tight')
print(f"\n✓ 저장: session_trajectory_spaghetti.png")

# 6-2. 세션 순서별 평균 비교 (Agent vs Freepass)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for idx, (score_col, score_name, y_range) in enumerate([
    ('avg_C2', 'C2 학습 지원', (1.5, 2.8)),
    ('Total', '전체 점수', (23, 29))
]):
    ax = axes[idx]
    
    for mode, color, label in [('agent', 'blue', 'Agent'), ('freepass', 'orange', 'Freepass')]:
        mode_data = multi_df[multi_df['assigned_mode'] == mode]
        session_avg = mode_data.groupby('session_order')[score_col].agg(['mean', 'std', 'count'])
        
        # 표준 오차
        session_avg['se'] = session_avg['std'] / np.sqrt(session_avg['count'])
        
        ax.errorbar(session_avg.index, session_avg['mean'], 
                   yerr=session_avg['se'], 
                   marker='o', linewidth=2, markersize=8, 
                   color=color, label=label, capsize=5)
    
    ax.set_xlabel('세션 순서', fontsize=11)
    ax.set_ylabel('점수', fontsize=11)
    ax.set_title(f'{score_name} - 세션별 평균 추이', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(y_range)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ 저장: session_trajectory_comparison.png")

# ═══════════════════════════════════════════════════════════════════════════
# 7. 결과 저장
# ═══════════════════════════════════════════════════════════════════════════

# 학생별 기울기
df_slopes.to_csv(OUTPUT_DIR / 'student_learning_slopes.csv', index=False, encoding='utf-8-sig')
print(f"✓ 저장: student_learning_slopes.csv")

# 세션별 평균
session_summary = []
for mode in ['agent', 'freepass']:
    mode_data = multi_df[multi_df['assigned_mode'] == mode]
    for session_order in range(1, mode_data['session_order'].max() + 1):
        session_data = mode_data[mode_data['session_order'] == session_order]
        if len(session_data) > 0:
            session_summary.append({
                'mode': mode,
                'session_order': session_order,
                'n': len(session_data),
                'C2_mean': round(session_data['avg_C2'].mean(), 2),
                'C2_std': round(session_data['avg_C2'].std(), 2),
                'Total_mean': round(session_data['Total'].mean(), 2),
                'Total_std': round(session_data['Total'].std(), 2)
            })

df_session_summary = pd.DataFrame(session_summary)
df_session_summary.to_csv(OUTPUT_DIR / 'session_order_summary.csv', index=False, encoding='utf-8-sig')
print(f"✓ 저장: session_order_summary.csv")

print("\n" + "=" * 80)
print("🎉 분석 완료!")
print("=" * 80)
print(f"\n출력 파일:")
print(f"  - student_learning_slopes.csv (학생별 기울기)")
print(f"  - session_order_summary.csv (세션별 평균)")
print(f"  - session_trajectory_spaghetti.png (스파게티 플롯)")
print(f"  - session_trajectory_comparison.png (모드 비교)")

