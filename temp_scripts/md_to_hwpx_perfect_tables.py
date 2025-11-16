"""
Markdown → HWPX 변환 (완벽한 표 테두리)
셀 위치별로 정확한 borderFillIDRef 적용
"""
import os
import sys
import re
import zipfile
import shutil
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 스타일 매핑
STYLE_MAP = {
    'heading1': {'styleIDRef': '5', 'paraPrIDRef': '20', 'charPrIDRef': '14'},
    'heading2': {'styleIDRef': '6', 'paraPrIDRef': '21', 'charPrIDRef': '8'},
    'heading3': {'styleIDRef': '7', 'paraPrIDRef': '22', 'charPrIDRef': '15'},
    'heading4': {'styleIDRef': '8', 'paraPrIDRef': '23', 'charPrIDRef': '15'},
    'heading5': {'styleIDRef': '9', 'paraPrIDRef': '24', 'charPrIDRef': '15'},
    'body': {'styleIDRef': '12', 'paraPrIDRef': '17', 'charPrIDRef': '4'},
    'list_bullet': {'styleIDRef': '14', 'paraPrIDRef': '18', 'charPrIDRef': '4'},
    'list_para': {'styleIDRef': '13', 'paraPrIDRef': '19', 'charPrIDRef': '4'},
    'numbered_list': {'styleIDRef': '13', 'paraPrIDRef': '19', 'charPrIDRef': '4'},
    'empty': {'styleIDRef': '0', 'paraPrIDRef': '6', 'charPrIDRef': '5'},
}

def clean_markdown(text):
    """Markdown 전처리"""
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[.*?\]\]', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def remove_auto_numbering(text, heading_level):
    """자동 번호 제거"""
    if heading_level == 'heading1':
        text = re.sub(r'^[IⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s*', '', text)
    elif heading_level == 'heading2':
        text = re.sub(r'^\d+\.\s*', '', text)
    elif heading_level == 'heading3':
        text = re.sub(r'^[가-힣]\.\s*', '', text)
    elif heading_level == 'heading4':
        text = re.sub(r'^\d+\)\s*', '', text)
    elif heading_level == 'heading5':
        text = re.sub(r'^[가-힣]\)\s*', '', text)
    return text

def parse_markdown_table(md_text):
    """Markdown 표 파싱"""
    lines = [l for l in md_text.strip().split('\n') if l.strip()]
    
    if len(lines) < 3:
        return None
    
    headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
    
    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        rows.append(cells)
    
    return {
        'headers': headers,
        'rows': rows,
        'row_count': len(rows) + 1,
        'col_count': len(headers)
    }

def extract_tables_from_markdown(md_text):
    """Markdown에서 표 추출"""
    tables = []
    lines = md_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip().startswith('|') and '|' in line[1:]:
            table_lines = [line]
            start_line = i
            
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('|'):
                table_lines.append(lines[j])
                j += 1
            
            if len(table_lines) >= 3:
                table_md = '\n'.join(table_lines)
                table_data = parse_markdown_table(table_md)
                
                if table_data:
                    tables.append((table_data, start_line, j - 1))
            
            i = j
        else:
            i += 1
    
    return tables

