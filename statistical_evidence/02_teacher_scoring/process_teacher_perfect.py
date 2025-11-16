#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
교사 평가 완전 분석
latest_evaluations.json -> 모든 통계 산출
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from scipy import stats
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "teacher_evaluations"
RESULTS_DIR = BASE_DIR / "02_teacher_scoring" / "results"

SOURCE_FILE = DATA_DIR / "latest_evaluations.json"

print(f"{'='*80}")
print(f"교사 평가 완전 분석")
print(f"{'='*80}")
print(f"소스: {SOURCE_FILE}")
print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# [1] 데이터 로드
print("[1] 데이터 로드...")
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✓ 총 {len(data)}개 평가 로드\n")

# [2] 데이터 변환
print("[2] 데이터 변환...")

records = []
for item in data:
    if item.get('evaluation_status') == 'completed' and item.get('overall_score') is not None:
        record = {
            'id': item['id'],
            'session_id': item['conversation_session_id'],
            'teacher_id': item['evaluated_by'],
            'student_id': item['student_id'],
            # 중분류 (3개)
            'question_professionalism': item.get('question_professionalism_score', 0),
            'question_structuring': item.get('question_structuring_score', 0),
            'question_context': item.get('question_context_application_score', 0),
            'answer_customization': item.get('answer_customization_score', 0),
            'answer_systematicity': item.get('answer_systematicity_score', 0),
            'answer_expandability': item.get('answer_expandability_score', 0),
            'context_dialogue': item.get('context_dialogue_coherence_score', 0),
            'context_support': item.get('context_learning_support_score', 0),
            # 대분류 (3개)
            'question_total': item.get('question_total_score', 0),
            'answer_total': item.get('response_total_score', 0),
            'context_total': item.get('context_total_score', 0),
            # 전체
            'overall': item.get('overall_score', 0),
            'created_at': item['created_at']
        }
        records.append(record)

df = pd.DataFrame(records)
print(f"✓ {len(df)}개 완료된 평가 추출")
print(f"✓ 유니크 세션: {df['session_id'].nunique()}개")
print(f"✓ 유니크 교사: {df['teacher_id'].nunique()}명\n")

# [3] 세션별 평균 계산
print("[3] 세션별 교사 평균 계산...")

# 수치 컬럼만 선택
score_cols = [
    'question_professionalism', 'question_structuring', 'question_context',
    'answer_customization', 'answer_systematicity', 'answer_expandability',
    'context_dialogue', 'context_support',
    'question_total', 'answer_total', 'context_total', 'overall'
]

df_avg = df.groupby('session_id')[score_cols].mean().reset_index()
df_avg.columns = ['session_id'] + [f'teacher_{col}' for col in score_cols]

print(f"✓ {len(df_avg)}개 세션의 교사 평균 점수 계산\n")

# [4] 기본 통계
print("[4] 기본 통계 계산...")

stats_data = {}
for col in score_cols:
    teacher_col = f'teacher_{col}'
    stats_data[col] = {
        'mean': float(df_avg[teacher_col].mean()),
        'std': float(df_avg[teacher_col].std()),
        'median': float(df_avg[teacher_col].median()),
        'min': float(df_avg[teacher_col].min()),
        'max': float(df_avg[teacher_col].max())
    }

print(f"✓ {len(stats_data)}개 항목 통계 완료\n")

# [5] 교사 간 신뢰도 (ICC)
print("[5] 교사 간 신뢰도 분석...")

def calculate_teacher_icc(df, session_col, score_col):
    """교사 간 ICC 계산"""
    # 세션별로 2명 이상 평가한 경우만
    session_counts = df[session_col].value_counts()
    multi_rated = session_counts[session_counts >= 2].index
    
    if len(multi_rated) == 0:
        return 0.0
    
    df_multi = df[df[session_col].isin(multi_rated)]
    
    # 피벗: 세션 × 교사
    pivot = df_multi.pivot_table(
        index=session_col,
        columns='teacher_id',
        values=score_col,
        aggfunc='first'
    )
    
    # ICC 계산
    n_sessions = pivot.shape[0]
    n_raters = pivot.notna().sum(axis=1).mean()  # 평균 평가자 수
    
    if n_sessions < 2:
        return 0.0
    
    grand_mean = pivot.values[~np.isnan(pivot.values)].mean()
    
    # Between-session variance
    session_means = pivot.mean(axis=1, skipna=True)
    ss_between = n_raters * ((session_means - grand_mean) ** 2).sum()
    df_between = n_sessions - 1
    ms_between = ss_between / df_between if df_between > 0 else 0
    
    # Within-session variance
    ss_within = 0
    for idx in pivot.index:
        row_data = pivot.loc[idx].dropna()
        if len(row_data) > 1:
            row_mean = row_data.mean()
            ss_within += ((row_data - row_mean) ** 2).sum()
    
    df_within = sum(pivot.notna().sum(axis=1) - 1)
    ms_within = ss_within / df_within if df_within > 0 else 0
    
    # ICC(2,k)
    icc = (ms_between - ms_within) / ms_between if ms_between > 0 else 0
    
    return max(0, icc)  # 음수 방지

