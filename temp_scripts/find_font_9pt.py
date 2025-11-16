"""
맑은 고딕 9pt charPr 찾기
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

char_prs = root.findall('.//hh:charPr', ns)

print("="*80)
print("맑은 고딕 9pt charPr 찾기")
print("="*80)

print(f"\n총 {len(char_prs)}개 charPr 검사\n")

# 9pt = 900 (HWP 단위)
target_height = '900'

for char_pr in char_prs:
    char_id = char_pr.get('id')
    height = char_pr.get('height')
    
    if height == target_height:
        # 폰트 이름 확인
        font_names = []
        for lang in ['FaceNameHangul', 'FaceNameLatin', 'FaceNameHanja']:
            font_elem = char_pr.find(f'hh:{lang}', ns)
            if font_elem is not None and font_elem.get('name'):
                font_names.append(f"{lang}: {font_elem.get('name')}")
        
        # fontAttr (bold 여부)
        font_attr = char_pr.get('fontAttr', '0')
        is_bold = (int(font_attr) & 1) == 1
        
        print(f"charPrIDRef=\"{char_id}\" (height={height}, 9pt):")
        print(f"  Bold: {is_bold}")
        for fn in font_names:
            print(f"  {fn}")
        print()

print("\n" + "="*80)
print("권장 사항:")
print("="*80)
print("""
맑은 고딕 9pt charPr를 찾아서 표 셀에 적용
또는 새로운 charPr 정의 추가
""")

