#!/usr/bin/env python3
"""
하위권(Q1) 학생의 세션 순서에 따른 점수 변화 추이 그래프 생성
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
BASE = Path(__file__).parent.parent
DATA_DIR = BASE / 'data'
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

print("="*80)
print("하위권(Q1) 학생: 세션 순서에 따른 점수 변화 추이")
print("="*80)
print()

# 1. 데이터 로드
print("[1] 데이터 로드...")

# LLM 점수 (3개 모델 평균)
df_llm = pd.read_csv(BASE / '01_llm_scoring/results/llm_3models_averaged_perfect.csv')

# 컬럼명 단순화
df_llm = df_llm.rename(columns={
    'avg_A1_total': 'A1',
    'avg_A2_total': 'A2',
    'avg_A3_total': 'A3',
    'avg_B1_total': 'B1',
    'avg_B2_total': 'B2',
    'avg_B3_total': 'B3',
    'avg_C1_total': 'C1',
    'avg_C2_total': 'C2',
    'avg_overall': '전체'
})

print(f"✓ LLM 점수: {len(df_llm)}개 세션")

# 세션 메타데이터
df_session = pd.read_csv(DATA_DIR / 'session_data/full_sessions_with_scores.csv')
print(f"✓ 세션 메타: {len(df_session)}개 세션")

# username_clean 생성
df_session['username_clean'] = df_session['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)

# 중간고사 점수 및 Quartile
df_midterm = pd.read_csv(DATA_DIR / 'session_data/midterm_scores_with_quartile.csv')
df_midterm['username_clean'] = df_midterm['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)

# 병합
df = df_llm.merge(df_session[['session_id', 'username_clean', 'mode', 'session_order']], on='session_id', how='inner')
df = df.merge(df_midterm[['username_clean', 'quartile']], on='username_clean', how='left')

print(f"✓ 병합 후: {len(df)}개 세션")

# Q1만 필터링
df_q1 = df[df['quartile'] == 'Q1'].copy()
print(f"✓ Q1 하위권: {len(df_q1)}개 세션 (Agent: {len(df_q1[df_q1['mode']=='agent'])}, Freepass: {len(df_q1[df_q1['mode']=='freepass'])})")
print()

# 2. 세션 순서별 데이터 집계
print("[2] 세션 순서별 데이터 집계...")

items = {
    'A1': 'A1 수학 전문성',
    'A2': 'A2 질문 구조화',
    'A3': 'A3 학습 맥락',
    'B1': 'B1 학습자 맞춤도',
    'B2': 'B2 설명 체계성',
    'B3': 'B3 학습 확장성',
    'C1': 'C1 대화 일관성',
    'C2': 'C2 학습 지원',
    '전체': '전체 점수'
}

def aggregate_by_session_order(df, mode, item_col):
    """세션 순서별로 집계"""
    df_mode = df[df['mode'] == mode].copy()
    
    grouped = df_mode.groupby('session_order')[item_col].agg([
        ('n', 'count'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('sem', lambda x: stats.sem(x))
    ]).reset_index()
    
    # 신뢰구간 계산 (95%)
    grouped['ci_lower'] = grouped['mean'] - 1.96 * grouped['sem']
    grouped['ci_upper'] = grouped['mean'] + 1.96 * grouped['sem']
    
    return grouped.to_dict('records')

# 모든 항목에 대해 집계
result = {
    'agent': {},
    'freepass': {}
}

for code, name in items.items():
    for mode in ['agent', 'freepass']:
        data = aggregate_by_session_order(df_q1, mode, code)
        result[mode][code] = {
            'name': name,
            'data': data
        }

print(f"세션 순서 범위: {df_q1['session_order'].min()} ~ {df_q1['session_order'].max()}")
print(f"✓ Agent Q1: {len(df_q1[df_q1['mode']=='agent'])}, Freepass Q1: {len(df_q1[df_q1['mode']=='freepass'])}")
print()

# 3. 그래프 생성
print("[3] 그래프 생성...")

for stat_type in ['mean', 'median']:
    fig, axes = plt.subplots(3, 3, figsize=(20, 16))
    fig.suptitle(f'하위권(Q1) 학생: 세션 순서에 따른 항목별 점수 변화 추이 ({stat_type.upper()})', 
                 fontsize=20, fontweight='bold', y=0.995)
    
    axes = axes.flatten()
    
    for idx, (code, name) in enumerate(items.items()):
        ax = axes[idx]
        
        # Agent 데이터
        agent_data = result['agent'][code]['data']
        agent_orders = [d['session_order'] for d in agent_data]
        agent_values = [d[stat_type] for d in agent_data]
        agent_sems = [d['sem'] for d in agent_data]
        
        # Freepass 데이터
        freepass_data = result['freepass'][code]['data']
        freepass_orders = [d['session_order'] for d in freepass_data]
        freepass_values = [d[stat_type] for d in freepass_data]
        freepass_sems = [d['sem'] for d in freepass_data]
        
        # 오차 막대 그래프
        ax.errorbar(agent_orders, agent_values, yerr=agent_sems, 
                   fmt='o-', linewidth=2, markersize=8, capsize=5, capthick=2,
                   label='Agent (명료화)', color='#2E86AB', alpha=0.8)
        ax.errorbar(freepass_orders, freepass_values, yerr=freepass_sems,
                   fmt='s-', linewidth=2, markersize=8, capsize=5, capthick=2,
                   label='Freepass (즉시답변)', color='#A23B72', alpha=0.8)
        
        ax.set_xlabel('세션 순서 (회차)', fontsize=11)
        ax.set_ylabel('점수', fontsize=11)
        ax.set_title(name, fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks(range(1, max(df_q1['session_order'].max(), 10) + 1))
    
    # 마지막 subplot 제거 (9개만 사용)
    fig.delaxes(axes[-1])
    
    plt.tight_layout()
    
    # 저장
    output_file = RESULTS_DIR / f'figure_q1_session_order_trends_{stat_type}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 그래프 저장: {output_file}")

# 4. JSON 저장
output_json = RESULTS_DIR / 'figure_q1_session_order_trends.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"✓ 데이터 저장: {output_json}")
print()

# 5. 통계 요약
print("[4] 통계 요약...")
print()

for mode_name, mode in [('Agent', 'agent'), ('Freepass', 'freepass')]:
    overall_data = result[mode]['전체']['data']
    
    # 초기 세션 (1-3회차)
    early = [d for d in overall_data if d['session_order'] <= 3]
    if early:
        early_mean = np.mean([d['mean'] for d in early])
        early_sem = np.mean([d['sem'] for d in early])
    else:
        early_mean = early_sem = 0
    
    # 후기 세션 (마지막 3개)
    max_order = max([d['session_order'] for d in overall_data])
    late = [d for d in overall_data if d['session_order'] >= max_order - 2]
    if late:
        late_mean = np.mean([d['mean'] for d in late])
        late_sem = np.mean([d['sem'] for d in late])
    else:
        late_mean = late_sem = 0
    
    print(f"【{mode_name} 모드】 Q1 하위권")
    print(f"  초기 세션(1-3회차): {early_mean:.2f}점 (평균 SEM={early_sem:.3f})")
    print(f"  후기 세션: {late_mean:.2f}점 (평균 SEM={late_sem:.3f})")
    print(f"  변화: {late_mean - early_mean:+.2f}점")
    print()

print("="*80)
print("하위권(Q1) 세션 추이 그래프 생성 완료!")
print("="*80)
print()
print("생성된 파일:")
print("  - figure_q1_session_order_trends_mean.png (평균)")
print("  - figure_q1_session_order_trends_median.png (중앙값)")
print("  - figure_q1_session_order_trends.json (데이터)")
print()

