#!/usr/bin/env python3
"""
하위권(Q1) 학생의 세션 순서에 따른 전체 점수 변화 추이 그래프 생성 (총점만)
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
print("하위권(Q1) 학생: 세션 순서에 따른 전체 점수 변화 추이 (총점)")
print("="*80)
print()

# 1. 데이터 로드
print("[1] 데이터 로드...")

# LLM 점수 (3개 모델 평균)
df_llm = pd.read_csv(BASE / '01_llm_scoring/results/llm_3models_averaged_perfect.csv')

# 컬럼명 단순화
df_llm = df_llm.rename(columns={
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

def aggregate_by_session_order(df, mode):
    """세션 순서별로 집계"""
    df_mode = df[df['mode'] == mode].copy()
    
    grouped = df_mode.groupby('session_order')['전체'].agg([
        ('n', 'count'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('sem', lambda x: stats.sem(x) if len(x) > 1 else 0)
    ]).reset_index()
    
    # 신뢰구간 계산 (95%)
    grouped['ci_lower'] = grouped['mean'] - 1.96 * grouped['sem']
    grouped['ci_upper'] = grouped['mean'] + 1.96 * grouped['sem']
    
    return grouped

# Agent와 Freepass 집계
agent_data = aggregate_by_session_order(df_q1, 'agent')
freepass_data = aggregate_by_session_order(df_q1, 'freepass')

print(f"세션 순서 범위: {df_q1['session_order'].min()} ~ {df_q1['session_order'].max()}")
print()

# 3. 그래프 생성
print("[3] 그래프 생성...")

# 평균값 기반 그래프
fig, ax = plt.subplots(figsize=(12, 8))

# Agent 데이터
ax.errorbar(agent_data['session_order'], agent_data['mean'], 
           yerr=agent_data['sem'], 
           fmt='o-', linewidth=3, markersize=10, capsize=6, capthick=2.5,
           label='Agent (명료화)', color='#2E86AB', alpha=0.9, elinewidth=2)

# Freepass 데이터
ax.errorbar(freepass_data['session_order'], freepass_data['mean'],
           yerr=freepass_data['sem'],
           fmt='s-', linewidth=3, markersize=10, capsize=6, capthick=2.5,
           label='Freepass (즉시답변)', color='#A23B72', alpha=0.9, elinewidth=2)

ax.set_xlabel('세션 순서 (회차)', fontsize=14, fontweight='bold')
ax.set_ylabel('전체 점수 (40점 만점)', fontsize=14, fontweight='bold')
ax.set_title('하위권(Q1) 학생: 세션 순서에 따른 전체 점수 변화 추이', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(loc='best', fontsize=12, framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xticks(range(1, int(df_q1['session_order'].max()) + 1))
ax.set_ylim(20, 32)

# 초기와 후기 구분선 추가
ax.axvline(x=3.5, color='gray', linestyle=':', linewidth=2, alpha=0.5, label='초기/후기 구분')

plt.tight_layout()

# 저장
output_file = RESULTS_DIR / 'figure_q1_overall_score_trend.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ 그래프 저장: {output_file}")
print()

# 4. 통계 요약
print("[4] 통계 요약...")
print()

for mode_name, data in [('Agent', agent_data), ('Freepass', freepass_data)]:
    # 초기 세션 (1-3회차)
    early = data[data['session_order'] <= 3]
    early_mean = early['mean'].mean() if len(early) > 0 else 0
    early_sem = early['sem'].mean() if len(early) > 0 else 0
    early_n = early['n'].sum() if len(early) > 0 else 0
    
    # 후기 세션 (4회차 이상)
    late = data[data['session_order'] >= 4]
    late_mean = late['mean'].mean() if len(late) > 0 else 0
    late_sem = late['sem'].mean() if len(late) > 0 else 0
    late_n = late['n'].sum() if len(late) > 0 else 0
    
    print(f"【{mode_name} 모드】 Q1 하위권")
    print(f"  초기 세션(1-3회차): {early_mean:.2f}점 (평균 SEM={early_sem:.3f}, n={early_n})")
    print(f"  후기 세션(4회차~): {late_mean:.2f}점 (평균 SEM={late_sem:.3f}, n={late_n})")
    print(f"  변화: {late_mean - early_mean:+.2f}점")
    print()

# 5. JSON 저장
result = {
    'agent': agent_data.to_dict('records'),
    'freepass': freepass_data.to_dict('records')
}

output_json = RESULTS_DIR / 'figure_q1_overall_score_trend.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"✓ 데이터 저장: {output_json}")
print()

print("="*80)
print("하위권(Q1) 전체 점수 추이 그래프 생성 완료!")
print("="*80)
print()
print("생성된 파일:")
print("  - figure_q1_overall_score_trend.png")
print("  - figure_q1_overall_score_trend.json")
print()


