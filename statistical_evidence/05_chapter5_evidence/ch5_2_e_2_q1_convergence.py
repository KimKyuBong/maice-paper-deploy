#!/usr/bin/env python3
"""
5장 2절 라항 (2): Q1 하위권 효과의 수렴

목적: 표Ⅴ-12 계산
- 교사 평가 Q1 하위권 Agent/Freepass 비교
- LLM 3개 모델별 Q1 하위권 Agent/Freepass 비교
- Claude, GPT-5, Gemini 각 모델별 점수 계산
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

print("="*80)
print("5장 2절 라항 (2): Q1 하위권 효과의 수렴")
print("표Ⅴ-12: Q1(하위권) Agent 우위 폭 비교")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent

# 데이터 로드
LLM_FILE = BASE_DIR / "data" / "llm_evaluations" / "llm_3models_284_PERFECT_FINAL.csv"
SESSION_FILE = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"
STUDENT_FILE = BASE_DIR / "data" / "session_data" / "midterm_scores_with_quartile.csv"
TEACHER_FILE = BASE_DIR / "02_teacher_scoring" / "results" / "teacher_averaged_scores_perfect.csv"

df_llm = pd.read_csv(LLM_FILE)
df_session = pd.read_csv(SESSION_FILE)
df_student = pd.read_csv(STUDENT_FILE, dtype={'username': str})
df_teacher = pd.read_csv(TEACHER_FILE)

# 병합 (username 정규화: @ 제거, . 제거)
df_session['username_clean'] = df_session['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
df_student['username_clean'] = df_student['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)

df_llm_merged = pd.merge(df_llm, df_session[['session_id', 'username', 'mode']], on='session_id', how='inner')
df_llm_merged['username_clean'] = df_llm_merged['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
df_llm_merged = pd.merge(df_llm_merged, df_student[['username_clean', 'quartile']], on='username_clean', how='left')

df_teacher_merged = pd.merge(df_teacher, df_session[['session_id', 'username', 'mode']], on='session_id', how='inner')
df_teacher_merged['username_clean'] = df_teacher_merged['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
df_teacher_merged = pd.merge(df_teacher_merged, df_student[['username_clean', 'quartile']], on='username_clean', how='left')

# Q1만 필터링
q1_llm = df_llm_merged[df_llm_merged['quartile'] == 'Q1']
q1_teacher = df_teacher_merged[df_teacher_merged['quartile'] == 'Q1']

results = {}

# 1. 교사 평가 Q1
print("1. 교사 평가 Q1 하위권:")
print("-"*80)
teacher_agent = q1_teacher[q1_teacher['mode'] == 'agent']['teacher_overall'].mean()
teacher_freepass = q1_teacher[q1_teacher['mode'] == 'freepass']['teacher_overall'].mean()
teacher_diff = teacher_agent - teacher_freepass

print(f"  Agent: {teacher_agent:.2f}")
print(f"  Freepass: {teacher_freepass:.2f}")
print(f"  차이: {teacher_diff:+.2f}")
print()

results['teacher'] = {
    'agent': float(round(teacher_agent, 2)),
    'freepass': float(round(teacher_freepass, 2)),
    'difference': float(round(teacher_diff, 2))
}

# 2. LLM 3개 모델별 Q1
print("2. LLM 모델별 Q1 하위권:")
print("-"*80)

models = {
    'anthropic_overall': 'Claude-4.5-Haiku',
    'openai_overall': 'GPT-5-mini',
    'gemini_overall': 'Gemini-2.5-Flash'
}

for col, model_name in models.items():
    if col in q1_llm.columns:
        agent_scores = q1_llm[q1_llm['mode'] == 'agent'][col].dropna()
        freepass_scores = q1_llm[q1_llm['mode'] == 'freepass'][col].dropna()
        
        if len(agent_scores) > 0 and len(freepass_scores) > 0:
            agent_mean = agent_scores.mean()
            freepass_mean = freepass_scores.mean()
            diff = agent_mean - freepass_mean
            
            print(f"  {model_name}:")
            print(f"    Agent: {agent_mean:.2f} (n={len(agent_scores)})")
            print(f"    Freepass: {freepass_mean:.2f} (n={len(freepass_scores)})")
            print(f"    차이: {diff:+.2f}")
            print()
            
            results[model_name.lower().replace('-', '_')] = {
                'agent': float(round(agent_mean, 2)),
                'freepass': float(round(freepass_mean, 2)),
                'difference': float(round(diff, 2)),
                'agent_n': int(len(agent_scores)),
                'freepass_n': int(len(freepass_scores))
            }

# 결과 저장
output_results = {
    "table": "표Ⅴ-12",
    "title": "Q1(하위권) Agent 우위 폭 비교",
    "results": results,
    "data_files": [
        str(LLM_FILE.relative_to(BASE_DIR)),
        str(TEACHER_FILE.relative_to(BASE_DIR)),
        str(SESSION_FILE.relative_to(BASE_DIR)),
        str(STUDENT_FILE.relative_to(BASE_DIR))
    ]
}

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ch5_2_e_2_q1_convergence.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_results, f, ensure_ascii=False, indent=2)

print(f"✓ 결과 저장: {output_file}")
print("="*80)

