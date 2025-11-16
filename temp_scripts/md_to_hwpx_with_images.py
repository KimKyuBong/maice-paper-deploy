"""
Markdown → HWPX 변환 (표 + 이미지 포함)
"""
import os
import sys
import re
import zipfile
import shutil
import json
from datetime import datetime
from PIL import Image

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

# 새 borderFill XML 정의 (C1용)
NEW_BORDER_FILL_C1 = '''<hh:borderFill id="52" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">
<hh:slash type="NONE" Crooked="0" isCounter="0"/>
<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>
<hh:leftBorder type="NONE" width="0.12 mm" color="#5D5D5D"/>
<hh:rightBorder type="SOLID" width="0.12 mm" color="#5D5D5D"/>
<hh:topBorder type="SOLID" width="0.12 mm" color="#5D5D5D"/>
<hh:bottomBorder type="SOLID" width="0.7 mm" color="#5D5D5D"/>
<hh:diagonal type="SLASH" width="0.1 mm" color="#000000"/>
</hh:borderFill>'''

def clean_markdown(text):
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[.*?\]\]', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def remove_auto_numbering(text, heading_level):
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

def get_image_size_in_hwp_units(png_path):
    """
    PNG 파일 크기를 HWP 단위로 변환
    HWP 단위: 1/7200 inch
    """
    try:
        img = Image.open(png_path)
        width_px, height_px = img.size
        
        # DPI 기본값: 96 (화면 해상도)
        dpi = img.info.get('dpi', (96, 96))[0]
        
        # inch로 변환
        width_inch = width_px / dpi
        height_inch = height_px / dpi
        
        # HWP 단위로 변환 (1 inch = 7200 HWP units)
        width_hwp = int(width_inch * 7200)
        height_hwp = int(height_inch * 7200)
        
        # 최대 너비 제한: A4 용지 너비 (약 115000)
        max_width = 115000
        if width_hwp > max_width:
            ratio = max_width / width_hwp
            width_hwp = max_width
            height_hwp = int(height_hwp * ratio)
        
        return width_hwp, height_hwp
    except Exception as e:
        print(f"이미지 크기 읽기 오류: {png_path} - {e}")
        return 70000, 50000  # 기본값

def create_image_xml(image_id, width, height):
    """
    이미지 XML 생성 (원본 구조 기반, 한 줄로)
    """
    # 원본과 동일하게 한 줄로 생성 (개행 없음)
    xml = f'<hp:pic id="{2000000000 + image_id}" zOrder="{10 + image_id}" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="{927519913 + image_id}" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{width}" height="{height}"/><hp:curSz width="{width}" height="{height}"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{width//2}" centerY="{height//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="diagram{image_id}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{width}" y="0"/><hc:pt2 x="{width}" y="{height}"/><hc:pt3 x="0" y="{height}"/></hp:imgRect><hp:imgClip left="0" right="{width}" top="0" bottom="{height}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{width}" dimheight="{height}"/><hp:effects/><hp:sz width="{width}" widthRelTo="ABSOLUTE" height="{height}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="1765" horzOffset="4764"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic>'
    return xml

def parse_markdown_table(md_text):
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
    tables = []
    lines = md_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            if '|' in next_line and all(c in '|-: ' for c in next_line):
                table_lines = [line, next_line]
                j = i + 2
                while j < len(lines) and '|' in lines[j] and lines[j].strip():
                    table_lines.append(lines[j])
                    j += 1
                
                table_md = '\n'.join(table_lines)
                table_data = parse_markdown_table(table_md)
                
                if table_data:
                    tables.append({
                        'start_line': i,
                        'end_line': j - 1,
                        'data': table_data
                    })
                i = j
                continue
        i += 1
    
    return tables

def get_border_fill_id(row_idx, col_idx, total_rows, total_cols):
    """
    셀 위치에 따라 적절한 borderFillIDRef 반환
    """
    is_header = (row_idx == 0)
    is_last_row = (row_idx == total_rows - 1)
    is_first_col = (col_idx == 0)
    is_last_col = (col_idx == total_cols - 1)
    
    # 헤더 행
    if is_header:
        if is_first_col:
            return "19"  # A1
        elif is_last_col:
            return "17"  # A3
        else:
            return "12"  # A2
    
    # 마지막 행
    elif is_last_row:
        if is_first_col:
            return "52"  # C1 (새로 추가한 스타일)
        elif is_last_col:
            return "15"  # C3
        else:
            return "10"  # C2
    
    # 데이터 행
    else:
        if is_first_col:
            return "9"   # B1
        elif is_last_col:
            return "8"   # B3
        else:
            return "7"   # B2

