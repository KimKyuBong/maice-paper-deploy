#!/usr/bin/env python3
"""
모든 항목별 세션 추이 그래프 생성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

목적: A1~C2 + Total 모든 항목의 세션별 변화를 한 그림에 표시
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

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
print("📊 모든 항목별 세션 추이 그래프 생성")
print("=" * 80)

df = pd.read_csv(DATA_DIR / 'llm_284sessions_complete.csv')

# 항목 정의
items = {
    'A1 수학전문성': 'avg_A1',
    'A2 질문구조화': 'avg_A2',
    'A3 학습맥락': 'avg_A3',
    'B1 학습자맞춤': 'avg_B1',
    'B2 설명체계성': 'avg_B2',
    'B3 학습확장성': 'avg_B3',
    'C1 대화일관성': 'avg_C1',
    'C2 학습지원': 'avg_C2'
}

# Total 계산
df['Total'] = df[list(items.values())].sum(axis=1)
items['전체'] = 'Total'

# 시간순 정렬
df = df.sort_values(['student_name', 'session_id'])

# 세션 순서 번호
df['session_order'] = df.groupby('student_name').cumcount() + 1

# 복수 세션 학생
student_sessions = df.groupby('student_name').agg({
    'session_id': 'count',
    'assigned_mode': 'first'
}).rename(columns={'session_id': 'n_sessions'})

multi_session_students = student_sessions[student_sessions['n_sessions'] >= 2]

# 복수 세션 학생만
multi_df = df[df['student_name'].isin(multi_session_students.index)].copy()

print(f"\n✓ 복수 세션 학생: {len(multi_session_students)}명")
print(f"  분석 세션 수: {len(multi_df)}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. 그래프 1: 모든 항목 (3x3 서브플롯)
# ═══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.suptitle('세션 순서에 따른 항목별 점수 변화 추이', fontsize=18, fontweight='bold', y=0.995)

axes = axes.flatten()

for idx, (item_name, col_name) in enumerate(items.items()):
    ax = axes[idx]
    
    # Agent 모드
    agent_data = multi_df[multi_df['assigned_mode'] == 'agent']
    agent_summary = agent_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    agent_summary['se'] = agent_summary['std'] / np.sqrt(agent_summary['count'])
    
    ax.errorbar(agent_summary.index, agent_summary['mean'],
               yerr=agent_summary['se'],
               marker='o', linewidth=2.5, markersize=8,
               color='blue', label='Agent', capsize=5, alpha=0.8)
    
    # Freepass 모드
    free_data = multi_df[multi_df['assigned_mode'] == 'freepass']
    free_summary = free_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    free_summary['se'] = free_summary['std'] / np.sqrt(free_summary['count'])
    
    ax.errorbar(free_summary.index, free_summary['mean'],
               yerr=free_summary['se'],
               marker='s', linewidth=2.5, markersize=8,
               color='orange', label='Freepass', capsize=5, alpha=0.8)
    
    # 꾸미기
    ax.set_xlabel('세션 순서', fontsize=11, fontweight='bold')
    ax.set_ylabel('점수', fontsize=11, fontweight='bold')
    ax.set_title(item_name, fontsize=13, fontweight='bold', pad=10)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0.5, 12.5)
    
    # 전체는 y축 범위 다르게
    if item_name == '전체':
        ax.set_ylim(23, 30)
    else:
        # 각 항목별 적절한 범위
        if item_name in ['A3 학습맥락', 'B3 학습확장성', 'C2 학습지원']:
            ax.set_ylim(0.5, 4.5)
        else:
            ax.set_ylim(2.5, 5.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_all_items_grid.png', 
            dpi=300, bbox_inches='tight')
print(f"\n✓ 저장: session_trajectory_all_items_grid.png")

# ═══════════════════════════════════════════════════════════════════════════
# 3. 그래프 2: Agent만 모든 항목 한 그래프에
# ═══════════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(1, 1, figsize=(14, 8))

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
          '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#000000']

for idx, (item_name, col_name) in enumerate(items.items()):
    agent_data = multi_df[multi_df['assigned_mode'] == 'agent']
    agent_summary = agent_data.groupby('session_order')[col_name].mean()
    
    # 전체는 굵게
    if item_name == '전체':
        ax.plot(agent_summary.index, agent_summary.values,
               marker='o', linewidth=3.5, markersize=10,
               color=colors[idx], label=item_name, alpha=1.0, zorder=10)
    else:
        ax.plot(agent_summary.index, agent_summary.values,
               marker='o', linewidth=2, markersize=7,
               color=colors[idx], label=item_name, alpha=0.7)

ax.set_xlabel('세션 순서', fontsize=13, fontweight='bold')
ax.set_ylabel('점수', fontsize=13, fontweight='bold')
ax.set_title('Agent 모드: 세션별 모든 항목 점수 변화', 
            fontsize=15, fontweight='bold', pad=15)
ax.legend(fontsize=11, loc='best', ncol=2)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(0.5, 12.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_agent_all_items.png',
            dpi=300, bbox_inches='tight')
print(f"✓ 저장: session_trajectory_agent_all_items.png")

# ═══════════════════════════════════════════════════════════════════════════
# 4. 그래프 3: 유의한 항목만 강조 (Agent vs Freepass)
# ═══════════════════════════════════════════════════════════════════════════

# 유의한 항목 (p<0.05)
significant_items = {
    'A1 수학전문성': ('avg_A1', 'agent', 0.015),
    'A2 질문구조화': ('avg_A2', 'both', 0.006),  # 둘 다 유의
    'B1 학습자맞춤': ('avg_B1', 'agent', 0.003),
    'B2 설명체계성': ('avg_B2', 'agent', 0.040),
    'C1 대화일관성': ('avg_C1', 'both', 0.015),  # 둘 다 유의
    '전체': ('Total', 'agent', 0.028)
}

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('반복 사용 시 유의하게 변화한 항목 (p<0.05)', 
            fontsize=16, fontweight='bold', y=0.995)

axes = axes.flatten()

for idx, (item_name, (col_name, sig_mode, p_val)) in enumerate(significant_items.items()):
    ax = axes[idx]
    
    # Agent
    agent_data = multi_df[multi_df['assigned_mode'] == 'agent']
    agent_summary = agent_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    agent_summary['se'] = agent_summary['std'] / np.sqrt(agent_summary['count'])
    
    ax.errorbar(agent_summary.index, agent_summary['mean'],
               yerr=agent_summary['se'],
               marker='o', linewidth=2.5, markersize=9,
               color='blue', label='Agent', capsize=5, alpha=0.9)
    
    # Freepass
    free_data = multi_df[multi_df['assigned_mode'] == 'freepass']
    free_summary = free_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    free_summary['se'] = free_summary['std'] / np.sqrt(free_summary['count'])
    
    ax.errorbar(free_summary.index, free_summary['mean'],
               yerr=free_summary['se'],
               marker='s', linewidth=2.5, markersize=9,
               color='orange', label='Freepass', capsize=5, alpha=0.9)
    
    # p값 표시
    if sig_mode == 'both':
        title = f'{item_name}\n(Agent p={p_val:.3f}*, Freepass도 유의)'
    else:
        title = f'{item_name}\n(Agent p={p_val:.3f}*)'
    
    ax.set_xlabel('세션 순서', fontsize=11, fontweight='bold')
    ax.set_ylabel('점수', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0.5, 12.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_significant_items.png',
            dpi=300, bbox_inches='tight')
print(f"✓ 저장: session_trajectory_significant_items.png")

# ═══════════════════════════════════════════════════════════════════════════
# 5. 그래프 4: 간결한 버전 (논문용 - 주요 항목만)
# ═══════════════════════════════════════════════════════════════════════════

# 주요 항목: C2, Total, B1, A2
key_items = {
    'C2 학습지원': 'avg_C2',
    '전체 점수': 'Total',
    'B1 학습자맞춤': 'avg_B1',
    'A2 질문구조화': 'avg_A2'
}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('세션 순서에 따른 주요 항목 점수 변화', 
            fontsize=16, fontweight='bold', y=0.995)

axes = axes.flatten()

for idx, (item_name, col_name) in enumerate(key_items.items()):
    ax = axes[idx]
    
    # Agent
    agent_data = multi_df[multi_df['assigned_mode'] == 'agent']
    agent_summary = agent_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    agent_summary['se'] = agent_summary['std'] / np.sqrt(agent_summary['count'])
    
    ax.errorbar(agent_summary.index, agent_summary['mean'],
               yerr=agent_summary['se'],
               marker='o', linewidth=3, markersize=10,
               color='blue', label='Agent', capsize=6, alpha=0.9)
    
    # Freepass
    free_data = multi_df[multi_df['assigned_mode'] == 'freepass']
    free_summary = free_data.groupby('session_order')[col_name].agg(['mean', 'std', 'count'])
    free_summary['se'] = free_summary['std'] / np.sqrt(free_summary['count'])
    
    ax.errorbar(free_summary.index, free_summary['mean'],
               yerr=free_summary['se'],
               marker='s', linewidth=3, markersize=10,
               color='orange', label='Freepass', capsize=6, alpha=0.9)
    
    ax.set_xlabel('세션 순서', fontsize=12, fontweight='bold')
    ax.set_ylabel('점수', fontsize=12, fontweight='bold')
    ax.set_title(item_name, fontsize=14, fontweight='bold', pad=10)
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0.5, 12.5)
    
    # y축 범위
    if item_name == '전체 점수':
        ax.set_ylim(23, 30)
    else:
        ax.set_ylim(1.5, 5.0)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'session_trajectory_key_items.png',
            dpi=300, bbox_inches='tight')
print(f"✓ 저장: session_trajectory_key_items.png")

print("\n" + "=" * 80)
print("🎉 모든 그래프 생성 완료!")
print("=" * 80)
print(f"\n생성된 파일:")
print(f"  1. session_trajectory_all_items_grid.png (3x3 격자, 모든 항목)")
print(f"  2. session_trajectory_agent_all_items.png (Agent만, 한 그래프)")
print(f"  3. session_trajectory_significant_items.png (유의한 항목만)")
print(f"  4. session_trajectory_key_items.png (주요 4개 항목, 논문용)")

