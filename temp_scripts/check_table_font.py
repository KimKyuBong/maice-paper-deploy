"""
원본 표에서 사용된 charPr 확인
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

# section2.xml에서 표 찾기
tree = ET.parse('hwp/analyze_original/Contents/section2.xml')
root = tree.getroot()
ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

tables = root.findall('.//hp:tbl', ns)

print("="*80)
print("원본 표에서 사용된 charPrIDRef")
print("="*80)

if tables:
    table = tables[0]
    
    # 모든 run의 charPrIDRef 수집
    runs = table.findall('.//hp:run', ns)
    char_prs = set()
    
    for run in runs:
        char_pr = run.get('charPrIDRef')
        if char_pr:
            char_prs.add(char_pr)
    
    print(f"\n첫 번째 표에서 사용된 charPrIDRef: {sorted(char_prs)}")
    
    # header.xml에서 해당 charPr 확인
    print("\n" + "="*80)
    print("각 charPr 상세 정보:")
    print("="*80)
    
    tree2 = ET.parse('hwp/analyze_original/Contents/header.xml')
    root2 = tree2.getroot()
    ns2 = {'hh': 'http://www.hancom.co.kr/hwpml/2011/head'}
    
    for char_id in sorted(char_prs, key=int):
        char_pr = root2.find(f'.//hh:charPr[@id="{char_id}"]', ns2)
        
        if char_pr is not None:
            height = char_pr.get('height', 'N/A')
            
            print(f"\ncharPrIDRef=\"{char_id}\":")
            print(f"  height: {height} ({int(height)/100 if height != 'N/A' else '?'}pt)")
            
            # XML에서 맑은 고딕 찾기
            char_str = ET.tostring(char_pr, encoding='unicode')
            if '맑은 고딕' in char_str:
                print(f"  ✓ 맑은 고딕!")

print("\n" + "="*80)
print("표 셀용 권장 charPrIDRef:")
print("="*80)
print("맑은 고딕 9pt인 ID를 사용")

