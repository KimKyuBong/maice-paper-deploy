#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAICE 학생 설문조사 모드별 분석 (N=47) - 최종 버전
- 불명확한 응답 제외
- Agent vs Freepass 모드별 설문 결과 비교
- 2025-11-13
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
survey_path = Path(__file__).parent.parent / "data" / "MAICE 사용 설문조사 (2025학년도 2학년 수학)(1-47).csv"
session_path = Path(__file__).parent.parent / "data" / "session_data" / "full_sessions_with_scores.csv"

survey_df = pd.read_csv(survey_path)
session_df = pd.read_csv(session_path)

print("="*100)
print("MAICE 학생 설문조사 모드별 분석 (N=47) - 최종 버전")
print("불명확한 응답 제외")
print("="*100)

# 세션 데이터에서 학생별 모드 정보 추출
# username 컬럼 사용 (전자 메일 형식: 24.001@bssm.hs.kr)
session_df['username_clean'] = session_df['username'].astype(str).str.split('@').str[0]
student_mode = session_df.groupby('username_clean')['mode'].first().reset_index()
student_mode.columns = ['username_clean', 'assigned_mode']

# 설문 데이터의 전자 메일에서 username 추출
survey_df['username_clean'] = survey_df['전자 메일'].astype(str).str.split('@').str[0]

# 설문 데이터와 모드 정보 병합
survey_with_mode = survey_df.merge(student_mode, on='username_clean', how='left')

# 수동 분류 매핑 (불명확 제외)
preference_mapping = {
    # Agent 모드
    2: 'B', 4: 'B', 5: 'B', 6: 'B', 9: 'B', 11: 'B',
    14: 'A', 15: 'B', 16: 'B', 18: 'UNKNOWN',  # 불명확
    23: 'MIXED', 24: 'A', 25: 'B', 29: 'B', 31: 'A', 33: 'B',
    36: 'UNKNOWN', 37: 'UNKNOWN',  # 불명확
    38: 'A', 39: 'MIXED', 40: 'B', 44: 'B', 47: 'B',
    
    # Freepass 모드
    1: 'B', 3: 'A', 7: 'B', 8: 'B', 10: 'A', 12: 'B', 13: 'A',
    17: 'A', 19: 'B', 20: 'A', 21: 'MIXED', 22: 'A', 26: 'MIXED',
    27: 'B', 28: 'B', 32: 'B', 34: 'A', 35: 'B', 41: 'B',
    42: 'B', 43: 'MIXED', 45: 'B', 46: 'A',
}

mode_col = '두 답변 방식 중 어떤 방식이 더 좋아요?\xa0어떤 걸 선택했는지, 왜 그렇게 생각하는지 자세히 써주세요'
survey_with_mode['preference'] = survey_with_mode['ID'].map(preference_mapping)

# 불명확한 응답 제외
valid_survey = survey_with_mode[survey_with_mode['preference'] != 'UNKNOWN'].copy()

print(f"\n전체 응답자: {len(survey_with_mode)}명")
print(f"불명확 응답 제외: {len(survey_with_mode[survey_with_mode['preference'] == 'UNKNOWN'])}명")
print(f"유효 응답자: {len(valid_survey)}명")

# 모드별 통계
print(f"\n모드별 응답자 수 (불명확 제외):")
mode_counts = valid_survey['assigned_mode'].value_counts()
print(mode_counts)

# 모드별 선호도 집계
print("\n" + "="*100)
print("1. 모드별 A/B 방식 선호도 (불명확 제외)")
print("="*100)

