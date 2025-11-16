"""
Markdown에서 머메이드 블록 추출 및 PNG 매핑
"""
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("머메이드 블록 추출 및 PNG 매핑")
print("="*80)

# 1. Markdown에서 머메이드 블록 찾기
md_files = [
    ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
    ("Ⅱ. 이론적 배경", "docs/chapters/02-theoretical-background.md"),
    ("Ⅲ. 시스템 설계", "docs/chapters/03-system-design.md"),
    ("Ⅳ. 시스템 구현", "docs/chapters/04-system-implementation.md"),
    ("Ⅴ. 연구 방법", "docs/chapters/05-research-methods.md"),
    ("Ⅵ. 결과", "docs/chapters/06-results.md"),
    ("Ⅶ. 논의 및 결론", "docs/chapters/07-discussion-conclusion.md"),
    ("Ⅷ. 참고문헌", "docs/chapters/08-references.md"),
]

mermaid_blocks = []

for chapter_name, md_path in md_files:
    if not os.path.exists(md_path):
        continue
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 머메이드 블록 찾기
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        print(f"\n{chapter_name}: {len(matches)}개 머메이드 블록")
        
        for i, block in enumerate(matches, 1):
            # 블록 앞의 컨텍스트 찾기 (제목이나 설명)
            block_pos = content.find(f'```mermaid\n{block}')
            context_before = content[max(0, block_pos-500):block_pos]
            
            # [그림X-Y] 형식 찾기
            caption_match = re.search(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]([^\n]*)', context_before)
            
            # figure 참조 찾기
            figure_ref = re.search(r'figure(\d+-\d+)', context_before, re.IGNORECASE)
            
            figure_num = None
            caption_text = None
            
            if caption_match:
                # 로마숫자 → 아라비아 숫자 변환
                roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
                roman = caption_match.group(1)
                num = caption_match.group(2)
                
                chapter_num = roman_map.get(roman, '?')
                figure_num = f"{chapter_num}-{num}"
                caption_text = caption_match.group(3).strip()
            
            mermaid_blocks.append({
                'chapter': chapter_name,
                'index': i,
                'content': block[:100],
                'figure_num': figure_num,
                'caption': caption_text,
                'file_ref': figure_ref.group(0) if figure_ref else None
            })
            
            print(f"  블록 {i}:")
            if figure_num:
                print(f"    그림 번호: {figure_num}")
            if caption_text:
                print(f"    캡션: {caption_text}")

print(f"\n\n총 {len(mermaid_blocks)}개 머메이드 블록 발견")

# 2. PNG 파일 목록
print("\n" + "="*80)
print("PNG 다이어그램 파일 목록")
print("="*80)

png_dir = "docs/diagrams/output/png"
png_files = []

if os.path.exists(png_dir):
    for file in sorted(os.listdir(png_dir)):
        if file.endswith('.png'):
            png_files.append(file)
            print(f"  - {file}")

print(f"\n총 {len(png_files)}개 PNG 파일")

# 3. 매핑
print("\n" + "="*80)
print("머메이드 블록 ↔ PNG 파일 매핑")
print("="*80)

mappings = []

for block_info in mermaid_blocks:
    figure_num = block_info.get('figure_num')
    
    if figure_num:
        # 3-1 → figure3-1-*.png 찾기
        matched_png = None
        for png in png_files:
            if f"figure{figure_num}-" in png or f"figure{figure_num}." in png:
                matched_png = png
                break
        
        if matched_png:
            mappings.append({
                'chapter': block_info['chapter'],
                'figure_num': figure_num,
                'png_file': matched_png,
                'caption': block_info.get('caption')
            })
            
            print(f"\n✓ {block_info['chapter']}")
            print(f"  그림 {figure_num} → {matched_png}")
            if block_info.get('caption'):
                print(f"  캡션: {block_info['caption']}")

print(f"\n\n총 {len(mappings)}개 매핑 완료")

# 매핑 결과 저장
import json
with open('hwp/mermaid_to_png_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mappings, f, ensure_ascii=False, indent=2)

print(f"\n✓ 매핑 정보 저장: hwp/mermaid_to_png_mapping.json")

print("\n" + "="*80)
print("다음 단계:")
print("="*80)
print("""
1. PNG 파일들을 BinData 폴더에 복사
2. 머메이드 블록 위치에 이미지 XML 삽입
3. HWPX 재생성
""")

