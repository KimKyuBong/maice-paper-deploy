#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5장 그림Ⅴ-1: 세션 순서에 따른 항목별 점수 변화 추이 오차 막대 그래프

목적: 세션 순서(session_order)별로 각 항목(A1-C2, 전체)의 평균 점수와 표준 오차를 계산하여
Agent와 Freepass 모드의 변화 추이를 비교하는 오차 막대 그래프 생성

출력:
- 항목별 서브플롯 (A1, A2, A3, B1, B2, B3, C1, C2, 전체)
- Agent vs Freepass 비교
- 오차 막대 (표준 오차 또는 신뢰구간)
- 중분위(median) 또는 평균(mean) 점수
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import json
from scipy import stats

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
LLM_AVG = BASE_DIR / "01_llm_scoring" / "results" / "llm_3models_averaged_perfect.csv"
SESSION_DATA = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"
RESULTS_DIR = BASE_DIR / "04_effect_size" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("그림Ⅴ-1: 세션 순서에 따른 항목별 점수 변화 추이")
print("="*80)
print()

# 데이터 로드
print("[1] 데이터 로드...")
df_llm = pd.read_csv(LLM_AVG)
df_session = pd.read_csv(SESSION_DATA)

print(f"✓ LLM 점수: {len(df_llm)}개 세션")
print(f"✓ 세션 메타: {len(df_session)}개 세션")

# 데이터 병합
df = pd.merge(
    df_llm,
    df_session[['session_id', 'username', 'mode', 'session_order']],
    on='session_id',
    how='inner'
)

print(f"✓ 병합 후: {len(df)}개 세션")
print()

# 항목 정의
items = {
    'A1': 'A1 수학 전문성',
    'A2': 'A2 질문 구조화',
    'A3': 'A3 학습 맥락',
    'B1': 'B1 학습자 맞춤도',
    'B2': 'B2 설명 체계성',
    'B3': 'B3 학습 확장성',
    'C1': 'C1 대화 일관성',
    'C2': 'C2 학습 지원',
    '전체': '전체'
}

# 세션 순서별 그룹화
print("[2] 세션 순서별 데이터 집계...")
print(f"세션 순서 범위: {df['session_order'].min()} ~ {df['session_order'].max()}")

# 세션 순서별로 그룹화하여 통계 계산
results = {}
for mode in ['agent', 'freepass']:
    df_mode = df[df['mode'] == mode].copy()
    
    mode_results = {}
    for item_key, item_name in items.items():
        if item_key == '전체':
            col = 'avg_overall'
        else:
            # avg_A1_total 형식
            col = f'avg_{item_key}_total'
        
        if col not in df_mode.columns:
            print(f"⚠️  컬럼 없음: {col}")
            continue
        
        # 세션 순서별 집계
        grouped = df_mode.groupby('session_order')[col].agg([
            'count',
            'mean',
            'median',
            'std',
            lambda x: stats.sem(x)  # 표준 오차
        ]).reset_index()
        
        grouped.columns = ['session_order', 'n', 'mean', 'median', 'std', 'sem']
        
        # 신뢰구간 95% (표준 오차 기준)
        grouped['ci_lower'] = grouped['mean'] - 1.96 * grouped['sem']
        grouped['ci_upper'] = grouped['mean'] + 1.96 * grouped['sem']
        
        mode_results[item_key] = {
            'name': item_name,
            'data': grouped.to_dict('records')
        }
    
    results[mode] = mode_results

print(f"✓ Agent: {len(df[df['mode']=='agent'])}, Freepass: {len(df[df['mode']=='freepass'])}")
print()

# 그래프 생성
print("[3] 그래프 생성...")

fig, axes = plt.subplots(3, 3, figsize=(18, 15))
axes = axes.flatten()

