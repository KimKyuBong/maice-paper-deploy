"""
원본 HWPX의 이미지 XML 구조 분석
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

# 원본 HWPX 추출
hwpx_path = "hwp/report_backup_20251112_020239.hwpx"
extract_dir = "hwp/analyze_original"

if os.path.exists(extract_dir):
    import shutil
    shutil.rmtree(extract_dir)

os.makedirs(extract_dir)

with zipfile.ZipFile(hwpx_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print("="*80)
print("이미지 XML 구조 분석")
print("="*80)

# BinData 폴더 확인
bindata_dir = os.path.join(extract_dir, "BinData")
if os.path.exists(bindata_dir):
    print(f"\n1. BinData 폴더 내용:")
    for file in sorted(os.listdir(bindata_dir)):
        file_path = os.path.join(bindata_dir, file)
        size = os.path.getsize(file_path)
        print(f"   - {file} ({size:,} bytes)")

# section XML에서 이미지 참조 찾기
print(f"\n2. 이미지 참조 XML 구조:")
contents_dir = os.path.join(extract_dir, "Contents")

for section_file in sorted(os.listdir(contents_dir)):
    if not section_file.startswith('section') or not section_file.endswith('.xml'):
        continue
    
    section_path = os.path.join(contents_dir, section_file)
    
    try:
        tree = ET.parse(section_path)
        root = tree.getroot()
        
        # 모든 네임스페이스 찾기
        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
            'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'
        }
        
        # 이미지 관련 요소 찾기
        # <hp:ctrl> 요소 중 이미지 관련 찾기
        for ctrl in root.findall('.//hp:ctrl', namespaces):
            # ctrl 아래의 모든 자식 확인
            for child in ctrl:
                if 'Pic' in child.tag or 'img' in child.tag.lower() or 'image' in child.tag.lower():
                    print(f"\n[{section_file}]")
                    print(f"  태그: {child.tag}")
                    print(f"  속성: {child.attrib}")
                    
                    # 하위 요소 출력
                    for subchild in child:
                        print(f"    └ {subchild.tag}: {subchild.attrib}")
                        for subsubchild in subchild:
                            print(f"      └ {subsubchild.tag}: {subsubchild.attrib}")
        
        # 더 직접적으로 찾기: 모든 요소 순회
        for elem in root.iter():
            if any(keyword in elem.tag.lower() for keyword in ['pic', 'img', 'image']):
                print(f"\n[{section_file}] 발견!")
                print(f"  전체 경로: {elem.tag}")
                print(f"  속성: {elem.attrib}")
                
                # 부모 요소 확인
                parent_map = {c: p for p in tree.iter() for c in p}
                if elem in parent_map:
                    parent = parent_map[elem]
                    print(f"  부모: {parent.tag} {parent.attrib}")
    
    except Exception as e:
        print(f"Error parsing {section_file}: {e}")

print("\n" + "="*80)
print("3. 원시 XML 검색 (정규표현식)")
print("="*80)

import re

for section_file in sorted(os.listdir(contents_dir)):
    if not section_file.startswith('section') or not section_file.endswith('.xml'):
        continue
    
    section_path = os.path.join(contents_dir, section_file)
    
    with open(section_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # img, pic, image 관련 태그 찾기
    patterns = [
        r'<[^>]*[Pp]ic[^>]*>',
        r'<[^>]*[Ii]mg[^>]*>',
        r'<[^>]*[Ii]mage[^>]*>',
        r'<[^>]*Rect[^>]*>',
        r'binData[^>]*>',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, xml_content)
        if matches:
            print(f"\n[{section_file}] 패턴: {pattern}")
            for match in matches[:3]:  # 처음 3개만
                print(f"  {match}")

print("\n완료!")

