"""
Markdown 표 → HWP 표 XML 생성기
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_markdown_table(md_text):
    """
    Markdown 표 파싱
    Returns: {'headers': [...], 'rows': [[...],...]}
    """
    lines = md_text.strip().split('\n')
    
    if len(lines) < 3:
        return None
    
    # 헤더
    header_line = lines[0]
    headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
    
    # 구분선 건너뛰기
    # 데이터 행들
    rows = []
    for line in lines[2:]:
        if not line.strip():
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        rows.append(cells)
    
    return {
        'headers': headers,
        'rows': rows,
        'row_count': len(rows) + 1,  # +1 for header
        'col_count': len(headers)
    }

def escape_xml(text):
    """XML 이스케이프"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    # 볼드 제거
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

def create_table_cell_xml(text, row, col, is_header=False):
    """표 셀 XML 생성"""
    escaped_text = escape_xml(text)
    
    # 헤더 셀은 스타일 다르게
    style_id = "20" if is_header else "20"  # 표 중간 스타일
    header_attr = "1" if is_header else "0"
    
    cell_xml = f'''<hp:tc name="" header="{header_attr}" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="19">
<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
<hp:p id="2147483648" paraPrIDRef="9" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">
<hp:run charPrIDRef="4"><hp:t>{escaped_text}</hp:t></hp:run>
</hp:p>
</hp:subList>
<hp:cellAddr colAddr="{col}" rowAddr="{row}"/>
<hp:cellSpan colSpan="1" rowSpan="1"/>
<hp:cellSz width="10915" height="3000"/>
<hp:cellMargin left="141" right="141" top="141" bottom="141"/>
</hp:tc>'''
    
    return cell_xml

def create_table_xml(table_data, table_id):
    """완전한 HWP 표 XML 생성"""
    
    rows = table_data['row_count']
    cols = table_data['col_count']
    headers = table_data['headers']
    data_rows = table_data['rows']
    
    # 표 시작
    table_xml = f'''<hp:tbl id="{table_id}" zOrder="5" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="TABLE" repeatHeader="1" rowCnt="{rows}" colCnt="{cols}" cellSpacing="0" borderFillIDRef="3" noAdjust="0">
<hp:sz width="43660" widthRelTo="ABSOLUTE" height="{rows * 3000}" heightRelTo="ABSOLUTE" protect="0"/>
<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
<hp:outMargin left="141" right="141" top="141" bottom="141"/>
<hp:inMargin left="141" right="141" top="141" bottom="141"/>
'''
    
    # 헤더 행
    table_xml += '<hp:tr>'
    for col_idx, header in enumerate(headers):
        cell_xml = create_table_cell_xml(header, 0, col_idx, is_header=True)
        table_xml += cell_xml
    table_xml += '</hp:tr>\n'
    
    # 데이터 행들
    for row_idx, row_data in enumerate(data_rows, 1):
        table_xml += '<hp:tr>'
        for col_idx, cell_text in enumerate(row_data):
            cell_xml = create_table_cell_xml(cell_text, row_idx, col_idx, is_header=False)
            table_xml += cell_xml
        table_xml += '</hp:tr>\n'
    
    table_xml += '</hp:tbl>'
    
    return table_xml

# 테스트
test_md_table = '''
| 구분 | 평가 영역 | 코드 | 평가 내용 |
|------|----------|:----:|----------|
| **질문 평가** | 수학적 전문성 | A1 | 수학 개념의 정확성 |
| | 질문 구조화 | A2 | 질문 대상·범위 |
| | 학습 맥락 적용 | A3 | 학습자 수준 |
'''

print("\n\n" + "="*80)
print("Markdown 표 파싱 테스트")
print("="*80)

table_data = parse_markdown_table(test_md_table)

if table_data:
    print(f"\n파싱 결과:")
    print(f"  행: {table_data['row_count']}")
    print(f"  열: {table_data['col_count']}")
    print(f"  헤더: {table_data['headers']}")
    print(f"  데이터: {len(table_data['rows'])}행")
    
    # XML 생성
    table_xml = create_table_xml(table_data, table_id=9999999)
    
    print(f"\n생성된 표 XML (처음 1000자):")
    print("-"*80)
    print(table_xml[:1000])
    print("...")
    
    # 파일로 저장
    with open('hwp/test_table.xml', 'w', encoding='utf-8') as f:
        f.write(table_xml)
    
    print(f"\n✓ 테스트 표 XML 저장: hwp/test_table.xml")

print("\n" + "="*80)
print("✓ 표 생성 로직 준비 완료")
print("="*80)