for idx, (item_key, item_name) in enumerate(items.items()):
    ax = axes[idx]
    
    # Agent 데이터
    agent_data = results['agent'][item_key]['data']
    agent_df = pd.DataFrame(agent_data)
    
    # Freepass 데이터
    freepass_data = results['freepass'][item_key]['data']
    freepass_df = pd.DataFrame(freepass_data)
    
    # 중분위(median) 점수로 플롯
    if len(agent_df) > 0:
        ax.errorbar(
            agent_df['session_order'],
            agent_df['median'],
            yerr=agent_df['sem'],  # 표준 오차
            fmt='o-',
            color='#2E86AB',
            label='Agent (중분위)',
            capsize=5,
            capthick=2,
            linewidth=2,
            markersize=6,
            alpha=0.8
        )
    
    if len(freepass_df) > 0:
        ax.errorbar(
            freepass_df['session_order'],
            freepass_df['median'],
            yerr=freepass_df['sem'],
            fmt='s--',
            color='#A23B72',
            label='Freepass (중분위)',
            capsize=5,
            capthick=2,
            linewidth=2,
            markersize=6,
            alpha=0.8
        )
    
    ax.set_title(item_name, fontsize=12, fontweight='bold')
    ax.set_xlabel('세션 순서', fontsize=10)
    ax.set_ylabel('점수 (중분위)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # y축 범위 자동 조정 (데이터에 맞게, 여백 추가)
    if len(agent_df) > 0 or len(freepass_df) > 0:
        all_values = []
        if len(agent_df) > 0:
            all_values.extend(agent_df['median'].values)
            all_values.extend((agent_df['median'] - agent_df['sem']).fillna(0).values)
            all_values.extend((agent_df['median'] + agent_df['sem']).fillna(0).values)
        if len(freepass_df) > 0:
            all_values.extend(freepass_df['median'].values)
            all_values.extend((freepass_df['median'] - freepass_df['sem']).fillna(0).values)
            all_values.extend((freepass_df['median'] + freepass_df['sem']).fillna(0).values)
        
        # NaN 제거
        all_values = [v for v in all_values if not np.isnan(v)]
        
        if len(all_values) > 0:
            y_min_val = np.nanmin(all_values)
            y_max_val = np.nanmax(all_values)
            y_range = y_max_val - y_min_val
            
            # 범위의 20%를 여백으로 추가 (위쪽 여백을 더 크게)
            # 하단: 범위의 10% (최대 0.8), 상단: 범위의 20% (최대 1.5)
            bottom_margin = max(0.3, min(0.8, y_range * 0.1))
            top_margin = max(0.8, min(1.5, y_range * 0.2))
            y_min = max(0, y_min_val - bottom_margin)
            y_max = y_max_val + top_margin
            ax.set_ylim(y_min, y_max)

plt.tight_layout()

# 그래프 저장
output_png = RESULTS_DIR / "figure_v1_session_order_trends_median.png"
plt.savefig(output_png, dpi=300, bbox_inches='tight')
print(f"✓ 그래프 저장: {output_png}")
plt.close()

# 평균 점수로도 그래프 생성
fig, axes = plt.subplots(3, 3, figsize=(18, 15))
axes = axes.flatten()

for idx, (item_key, item_name) in enumerate(items.items()):
    ax = axes[idx]
    
    agent_data = results['agent'][item_key]['data']
    agent_df = pd.DataFrame(agent_data)
    
    freepass_data = results['freepass'][item_key]['data']
    freepass_df = pd.DataFrame(freepass_data)
    
    # 평균(mean) 점수로 플롯
    if len(agent_df) > 0:
        ax.errorbar(
            agent_df['session_order'],
            agent_df['mean'],
            yerr=agent_df['sem'],
            fmt='o-',
            color='#2E86AB',
            label='Agent (평균)',
            capsize=5,
            capthick=2,
            linewidth=2,
            markersize=6,
            alpha=0.8
        )
    
    if len(freepass_df) > 0:
        ax.errorbar(
            freepass_df['session_order'],
            freepass_df['mean'],
            yerr=freepass_df['sem'],
            fmt='s--',
            color='#A23B72',
            label='Freepass (평균)',
            capsize=5,
            capthick=2,
            linewidth=2,
            markersize=6,
            alpha=0.8
        )
    
    ax.set_title(item_name, fontsize=12, fontweight='bold')
    ax.set_xlabel('세션 순서', fontsize=10)
    ax.set_ylabel('점수 (평균)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # y축 범위 자동 조정 (데이터에 맞게, 여백 추가)
    if len(agent_df) > 0 or len(freepass_df) > 0:
        all_values = []
        if len(agent_df) > 0:
            all_values.extend(agent_df['mean'].values)
            all_values.extend((agent_df['mean'] - agent_df['sem']).fillna(0).values)
            all_values.extend((agent_df['mean'] + agent_df['sem']).fillna(0).values)
        if len(freepass_df) > 0:
            all_values.extend(freepass_df['mean'].values)
            all_values.extend((freepass_df['mean'] - freepass_df['sem']).fillna(0).values)
            all_values.extend((freepass_df['mean'] + freepass_df['sem']).fillna(0).values)
        
        # NaN 제거
        all_values = [v for v in all_values if not np.isnan(v)]
        
        if len(all_values) > 0:
            y_min_val = np.nanmin(all_values)
            y_max_val = np.nanmax(all_values)
            y_range = y_max_val - y_min_val
            
            # 범위의 20%를 여백으로 추가 (위쪽 여백을 더 크게)
            # 하단: 범위의 10% (최대 0.8), 상단: 범위의 20% (최대 1.5)
            bottom_margin = max(0.3, min(0.8, y_range * 0.1))
            top_margin = max(0.8, min(1.5, y_range * 0.2))
            y_min = max(0, y_min_val - bottom_margin)
            y_max = y_max_val + top_margin
            ax.set_ylim(y_min, y_max)

plt.tight_layout()

output_png_mean = RESULTS_DIR / "figure_v1_session_order_trends_mean.png"
plt.savefig(output_png_mean, dpi=300, bbox_inches='tight')
print(f"✓ 그래프 저장: {output_png_mean}")

# 결과를 JSON으로 저장
output_json = RESULTS_DIR / "figure_v1_session_order_trends.json"
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print(f"✓ 데이터 저장: {output_json}")
print()

print("="*80)
print("그림Ⅴ-1 생성 완료!")
print("="*80)
print(f"\n생성된 파일:")
print(f"  - {output_png.name} (중분위)")
print(f"  - {output_png_mean.name} (평균)")
print(f"  - {output_json.name} (데이터)")
print()