def create_table_cell_xml(text, row_idx, col_idx, total_rows, total_cols):
    """표 셀 XML 생성"""
    border_fill_id = get_border_fill_id(row_idx, col_idx, total_rows, total_cols)
    
    # 셀 본문 생성
    char_pr_id = "16"  # 표 내부: 맑은 고딕 9pt
    
    # 표 내부 텍스트도 이스케이프
    text = escape_xml(text)
    
    cell_xml = f'''<hp:cell borderFillIDRef="{border_fill_id}">
<hp:cellProperty>
<hp:padding left="1.4 mm" right="1.4 mm" top="0.35 mm" bottom="0.35 mm"/>
</hp:cellProperty>
<hp:p styleIDRef="0" paraPrIDRef="6">
<hp:run charPrIDRef="{char_pr_id}">
<hp:t>{text}</hp:t>
</hp:run>
</hp:p>
</hp:cell>'''
    return cell_xml

def create_table_xml(table_data):
    """Markdown 표 데이터 → HWP 표 XML"""
    headers = table_data['headers']
    rows = table_data['rows']
    total_rows = len(rows) + 1
    total_cols = len(headers)
    col_width = int(115920 / total_cols)
    
    table_xml_parts = [
        '<hp:run charPrIDRef="4">',
        '<hp:ctrl>',
        '<hp:tbl id="2001261744" zOrder="11" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="927519921" pageBreak="CELL">',
        '<hp:shapeComponent>',
        '<hp:offset horzOffset="0" vertOffset="0" groupVertOffset="0" groupVertRelTo="PARA" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" flowWithText="0" allowOverlap="0" holdAnchorAndSO="0"/>',
        '<hp:orgSz width="115920" height="10000"/>',
        '<hp:curSz width="115920" height="10000"/>',
        '<hp:flip/>',
        '</hp:shapeComponent>',
        '<hp:caption>',
        '<hp:side type="TOP"/>',
        '<hp:p styleIDRef="10" paraPrIDRef="14"><hp:run charPrIDRef="11"/></hp:p>',
        '</hp:caption>',
        '<hp:table pageBreak="CELL" repeatHeader="0" rowCnt="' + str(total_rows) + '" colCnt="' + str(total_cols) + '" cellSpacing="0" borderFillIDRef="4">',
        '<hp:tr>',
    ]
    
    # 헤더 행
    for col_idx, header in enumerate(headers):
        cell_xml = create_table_cell_xml(header, 0, col_idx, total_rows, total_cols)
        table_xml_parts.append(cell_xml)
    
    table_xml_parts.append('</hp:tr>')
    
    # 데이터 행
    for row_idx, row in enumerate(rows, start=1):
        table_xml_parts.append('<hp:tr>')
        for col_idx, cell in enumerate(row):
            cell_xml = create_table_cell_xml(cell, row_idx, col_idx, total_rows, total_cols)
            table_xml_parts.append(cell_xml)
        table_xml_parts.append('</hp:tr>')
    
    table_xml_parts.extend([
        '</hp:table>',
        '</hp:tbl>',
        '</hp:ctrl>',
        '</hp:run>'
    ])
    
    return '\n'.join(table_xml_parts)

def parse_markdown(md_text):
    """
    Markdown → 구조화된 요소 리스트
    이미지 참조(머메이드 블록)도 파싱
    """
    md_text = clean_markdown(md_text)
    
    # 표 추출
    tables = extract_tables_from_markdown(md_text)
    table_ranges = [(t['start_line'], t['end_line']) for t in tables]
    
    # 머메이드 블록 추출
    mermaid_blocks = []
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    for match in re.finditer(mermaid_pattern, md_text, re.DOTALL):
        # 블록 앞 컨텍스트에서 그림 번호 찾기
        start_pos = match.start()
        context_before = md_text[max(0, start_pos - 500):start_pos]
        
        # [그림X-Y] 형식 찾기
        caption_match = re.search(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', context_before)
        
        if caption_match:
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            roman = caption_match.group(1)
            num = caption_match.group(2)
            chapter_num = roman_map.get(roman, '?')
            figure_num = f"{chapter_num}-{num}"
            
            mermaid_blocks.append({
                'figure_num': figure_num,
                'start': match.start(),
                'end': match.end()
            })
    
    # 머메이드 블록 제거 (표는 나중에 처리)
    for block in reversed(mermaid_blocks):
        md_text = md_text[:block['start']] + f"[MERMAID:{block['figure_num']}]" + md_text[block['end']:]
    
    lines = md_text.split('\n')
    elements = []
    
    def in_table_range(line_num):
        for start, end in table_ranges:
            if start <= line_num <= end:
                return True
        return False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 표 처리
        if in_table_range(i):
            for table in tables:
                if table['start_line'] == i:
                    elements.append({
                        'type': 'table',
                        'data': table['data']
                    })
                    i = table['end_line'] + 1
                    break
            else:
                i += 1
            continue
        
        # 머메이드 이미지 참조
        if line.startswith('[MERMAID:'):
            figure_num = line[9:-1]  # [MERMAID:3-1] → 3-1
            elements.append({
                'type': 'mermaid_image',
                'figure_num': figure_num
            })
            i += 1
            continue
        
        # 제목 파싱
        if line.startswith('#'):
            level = len(line.split()[0])
            text = line.lstrip('#').strip()
            
            if level <= 5:
                heading_key = f'heading{level}'
                text = remove_auto_numbering(text, heading_key)
                
                # 볼드 제거
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                
                elements.append({
                    'type': heading_key,
                    'text': text
                })
        
        # 글머리표 리스트
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            
            # 길이 또는 콜론으로 구분
            if len(text) > 50 or ':' in text:
                list_type = 'list_para'
            else:
                list_type = 'list_bullet'
            
            elements.append({
                'type': list_type,
                'text': text
            })
        
        # 번호 리스트
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line).strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            elements.append({
                'type': 'numbered_list',
                'text': text
            })
        
        # 빈 줄
        elif not line:
            elements.append({'type': 'empty', 'text': ''})
        
        # 본문
        else:
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            elements.append({
                'type': 'body',
                'text': text
            })
        
        i += 1
    
    return elements

