#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
교사 평가 모드별 비교 분석
표Ⅴ-9, 표Ⅴ-10 검증용
평가자 96, 97만 사용
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
TEACHER_AVG = BASE_DIR / "02_teacher_scoring" / "results" / "teacher_averaged_scores_perfect.csv"
SESSION_DATA = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"
STUDENT_INFO = BASE_DIR / "data" / "session_data" / "midterm_scores_with_quartile.csv"

print(f"{'='*80}")
print(f"교사 평가 모드별 & Quartile별 분석")
print(f"평가자 96, 97만 사용")
print(f"{'='*80}\n")

# [1] 데이터 로드
print("[1] 데이터 로드...")
df_teacher = pd.read_csv(TEACHER_AVG)
df_session = pd.read_csv(SESSION_DATA)
df_student = pd.read_csv(STUDENT_INFO)

print(f"✓ 교사 평가: {len(df_teacher)}개 세션")
print(f"✓ 세션 메타: {len(df_session)}개")
print(f"✓ 학생 정보: {len(df_student)}개\n")

# [2] 데이터 병합
print("[2] 데이터 병합...")

# session_id로 교사 평가와 세션 병합
df = pd.merge(
    df_teacher,
    df_session[['session_id', 'username', 'mode']],
    on='session_id',
    how='inner'
)

# username으로 학생 정보(Quartile) 병합
if 'username' in df.columns and 'username' in df_student.columns:
    # username 정규화: @ 제거, . 제거 (24.010@bssm.hs.kr -> 24010)
    df['username_clean'] = df['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
    df_student['username_clean'] = df_student['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
    
    df = pd.merge(
        df,
        df_student[['username_clean', 'quartile', 'midterm_total']],
        on='username_clean',
        how='left'
    )
    print(f"✓ Quartile 정보 병합 완료")
    print(f"  - Quartile 정보 있는 세션: {df['quartile'].notna().sum()}개")
else:
    print(f"⚠️  username 컬럼이 없어 Quartile 병합 실패")

print(f"✓ 병합 완료: {len(df)}개 세션")
print(f"✓ Agent: {len(df[df['mode']=='agent'])}개")
print(f"✓ Freepass: {len(df[df['mode']=='freepass'])}개\n")

# [3] 전체 모드 비교 (표Ⅴ-9)
print("[3] 전체 모드 비교 분석 (표Ⅴ-9)...")

mode_comparison = {}

# 전체 점수
agent_overall = df[df['mode'] == 'agent']['teacher_overall']
freepass_overall = df[df['mode'] == 'freepass']['teacher_overall']

t_stat, p_value = stats.ttest_ind(agent_overall, freepass_overall)
pooled_std = np.sqrt((agent_overall.std()**2 + freepass_overall.std()**2) / 2)
cohens_d = (agent_overall.mean() - freepass_overall.mean()) / pooled_std if pooled_std > 0 else 0

mode_comparison['overall'] = {
    'agent_mean': float(agent_overall.mean()),
    'agent_std': float(agent_overall.std()),
    'agent_n': int(len(agent_overall)),
    'freepass_mean': float(freepass_overall.mean()),
    'freepass_std': float(freepass_overall.std()),
    'freepass_n': int(len(freepass_overall)),
    'difference': float(agent_overall.mean() - freepass_overall.mean()),
    't_stat': float(t_stat),
    'p_value': float(p_value),
    'cohens_d': float(cohens_d)
}

# 영역별 비교
for area, col in [('question', 'teacher_question_total'), 
                   ('answer', 'teacher_answer_total'), 
                   ('context', 'teacher_context_total')]:
    agent_area = df[df['mode'] == 'agent'][col]
    freepass_area = df[df['mode'] == 'freepass'][col]
    
    t_stat, p_value = stats.ttest_ind(agent_area, freepass_area)
    pooled_std = np.sqrt((agent_area.std()**2 + freepass_area.std()**2) / 2)
    cohens_d = (agent_area.mean() - freepass_area.mean()) / pooled_std if pooled_std > 0 else 0
    
    mode_comparison[area] = {
        'agent_mean': float(agent_area.mean()),
        'agent_std': float(agent_area.std()),
        'agent_n': int(len(agent_area)),
        'freepass_mean': float(freepass_area.mean()),
        'freepass_std': float(freepass_area.std()),
        'freepass_n': int(len(freepass_area)),
        'difference': float(agent_area.mean() - freepass_area.mean()),
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d)
    }

print(f"✓ 모드별 비교 완료\n")

# [4] Quartile별 분석 (표Ⅴ-10)
print("[4] Quartile별 분석 (표Ⅴ-10)...")

quartile_analysis = {}

if 'quartile' in df.columns:
    overall_quartile = {}
    
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        df_q = df[df['quartile'] == q]
        
        if len(df_q) > 0:
            agent_q = df_q[df_q['mode'] == 'agent']['teacher_overall']
            freepass_q = df_q[df_q['mode'] == 'freepass']['teacher_overall']
            
            if len(agent_q) > 0 and len(freepass_q) > 0:
                t_stat, p_value = stats.ttest_ind(agent_q, freepass_q)
                pooled_std = np.sqrt((agent_q.std()**2 + freepass_q.std()**2) / 2)
                cohens_d = (agent_q.mean() - freepass_q.mean()) / pooled_std if pooled_std > 0 else 0
                
                overall_quartile[q] = {
                    'n': int(len(df_q)),
                    'agent_n': int(len(agent_q)),
                    'freepass_n': int(len(freepass_q)),
                    'agent_mean': float(agent_q.mean()),
                    'agent_std': float(agent_q.std()),
                    'freepass_mean': float(freepass_q.mean()),
                    'freepass_std': float(freepass_q.std()),
                    'difference': float(agent_q.mean() - freepass_q.mean()),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d)
                }
    
    quartile_analysis['overall'] = overall_quartile
    print(f"✓ Quartile별 분석 완료\n")
