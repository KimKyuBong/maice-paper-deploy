"""
원본에서 볼드만 적용된 charPr 찾기
"""
import re
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("header.xml에서 charPr 속성 상세 분석")
print("="*80)

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()

# 네임스페이스
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

# 모든 charPr 찾기
char_prs = root.findall('.//hh:charPr', ns)

print(f"\n총 {len(char_prs)}개 charPr 발견\n")
print("ID | Height | fontAttr | Bold여부")
print("-"*80)

for char_pr in char_prs[:25]:
    char_id = char_pr.get('id')
    height = char_pr.get('height', 'N/A')
    font_attr = char_pr.get('fontAttr', 'N/A')
    
    # fontAttr 비트 확인
    is_bold = "?"
    if font_attr != 'N/A':
        # fontAttr의 첫 번째 비트가 bold
        attr_int = int(font_attr)
        is_bold = "Yes" if (attr_int & 1) else "No"
    
    print(f"{char_id:2s} | {height:5s} | {font_attr:8s} | {is_bold}")

# 크기 1000 (10pt)에서 볼드인 것 찾기
print("\n\n" + "="*80)
print("크기 1000 (10pt) charPr 중 볼드 찾기")
print("="*80)

bold_10pt = []
normal_10pt = []

for char_pr in char_prs:
    char_id = char_pr.get('id')
    height = char_pr.get('height', 'N/A')
    font_attr = char_pr.get('fontAttr', '0')
    
    if height == '1000':
        attr_int = int(font_attr)
        is_bold = (attr_int & 1) == 1
        
        if is_bold:
            bold_10pt.append(char_id)
        else:
            normal_10pt.append(char_id)

print(f"\n크기 1000 (10pt) 중:")
print(f"  - 볼드: charPrIDRef = {bold_10pt}")
print(f"  - 일반: charPrIDRef = {normal_10pt}")

print("\n\n" + "="*80)
print("권장 사항:")
print("="*80)
if bold_10pt:
    print(f"""
일반 본문 텍스트: charPrIDRef="4" (또는 {normal_10pt[0] if normal_10pt else '4'})
볼드 본문 텍스트: charPrIDRef="{bold_10pt[0]}" (크기 동일, 볼드만 적용)
""")