def escape_xml(text):
    """XML 특수문자 이스케이프"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def create_paragraph_xml(element):
    """요소 → XML 생성"""
    elem_type = element['type']
    
    if elem_type == 'table':
        return create_table_xml(element['data'])
    
    if elem_type == 'mermaid_image':
        return f"[IMAGE_PLACEHOLDER:{element['figure_num']}]"
    
    text = element.get('text', '')
    text = escape_xml(text)  # XML 특수문자 이스케이프
    style = STYLE_MAP.get(elem_type, STYLE_MAP['body'])
    
    xml = f'''<hp:p styleIDRef="{style['styleIDRef']}" paraPrIDRef="{style['paraPrIDRef']}">
<hp:run charPrIDRef="{style['charPrIDRef']}">
<hp:t>{text}</hp:t>
</hp:run>
</hp:p>'''
    
    return xml

def create_image_paragraph_xml(image_id, width, height):
    """이미지를 포함한 문단 XML 생성 (원본과 완전히 동일)"""
    pic_xml = create_image_xml(image_id, width, height)
    
    # 원본과 동일하게 한 줄로 생성
    xml = f'<hp:p id="0" paraPrIDRef="37" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4">{pic_xml}<hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="6440" vertsize="1100" textheight="1100" baseline="935" spacing="880" horzpos="0" horzsize="43936" flags="1441792"/></hp:linesegarray></hp:p>'
    
    return xml

def add_custom_borderfills_to_header(header_path):
    """header.xml에 커스텀 borderFill 추가"""
    with open(header_path, 'r', encoding='utf-8') as f:
        header_content = f.read()
    
    # </hh:borderFills> 태그 앞에 삽입
    if 'id="52"' not in header_content:
        insert_pos = header_content.find('</hh:borderFills>')
        if insert_pos != -1:
            header_content = header_content[:insert_pos] + NEW_BORDER_FILL_C1 + '\n' + header_content[insert_pos:]
            
            with open(header_path, 'w', encoding='utf-8') as f:
                f.write(header_content)
            
            print("✓ 커스텀 borderFill (ID 52) 추가 완료")

def copy_images_to_bindata(extracted_dir, image_mapping, use_png=True):
    """
    PNG 파일들을 BinData 폴더에 복사 (PNG 그대로 또는 BMP로 변환)
    image_mapping: { 'figure_num': 'png_file', ... }
    use_png: True면 PNG 그대로, False면 BMP로 변환
    """
    bindata_dir = os.path.join(extracted_dir, "BinData")
    if not os.path.exists(bindata_dir):
        os.makedirs(bindata_dir)
    
    png_source_dir = "docs/diagrams/output/png"
    
    copied_images = {}
    image_id = 100  # 시작 ID
    
    for figure_num, png_file in image_mapping.items():
        src_path = os.path.join(png_source_dir, png_file)
        if not os.path.exists(src_path):
            print(f"⚠ PNG 파일 없음: {src_path}")
            continue
        
        if use_png:
            # PNG 그대로 복사
            dst_filename = f"diagram{image_id}.PNG"
            dst_path = os.path.join(bindata_dir, dst_filename)
            shutil.copy2(src_path, dst_path)
        else:
            # PNG를 BMP로 변환
            from PIL import Image
            img = Image.open(src_path)
            
            # RGB 모드로 변환
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            dst_filename = f"diagram{image_id}.BMP"
            dst_path = os.path.join(bindata_dir, dst_filename)
            img.save(dst_path, 'BMP')
        
        # 이미지 크기 읽기
        width, height = get_image_size_in_hwp_units(src_path)
        
        copied_images[figure_num] = {
            'id': image_id,
            'filename': dst_filename,
            'width': width,
            'height': height
        }
        
        format_name = "PNG" if use_png else "BMP"
        print(f"✓ {figure_num} → {dst_filename} ({width}x{height})")
        image_id += 1
    
    return copied_images

def create_hwpx_final(output_filename=None):
    if output_filename is None:
        from datetime import datetime
        output_filename = f"hwp/report_with_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    """최종 HWPX 생성 (이미지 포함)"""
    template_hwpx = "hwp/report_backup_20251112_020239.hwpx"
    temp_dir = "hwp/extracted_hwpx"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    print("\n" + "="*80)
    print("HWPX 생성 시작 (이미지 포함)")
    print("="*80)
    
    # 1. 원본 HWPX 압축 해제
    with zipfile.ZipFile(template_hwpx, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    print("✓ 원본 HWPX 압축 해제 완료")
    
    # 2. 커스텀 borderFill 추가
    header_path = os.path.join(temp_dir, "Contents", "header.xml")
    add_custom_borderfills_to_header(header_path)
    
    # 3. 이미지 매핑 로드
    with open('hwp/mermaid_to_png_mapping.json', 'r', encoding='utf-8') as f:
        mappings = json.load(f)
    
    image_mapping = {m['figure_num']: m['png_file'] for m in mappings}
    
    # 4. 이미지를 BinData에 복사 (PNG 그대로)
    copied_images = copy_images_to_bindata(temp_dir, image_mapping, use_png=True)
    
    # 5. Markdown 파일들 파싱
    md_files = [
        ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
        ("Ⅱ. 이론적 배경", "docs/chapters/02-theoretical-background.md"),
        ("Ⅲ. 시스템 설계", "docs/chapters/03-system-design.md"),
        ("Ⅳ. 시스템 구현", "docs/chapters/04-system-implementation.md"),
        ("Ⅴ. 연구 방법", "docs/chapters/05-research-methods.md"),
        ("Ⅵ. 결과", "docs/chapters/06-results.md"),
        ("Ⅶ. 논의 및 결론", "docs/chapters/07-discussion-conclusion.md"),
        ("Ⅷ. 참고문헌", "docs/chapters/08-references.md"),
    ]
    
    all_paragraphs = []
    
    for chapter_name, md_path in md_files:
        if not os.path.exists(md_path):
            print(f"⚠ 파일 없음: {md_path}")
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        elements = parse_markdown(md_content)
        
        for elem in elements:
            para_xml = create_paragraph_xml(elem)
            
            # 이미지 플레이스홀더 교체
            if '[IMAGE_PLACEHOLDER:' in para_xml:
                figure_num = re.search(r'\[IMAGE_PLACEHOLDER:(.*?)\]', para_xml).group(1)
                
                if figure_num in copied_images:
                    img_info = copied_images[figure_num]
                    image_xml = create_image_paragraph_xml(img_info['id'], img_info['width'], img_info['height'])
                    para_xml = image_xml
                else:
                    # 이미지가 없으면 빈 문단으로 교체
                    para_xml = '<hp:p styleIDRef="0" paraPrIDRef="6"><hp:run charPrIDRef="5"><hp:t></hp:t></hp:run></hp:p>'
            
            all_paragraphs.append(para_xml)
        
        print(f"✓ {chapter_name}: {len(elements)}개 요소 파싱")
    
    print(f"\n총 {len(all_paragraphs)}개 문단 생성 (이미지 포함)")
    
    # 6. section2.xml 수정
    section2_path = os.path.join(temp_dir, "Contents", "section2.xml")
    
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    # 첫 번째 <hp:p> 태그 전까지의 헤더 추출
    first_para_pos = original_xml.find('<hp:p')
    
    if first_para_pos == -1:
        close_tag_pos = original_xml.rfind('</hs:sec>')
        header = original_xml[:close_tag_pos] if close_tag_pos != -1 else original_xml
    else:
        header = original_xml[:first_para_pos]
    
    # 새 section2.xml 생성
    new_section2 = header + '\n' + '\n'.join(all_paragraphs) + '\n</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_section2)
    
    print("✓ section2.xml 교체 완료")
    
    # 7. 새 HWPX 압축
    # 먼저 mimetype을 압축 없이 추가
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_STORED) as zipf:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zipf.write(mimetype_path, 'mimetype')
    
    # 나머지 파일들을 압축하여 추가
    with zipfile.ZipFile(output_filename, 'a', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == 'mimetype':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    file_size = os.path.getsize(output_filename)
    print(f"\n✓ 새 HWPX 생성 완료: {output_filename}")
    print(f"✓ 파일 크기: {file_size:,} bytes")
    print("="*80)

if __name__ == "__main__":
    create_hwpx_final()