else:
    print(f"⚠️  Quartile 정보 없음\n")

# [5] 결과 저장
print("[5] 결과 저장...")

# 모드별 비교
mode_file = RESULTS_DIR / "teacher_mode_comparison_perfect.json"
with open(mode_file, 'w', encoding='utf-8') as f:
    json.dump(mode_comparison, f, ensure_ascii=False, indent=2)
print(f"✓ {mode_file.name}")

# Quartile별 분석
if quartile_analysis:
    quartile_file = RESULTS_DIR / "teacher_quartile_analysis_perfect.json"
    with open(quartile_file, 'w', encoding='utf-8') as f:
        json.dump(quartile_analysis, f, ensure_ascii=False, indent=2)
    print(f"✓ {quartile_file.name}")

# 요약
summary = {
    "분석시각": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "총세션": len(df),
    "agent_n": int(len(df[df['mode']=='agent'])),
    "freepass_n": int(len(df[df['mode']=='freepass'])),
    "전체차이": mode_comparison['overall']['difference'],
    "전체_p": mode_comparison['overall']['p_value'],
    "전체_d": mode_comparison['overall']['cohens_d'],
    "응답차이": mode_comparison['answer']['difference'],
    "응답_p": mode_comparison['answer']['p_value'],
    "응답_d": mode_comparison['answer']['cohens_d']
}

summary_file = RESULTS_DIR / "teacher_mode_summary_perfect.json"
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

overall = mode_comparison['overall']
print(f"\n전체 점수:")
print(f"  • Agent: {overall['agent_mean']:.2f} (SD={overall['agent_std']:.2f})")
print(f"  • Freepass: {overall['freepass_mean']:.2f} (SD={overall['freepass_std']:.2f})")
print(f"  • 차이: {overall['difference']:+.2f}")
print(f"  • t={overall['t_stat']:.2f}, p={overall['p_value']:.3f}, d={overall['cohens_d']:.3f}")

answer = mode_comparison['answer']
print(f"\n응답 영역:")
print(f"  • Agent: {answer['agent_mean']:.2f} (SD={answer['agent_std']:.2f})")
print(f"  • Freepass: {answer['freepass_mean']:.2f} (SD={answer['freepass_std']:.2f})")
print(f"  • 차이: {answer['difference']:+.2f}")
print(f"  • t={answer['t_stat']:.2f}, p={answer['p_value']:.3f}, d={answer['cohens_d']:.3f}")

if quartile_analysis and 'overall' in quartile_analysis:
    print(f"\nQuartile별 전체 점수:")
    for q, data in quartile_analysis['overall'].items():
        sig = '***' if data['p_value'] < 0.001 else '**' if data['p_value'] < 0.01 else '*' if data['p_value'] < 0.05 else ''
        print(f"  {q}: n={data['n']}, Agent={data['agent_mean']:.2f} (SD={data['agent_std']:.2f}, n={data['agent_n']}), Freepass={data['freepass_mean']:.2f} (SD={data['freepass_std']:.2f}, n={data['freepass_n']}), diff={data['difference']:+.2f}, p={data['p_value']:.3f}{sig}, d={data['cohens_d']:.3f}")

print(f"\n결과 위치: {RESULTS_DIR}")
print(f"{'='*80}\n")

