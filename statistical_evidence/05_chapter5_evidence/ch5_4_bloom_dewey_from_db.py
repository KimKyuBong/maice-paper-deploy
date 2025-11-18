#!/usr/bin/env python3
"""
5장 4절: Bloom-Dewey 이론 실증 분석 (DB 데이터 기반)

목적: 표Ⅴ-23, Ⅴ-25, Ⅴ-26 계산용 원본 데이터 추출
- DB 로그 1,589건 확인 및 추출
- LLM 평가점수와 매칭
- Bloom/Dewey 분석을 위한 기본 데이터 제공
"""

import pandas as pd
import json
from pathlib import Path

print("="*80)
print("5장 4절: Bloom-Dewey 이론 실증 분석")
print("DB 로그 데이터 확인 및 추출")
print("="*80)
print()

BASE_DIR = Path(__file__).parent.parent

# 데이터 로드
DB_LOGS_FILE = BASE_DIR / "data" / "db_exports" / "public_llm_prompt_logs_full.csv"
DB_RESPONSE_FILE = BASE_DIR / "data" / "db_exports" / "public_llm_response_logs_full.csv"
LLM_FILE = BASE_DIR / "01_llm_scoring" / "results" / "llm_3models_averaged_perfect.csv"
SESSION_FILE = BASE_DIR / "data" / "session_data" / "full_sessions_with_scores.csv"

df_logs = pd.read_csv(DB_LOGS_FILE)
df_responses = pd.read_csv(DB_RESPONSE_FILE)
df_llm = pd.read_csv(LLM_FILE)
df_session = pd.read_csv(SESSION_FILE)

print("[1] 데이터 로드...")
print(f"✓ 프롬프트 로그: {len(df_logs)}개")
print(f"✓ 응답 로그: {len(df_responses)}개")
print(f"✓ LLM 평가: {len(df_llm)}개 세션")
print(f"✓ 세션 메타: {len(df_session)}개")
print()

# 에이전트별 분류
print("[2] 에이전트별 분류...")
if 'tool_name' in df_logs.columns:
    agent_counts = df_logs['tool_name'].value_counts()
    print("프롬프트 로그 (tool_name):")
    for agent, count in agent_counts.items():
        print(f"  - {agent}: {count:,}건")
elif 'agent_name' in df_logs.columns:
    agent_counts = df_logs['agent_name'].value_counts()
    print("프롬프트 로그 (agent_name):")
    for agent, count in agent_counts.items():
        print(f"  - {agent}: {count:,}건")
else:
    print("⚠️  tool_name/agent_name 컬럼 없음")
print()

# 총 로그 건수 확인
total_logs = len(df_logs) + len(df_responses)
print(f"총 프롬프트-응답 로그: {total_logs:,}건")
print(f"  (프롬프트: {len(df_logs):,}건 + 응답: {len(df_responses):,}건)")
print()

# 세션 ID 매칭 확인
print("[3] 세션 ID 매칭 확인...")
log_session_ids = set(df_logs['session_id'].dropna().unique())
response_session_ids = set(df_responses['session_id'].dropna().unique())
llm_session_ids = set(df_llm['session_id'].unique())
session_meta_ids = set(df_session['session_id'].unique())

common_sessions = log_session_ids & llm_session_ids & session_meta_ids
print(f"  DB 로그 세션: {len(log_session_ids)}개")
print(f"  LLM 평가 세션: {len(llm_session_ids)}개")
print(f"  세션 메타 세션: {len(session_meta_ids)}개")
print(f"  공통 세션: {len(common_sessions)}개")
print()

# 결과 저장
results = {
    "table": "표Ⅴ-23, Ⅴ-25, Ⅴ-26",
    "title": "Bloom-Dewey 이론 실증 분석 원본 데이터",
    "note": "질적 코딩 기반 분석. DB 로그를 수동으로 Bloom/Dewey 단계 코딩 필요",
    "db_logs_summary": {
        "prompt_logs": len(df_logs),
        "response_logs": len(df_responses),
        "total_logs": total_logs,
        "unique_sessions_in_logs": len(log_session_ids),
        "common_sessions_with_llm": len(common_sessions)
    },
    "agent_distribution": agent_counts.to_dict() if 'tool_name' in df_logs.columns or 'agent_name' in df_logs.columns else {},
    "data_files": {
        "prompt_logs": str(DB_LOGS_FILE.relative_to(BASE_DIR)),
        "response_logs": str(DB_RESPONSE_FILE.relative_to(BASE_DIR)),
        "llm_scores": str(LLM_FILE.relative_to(BASE_DIR)),
        "session_metadata": str(SESSION_FILE.relative_to(BASE_DIR))
    },
    "analysis_note": {
        "bloom_coding": "237건 답변(answer_generator_llm)을 Bloom 단계로 수동 코딩",
        "dewey_tracking": "대화 흐름을 Dewey 5단계로 추적 (278건 명료화 질문)",
        "score_matching": "LLM 평가점수와 대화 로그 매칭하여 점수 구간별 분석"
    }
}

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ch5_4_bloom_dewey_from_db.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

# 원본 데이터도 저장 (분석용)
df_logs_merged = pd.merge(
    df_logs,
    df_llm[['session_id', 'avg_overall']],
    on='session_id',
    how='left'
)

output_csv = OUTPUT_DIR / "llm_prompt_logs_with_scores.csv"
df_logs_merged.to_csv(output_csv, index=False, encoding='utf-8')
print(f"✓ 점수 매칭된 프롬프트 로그 저장: {output_csv}")
print()

print(f"✓ 결과 저장: {output_file}")
print()
print("📌 Bloom/Dewey 분석은 DB 로그를 질적 코딩하는 별도 프로세스가 필요합니다.")
print("="*80)


