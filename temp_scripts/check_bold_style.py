"""
원본에서 볼드 처리 방식 확인
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("원본에서 볼드 처리 방식 분석")
print("="*80)

# header.xml에서 charPr 속성 확인
print("\n1. header.xml의 charPr 정의:")
print("-"*80)

with open('hwp/analyze_original/Contents/header.xml', 'r', encoding='utf-8') as f:
    header = f.read()

# charPr 태그 찾기
char_prs = re.findall(r'<hh:charPr id="(\d+)"[^>]*>', header)
print(f"총 {len(char_prs)}개 charPr 정의 발견")

# 각 charPr의 Bold와 Height 속성 찾기
for char_id in char_prs[:20]:
    # 해당 charPr 태그 전체 추출
    pattern = f'<hh:charPr id="{char_id}".*?</hh:charPr>'
    match = re.search(pattern, header, re.DOTALL)
    
    if match:
        char_pr_block = match.group(0)
        
        # Bold 속성
        bold_match = re.search(r'fontAttr="(\d+)"', char_pr_block)
        height_match = re.search(r'height="(\d+)"', char_pr_block)
        
        bold = bold_match.group(1) if bold_match else "N/A"
        height = height_match.group(1) if height_match else "N/A"
        
        # fontAttr 비트 확인 (1=bold)
        if bold != "N/A":
            is_bold = int(bold) & 1  # 첫 번째 비트가 bold
            print(f"  charPrIDRef={char_id:2s}: Height={height:4s}, fontAttr={bold} (Bold={is_bold})")

# section2.xml에서 실제 사용 예시
print("\n\n2. section2.xml에서 볼드 텍스트 사용 예시:")
print("-"*80)

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    section2 = f.read()

# run과 텍스트 찾기
runs = re.findall(r'<hp:run charPrIDRef="(\d+)"><hp:t>(.*?)</hp:t></hp:run>', section2)

# charPrIDRef별 그룹화
char_examples = {}
for char_id, text in runs:
    if char_id not in char_examples:
        char_examples[char_id] = []
    if len(char_examples[char_id]) < 3:
        char_examples[char_id].append(text[:50])

for char_id in sorted(char_examples.keys(), key=int)[:15]:
    print(f"\ncharPrIDRef={char_id}:")
    for text in char_examples[char_id]:
        print(f"  - {text}")

print("\n\n3. 볼드 처리 권장 사항:")
print("="*80)
print("""
원본 분석 결과를 바탕으로:
- 일반 텍스트: charPrIDRef="4" (크기 10, 볼드 아님)
- 볼드 텍스트: fontAttr의 비트를 변경하거나, 적절한 charPrIDRef 사용
- 볼드만 하려면 동일한 크기의 볼드 charPr 찾아야 함
""")