for mode in ['agent', 'freepass']:
    mode_df = valid_survey[valid_survey['assigned_mode'] == mode]
    pref_counts = mode_df['preference'].value_counts()
    
    print(f"\n【{mode.upper()} 모드 (N={len(mode_df)})】")
    total = len(mode_df)
    a_count = pref_counts.get('A', 0)
    b_count = pref_counts.get('B', 0)
    mixed_count = pref_counts.get('MIXED', 0)
    
    print(f"  A 방식 선호: {a_count}명 ({a_count/total*100:.1f}%)")
    print(f"  B 방식 선호: {b_count}명 ({b_count/total*100:.1f}%)")
    print(f"  혼합 선호: {mixed_count}명 ({mixed_count/total*100:.1f}%)")
    
    # B 방식 선호 비율 (A+B만, 혼합 제외)
    valid_total = a_count + b_count
    if valid_total > 0:
        b_ratio = b_count / valid_total * 100
        print(f"  → B 방식 선호 비율 (A+B만): {b_ratio:.1f}%")
        print(f"  → A 방식 선호 비율 (A+B만): {100-b_ratio:.1f}%")

# 전체 통계
print("\n" + "="*100)
print("2. 전체 선호도 통계 (불명확 제외)")
print("="*100)

total_pref = valid_survey['preference'].value_counts()
total_n = len(valid_survey)
a_total = total_pref.get('A', 0)
b_total = total_pref.get('B', 0)
mixed_total = total_pref.get('MIXED', 0)

print(f"\n전체 (N={total_n}):")
print(f"  A 방식 선호: {a_total}명 ({a_total/total_n*100:.1f}%)")
print(f"  B 방식 선호: {b_total}명 ({b_total/total_n*100:.1f}%)")
print(f"  혼합 선호: {mixed_total}명 ({mixed_total/total_n*100:.1f}%)")

valid_total = a_total + b_total
if valid_total > 0:
    b_ratio_total = b_total / valid_total * 100
    print(f"  → B 방식 선호 비율 (A+B만): {b_ratio_total:.1f}%")

# 점수 관련 컬럼 정의
score_questions = {
    '메타인지_모르는지알게됨': ' AI와 대화하면서 내가 뭘 모르는지 정확히 알게 됐다',
    '메타인지_혼자풀수있음': 'AI와 대화하다 보니 문제를 혼자 힘으로 풀 수 있었다',
    '메타인지_다음질문알게됨': 'AI와 대화한 뒤 다음엔 뭘 물어봐야 할지 알게 됐다',
    'AI상호작용_이해잘함': 'AI가 내가 묻고 싶은 걸 잘 이해해줬다',
    'AI상호작용_도움충분': 'AI가 공부하는 데 충분히 도움을 줬다',
    '질문능력_분명하게말함': '질문할 때 내가 뭘 알고 싶은지 분명하게 말한다',
    '질문능력_상황설명함': '질문할 때 "나는 지금 이런 상황이야"라고 설명도 같이 한다',
    '자기조절_모르는지앎': '공부할 때 내가 뭘 모르는지 정확히 안다',
    '자기조절_질문만듦': '어려운 내용이 나오면 스스로 질문을 만들어본다',
    '개념이해_귀납법구조': ' 수학적 귀납법을 이용한 증명이 어떻게 구성되는지 이해했다',
    '개념이해_귀납가정': '귀납 가정을 어떻게 써서 증명하는지 안다',
    '개념이해_자기검증': '내가 쓴 증명이 맞는지 스스로 확인할 수 있다',
    '시스템_도움됨': 'MAICE가 수학 공부에 도움이 됐다',
    '시스템_쉬움': 'MAICE는\xa0사용하기 쉬웠다',
    '시스템_계속쓰고싶음': '앞으로도 MAICE를 계속\xa0쓰고 싶다'
}

categories = {
    '메타인지 효과': [k for k in score_questions.keys() if k.startswith('메타인지')],
    'AI 상호작용 품질': [k for k in score_questions.keys() if k.startswith('AI상호작용')],
    '질문 능력': [k for k in score_questions.keys() if k.startswith('질문능력')],
    '자기조절 학습': [k for k in score_questions.keys() if k.startswith('자기조절')],
    '개념 이해': [k for k in score_questions.keys() if k.startswith('개념이해')],
    '시스템 만족도': [k for k in score_questions.keys() if k.startswith('시스템')]
}

# 모드별 카테고리 분석 (불명확 제외)
print("\n" + "="*100)
print("3. 모드별 카테고리 평균 점수 비교 (불명확 제외)")
print("="*100)

