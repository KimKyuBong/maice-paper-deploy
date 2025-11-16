"""
새로 생성된 파일 검증
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

hwpx_file = "hwp/report_clean_tables_20251112_034350.hwpx"

print("="*80)
print(f"파일 검증: {hwpx_file}")
print("="*80)

with zipfile.ZipFile(hwpx_file, 'r') as zf:
    # 이미지 파일 확인
    diagrams = [f for f in zf.namelist() if f.startswith('BinData/diagram')]
    print(f"\n✓ diagram 파일: {len(diagrams)}개")
    
    # XML 확인
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    tree = ET.fromstring(xml.encode('utf-8'))
    
    ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
    pics = tree.findall('.//hp:pic', ns)
    
    print(f"✓ <hp:pic> 태그: {len(pics)}개")
    
    # 실제 삽입된 이미지 확인
    import re
    diagram_refs = re.findall(r'binaryItemIDRef="(diagram\d+)"', xml)
    print(f"✓ diagram 참조: {len(diagram_refs)}개")
    
    for ref in diagram_refs:
        print(f"  - {ref}")

print("\n" + "="*80)
print(f"이 파일을 열어보세요:")
print(f"  {hwpx_file}")
print("="*80)

