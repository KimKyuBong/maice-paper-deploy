#!/usr/bin/env python3
"""
3개 LLM 모델의 세부항목(A1~C2) + 총점 완전 추출
JSONL에서 정규식으로 직접 파싱

출력: llm_3models_284sessions_COMPLETE.csv
- session_id
- gemini_A1, gemini_A2, ..., gemini_C2, gemini_total
- anthropic_A1, anthropic_A2, ..., anthropic_C2, anthropic_total
- openai_A1, openai_A2, ..., openai_C2, openai_total
- avg_A1, avg_A2, ..., avg_C2, avg_total
"""

import json
import re
import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("3개 모델 세부항목 + 총점 완전 추출")
print("=" * 80)

# 파일 경로
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'analysis' / 'threemodel'

files = {
    'gemini': DATA_DIR / 'gemini_results_20251105_174045.jsonl',
    'anthropic': DATA_DIR / 'anthropic_haiku45_results_20251105.jsonl',
    'openai': DATA_DIR / 'openai_gpt5mini_results_20251105.jsonl'
}

def parse_jsonl_with_items(file_path, model_name):
    """JSONL에서 세부항목 + 총점 추출 (스크립트 방식)"""
    results = []
    failed = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                
                # 세션 ID 추출 (모델별로 다름)
                if model_name == 'gemini':
                    custom_id = data.get('metadata', {}).get('key', '')
                else:
                    custom_id = data.get('custom_id', '')
                
                session_id = custom_id.replace('session_', '')
                
                if not session_id:
                    failed += 1
                    continue
                
                # 응답 텍스트 추출 (모델별로 다름)
                text = None
                
                if model_name == 'gemini':
                    response = data.get('response', {})
                    candidates = response.get('candidates', [])
                    if isinstance(candidates, list) and len(candidates) > 0:
                        text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    else:
                        text = ''
                
                elif model_name == 'anthropic':
                    content = data.get('result', {}).get('message', {}).get('content', [])
                    if isinstance(content, list) and len(content) > 0:
                        text = content[0].get('text', '')
                    else:
                        text = str(content)
                
                elif model_name == 'openai':
                    body = data.get('response', {}).get('body', {})
                    if 'choices' in body:
                        content = body.get('choices', [])
                        if isinstance(content, list) and len(content) > 0:
                            text = content[0].get('message', {}).get('content', '')
                        else:
                            text = ''
                    else:
                        text = str(body)
                
                if not text:
                    failed += 1
                    continue
                
                # JSON 코드 블록 제거
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*$', '', text)
                text = text.strip()
                
                # 8개 항목 점수 추출
                item_mapping = [
                    ('A1', 'A1_math_expertise'),
                    ('A2', 'A2_question_structure'),
                    ('A3', 'A3_learning_context'),
                    ('B1', 'B1_learner_customization'),
                    ('B2', 'B2_explanation_systematicity'),
                    ('B3', 'B3_learning_expandability'),
                    ('C1', 'C1_dialogue_coherence'),
                    ('C2', 'C2_learning_support')
                ]
                
                total_40 = 0
                item_scores = {'session_id': session_id}
                
                for item_key, full_name in item_mapping:
                    # 항목 영역 찾기
                    start_pattern = f'"{full_name}"'
                    start_pos = text.find(start_pattern)
                    
                    if start_pos == -1:
                        # 항목 못 찾으면 최소점수
                        item_scores[item_key] = 1
                        total_40 += 1
                        continue
                    
                    # 다음 항목 위치 찾기
                    next_pos = len(text)
                    for _, next_name in item_mapping:
                        if next_name == full_name:
                            continue
                        pos = text.find(f'"{next_name}"', start_pos + 10)
                        if pos != -1 and pos < next_pos:
                            next_pos = pos
                    
                    # 항목 텍스트 추출
                    item_text = text[start_pos:next_pos]
                    
                    # value 값 추출 (정확히 4개)
                    values = re.findall(r'"value"\s*:\s*(\d+)', item_text)
                    checked_count = sum(int(v) for v in values[:4])  # 최대 4개만
                    score = checked_count + 1  # 0개=1점, 1개=2점, ..., 4개=5점
                    
                    item_scores[item_key] = score
                    total_40 += score
                
                item_scores['total'] = total_40
                results.append(item_scores)
                
            except Exception as e:
                failed += 1
                continue
    
    df = pd.DataFrame(results)
    print(f"  {model_name:12}: {len(df):3}개 파싱 성공, {failed:3}개 실패")
    
    return df

# 각 모델 파싱
print("\n파싱 중...")
df_gemini = parse_jsonl_with_items(files['gemini'], 'gemini')
df_anthropic = parse_jsonl_with_items(files['anthropic'], 'anthropic')
df_openai = parse_jsonl_with_items(files['openai'], 'openai')

# 컬럼명에 모델명 prefix 추가
item_cols = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'total']

df_gemini = df_gemini.rename(columns={col: f'gemini_{col}' for col in item_cols})
df_anthropic = df_anthropic.rename(columns={col: f'anthropic_{col}' for col in item_cols})
df_openai = df_openai.rename(columns={col: f'openai_{col}' for col in item_cols})

# 병합
df_merged = df_gemini.merge(df_anthropic, on='session_id', how='outer')
df_merged = df_merged.merge(df_openai, on='session_id', how='outer')

# session_id를 숫자로 변환하여 정렬
df_merged['session_id'] = pd.to_numeric(df_merged['session_id'])
df_merged = df_merged.sort_values('session_id').reset_index(drop=True)

print(f"\n병합 완료: {len(df_merged)} 세션")

# 3개 모델 평균 계산
items = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'total']

for item in items:
    cols = [f'gemini_{item}', f'anthropic_{item}', f'openai_{item}']
    df_merged[f'avg_{item}'] = df_merged[cols].mean(axis=1)

# 컬럼 순서 정리
col_order = ['session_id']

# 항목별로 gemini, anthropic, openai, avg 순서
for item in ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2']:
    col_order.extend([f'gemini_{item}', f'anthropic_{item}', f'openai_{item}', f'avg_{item}'])

# 총점
col_order.extend(['gemini_total', 'anthropic_total', 'openai_total', 'avg_total'])

df_final = df_merged[col_order]

# 저장
output_file = BASE_DIR / 'statistical_evidence' / 'data' / 'llm_evaluations' / 'llm_3models_284sessions_COMPLETE.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ 저장 완료!")
print(f"   파일: {output_file.name}")
print(f"   경로: {output_file.parent}")

print(f"\n📊 데이터 구조:")
print(f"   세션 수: {len(df_final)}")
print(f"   컬럼 수: {len(df_final.columns)}")

print(f"\n컬럼 구성:")
print(f"   - session_id: 1개")
print(f"   - 세부항목 (A1~C2): 8개 × 4 (gemini, anthropic, openai, avg) = 32개")
print(f"   - 총점 (total): 1개 × 4 = 4개")
print(f"   - 합계: 37개 컬럼")

print(f"\n첫 3개 세션 (총점만):")
print(df_final[['session_id', 'gemini_total', 'anthropic_total', 'openai_total', 'avg_total']].head(3))

print(f"\n파일 경로:")
print(f"  {output_file}")

EOF

