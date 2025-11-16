"""
Section XML 구조 분석 - 문단(paragraph) 구조 파악
"""
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

# section0.xml 파싱
print("="*80)
print("Section XML 구조 분석")
print("="*80)

tree = ET.parse("hwp/extracted_hwpx/Contents/section0.xml")
root = tree.getroot()

print(f"\n루트 태그: {root.tag}")
print(f"네임스페이스: {root.attrib}")

# 첫 몇 개 문단 찾기
namespaces = {
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
}

paragraphs = root.findall('.//hp:p', namespaces)
print(f"\n총 문단 수: {len(paragraphs)}")

print("\n처음 5개 문단 구조:")
print("-"*80)

for i, para in enumerate(paragraphs[:5], 1):
    print(f"\n문단 {i}:")
    print(f"  ID: {para.get('id')}")
    print(f"  paraPrIDRef: {para.get('paraPrIDRef')}")  # 문단 스타일 ID
    print(f"  styleIDRef: {para.get('styleIDRef')}")    # 스타일 ID
    
    # 텍스트 내용 찾기
    runs = para.findall('.//hp:run', namespaces)
    print(f"  run 개수: {len(runs)}")
    
    for j, run in enumerate(runs[:2], 1):
        # 텍스트 찾기
        texts = run.findall('.//hp:t', namespaces)
        for text_elem in texts:
            if text_elem.text:
                print(f"    텍스트 {j}: {text_elem.text[:50]}")
        
        # charPrIDRef (문자 스타일)
        char_pr = run.get('charPrIDRef')
        if char_pr:
            print(f"    charPrIDRef: {char_pr}")

print("\n\n" + "="*80)
print("스타일 ID 매핑 (header.xml에서 확인한 것)")
print("="*80)
print("""
styleIDRef="5"  → "Ⅰ. 제목" (Outline 1)
styleIDRef="6"  → "1. 제목" (Outline 2)
styleIDRef="7"  → "가. 제목" (Outline 3)
styleIDRef="12" → "본문" (Body)
styleIDRef="14" → "․ 글머리표"
""")

print("\n" + "="*80)
print("XML 구조 요약")
print("="*80)
print("""
<hp:p id="..." paraPrIDRef="..." styleIDRef="...">
    <hp:run charPrIDRef="...">
        <hp:t>텍스트 내용</hp:t>
    </hp:run>
</hp:p>

핵심:
- hp:p = 문단 (paragraph)
- styleIDRef = 스타일 ID (5=Ⅰ.제목, 6=1.제목, 7=가.제목, 12=본문)
- hp:run = 텍스트 런 (문자 서식 단위)
- hp:t = 실제 텍스트
""")