def escape_xml(text):
    """XML 이스케이프 및 볼드 제거"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

def get_border_fill_id(row_idx, col_idx, total_rows, total_cols):
    """
    셀 위치에 따른 정확한 borderFillIDRef 반환
    """
    is_header = (row_idx == 0)
    is_last_row = (row_idx == total_rows - 1)
    is_first_col = (col_idx == 0)
    is_last_col = (col_idx == total_cols - 1)
    
    if is_header:
        # 헤더 행
        if is_first_col:
            return "19"  # 맨왼쪽
        elif is_last_col:
            return "17"  # 맨오른쪽
        else:
            return "12"  # 중간
    elif is_last_row:
        # 맨아래 행
        if is_last_col:
            return "15"  # 맨오른쪽
        else:
            return "10"  # 맨왼쪽 및 중간
    else:
        # 데이터 행 (중간)
        if is_first_col:
            return "11"  # 맨왼쪽
        elif is_last_col:
            return "14"  # 맨오른쪽
        else:
            return "13"  # 중간

def create_table_cell_xml(text, row, col, total_rows, total_cols, is_header=False):
    """셀 위치별 정확한 borderFill 적용"""
    escaped_text = escape_xml(text)
    
    # 위치별 borderFill
    border_fill_id = get_border_fill_id(row, col, total_rows, total_cols)
    
    header_attr = "1" if is_header else "0"
    style_id = "20"
    
    return f'''<hp:tc name="" header="{header_attr}" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="{border_fill_id}">
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

def create_table_xml(table_data, table_id):
    """완전한 HWP 표 XML 생성"""
    rows = table_data['row_count']
    cols = table_data['col_count']
    headers = table_data['headers']
    data_rows = table_data['rows']
    
    table_xml = f'''<hp:tbl id="{table_id}" zOrder="5" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="TABLE" repeatHeader="1" rowCnt="{rows}" colCnt="{cols}" cellSpacing="0" borderFillIDRef="3" noAdjust="0">
<hp:sz width="43660" widthRelTo="ABSOLUTE" height="{rows * 3000}" heightRelTo="ABSOLUTE" protect="0"/>
<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>
<hp:outMargin left="141" right="141" top="141" bottom="141"/>
<hp:inMargin left="141" right="141" top="141" bottom="141"/>
'''
    
    # 헤더 행
    table_xml += '<hp:tr>'
    for col_idx, header in enumerate(headers):
        table_xml += create_table_cell_xml(header, 0, col_idx, rows, cols, is_header=True)
    table_xml += '</hp:tr>\n'
    
    # 데이터 행들
    for row_idx, row_data in enumerate(data_rows, 1):
        table_xml += '<hp:tr>'
        for col_idx, cell_text in enumerate(row_data):
            table_xml += create_table_cell_xml(cell_text, row_idx, col_idx, rows, cols, is_header=False)
        table_xml += '</hp:tr>\n'
    
    table_xml += '</hp:tbl>'
    return table_xml

def parse_markdown_with_tables(md_text):
    """Markdown 파싱 (표 포함)"""
    table_info = extract_tables_from_markdown(md_text)
    lines = md_text.split('\n')
    paragraphs = []
    
    i = 0
    while i < len(lines):
        in_table = False
        for table_data, start, end in table_info:
            if start <= i <= end:
                if i == start:
                    paragraphs.append(('table', table_data))
                in_table = True
                break
        
        if in_table:
            i += 1
            continue
        
        line = lines[i].rstrip()
        
        if not line:
            paragraphs.append(('empty', ''))
        elif line.startswith('# '):
            text = remove_auto_numbering(line[2:].strip(), 'heading1')
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = remove_auto_numbering(line[3:].strip(), 'heading2')
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = remove_auto_numbering(line[4:].strip(), 'heading3')
            paragraphs.append(('heading3', text))
        elif line.startswith('#### '):
            text = remove_auto_numbering(line[5:].strip(), 'heading4')
            paragraphs.append(('heading4', text))
        elif line.startswith('##### '):
            text = remove_auto_numbering(line[6:].strip(), 'heading5')
            paragraphs.append(('heading5', text))
        elif line.startswith('- '):
            text = line[2:].strip()
            if len(text) > 80 or ':' in text[:30]:
                paragraphs.append(('list_para', text))
            else:
                paragraphs.append(('list_bullet', text))
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            paragraphs.append(('numbered_list', text))
        else:
            paragraphs.append(('body', line))
        
        i += 1
    
    return paragraphs

def remove_bold_markdown(text):
    """볼드 마크다운 제거"""
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def create_paragraph_xml(style_type, text, para_id):
    """문단 XML 생성"""
    style_info = STYLE_MAP.get(style_type, STYLE_MAP['body'])
    
    style_id = style_info['styleIDRef']
    para_pr = style_info['paraPrIDRef']
    char_pr = style_info['charPrIDRef']
    
    text = remove_bold_markdown(text) if text else ''
    escaped_text = escape_xml(text)
    
    run = f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>' if text else f'<hp:run charPrIDRef="{char_pr}"/>'
    
    return f'<hp:p id="{para_id}" paraPrIDRef="{para_pr}" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">{run}</hp:p>'

def create_table_paragraph_xml(table_data, para_id, table_id):
    """표를 포함한 문단 XML"""
    table_xml = create_table_xml(table_data, table_id)
    
    para_xml = f'<hp:p id="{para_id}" paraPrIDRef="6" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
    para_xml += f'<hp:run charPrIDRef="4">{table_xml}<hp:t/></hp:run>'
    para_xml += '</hp:p>'
    
    return para_xml

def extract_section_header(xml_content):
    """섹션 헤더 추출"""
    first_para_pos = xml_content.find('<hp:p')
    
    if first_para_pos == -1:
        close_tag_pos = xml_content.rfind('</hs:sec>')
        return xml_content[:close_tag_pos]
    
    return xml_content[:first_para_pos]

def create_hwpx_perfect(md_files, output_hwpx):
    """완벽한 표 테두리로 HWPX 생성"""
    print("="*80)
    print("Markdown → HWPX 변환 (완벽한 표 테두리)")
    print("="*80)
    
    # 1. 압축 해제
    template_hwpx = "hwp/report_backup_20251112_020239.hwpx"
    temp_dir = "hwp/temp_hwpx_perfect"
    
    print("\n1단계: 기존 HWPX 압축 해제...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"✓ 압축 해제 완료")
    
    # 2. Markdown 읽기
    print("\n2단계: Markdown 파싱 (표 포함)...")
    all_items = []
    
    for chapter_name, md_path in md_files:
        if not os.path.exists(md_path):
            print(f"  ⚠ 파일 없음: {md_path}")
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md_content = clean_markdown(md_content)
        items = parse_markdown_with_tables(md_content)
        all_items.extend(items)
        
        table_count = sum(1 for item_type, _ in items if item_type == 'table')
        para_count = len(items) - table_count
        
        print(f"  ✓ {chapter_name}: {para_count}개 문단, {table_count}개 표")
    
    total_tables = sum(1 for item_type, _ in all_items if item_type == 'table')
    total_paras = len(all_items) - total_tables
    
    print(f"\n총 {total_paras}개 문단, {total_tables}개 표")
    
    # 3. XML 생성
    print("\n3단계: section2.xml 재생성...")
    section2_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    header = extract_section_header(original_xml)
    print(f"  ✓ 헤더 추출")
    
    print(f"  XML 생성 중...")
    xml_items = []
    table_counter = 900000000
    
    for i, (item_type, content) in enumerate(all_items):
        para_id = 500000000 + i
        
        if item_type == 'table':
            table_counter += 1
            para_xml = create_table_paragraph_xml(content, para_id, table_counter)
            xml_items.append(para_xml)
        else:
            para_xml = create_paragraph_xml(item_type, content, para_id)
            xml_items.append(para_xml)
        
        if (i + 1) % 200 == 0:
            print(f"    진행: {i + 1}/{len(all_items)}")
    
    print(f"  ✓ {len(xml_items)}개 항목 XML 생성 완료")
    
    new_xml = header + '\n' + '\n'.join(xml_items) + '\n</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    
    print(f"  ✓ section2.xml 저장 ({len(new_xml):,}자)")
    
    # 4. HWPX 압축
    print("\n4단계: HWPX 파일 생성...")
    
    if os.path.exists(output_hwpx):
        os.remove(output_hwpx)
    
    with zipfile.ZipFile(output_hwpx, 'w', zipfile.ZIP_STORED) as zf:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zf.write(mimetype_path, 'mimetype')
    
    with zipfile.ZipFile(output_hwpx, 'a', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == 'mimetype':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)
    
    file_size = os.path.getsize(output_hwpx)
    print(f"✓ HWPX 생성 완료: {file_size:,} bytes")
    
    shutil.rmtree(temp_dir)
    print(f"✓ 임시 폴더 정리 완료")
    
    return output_hwpx

def main():
    print("\n" + "="*80)
    print("📝 Markdown → HWPX (완벽한 표 테두리)")
    print("="*80)
    print("\n개선사항:")
    print("  ✓ 셀 위치별 정확한 borderFillIDRef 적용")
    print("  ✓ 맨왼쪽: 왼쪽 NONE")
    print("  ✓ 맨오른쪽: 오른쪽 NONE")
    print("  ✓ 중간: 좌우 SOLID")
    print("  ✓ 헤더/데이터/맨아래 행별 구분")
    
    md_chapters = [
        ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
        ("Ⅱ. 이론적 배경", "docs/chapters/02-theoretical-background.md"),
        ("Ⅲ. 시스템 설계", "docs/chapters/03-system-design.md"),
        ("Ⅳ. 시스템 구현", "docs/chapters/04-system-implementation.md"),
        ("Ⅴ. 연구 방법", "docs/chapters/05-research-methods.md"),
        ("Ⅵ. 결과", "docs/chapters/06-results.md"),
        ("Ⅶ. 논의 및 결론", "docs/chapters/07-discussion-conclusion.md"),
        ("Ⅷ. 참고문헌", "docs/chapters/08-references.md"),
    ]
    
    output_file = f"hwp/report_perfect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        result_file = create_hwpx_perfect(md_chapters, output_file)
        
        print("\n" + "="*80)
        print("✅ 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n🎯 표 테두리 개선:")
        print("   - 헤더 맨왼쪽: 19 (왼쪽 NONE, 오른쪽 SOLID)")
        print("   - 헤더 중간: 12 (좌우 SOLID)")
        print("   - 헤더 맨오른쪽: 17 (왼쪽 SOLID, 오른쪽 NONE)")
        print("   - 데이터 맨왼쪽: 11 (왼쪽 NONE)")
        print("   - 데이터 중간: 13 (좌우 SOLID)")
        print("   - 데이터 맨오른쪽: 14 (오른쪽 NONE)")
        print("   - 맨아래: 10, 15")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

