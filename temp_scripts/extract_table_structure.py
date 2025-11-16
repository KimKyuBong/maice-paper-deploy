"""
원본에서 표 구조 완전 추출 및 분석
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("표 XML 구조 완전 분석")
print("="*80)

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 첫 번째 표 전체 추출
table_pattern = r'<hp:tbl id="(\d+)".*?</hp:tbl>'
tables = re.findall(table_pattern, content, re.DOTALL)

print(f"\n총 {len(tables)}개 표 발견")

if tables:
    first_table = tables[0]
    
    print("\n" + "="*80)
    print("첫 번째 표 완전 구조:")
    print("="*80)
    
    # 파일로 저장
    with open('hwp/first_table_template.xml', 'w', encoding='utf-8') as f:
        f.write(first_table)
    
    print(f"\n표 XML 저장: hwp/first_table_template.xml")
    print(f"크기: {len(first_table):,}자")
    
    # 표 속성 추출
    row_cnt = re.search(r'rowCnt="(\d+)"', first_table)
    col_cnt = re.search(r'colCnt="(\d+)"', first_table)
    
    print(f"\n표 크기: {row_cnt.group(1) if row_cnt else '?'}행 x {col_cnt.group(1) if col_cnt else '?'}열")
    
    # 셀 찾기
    cells = re.findall(r'<hp:tc[^>]*>.*?</hp:tc>', first_table, re.DOTALL)
    print(f"총 셀 개수: {len(cells)}")
    
    # 셀 내용 추출
    print("\n셀 내용:")
    for i, cell in enumerate(cells[:8], 1):
        # 셀 안의 텍스트 추출
        texts = re.findall(r'<hp:t>(.*?)</hp:t>', cell)
        text = ''.join(texts)[:60]
        
        # 셀 병합 확인
        colspan = re.search(r'<hp:cellSpan colSpan="(\d+)"', cell)
        rowspan = re.search(r'rowSpan="(\d+)"', cell)
        
        span_info = ""
        if colspan and int(colspan.group(1)) > 1:
            span_info += f" colspan={colspan.group(1)}"
        if rowspan and int(rowspan.group(1)) > 1:
            span_info += f" rowspan={rowspan.group(1)}"
        
        print(f"  셀 {i}{span_info}: {text}")

# 간단한 표 템플릿 생성
print("\n\n" + "="*80)
print("간단한 표 템플릿 생성")
print("="*80)

simple_table_template = '''
<hp:tbl id="{table_id}" zOrder="{zorder}" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="TABLE" repeatHeader="1" rowCnt="{rows}" colCnt="{cols}" cellSpacing="0" borderFillIDRef="3" noAdjust="0">
  <hp:sz width="43660" widthRelTo="ABSOLUTE" height="10000" heightRelTo="ABSOLUTE" protect="0"/>
  <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
  <hp:outMargin left="141" right="141" top="141" bottom="141"/>
  <hp:inMargin left="141" right="141" top="141" bottom="141"/>
  {rows_xml}
</hp:tbl>
'''

print("표 템플릿 구조:")
print(simple_table_template)

print("\n셀 템플릿:")
cell_template = '''
<hp:tc name="" header="{is_header}" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="19">
  <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
    <hp:p id="2147483648" paraPrIDRef="9" styleIDRef="20" pageBreak="0" columnBreak="0" merged="0">
      <hp:run charPrIDRef="4"><hp:t>{cell_text}</hp:t></hp:run>
    </hp:p>
  </hp:subList>
  <hp:cellAddr colAddr="{col}" rowAddr="{row}"/>
  <hp:cellSpan colSpan="1" rowSpan="1"/>
  <hp:cellSz width="10915" height="3000"/>
  <hp:cellMargin left="141" right="141" top="141" bottom="141"/>
</hp:tc>
'''
print(cell_template)

print("\n" + "="*80)
print("✓ 표 템플릿 준비 완료")
print("="*80)

