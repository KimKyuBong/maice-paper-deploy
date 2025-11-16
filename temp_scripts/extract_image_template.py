"""
원본에서 이미지 XML 템플릿 추출
"""
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

# 원본 section2.xml 파싱
tree = ET.parse('hwp/analyze_original/Contents/section2.xml')
root = tree.getroot()

# 네임스페이스
ns = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section'
}

# 이미지 찾기
pics = root.findall('.//hp:pic', ns)

print(f"총 {len(pics)}개 이미지 발견\n")

if pics:
    # 첫 번째 이미지 XML을 문자열로 변환
    pic = pics[0]
    
    # XML을 문자열로 변환
    xml_str = ET.tostring(pic, encoding='unicode')
    
    print("="*80)
    print("첫 번째 이미지 XML 템플릿:")
    print("="*80)
    print(xml_str)
    
    # 속성 확인
    print("\n" + "="*80)
    print("주요 속성:")
    print("="*80)
    for key, value in pic.attrib.items():
        print(f"  {key}: {value}")
    
    # 하위 요소 확인
    print("\n" + "="*80)
    print("하위 요소:")
    print("="*80)
    for child in pic:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        print(f"  <{tag}>")
        for attr, val in child.attrib.items():
            print(f"    {attr}: {val}")

