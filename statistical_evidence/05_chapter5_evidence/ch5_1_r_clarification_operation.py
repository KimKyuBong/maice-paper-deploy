#!/usr/bin/env python3
"""
5장 1절 라항: 명료화 프로세스 작동 확인

목적: 표Ⅴ-2 계산
- Agent 모드 세션 중 명료화 질문 수행 여부
- 명료화 수행/미수행 세션 수, 비율
- 평균 메시지 수 계산

데이터 소스: PostgreSQL DB (maice_agent.llm_prompt_logs)
- classifier_llm 호출 = 명료화 질문 수행
"""

import pandas as pd
import json
from pathlib import Path

print("="*80)
print("5장 1절 라항: 명료화 프로세스 작동 확인")
print("표Ⅴ-2: 명료화 수행 현황")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent

# 데이터 로드
DB_LOGS_FILE = BASE_DIR / "data" / "db_exports" / "public_llm_prompt_logs_full.csv"
SESSION_FILE = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"

df_logs = pd.read_csv(DB_LOGS_FILE)
df_session = pd.read_csv(SESSION_FILE)

print("[1] 데이터 로드...")
print(f"✓ DB 로그: {len(df_logs)}개 레코드")
print(f"✓ 세션 메타: {len(df_session)}개 세션")
print()

# Agent 모드 세션만 필터링
agent_sessions = df_session[df_session['mode'] == 'agent']
agent_session_ids = set(agent_sessions['session_id'].tolist())

print(f"[2] Agent 모드 세션: {len(agent_session_ids)}개")
print()

# 명료화 질문 수행 여부 확인
# classifier_llm 또는 question_improver_llm 호출 = 명료화 질문
print("[3] 명료화 질문 수행 여부 분석...")

# DB 로그에서 Agent 세션의 classifier_llm 호출 확인
agent_logs = df_logs[df_logs['session_id'].isin(agent_session_ids)]

# 명료화 질문 수행 세션 확인
clarification_tools = ['classifier_llm', 'question_improver_llm']
if 'tool_name' in agent_logs.columns:
    clarification_sessions = set(
        agent_logs[
            agent_logs['tool_name'].isin(clarification_tools)
        ]['session_id'].unique()
    )
elif 'agent_name' in agent_logs.columns:
    clarification_sessions = set(
        agent_logs[
            agent_logs['agent_name'].isin(clarification_tools)
        ]['session_id'].unique()
    )
else:
    # tool_name과 agent_name이 없으면 모든 로그를 확인
    print("⚠️  tool_name/agent_name 컬럼 없음. 모든 로그 확인...")
    clarification_sessions = set(agent_logs['session_id'].unique())

# 세션별 메시지 수 계산
session_message_counts = agent_logs.groupby('session_id').size().to_dict()

# 명료화 수행/미수행 세션 분류
performed_sessions = []
not_performed_sessions = []

for session_id in agent_session_ids:
    if session_id in clarification_sessions:
        performed_sessions.append(session_id)
    else:
        not_performed_sessions.append(session_id)

# 평균 메시지 수 계산
performed_message_counts = [
    session_message_counts.get(sid, 0) 
    for sid in performed_sessions
]
not_performed_message_counts = [
    session_message_counts.get(sid, 0) 
    for sid in not_performed_sessions
]

performed_avg_messages = sum(performed_message_counts) / len(performed_message_counts) if performed_message_counts else 0
not_performed_avg_messages = sum(not_performed_message_counts) / len(not_performed_message_counts) if not_performed_message_counts else 0

# 비율 계산
total_agent = len(agent_session_ids)
performed_count = len(performed_sessions)
not_performed_count = len(not_performed_sessions)
performed_pct = (performed_count / total_agent * 100) if total_agent > 0 else 0
not_performed_pct = (not_performed_count / total_agent * 100) if total_agent > 0 else 0

print(f"명료화 수행: {performed_count}개 ({performed_pct:.1f}%), 평균 메시지 {performed_avg_messages:.1f}개")
print(f"명료화 미수행: {not_performed_count}개 ({not_performed_pct:.1f}%), 평균 메시지 {not_performed_avg_messages:.1f}개")
print()

# 결과 저장
results = {
    "table": "표Ⅴ-2",
    "title": "명료화 수행 현황",
    "agent_total_sessions": int(total_agent),
    "clarification_performed": {
        "count": int(performed_count),
        "percentage": round(performed_pct, 1),
        "avg_messages": round(performed_avg_messages, 1)
    },
    "clarification_not_performed": {
        "count": int(not_performed_count),
        "percentage": round(not_performed_pct, 1),
        "avg_messages": round(not_performed_avg_messages, 1)
    },
    "data_files": [
        str(DB_LOGS_FILE.relative_to(BASE_DIR)),
        str(SESSION_FILE.relative_to(BASE_DIR))
    ],
    "method": "DB 로그(llm_prompt_logs)에서 classifier_llm/question_improver_llm 호출 여부로 판단"
}

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ch5_1_r_clarification_operation.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✓ 결과 저장: {output_file}")
print("="*80)

