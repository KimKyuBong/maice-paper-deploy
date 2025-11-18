#!/usr/bin/env python3
"""
5장 1절 다항: 사전 동질성 검증

목적: 표Ⅴ-2 근거 (사전 동질성 검증)
- Agent와 Freepass 집단 간 중간고사 성적 차이 검증
- 독립표본 t-검정
- t=1.18, p=0.242, Agent=57.71점, Freepass=63.47점
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

print("="*80)
print("5장 1절 다항: 사전 동질성 검증")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent
SESSION_FILE = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"
STUDENT_FILE = BASE_DIR / "data" / "session_data" / "midterm_scores_with_quartile.csv"

# 데이터 로드
df_session = pd.read_csv(SESSION_FILE)
df_student = pd.read_csv(STUDENT_FILE, dtype={'username': str})

# 학생별 모드 정보 추출 (첫 세션 기준)
student_mode = df_session.groupby('username')['mode'].first().reset_index()

# 중간고사 점수와 모드 병합
# df_student['username']은 이미 24.010@bssm.hs.kr 형태
# student_mode['username']도 24.010@bssm.hs.kr 형태
# 둘 다 동일한 형태로 username_clean 생성 (@ 제거, . 제거)
df_student['username_clean'] = df_student['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)
student_mode['username_clean'] = student_mode['username'].astype(str).str.replace('@bssm.hs.kr', '', regex=False).str.replace('.', '', regex=False)

df_merged = pd.merge(df_student, student_mode, on='username_clean', how='inner')

# Agent와 Freepass 집단 분리
agent_scores = df_merged[df_merged['mode'] == 'agent']['midterm_total'].dropna()
freepass_scores = df_merged[df_merged['mode'] == 'freepass']['midterm_total'].dropna()

# 통계 계산
agent_mean = agent_scores.mean()
agent_std = agent_scores.std()
agent_n = len(agent_scores)

freepass_mean = freepass_scores.mean()
freepass_std = freepass_scores.std()
freepass_n = len(freepass_scores)

# 등분산성 검정
levene_stat, levene_p = stats.levene(agent_scores, freepass_scores)
equal_var = levene_p > 0.05

# 독립표본 t-검정
t_stat, p_value = stats.ttest_ind(agent_scores, freepass_scores, equal_var=equal_var)

# 결과 출력
print(f"Agent 모드: 평균={agent_mean:.2f}점, SD={agent_std:.2f}, n={agent_n}")
print(f"Freepass 모드: 평균={freepass_mean:.2f}점, SD={freepass_std:.2f}, n={freepass_n}")
print(f"차이: {agent_mean - freepass_mean:.2f}점")
print(f"t={t_stat:.2f}, p={p_value:.3f}")
print()

# 결과 저장
results = {
    "table": "표Ⅴ-2 (사전 동질성)",
    "title": "사전 동질성 검증",
    "agent": {
        "mean": float(round(agent_mean, 2)),
        "std": float(round(agent_std, 2)),
        "n": int(agent_n)
    },
    "freepass": {
        "mean": float(round(freepass_mean, 2)),
        "std": float(round(freepass_std, 2)),
        "n": int(freepass_n)
    },
    "difference": float(round(agent_mean - freepass_mean, 2)),
    "t_stat": float(round(t_stat, 2)),
    "p_value": float(round(p_value, 3)),
    "equal_variance": bool(equal_var),
    "levene_p": float(levene_p),
    "data_files": [
        str(SESSION_FILE.relative_to(BASE_DIR)),
        str(STUDENT_FILE.relative_to(BASE_DIR))
    ]
}

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ch5_1_d_pre_homogeneity.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✓ 결과 저장: {output_file}")
print("="*80)

