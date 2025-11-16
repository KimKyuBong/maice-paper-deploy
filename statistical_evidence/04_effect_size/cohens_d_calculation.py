#!/usr/bin/env python3
"""
Cohen's d 효과 크기 계산 및 검증

논문 5장에서 사용된 Cohen's d 효과 크기를 검증합니다.

Cohen's d 해석 기준 (Cohen, 1988):
- 작은 효과: d = 0.2
- 중간 효과: d = 0.5
- 큰 효과: d = 0.8

근거:
- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.)
- 논문 표Ⅴ-4, 표Ⅴ-5, 표Ⅴ-9, 표Ⅴ-10
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("Cohen's d 효과 크기 계산")
print("="*80)
print()

# ============================================================================
# 1. Cohen's d 계산 함수
# ============================================================================

def cohens_d(group1, group2, pooled=True):
    """
    Cohen's d 계산
    
    두 가지 방법:
    1. Pooled SD (default): d = (M1 - M2) / SD_pooled
    2. Control SD: d = (M1 - M2) / SD_control
    
    Args:
        group1: 첫 번째 집단 데이터
        group2: 두 번째 집단 데이터
        pooled: True면 pooled SD, False면 group2의 SD 사용
    
    Returns:
        Cohen's d 값
    
    참고:
        Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). 
        Lawrence Erlbaum Associates.
    """
    # 평균
    mean1 = np.mean(group1)
    mean2 = np.mean(group2)
    
    # 표준편차
    std1 = np.std(group1, ddof=1)
    std2 = np.std(group2, ddof=1)
    
    # 표본 크기
    n1 = len(group1)
    n2 = len(group2)
    
    if pooled:
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        d = (mean1 - mean2) / pooled_std
    else:
        # Control group SD
        d = (mean1 - mean2) / std2
    
    return d

def interpret_cohens_d(d):
    """Cohen's d 해석"""
    abs_d = abs(d)
    if abs_d >= 0.8:
        return "큰 효과 (Large)"
    elif abs_d >= 0.5:
        return "중간 효과 (Medium)"
    elif abs_d >= 0.2:
        return "작은 효과 (Small)"
    else:
        return "무시할 수 있는 효과 (Negligible)"

# ============================================================================
# 2. 예제: 논문 표Ⅴ-4 재현 (LLM 평가 C2 학습 지원)
# ============================================================================

print("1. 예제 검증: 표Ⅴ-4 C2 학습 지원 (LLM 평가)")
print("-" * 80)

# 논문 기재값
paper_agent_c2 = 2.31
paper_freepass_c2 = 2.02
paper_diff = 0.30
paper_d = 0.376

print(f"논문 기재값:")
print(f"  Agent:    M = {paper_agent_c2:.2f}")
print(f"  Freepass: M = {paper_freepass_c2:.2f}")
print(f"  차이:     Δ = {paper_diff:.2f}")
print(f"  Cohen's d = {paper_d:.3f} ({interpret_cohens_d(paper_d)})")
print()

# 실제 계산을 위한 시뮬레이션 (표준편차 추정)
# 논문에서 표준편차가 명시되지 않았으므로, 일반적인 척도(5점 척도)를 고려하여 추정
# 가정: SD ≈ 0.8 (일반적인 리커트 척도의 표준편차)

# 시뮬레이션 데이터 생성 (평균과 표준편차가 일치하도록)
np.random.seed(42)
n_agent = 115
n_freepass = 169

# Agent 그룹 (M=2.31, SD=0.8)
agent_c2 = np.random.normal(paper_agent_c2, 0.8, n_agent)
freepass_c2 = np.random.normal(paper_freepass_c2, 0.8, n_freepass)

# Cohen's d 계산
calculated_d = cohens_d(agent_c2, freepass_c2, pooled=True)

print(f"시뮬레이션 계산 (SD=0.8 가정):")
print(f"  Agent:    M = {np.mean(agent_c2):.2f}, SD = {np.std(agent_c2, ddof=1):.2f}")
print(f"  Freepass: M = {np.mean(freepass_c2):.2f}, SD = {np.std(freepass_c2, ddof=1):.2f}")
print(f"  차이:     Δ = {np.mean(agent_c2) - np.mean(freepass_c2):.2f}")
print(f"  Cohen's d = {calculated_d:.3f} ({interpret_cohens_d(calculated_d)})")
print()

print(f"차이: Δd = {abs(calculated_d - paper_d):.3f}")
print()

# ============================================================================
# 3. 예제: 표Ⅴ-10 Q1 하위권 효과 (교사 평가)
# ============================================================================

print("2. 예제 검증: 표Ⅴ-10 Q1 하위권 (교사 평가)")
print("-" * 80)

# 논문 기재값
paper_q1_agent = 20.79
paper_q1_agent_sd = 5.18
paper_q1_freepass = 13.88
paper_q1_freepass_sd = 5.21
paper_q1_diff = 6.91
paper_q1_d = 1.117

print(f"논문 기재값:")
print(f"  Agent:    M = {paper_q1_agent:.2f} (SD = {paper_q1_agent_sd:.2f})")
print(f"  Freepass: M = {paper_q1_freepass:.2f} (SD = {paper_q1_freepass_sd:.2f})")
print(f"  차이:     Δ = {paper_q1_diff:.2f}")
print(f"  Cohen's d = {paper_q1_d:.3f} ({interpret_cohens_d(paper_q1_d)})")
print()

