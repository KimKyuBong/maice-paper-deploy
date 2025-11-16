#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모드별(Agent/Freepass) & Quartile별 분석
표V-5, V-6, V-7 검증용
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from scipy import stats
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "04_effect_size" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 소스 파일
LLM_AVG = BASE_DIR / "01_llm_scoring" / "results" / "llm_3models_averaged_perfect.csv"
SESSION_DATA = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"

print(f"{'='*80}")
print(f"모드별 & Quartile별 분석")
print(f"{'='*80}\n")

# [1] 데이터 로드
print("[1] 데이터 로드...")
df_llm = pd.read_csv(LLM_AVG)
df_session = pd.read_csv(SESSION_DATA)

print(f"✓ LLM 평균: {len(df_llm)}개")
print(f"✓ 세션 메타: {len(df_session)}개\n")

# [2] 데이터 병합
print("[2] 데이터 병합...")

# session_id로 병합
df = pd.merge(
    df_llm,
    df_session,
    on='session_id',
    how='inner'
)

print(f"✓ 병합 완료: {len(df)}개 세션")
print(f"✓ Agent: {len(df[df['mode']=='agent'])}개")
print(f"✓ Freepass: {len(df[df['mode']=='freepass'])}개\n")

# [3] 모드별 비교 (표V-5)
print("[3] 모드별 비교 분석 (표V-5)...")

categories = {
    'A1': 'avg_A1_total',
    'A2': 'avg_A2_total',
    'A3': 'avg_A3_total',
    'B1': 'avg_B1_total',
    'B2': 'avg_B2_total',
    'B3': 'avg_B3_total',
    'C1': 'avg_C1_total',
    'C2': 'avg_C2_total'
}

mode_comparison = {}

for cat_code, col_name in categories.items():
    if col_name in df.columns:
        agent = df[df['mode'] == 'agent'][col_name]
        freepass = df[df['mode'] == 'freepass'][col_name]
        
        # t-test
        t_stat, p_value = stats.ttest_ind(agent, freepass)
        
        # Cohen's d
        pooled_std = np.sqrt((agent.std()**2 + freepass.std()**2) / 2)
        cohens_d = (agent.mean() - freepass.mean()) / pooled_std if pooled_std > 0 else 0
        
        mode_comparison[cat_code] = {
            'agent_mean': float(agent.mean()),
            'agent_std': float(agent.std()),
            'agent_n': int(len(agent)),
            'freepass_mean': float(freepass.mean()),
            'freepass_std': float(freepass.std()),
            'freepass_n': int(len(freepass)),
            'difference': float(agent.mean() - freepass.mean()),
            't_stat': float(t_stat),
            'p_value': float(p_value),
            'cohens_d': float(cohens_d),
            'significant': bool(p_value < 0.05)
        }

print(f"✓ {len(mode_comparison)}개 중분류 모드별 비교 완료\n")

# [4] Quartile별 분석 (표V-6, V-7)
print("[4] Quartile별 분석...")

