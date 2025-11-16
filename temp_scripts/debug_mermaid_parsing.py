"""
Markdown 머메이드 블록 파싱 디버깅
"""
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

md_file = "docs/chapters/03-system-design.md"

with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("="*80)
print("머메이드 블록 검색")
print("="*80)

# 머메이드 블록 찾기
pattern = r'```mermaid\n(.*?)\n```'
matches = list(re.finditer(pattern, content, re.DOTALL))

print(f"\n총 {len(matches)}개 머메이드 블록 발견")

for i, match in enumerate(matches, 1):
    start_pos = match.start()
    
    # 앞 500자
    before = content[max(0, start_pos-500):start_pos]
    
    # 그림 번호 찾기
    caption_match = re.search(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]([^\n]*)', before)
    
    print(f"\n블록 {i} (위치: {start_pos}):")
    if caption_match:
        roman = caption_match.group(1)
        num = caption_match.group(2)
        caption = caption_match.group(3).strip()
        
        roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
        chapter = roman_map.get(roman, '?')
        figure_num = f"{chapter}-{num}"
        
        print(f"  ✓ 그림 {figure_num}: {caption[:50]}")
    else:
        print(f"  ✗ 그림 번호 없음")
        print(f"  앞 내용: ...{before[-100:]}")

# 파싱 테스트
print("\n" + "="*80)
print("clean_markdown + parse_markdown 테스트")
print("="*80)

# 스크립트에서 함수 임포트
import sys
sys.path.insert(0, '.')
from md_to_hwpx_with_images import clean_markdown, parse_markdown

md_content = content
md_content = clean_markdown(md_content)

elements = parse_markdown(md_content)

# mermaid_image 타입 찾기
image_elements = [e for e in elements if e.get('type') == 'mermaid_image']

print(f"\n파싱된 mermaid_image 요소: {len(image_elements)}개")
for elem in image_elements:
    print(f"  - figure_num: {elem.get('figure_num')}")

# 전체 요소 중 몇 번째에 있는지
print(f"\n전체 요소 수: {len(elements)}개")
for i, elem in enumerate(elements):
    if elem.get('type') == 'mermaid_image':
        # 앞뒤 요소 확인
        if i > 0:
            prev = elements[i-1]
            print(f"\n이미지 {elem.get('figure_num')} 위치: {i}번째")
            print(f"  이전 요소: {prev.get('type')}")
            if prev.get('text'):
                print(f"    텍스트: {prev.get('text')[:60]}")

