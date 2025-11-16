"""
9pt charPr의 폰트 이름 확인
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('hwp/analyze_original/Contents/header.xml')
root = tree.getroot()
ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}

char_prs = root.findall('.//hh:charPr', ns)

print("="*80)
print("9pt charPr의 폰트 이름 상세 확인")
print("="*80)

target_ids = ['2', '3', '16', '47', '52', '54']

for char_id in target_ids:
    char_pr = root.find(f'.//hh:charPr[@id="{char_id}"]', ns)
    
    if char_pr is not None:
        height = char_pr.get('height')
        
        # 모든 언어별 폰트 이름
        hangul = char_pr.find('hh:fontIDHangul', ns)
        latin = char_pr.find('hh:fontIDLatin', ns)
        
        # 새 방식으로도 확인
        face_hangul = char_pr.find('.//hh:faceNameHangul', ns)
        face_latin = char_pr.find('.//hh:faceNameLatin', ns)
        
        print(f"\ncharPrIDRef=\"{char_id}\" (height={height}):")
        
        if hangul is not None:
            print(f"  fontIDHangul: {hangul.get('val')}")
        if latin is not None:
            print(f"  fontIDLatin: {latin.get('val')}")
        if face_hangul is not None:
            print(f"  faceNameHangul: {face_hangul.text}")
        if face_latin is not None:
            print(f"  faceNameLatin: {face_latin.text}")
        
        # XML 일부 출력
        char_str = ET.tostring(char_pr, encoding='unicode')
        if '맑은 고딕' in char_str or 'Malgun' in char_str:
            print(f"  ✓ 맑은 고딕 발견!")
            print(f"  XML (처음 300자): {char_str[:300]}")

print("\n" + "="*80)
print("권장:")
print("="*80)
print("맑은 고딕 9pt charPr ID를 표 셀에 적용")

