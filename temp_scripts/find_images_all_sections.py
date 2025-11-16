"""
모든 섹션에서 이미지 찾기
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("전체 섹션에서 이미지 찾기")
print("="*80)

sections_dir = 'hwp/analyze_original/Contents'

for i in range(10):
    section_file = os.path.join(sections_dir, f'section{i}.xml')
    
    if not os.path.exists(section_file):
        continue
    
    with open(section_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # BinData 참조 찾기
    bindata_refs = re.findall(r'BinData/[\w\.]+', content)
    
    # 이미지 관련 태그 찾기
    img_tags = re.findall(r'<hp:img[^>]*>', content)
    drawing_tags = re.findall(r'<hp:d', content)
    
    if bindata_refs or img_tags:
        print(f"\nsection{i}.xml:")
        print(f"  BinData 참조: {len(bindata_refs)}개")
        print(f"  이미지 태그: {len(img_tags)}개")
        
        if bindata_refs:
            print(f"  참조 파일 (처음 5개):")
            for ref in sorted(set(bindata_refs))[:5]:
                print(f"    - {ref}")
        
        if img_tags:
            print(f"  img 태그 예시:")
            print(f"    {img_tags[0]}")

print("\n\n" + "="*80)
print("이미지 XML 구조 추출")
print("="*80)

# 이미지가 있는 섹션에서 전체 구조 추출
for i in range(10):
    section_file = os.path.join(sections_dir, f'section{i}.xml')
    
    if not os.path.exists(section_file):
        continue
    
    with open(section_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'BinData/image' in content:
        # 첫 번째 이미지 컨트롤 전체 추출
        # drawingObject 또는 picture 찾기
        match = re.search(r'<hp:ctrl>.*?BinData/image\d+\.BMP.*?</hp:ctrl>', content, re.DOTALL)
        
        if match:
            img_ctrl = match.group(0)
            
            with open(f'hwp/image_ctrl_section{i}.xml', 'w', encoding='utf-8') as f:
                f.write(img_ctrl)
            
            print(f"\nsection{i}.xml에서 이미지 컨트롤 추출:")
            print(f"  저장: hwp/image_ctrl_section{i}.xml")
            print(f"  크기: {len(img_ctrl):,}자")
            print(f"\n  처음 500자:")
            print(img_ctrl[:500])
            break

print("\n" + "="*80)
print("분석 완료")
print("="*80)