# ICC 계산
icc_results = {}
for col in ['overall', 'question_total', 'answer_total', 'context_total']:
    icc_results[col] = calculate_teacher_icc(df, 'session_id', col)

print(f"✓ ICC 계산 완료")
print(f"  전체 ICC: {icc_results['overall']:.3f}\n")

# [6] 교사 간 상관관계
print("[6] 교사 간 상관관계...")

# 2명이 모두 평가한 세션만
session_counts = df.groupby('session_id').size()
dual_sessions = session_counts[session_counts == 2].index

if len(dual_sessions) > 0:
    df_dual = df[df['session_id'].isin(dual_sessions)]
    
    correlations = {}
    for col in ['overall', 'question_total', 'answer_total', 'context_total']:
        # 교사별로 피벗
        pivot = df_dual.pivot_table(
            index='session_id',
            columns='teacher_id',
            values=col,
            aggfunc='first'
        )
        
        if pivot.shape[1] >= 2:
            corr_matrix = pivot.corr()
            # 평균 상관계수
            corr_vals = []
            for i in range(len(corr_matrix)):
                for j in range(i+1, len(corr_matrix)):
                    corr_vals.append(corr_matrix.iloc[i, j])
            
            correlations[col] = np.mean(corr_vals) if corr_vals else 0.0
        else:
            correlations[col] = 0.0
    
    print(f"✓ {len(dual_sessions)}개 이중 평가 세션 기반 상관분석\n")
else:
    correlations = {col: 0.0 for col in ['overall', 'question_total', 'answer_total', 'context_total']}
    print(f"⚠️  이중 평가 세션 없음\n")

# [7] 결과 저장
print("[7] 결과 저장...")

# 교사 평균 점수 (필수 CSV)
avg_file = RESULTS_DIR / "teacher_averaged_scores_perfect.csv"
df_avg.to_csv(avg_file, index=False, encoding='utf-8')
print(f"✓ {avg_file.name}")

# 기본 통계
stats_file = RESULTS_DIR / "teacher_statistics_perfect.json"
with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(stats_data, f, ensure_ascii=False, indent=2)
print(f"✓ {stats_file.name}")

# ICC 신뢰도
icc_file = RESULTS_DIR / "teacher_icc_perfect.json"
with open(icc_file, 'w', encoding='utf-8') as f:
    json.dump(icc_results, f, ensure_ascii=False, indent=2)
print(f"✓ {icc_file.name}")

# 상관관계
corr_file = RESULTS_DIR / "teacher_correlations_perfect.json"
with open(corr_file, 'w', encoding='utf-8') as f:
    json.dump(correlations, f, ensure_ascii=False, indent=2)
print(f"✓ {corr_file.name}")

# 요약
summary = {
    "분석시각": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "총평가수": len(df),
    "평가세션수": len(df_avg),
    "교사수": int(df['teacher_id'].nunique()),
    "전체평균": stats_data['overall']['mean'],
    "ICC": icc_results['overall'],
    "평균상관": correlations.get('overall', 0.0)
}

summary_file = RESULTS_DIR / "teacher_summary_perfect.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ {summary_file.name}\n")

# 최종 출력
print(f"{'='*80}")
print(f"교사 평가 분석 완료!")
print(f"{'='*80}")
print(f"\n주요 결과:")
print(f"  • 총 평가 수: {len(df)}")
print(f"  • 평가 세션 수: {len(df_avg)}")
print(f"  • 참여 교사 수: {df['teacher_id'].nunique()}")
print(f"  • 전체 평균: {stats_data['overall']['mean']:.2f} (±{stats_data['overall']['std']:.2f})")
print(f"  • 질문 평균: {stats_data['question_total']['mean']:.2f}")
print(f"  • 답변 평균: {stats_data['answer_total']['mean']:.2f}")
print(f"  • 맥락 평균: {stats_data['context_total']['mean']:.2f}")
print(f"\n신뢰도:")
print(f"  • ICC (전체): {icc_results['overall']:.3f}")
print(f"  • 평균 상관: {correlations.get('overall', 0):.3f}")
print(f"\n결과 위치: {RESULTS_DIR}")
print(f"{'='*80}\n")





