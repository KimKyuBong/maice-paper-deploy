"""
원본과 생성된 파일의 이미지 비교
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("원본 vs 생성된 파일 이미지 비교")
print("="*80)

# 1. 원본 파일의 이미지 확인
print("\n1. 원본 파일:")
original = "hwp/report_backup_20251112_020239.hwpx"
with zipfile.ZipFile(original, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    tree = ET.fromstring(xml.encode('utf-8'))
    
    ns = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hc': 'http://www.hancom.co.kr/hwpml/2011/core'
    }
    
    pics = tree.findall('.//hp:pic', ns)
    print(f"  이미지 수: {len(pics)}개")
    
    # 첫 이미지 주변 문맥 확인
    for i, pic in enumerate(pics[:3], 1):
        # 부모 요소 찾기
        parent = None
        for p in tree.iter():
            if pic in list(p):
                parent = p
                break
        
        if parent is not None and parent.tag.endswith('p'):
            # 같은 문단의 텍스트 찾기
            texts = []
            for t in parent.findall('.//hp:t', ns):
                if t.text:
                    texts.append(t.text[:50])
            
            img = pic.find('.//hc:img', ns)
            ref = img.get('binaryItemIDRef') if img is not None else 'None'
            
            print(f"\n  이미지 {i}:")
            print(f"    참조: {ref}")
            if texts:
                print(f"    문맥: {texts[0]}")

# 2. 생성된 파일의 이미지 확인
print("\n" + "="*80)
print("2. 생성된 파일:")
generated = "hwp/report_with_images_20251112_033238.hwpx"
with zipfile.ZipFile(generated, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    tree = ET.fromstring(xml.encode('utf-8'))
    
    pics = tree.findall('.//hp:pic', ns)
    print(f"  이미지 수: {len(pics)}개")
    
    for i, pic in enumerate(pics, 1):
        parent = None
        for p in tree.iter():
            if pic in list(p):
                parent = p
                break
        
        if parent is not None and parent.tag.endswith('p'):
            texts = []
            for t in parent.findall('.//hp:t', ns):
                if t.text:
                    texts.append(t.text[:50])
            
            img = pic.find('.//hc:img', ns)
            ref = img.get('binaryItemIDRef') if img is not None else 'None'
            
            print(f"\n  이미지 {i}:")
            print(f"    참조: {ref}")
            if texts:
                print(f"    문맥: {texts[0]}")
    
    # BinData 확인
    print(f"\n  BinData 파일:")
    diagrams = [f for f in zf.namelist() if f.startswith('BinData/diagram')]
    for d in diagrams:
        info = zf.getinfo(d)
        print(f"    {d}: {info.file_size:,} bytes")

# 3. 이미지가 있어야 할 위치 확인
print("\n" + "="*80)
print("3. Markdown에서 이미지 위치:")
print("="*80)

import os
md_files = [
    "docs/chapters/03-system-design.md",
    "docs/chapters/05-research-methods.md"
]

for md_file in md_files:
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 그림 참조 찾기
        import re
        figures = re.findall(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]([^\n]*)', content)
        
        if figures:
            print(f"\n{md_file}:")
            for roman, num, caption in figures[:3]:
                roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
                chapter = roman_map.get(roman, '?')
                print(f"  그림 {chapter}-{num}: {caption.strip()[:40]}")