# Quartile 정보 확인
if 'quartile' in df.columns:
    quartile_analysis = {}
    
    # C2만 분석 (표V-6)
    if 'avg_C2_total' in df.columns:
        c2_quartile = {}
        
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            df_q = df[df['quartile'] == q]
            
            if len(df_q) > 0:
                agent_q = df_q[df_q['mode'] == 'agent']['avg_C2_total']
                freepass_q = df_q[df_q['mode'] == 'freepass']['avg_C2_total']
                
                if len(agent_q) > 0 and len(freepass_q) > 0:
                    t_stat, p_value = stats.ttest_ind(agent_q, freepass_q)
                    pooled_std = np.sqrt((agent_q.std()**2 + freepass_q.std()**2) / 2)
                    cohens_d = (agent_q.mean() - freepass_q.mean()) / pooled_std if pooled_std > 0 else 0
                    
                    c2_quartile[q] = {
                        'n': int(len(df_q)),
                        'agent_mean': float(agent_q.mean()),
                        'freepass_mean': float(freepass_q.mean()),
                        'difference': float(agent_q.mean() - freepass_q.mean()),
                        'p_value': float(p_value),
                        'cohens_d': float(cohens_d)
                    }
        
        quartile_analysis['C2'] = c2_quartile
    
    # 전체 점수 (표V-7)
    if 'avg_overall' in df.columns:
        overall_quartile = {}
        
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            df_q = df[df['quartile'] == q]
            
            if len(df_q) > 0:
                agent_q = df_q[df_q['mode'] == 'agent']['avg_overall']
                freepass_q = df_q[df_q['mode'] == 'freepass']['avg_overall']
                
                if len(agent_q) > 0 and len(freepass_q) > 0:
                    t_stat, p_value = stats.ttest_ind(agent_q, freepass_q)
                    pooled_std = np.sqrt((agent_q.std()**2 + freepass_q.std()**2) / 2)
                    cohens_d = (agent_q.mean() - freepass_q.mean()) / pooled_std if pooled_std > 0 else 0
                    
                    overall_quartile[q] = {
                        'n': int(len(df_q)),
                        'agent_mean': float(agent_q.mean()),
                        'freepass_mean': float(freepass_q.mean()),
                        'difference': float(agent_q.mean() - freepass_q.mean()),
                        'p_value': float(p_value),
                        'cohens_d': float(cohens_d)
                    }
        
        quartile_analysis['overall'] = overall_quartile
    
    print(f"✓ Quartile별 분석 완료\n")
else:
    print(f"⚠️  Quartile 정보 없음\n")
    quartile_analysis = {}

# [5] 결과 저장
print("[5] 결과 저장...")

# 모드별 비교
mode_file = RESULTS_DIR / "mode_comparison_perfect.json"
with open(mode_file, 'w', encoding='utf-8') as f:
    json.dump(mode_comparison, f, ensure_ascii=False, indent=2)
print(f"✓ {mode_file.name}")

# Quartile별 분석
if quartile_analysis:
    quartile_file = RESULTS_DIR / "quartile_analysis_perfect.json"
    with open(quartile_file, 'w', encoding='utf-8') as f:
        json.dump(quartile_analysis, f, ensure_ascii=False, indent=2)
    print(f"✓ {quartile_file.name}")

# 요약
summary = {
    "분석시각": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "총세션": len(df),
    "agent_n": int(len(df[df['mode']=='agent'])),
    "freepass_n": int(len(df[df['mode']=='freepass'])),
    "유의한_중분류": [
        cat for cat, data in mode_comparison.items()
        if data['significant']
    ],
    "C2_차이": mode_comparison.get('C2', {}).get('difference', 0),
    "C2_p": mode_comparison.get('C2', {}).get('p_value', 1.0),
    "C2_d": mode_comparison.get('C2', {}).get('cohens_d', 0)
}

summary_file = RESULTS_DIR / "mode_quartile_summary_perfect.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ {summary_file.name}\n")

# 최종 출력
print(f"{'='*80}")
print(f"분석 완료!")
print(f"{'='*80}")
print(f"\n모드별 비교:")
print(f"  • Agent: {summary['agent_n']}개")
print(f"  • Freepass: {summary['freepass_n']}개")

if 'C2' in mode_comparison:
    c2 = mode_comparison['C2']
    print(f"\nC2 학습 지원:")
    print(f"  • Agent: {c2['agent_mean']:.2f}")
    print(f"  • Freepass: {c2['freepass_mean']:.2f}")
    print(f"  • 차이: {c2['difference']:+.2f}")
    print(f"  • p-value: {c2['p_value']:.4f}")
    print(f"  • Cohen's d: {c2['cohens_d']:.3f}")

print(f"\n유의한 중분류: {summary['유의한_중분류']}")

if quartile_analysis:
    print(f"\nQuartile 분석:")
    if 'C2' in quartile_analysis:
        print(f"  C2 Quartile별 차이:")
        for q, data in quartile_analysis['C2'].items():
            print(f"    {q}: {data['difference']:+.2f} (p={data['p_value']:.3f}, d={data['cohens_d']:.3f})")

print(f"\n결과 위치: {RESULTS_DIR}")
print(f"{'='*80}\n")