mode_comparison = []
for cat_name, items in categories.items():
    agent_scores = []
    freepass_scores = []
    
    agent_df = valid_survey[valid_survey['assigned_mode'] == 'agent']
    freepass_df = valid_survey[valid_survey['assigned_mode'] == 'freepass']
    
    for item_key in items:
        question = score_questions[item_key]
        if question in valid_survey.columns:
            agent = pd.to_numeric(agent_df[question], errors='coerce').dropna()
            freepass = pd.to_numeric(freepass_df[question], errors='coerce').dropna()
            agent_scores.extend(agent.tolist())
            freepass_scores.extend(freepass.tolist())
    
    if agent_scores and freepass_scores:
        agent_mean = np.mean(agent_scores)
        freepass_mean = np.mean(freepass_scores)
        diff = agent_mean - freepass_mean
        
        t_stat, p_value = stats.ttest_ind(agent_scores, freepass_scores)
        pooled_std = np.sqrt((np.var(agent_scores) + np.var(freepass_scores)) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0
        
        mode_comparison.append({
            '카테고리': cat_name,
            'Agent 평균': agent_mean,
            'Freepass 평균': freepass_mean,
            '차이': diff,
            't': t_stat,
            'p': p_value,
            "Cohen's d": cohens_d,
            'Agent N': len(agent_scores),
            'Freepass N': len(freepass_scores)
        })

comparison_df = pd.DataFrame(mode_comparison)
comparison_df = comparison_df.sort_values('차이', ascending=False)

print("\n카테고리별 모드 비교:")
print(comparison_df.to_string(index=False))

# 유의한 차이
print("\n【유의한 차이 (p < 0.05)】")
significant = comparison_df[comparison_df['p'] < 0.05]
if len(significant) > 0:
    print(significant[['카테고리', 'Agent 평균', 'Freepass 평균', '차이', 'p', "Cohen's d"]].to_string(index=False))
else:
    print("  없음")

# 시각화
print("\n" + "="*100)
print("4. 시각화 생성")
print("="*100)

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

# 1. 모드별 선호도 비교
ax1 = fig.add_subplot(gs[0, 0])
modes = ['Agent', 'Freepass']
a_counts = []
b_counts = []
mixed_counts = []

for mode in ['agent', 'freepass']:
    mode_df = valid_survey[valid_survey['assigned_mode'] == mode]
    pref_counts = mode_df['preference'].value_counts()
    a_counts.append(pref_counts.get('A', 0))
    b_counts.append(pref_counts.get('B', 0))
    mixed_counts.append(pref_counts.get('MIXED', 0))

x_pos = np.arange(len(modes))
width = 0.25

bars1 = ax1.bar(x_pos - width, a_counts, width, label='A 방식 (즉시 답변)', 
               color='#FF9999', alpha=0.9, edgecolor='darkred', linewidth=1.5)
bars2 = ax1.bar(x_pos, b_counts, width, label='B 방식 (질문 유도)', 
               color='#66B2FF', alpha=0.9, edgecolor='navy', linewidth=1.5)
bars3 = ax1.bar(x_pos + width, mixed_counts, width, label='혼합', 
               color='#FFD700', alpha=0.9, edgecolor='darkorange', linewidth=1.5)

ax1.set_xticks(x_pos)
ax1.set_xticklabels(modes, fontsize=12, fontweight='bold')
ax1.set_ylabel('응답자 수', fontsize=11, fontweight='bold')
ax1.set_title('모드별 A/B 방식 선호도 (불명확 제외)', fontsize=13, fontweight='bold', pad=15)
ax1.legend(fontsize=10, loc='upper left')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# 값 표시
for bars, values in [(bars1, a_counts), (bars2, b_counts), (bars3, mixed_counts)]:
    for bar, val in zip(bars, values):
        if val > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., val + 0.3,
                    f'{val}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

# 2. B 방식 선호 비율 (A+B만)
ax2 = fig.add_subplot(gs[0, 1])
b_ratios = []
for mode in ['agent', 'freepass']:
    mode_df = valid_survey[valid_survey['assigned_mode'] == mode]
    pref_counts = mode_df['preference'].value_counts()
    a_count = pref_counts.get('A', 0)
    b_count = pref_counts.get('B', 0)
    total = a_count + b_count
    if total > 0:
        b_ratios.append(b_count / total * 100)
    else:
        b_ratios.append(0)

bars = ax2.bar(modes, b_ratios, color=['#66B2FF', '#FF9999'], alpha=0.8, 
              edgecolor='black', linewidth=2)
ax2.set_ylabel('B 방식 선호 비율 (%)', fontsize=11, fontweight='bold')
ax2.set_title('B 방식 선호 비율 (A+B만, 혼합 제외)', fontsize=12, fontweight='bold', pad=15)
ax2.set_ylim(0, 100)
ax2.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# 값 표시
for bar, val in zip(bars, b_ratios):
    ax2.text(bar.get_x() + bar.get_width()/2., val + 2,
            f'{val:.1f}%', ha='center', va='bottom',
            fontsize=12, fontweight='bold')

# 3. 카테고리별 모드 비교
ax3 = fig.add_subplot(gs[1, :])
x_pos = np.arange(len(comparison_df))
width = 0.35

bars1 = ax3.bar(x_pos - width/2, comparison_df['Agent 평균'], width,
               label='Agent 모드', color='#66B2FF', alpha=0.9, edgecolor='navy', linewidth=1.5)
bars2 = ax3.bar(x_pos + width/2, comparison_df['Freepass 평균'], width,
               label='Freepass 모드', color='#FF9999', alpha=0.9, edgecolor='darkred', linewidth=1.5)

ax3.set_xticks(x_pos)
ax3.set_xticklabels(comparison_df['카테고리'], rotation=25, ha='right', fontsize=10)
ax3.set_ylabel('평균 점수 (5점 척도)', fontsize=11, fontweight='bold')
ax3.set_title('카테고리별 모드 비교 (불명확 제외)', fontsize=13, fontweight='bold', pad=15)
ax3.legend(fontsize=11, loc='upper right')
ax3.set_ylim(3.5, 5.5)
ax3.axhline(y=4.0, color='red', linestyle='--', alpha=0.4, linewidth=1.5)
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# 값 표시
for bars, means in [(bars1, comparison_df['Agent 평균']), (bars2, comparison_df['Freepass 평균'])]:
    for bar, val in zip(bars, means):
        ax3.text(bar.get_x() + bar.get_width()/2., val + 0.05,
                f'{val:.2f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')

plt.suptitle('MAICE 학생 설문조사 모드별 분석 결과 (N=44, 불명확 제외)',
            fontsize=15, fontweight='bold', y=0.98)

output_dir = Path(__file__).parent / "results"
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "survey_47_mode_comparison_final.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ 시각화 저장 완료: {output_path}")

