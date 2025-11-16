"""
원본 HWP에서 표와 이미지 구조 분석
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("원본 HWP의 표와 이미지 구조 분석")
print("="*80)

# section2.xml 읽기
with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 표 찾기
print("\n1. 표 (table) 구조 분석:")
print("-"*80)

table_pattern = r'<hp:tbl id="(\d+)"[^>]*>'
tables = re.findall(table_pattern, content)
print(f"총 {len(tables)}개 표 발견")

# 첫 번째 표 상세 분석
if tables:
    first_table_id = tables[0]
    # 첫 번째 표의 전체 구조 추출
    table_full_pattern = f'<hp:tbl id="{first_table_id}".*?</hp:tbl>'
    table_match = re.search(table_full_pattern, content, re.DOTALL)
    
    if table_match:
        table_xml = table_match.group(0)
        print(f"\n첫 번째 표 (ID={first_table_id}) 구조:")
        print("-"*80)
        
        # 행/열 개수
        row_cnt = re.search(r'rowCnt="(\d+)"', table_xml)
        col_cnt = re.search(r'colCnt="(\d+)"', table_xml)
        
        if row_cnt and col_cnt:
            print(f"행 수: {row_cnt.group(1)}")
            print(f"열 수: {col_cnt.group(1)}")
        
        # 처음 1000자만 출력
        print(f"\nXML 구조 (처음 1000자):")
        print(table_xml[:1000])
        print("...")

# 2. 이미지 찾기
print("\n\n2. 이미지 (picture) 구조 분석:")
print("-"*80)

# img 태그 찾기
img_pattern = r'<hp:img[^>]*>'
images = re.findall(img_pattern, content)
print(f"총 {len(images)}개 이미지 발견")

if images:
    print(f"\n첫 3개 이미지 태그:")
    for i, img in enumerate(images[:3], 1):
        print(f"\n{i}. {img}")

# 그림 컨트롤 찾기
picture_pattern = r'<hp:picture.*?</hp:picture>'
pictures = re.findall(picture_pattern, content, re.DOTALL)
print(f"\n\n<hp:picture> 태그: {len(pictures)}개")

if pictures:
    print(f"\n첫 번째 그림 구조 (처음 800자):")
    print("-"*80)
    print(pictures[0][:800])
    print("...")

# 3. BinData 참조 확인
print("\n\n3. BinData 참조 (이미지 파일 링크):")
print("-"*80)

bindata_pattern = r'BinData/(image\d+\.BMP)'
bindata_refs = re.findall(bindata_pattern, content)
print(f"총 {len(set(bindata_refs))}개 이미지 파일 참조")

if bindata_refs:
    print("\n참조된 이미지 파일:")
    for img_file in sorted(set(bindata_refs))[:10]:
        print(f"  - BinData/{img_file}")

# 4. 표 제목 찾기
print("\n\n4. 표 제목 (caption) 분석:")
print("-"*80)

caption_pattern = r'styleIDRef="18".*?<hp:t>(.*?)</hp:t>'
captions = re.findall(caption_pattern, content, re.DOTALL)
print(f"총 {len(captions)}개 표 제목 발견")

for i, caption in enumerate(captions[:5], 1):
    caption_clean = caption.strip()[:60]
    print(f"  {i}. {caption_clean}")

print("\n\n" + "="*80)
print("분석 완료!")
print("="*80)
print("""
다음 단계:
1. Markdown 표 → HWP 표 XML 변환
2. 머메이드 PNG 이미지 → HWP 이미지 삽입
3. 표 제목, 그림 제목 매핑
""")

