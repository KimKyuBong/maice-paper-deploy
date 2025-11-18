#!/usr/bin/env python3
"""
5장 1절 나항: 데이터 수집 현황 (표Ⅴ-1)

목적: 표Ⅴ-1 계산
- 세션 수 (Agent, Freepass, 전체)
- 학생 수 (Agent, Freepass, 전체)
- 1인당 평균 세션 수
"""

import pandas as pd
from pathlib import Path
import json

print("="*80)
print("표Ⅴ-1: 수집 데이터 현황")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent
SESSION_FILE = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"

# 데이터 로드
df = pd.read_csv(SESSION_FILE)

# 세션 수 계산
agent_sessions = len(df[df['mode'] == 'agent'])
freepass_sessions = len(df[df['mode'] == 'freepass'])
total_sessions = len(df)

# 학생 수 계산
agent_students = df[df['mode'] == 'agent']['username'].nunique()
freepass_students = df[df['mode'] == 'freepass']['username'].nunique()
total_students = df['username'].nunique()

# 1인당 평균 계산
agent_avg = agent_sessions / agent_students if agent_students > 0 else 0
freepass_avg = freepass_sessions / freepass_students if freepass_students > 0 else 0
total_avg = total_sessions / total_students if total_students > 0 else 0

# 결과 출력
print(f"세션 수: Agent={agent_sessions}, Freepass={freepass_sessions}, 전체={total_sessions}")
print(f"학생 수: Agent={agent_students}, Freepass={freepass_students}, 전체={total_students}")
print(f"1인당 평균: Agent={agent_avg:.1f}, Freepass={freepass_avg:.1f}, 전체={total_avg:.1f}")
print()

# 결과 저장
results = {
    "table": "표Ⅴ-1",
    "title": "수집 데이터 현황",
    "session_counts": {
        "agent": int(agent_sessions),
        "freepass": int(freepass_sessions),
        "total": int(total_sessions)
    },
    "student_counts": {
        "agent": int(agent_students),
        "freepass": int(freepass_students),
        "total": int(total_students)
    },
    "average_sessions_per_student": {
        "agent": float(round(agent_avg, 1)),
        "freepass": float(round(freepass_avg, 1)),
        "total": float(round(total_avg, 1))
    },
    "data_file": str(SESSION_FILE.relative_to(BASE_DIR))
}

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ch5_1_n_data_collection.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✓ 결과 저장: {output_file}")
print("="*80)