# 결과를 CSV로 저장
summary = []
for mode in ['agent', 'freepass']:
    mode_df = valid_survey[valid_survey['assigned_mode'] == mode]
    pref_counts = mode_df['preference'].value_counts()
    a_count = pref_counts.get('A', 0)
    b_count = pref_counts.get('B', 0)
    mixed_count = pref_counts.get('MIXED', 0)
    total = len(mode_df)
    valid_total = a_count + b_count
    
    summary.append({
        '모드': mode.upper(),
        '총 응답자': total,
        'A 방식 선호': a_count,
        'B 방식 선호': b_count,
        '혼합': mixed_count,
        'B 방식 비율 (전체)': f"{b_count/total*100:.1f}%",
        'B 방식 비율 (A+B만)': f"{b_count/valid_total*100:.1f}%" if valid_total > 0 else "N/A"
    })

summary_df = pd.DataFrame(summary)
summary_path = output_dir / "survey_47_mode_preference_final.csv"
summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
print(f"✓ 모드별 선호도 요약 저장: {summary_path}")

comparison_path = output_dir / "survey_47_mode_comparison_final.csv"
comparison_df.to_csv(comparison_path, index=False, encoding='utf-8-sig')
print(f"✓ 모드 비교 결과 저장: {comparison_path}")

print("\n" + "="*100)
print("분석 완료!")
print("="*100)




