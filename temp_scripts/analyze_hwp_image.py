"""
원본 HWP에서 이미지 삽입 구조 분석
"""
import xml.etree.ElementTree as ET
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("원본 HWP 이미지 구조 분석")
print("="*80)

# section2.xml에서 이미지 찾기
tree = ET.parse('hwp/analyze_original/Contents/section2.xml')
root = tree.getroot()
ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

# 이미지 관련 요소 찾기
pictures = root.findall('.//hp:img', ns)
print(f"\n<hp:img> 태그: {len(pictures)}개")

if pictures:
    first_img = pictures[0]
    
    print("\n첫 번째 이미지 속성:")
    for key, value in first_img.attrib.items():
        print(f"  {key}: {value}")
    
    # 부모 요소 확인
    print("\n부모 구조 찾기...")
    
    # 파일로 section2.xml 일부 저장
    with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 첫 번째 img 태그 전후 추출
    img_pos = content.find('<hp:img')
    if img_pos != -1:
        # 앞 2000자, 뒤 2000자
        context = content[max(0, img_pos-2000):min(len(content), img_pos+2000)]
        
        with open('hwp/image_context.xml', 'w', encoding='utf-8') as f:
            f.write(context)
        
        print(f"\n✓ 이미지 전후 컨텍스트 저장: hwp/image_context.xml")
        
        # BinData 참조 찾기
        bindata_match = re.search(r'BinData/(image\d+\.BMP)', context)
        if bindata_match:
            print(f"\n참조된 이미지 파일: {bindata_match.group(0)}")

print("\n\n" + "="*80)
print("이미지 삽입 XML 템플릿 준비")
print("="*80)