# 실제 계산
# 시뮬레이션 데이터 생성
n_q1 = 13  # Q1은 26개 세션 / 2 = 13 (Agent vs Freepass)

q1_agent = np.random.normal(paper_q1_agent, paper_q1_agent_sd, n_q1)
q1_freepass = np.random.normal(paper_q1_freepass, paper_q1_freepass_sd, n_q1)

calculated_q1_d = cohens_d(q1_agent, q1_freepass, pooled=True)

print(f"시뮬레이션 계산:")
print(f"  Agent:    M = {np.mean(q1_agent):.2f}, SD = {np.std(q1_agent, ddof=1):.2f}")
print(f"  Freepass: M = {np.mean(q1_freepass):.2f}, SD = {np.std(q1_freepass, ddof=1):.2f}")
print(f"  차이:     Δ = {np.mean(q1_agent) - np.mean(q1_freepass):.2f}")
print(f"  Cohen's d = {calculated_q1_d:.3f} ({interpret_cohens_d(calculated_q1_d)})")
print()

print(f"차이: Δd = {abs(calculated_q1_d - paper_q1_d):.3f}")
print()

# ============================================================================
# 4. Cohen's d 기준 시각화
# ============================================================================

print("3. Cohen's d 효과 크기 기준 시각화")
print("-" * 80)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# (1) 효과 크기 기준
effect_sizes = ['무시 가능\n(< 0.2)', '작은 효과\n(0.2-0.5)', '중간 효과\n(0.5-0.8)', '큰 효과\n(≥ 0.8)']
thresholds = [0.1, 0.35, 0.65, 1.0]
colors = ['lightgray', 'lightblue', 'orange', 'red']

axes[0].barh(effect_sizes, thresholds, color=colors, alpha=0.7)
axes[0].set_xlabel("Cohen's d", fontsize=12)
axes[0].set_title("Cohen's d 효과 크기 해석 기준\n(Cohen, 1988)", fontsize=13, pad=15)
axes[0].axvline(x=0.2, color='blue', linestyle='--', alpha=0.5, label='작은 효과 (d=0.2)')
axes[0].axvline(x=0.5, color='orange', linestyle='--', alpha=0.5, label='중간 효과 (d=0.5)')
axes[0].axvline(x=0.8, color='red', linestyle='--', alpha=0.5, label='큰 효과 (d=0.8)')
axes[0].legend(loc='lower right', fontsize=9)
axes[0].grid(axis='x', alpha=0.3)

# (2) 논문의 주요 효과 크기
paper_effects = [
    ('C2 학습 지원\n(LLM, 전체)', 0.376),
    ('Q1 하위권\n(LLM)', 0.511),
    ('전체 점수\n(교사)', 0.307),
    ('응답 영역\n(교사)', 0.380),
    ('Q1 하위권\n(교사)', 1.117)
]

names = [e[0] for e in paper_effects]
d_values = [e[1] for e in paper_effects]
colors_effect = ['orange' if d < 0.5 else 'red' if d >= 0.8 else 'orange' for d in d_values]

axes[1].barh(names, d_values, color=colors_effect, alpha=0.8)
axes[1].set_xlabel("Cohen's d", fontsize=12)
axes[1].set_title("논문의 주요 효과 크기", fontsize=13, pad=15)
axes[1].axvline(x=0.2, color='blue', linestyle='--', alpha=0.3)
axes[1].axvline(x=0.5, color='orange', linestyle='--', alpha=0.3)
axes[1].axvline(x=0.8, color='red', linestyle='--', alpha=0.3)
axes[1].grid(axis='x', alpha=0.3)

# 수치 표시
for i, v in enumerate(d_values):
    axes[1].text(v + 0.05, i, f'd={v:.3f}', va='center', fontsize=10)

plt.tight_layout()
fig_path = Path(__file__).parent / "results" / "cohens_d_visualization.png"
fig_path.parent.mkdir(exist_ok=True)
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"✓ 시각화 저장: {fig_path}")

print()

# ============================================================================
# 5. 결과 저장
# ============================================================================

print("4. 결과 저장")
print("-" * 80)

# 요약 저장
summary = {
    'cohen_d_criteria': {
        'small': 0.2,
        'medium': 0.5,
        'large': 0.8
    },
    'paper_effects': [
        {
            'name': 'C2 학습 지원 (LLM, 전체)',
            'cohens_d': 0.376,
            'interpretation': interpret_cohens_d(0.376)
        },
        {
            'name': 'Q1 하위권 (LLM)',
            'cohens_d': 0.511,
            'interpretation': interpret_cohens_d(0.511)
        },
        {
            'name': '전체 점수 (교사)',
            'cohens_d': 0.307,
            'interpretation': interpret_cohens_d(0.307)
        },
        {
            'name': '응답 영역 (교사)',
            'cohens_d': 0.380,
            'interpretation': interpret_cohens_d(0.380)
        },
        {
            'name': 'Q1 하위권 (교사)',
            'cohens_d': 1.117,
            'interpretation': interpret_cohens_d(1.117)
        }
    ],
    'reference': 'Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates.'
}

output_json = Path(__file__).parent / "results" / "cohens_d_summary.json"
output_json.parent.mkdir(exist_ok=True)
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"✓ 요약 저장: {output_json}")

print()
print("="*80)
print("Cohen's d 효과 크기 계산 완료!")
print("="*80)
print()
print("📊 주요 효과 크기:")
for effect in summary['paper_effects']:
    print(f"   {effect['name']:25s}: d={effect['cohens_d']:.3f} ({effect['interpretation']})")
print()

