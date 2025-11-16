"""
Markdown → HWPX 변환 (목차 + 본문 + 부록)
"""
import os
import sys
import re
import zipfile
import shutil
import json
import hashlib
import base64
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('mermaid_conversion.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

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
    'toc_title': {'styleIDRef': '1', 'paraPrIDRef': '1', 'charPrIDRef': '1'},  # 차례/참고문헌 제목
    'toc_entry': {'styleIDRef': '4', 'paraPrIDRef': '2', 'charPrIDRef': '2'},  # 차례 표,그림,수식
    'appendix': {'styleIDRef': '5', 'paraPrIDRef': '20', 'charPrIDRef': '14'}, # 부록 제목 (Ⅰ급과 동일)
}

def mermaid_to_png(mermaid_code, output_path, width=1920, height=1080):
    """Playwright로 머메이드 다이어그램을 PNG로 변환"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: white;
            }}
            .mermaid {{
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
        <script>
            mermaid.initialize({{ 
                startOnLoad: true,
                theme: 'default',
                themeVariables: {{
                    fontSize: '16px'
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html_template)
            page.wait_for_timeout(2000)
            
            svg = page.query_selector('svg')
            if svg:
                svg.screenshot(path=output_path)
                browser.close()
                return True
            else:
                browser.close()
                return False
    except Exception as e:
        print(f"[ERROR] 머메이드 변환 실패: {e}")
        return False

def clean_markdown(text):
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[.*?\]\]', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def remove_auto_numbering(text, heading_level):
    """HWP 자동 번호와 중복되지 않도록 Markdown 번호 제거"""
    if heading_level == 'heading1':
        text = re.sub(r'^[IⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s*', '', text)
    elif heading_level == 'heading2':
        text = re.sub(r'^\d+(?:\.\d+)*\.\s*', '', text)
    elif heading_level == 'heading3':
        text = re.sub(r'^[가-힣]\.\s*', '', text)
    elif heading_level == 'heading4':
        text = re.sub(r'^\d+(?:\.\d+)*[\.\)]\s*', '', text)
    elif heading_level == 'heading5':
        text = re.sub(r'^[가-힣][\.\)]\s*', '', text)
    return text

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
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

def get_border_fill_id(row_idx, col_idx, total_rows, total_cols):
    """셀 위치별 borderFillIDRef 반환"""
    is_header = (row_idx == 0)
    is_last_row = (row_idx == total_rows - 1)
    is_first_col = (col_idx == 0)
    is_last_col = (col_idx == total_cols - 1)
    
    if is_header:
        if is_first_col:
            return "19"
        elif is_last_col:
            return "17"
        else:
            return "12"
    elif is_last_row:
        if is_first_col:
            return "16"
        elif is_last_col:
            return "15"
        else:
            return "10"
    else:
        if is_first_col:
            return "9"
        elif is_last_col:
            return "8"
        else:
            return "7"

def create_table_cell_xml(text, row, col, total_rows, total_cols, is_header=False):
    escaped_text = escape_xml(text)
    border_fill_id = get_border_fill_id(row, col, total_rows, total_cols)
    header_attr = "1" if is_header else "0"
    style_id = "20"
    char_pr_id = "16"
    
    return f'''<hp:tc name="" header="{header_attr}" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="{border_fill_id}">
<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">
<hp:p id="2147483648" paraPrIDRef="9" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">
<hp:run charPrIDRef="{char_pr_id}"><hp:t>{escaped_text}</hp:t></hp:run>
</hp:p>
</hp:subList>
<hp:cellAddr colAddr="{col}" rowAddr="{row}"/>
<hp:cellSpan colSpan="1" rowSpan="1"/>
<hp:cellSz width="10915" height="3000"/>
<hp:cellMargin left="141" right="141" top="141" bottom="141"/>
</hp:tc>'''

def create_table_xml(table_data, table_id):
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
    
    table_xml += '<hp:tr>'
    for col_idx, header in enumerate(headers):
        table_xml += create_table_cell_xml(header, 0, col_idx, rows, cols, is_header=True)
    table_xml += '</hp:tr>\n'
    
    for row_idx, row_data in enumerate(data_rows, 1):
        table_xml += '<hp:tr>'
        for col_idx, cell_text in enumerate(row_data):
            table_xml += create_table_cell_xml(cell_text, row_idx, col_idx, rows, cols, is_header=False)
        table_xml += '</hp:tr>\n'
    
    table_xml += '</hp:tbl>'
    return table_xml

def read_table_and_figure_list(md_files):
    """표차례와 그림차례 읽기"""
    tables = {}
    figures = {}
    
    for chapter_name, md_path in md_files:
        if not os.path.exists(md_path):
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 표 캡션 찾기
        table_captions = re.findall(r'\[표([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]\s*(.+?)(?:\n|$)', content)
        for roman, num, title in table_captions:
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            chapter_num = roman_map.get(roman, '?')
            table_id = f"{chapter_num}-{num}"
            tables[table_id] = title.strip()
        
        # 그림 캡션 찾기
        figure_captions = re.findall(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]\s*(.+?)(?:\n|$)', content)
        for roman, num, title in figure_captions:
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            chapter_num = roman_map.get(roman, '?')
            figure_id = f"{chapter_num}-{num}"
            figures[figure_id] = title.strip()
    
    return tables, figures

def convert_single_mermaid(mermaid_code, figure_num, output_dir, figure_title=""):
    """단일 머메이드 다이어그램 변환 (병렬 처리용)"""
    png_filename = f"diagram_{figure_num.replace('-', '_')}.png"
    png_path = os.path.join(output_dir, png_filename)
    
    try:
        logging.info(f"머메이드 변환 시작: {figure_num} - {figure_title}")
        
        if mermaid_to_png(mermaid_code, png_path):
            logging.info(f"머메이드 변환 성공: {figure_num} -> {png_filename}")
            return (figure_num, png_path, png_filename, True, None)
        else:
            error_msg = f"변환 실패 (반환값 False): {figure_num}"
            logging.error(error_msg)
            return (figure_num, None, png_filename, False, error_msg)
    
    except Exception as e:
        error_msg = f"머메이드 변환 예외 발생: {figure_num} - {str(e)}"
        logging.error(error_msg, exc_info=True)
        return (figure_num, None, png_filename, False, error_msg)

def extract_and_convert_mermaid(md_text, output_dir="mermaid_diagrams", max_workers=4, figure_list=None):
    """머메이드 코드를 추출하고 PNG로 병렬 변환"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    logging.info(f"머메이드 다이어그램 변환 시작 (병렬 처리: {max_workers} workers)")
    
    if figure_list:
        logging.info(f"그림차례: {len(figure_list)}개 그림 발견")
        for fig_id, fig_title in sorted(figure_list.items()):
            logging.info(f"  - [{fig_id}] {fig_title}")
    
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    mermaid_tasks = []
    
    # 1단계: 모든 머메이드 블록 수집
    for match in re.finditer(mermaid_pattern, md_text, re.DOTALL):
        mermaid_code = match.group(1)
        start_pos = match.start()
        context_before = md_text[max(0, start_pos - 500):start_pos]
        
        # [그림X-Y] 찾기 (가장 가까운 = 마지막 매치)
        caption_matches = list(re.finditer(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', context_before))
        
        if caption_matches:
            caption_match = caption_matches[-1]
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            roman = caption_match.group(1)
            num = caption_match.group(2)
            chapter_num = roman_map.get(roman, '?')
            figure_num = f"{chapter_num}-{num}"
            
            # 그림 제목 가져오기
            figure_title = figure_list.get(figure_num, "") if figure_list else ""
            
            mermaid_tasks.append((mermaid_code, figure_num, figure_title))
    
    logging.info(f"총 {len(mermaid_tasks)}개 머메이드 블록 발견")
    
    # 2단계: 병렬 변환
    converted_diagrams = {}
    failed_diagrams = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 모든 작업 제출
        future_to_task = {
            executor.submit(convert_single_mermaid, code, fig_num, output_dir, fig_title): fig_num
            for code, fig_num, fig_title in mermaid_tasks
        }
        
        # 완료되는 대로 결과 수집
        for future in as_completed(future_to_task):
            try:
                figure_num, png_path, png_filename, success, error_msg = future.result()
                
                if success:
                    converted_diagrams[figure_num] = png_path
                    print(f"  머메이드 다이어그램 변환 중: {figure_num}...")
                    print(f"    [OK] {png_filename}")
                else:
                    failed_diagrams.append((figure_num, error_msg))
                    print(f"  머메이드 다이어그램 변환 중: {figure_num}...")
                    print(f"    [ERROR] 변환 실패: {figure_num}")
                    if error_msg:
                        print(f"           {error_msg}")
            
            except Exception as e:
                figure_num = future_to_task.get(future, "Unknown")
                error_msg = f"결과 수집 중 예외 발생: {figure_num} - {str(e)}"
                logging.error(error_msg, exc_info=True)
                failed_diagrams.append((figure_num, error_msg))
                print(f"    [ERROR] {error_msg}")
    
    # 최종 요약
    logging.info(f"머메이드 변환 완료: 성공 {len(converted_diagrams)}/{len(mermaid_tasks)}")
    
    if failed_diagrams:
        logging.warning(f"변환 실패한 다이어그램 {len(failed_diagrams)}개:")
        for fig_num, err in failed_diagrams:
            logging.warning(f"  - {fig_num}: {err}")
    
    return converted_diagrams

def parse_markdown_with_tables(md_text):
    """마크다운 파싱 (표, 이미지, 코드 블록 처리)"""
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    mermaid_replacements = []
    
    for match in re.finditer(mermaid_pattern, md_text, re.DOTALL):
        start_pos = match.start()
        context_before = md_text[max(0, start_pos - 500):start_pos]
        
        # [그림X-Y] 찾기 (가장 가까운 = 마지막 매치)
        caption_matches = list(re.finditer(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', context_before))
        
        if caption_matches:
            caption_match = caption_matches[-1]  # 가장 가까운 캡션
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            roman = caption_match.group(1)
            num = caption_match.group(2)
            chapter_num = roman_map.get(roman, '?')
            figure_num = f"{chapter_num}-{num}"
            
            marker = f"[MERMAID_IMAGE:{figure_num}]"
            mermaid_replacements.append((match.start(), match.end(), marker))
    
    for start, end, marker in reversed(mermaid_replacements):
        md_text = md_text[:start] + marker + md_text[end:]
    
    code_block_pattern = r'```[a-z]*\n(.*?)\n```'
    code_replacements = []
    
    for match in re.finditer(code_block_pattern, md_text, re.DOTALL):
        marker = f"[CODE_BLOCK_{len(code_replacements)}]"
        code_replacements.append((match.start(), match.end(), marker, match.group(0)))
    
    for start, end, marker, original in reversed(code_replacements):
        md_text = md_text[:start] + marker + md_text[end:]
    
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
        
        if line.startswith('[MERMAID_IMAGE:'):
            figure_num = line[15:-1]
            paragraphs.append(('mermaid_image', figure_num))
            i += 1
            continue
        
        if line.startswith('[CODE_BLOCK_'):
            paragraphs.append(('empty', ''))
            i += 1
            continue
        
        if not line:
            paragraphs.append(('empty', ''))
        elif line.startswith('# '):
            text = line[2:].strip()
            text = remove_all_markdown_formatting(text)
            text = remove_auto_numbering(text, 'heading1')
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = line[3:].strip()
            text = remove_all_markdown_formatting(text)
            text = remove_auto_numbering(text, 'heading2')
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = line[4:].strip()
            text = remove_all_markdown_formatting(text)
            text = remove_auto_numbering(text, 'heading3')
            paragraphs.append(('heading3', text))
        elif line.startswith('#### '):
            text = line[5:].strip()
            text = remove_all_markdown_formatting(text)
            text = remove_auto_numbering(text, 'heading4')
            paragraphs.append(('heading4', text))
        elif line.startswith('##### '):
            text = line[6:].strip()
            text = remove_all_markdown_formatting(text)
            text = remove_auto_numbering(text, 'heading5')
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

def remove_all_markdown_formatting(text):
    """모든 Markdown 포맷 제거"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def create_paragraph_xml(style_type, text, para_id, image_info=None):
    """문단 XML 생성"""
    if style_type == 'mermaid_image' and image_info and text in image_info:
        img_data = image_info[text]
        return create_image_paragraph_xml(img_data)
    
    style_info = STYLE_MAP.get(style_type, STYLE_MAP['body'])
    
    style_id = style_info['styleIDRef']
    para_pr = style_info['paraPrIDRef']
    char_pr = style_info['charPrIDRef']
    
    escaped_text = escape_xml(text) if text else ''
    
    run = f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>' if text else f'<hp:run charPrIDRef="{char_pr}"/>'
    
    return f'<hp:p id="{para_id}" paraPrIDRef="{para_pr}" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">{run}</hp:p>'

def create_image_paragraph_xml(img_data):
    """PNG 이미지 문단 XML"""
    image_id = img_data['id']
    img_w = img_data['img_width']
    img_h = img_data['img_height']
    display_w = img_data['display_width']
    display_h = img_data['display_height']
    
    scale_x = display_w / img_w if img_w > 0 else 1
    scale_y = display_h / img_h if img_h > 0 else 1
    
    pic_xml = f'<hp:pic id="{2000000000 + image_id}" zOrder="{10 + image_id}" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="{927519913 + image_id}" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{display_w}" height="{display_h}"/><hp:curSz width="{display_w}" height="{display_h}"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{display_w//2}" centerY="{display_h//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="{scale_x}" e2="0" e3="0" e4="0" e5="{scale_y}" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image{image_id}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{img_w}" y="0"/><hc:pt2 x="{img_w}" y="{img_h}"/><hc:pt3 x="0" y="{img_h}"/></hp:imgRect><hp:imgClip left="0" right="{img_w}" top="0" bottom="{img_h}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{img_w}" dimheight="{img_h}"/><hp:effects/><hp:sz width="{display_w}" widthRelTo="ABSOLUTE" height="{display_h}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="1765" horzOffset="4764"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic>'
    
    return f'<hp:p id="0" paraPrIDRef="37" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4">{pic_xml}<hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="6440" vertsize="1100" textheight="1100" baseline="935" spacing="880" horzpos="0" horzsize="43936" flags="1441792"/></hp:linesegarray></hp:p>'

def create_table_paragraph_xml(table_data, para_id, table_id):
    """표 문단 XML"""
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

def copy_images_to_bindata_simple(temp_dir, mermaid_pngs):
    """PNG 이미지를 BinData에 복사하고 content.hpf에 등록"""
    bindata_dir = os.path.join(temp_dir, "BinData")
    
    image_info = {}
    image_id = 39
    
    hpf_items = []
    
    for figure_num, src_path in sorted(mermaid_pngs.items()):
        if not os.path.exists(src_path):
            print(f"  [WARNING] PNG 파일을 찾을 수 없음: {src_path}")
            continue
        
        dst_filename = f"image{image_id}.png"
        dst_path = os.path.join(bindata_dir, dst_filename)
        shutil.copy2(src_path, dst_path)
        
        with open(dst_path, 'rb') as f:
            data = f.read()
            hash_md5 = hashlib.md5(data).digest()
            hashkey = base64.b64encode(hash_md5).decode('ascii')
        
        img = Image.open(src_path)
        width_px, height_px = img.size
        dpi = img.info.get('dpi', (96, 96))[0]
        
        img_width_hwp = int(width_px / dpi * 7200)
        img_height_hwp = int(height_px / dpi * 7200)
        
        max_width = 80000
        if img_width_hwp > max_width:
            scale = max_width / img_width_hwp
            display_width = max_width
            display_height = int(img_height_hwp * scale)
        else:
            display_width = img_width_hwp
            display_height = img_height_hwp
        
        image_info[figure_num] = {
            'id': image_id,
            'filename': dst_filename,
            'img_width': img_width_hwp,
            'img_height': img_height_hwp,
            'display_width': display_width,
            'display_height': display_height,
            'hashkey': hashkey
        }
        
        hpf_item = f'<opf:item id="image{image_id}" href="BinData/{dst_filename}" media-type="image/png" isEmbeded="1" hashkey="{hashkey}"/>'
        hpf_items.append(hpf_item)
        
        print(f"  [OK] {figure_num} -> {dst_filename}")
        
        image_id += 1
    
    if hpf_items:
        hpf_path = os.path.join(temp_dir, "Contents", "content.hpf")
        with open(hpf_path, 'r', encoding='utf-8') as f:
            hpf_content = f.read()
        
        manifest_end = hpf_content.find('</opf:manifest>')
        if manifest_end != -1:
            all_items = '\n'.join(hpf_items)
            hpf_content = hpf_content[:manifest_end] + all_items + '\n' + hpf_content[manifest_end:]
            
            with open(hpf_path, 'w', encoding='utf-8') as f:
                f.write(hpf_content)
            
            print(f"  [OK] content.hpf에 {len(hpf_items)}개 이미지 등록")
    
    return image_info

# ==================== 목차 생성 함수 ====================

def extract_headings_from_markdown_raw(md_text):
    """Markdown에서 원본 제목 추출 (번호 유지)"""
    lines = md_text.split('\n')
    headings = []
    
    for line in lines:
        line = line.rstrip()
        
        if line.startswith('# '):
            text = line[2:].strip()
            # 볼드, 이탤릭 제거
            text = remove_all_markdown_formatting(text)
            headings.append({
                'level': 1,
                'text': text,  # 번호 유지
                'original': line
            })
        elif line.startswith('## '):
            text = line[3:].strip()
            text = remove_all_markdown_formatting(text)
            headings.append({
                'level': 2,
                'text': text,  # 번호 유지
                'original': line
            })
        elif line.startswith('### '):
            text = line[4:].strip()
            text = remove_all_markdown_formatting(text)
            headings.append({
                'level': 3,
                'text': text,  # 번호 유지
                'original': line
            })
        elif line.startswith('#### '):
            text = line[5:].strip()
            text = remove_all_markdown_formatting(text)
            headings.append({
                'level': 4,
                'text': text,
                'original': line
            })
        elif line.startswith('##### '):
            text = line[6:].strip()
            text = remove_all_markdown_formatting(text)
            headings.append({
                'level': 5,
                'text': text,
                'original': line
            })
    
    return headings

def create_toc_section_xml(headings):
    """목차 섹션 XML 생성 (section1.xml 전체)"""
    xml_header = '''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0">'''
    
    # 섹션 설정 (원본과 동일하게 - outlineShapeIDRef="4")
    sec_pr = '''<hp:p id="0" paraPrIDRef="5" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4"><hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl><hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="4" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0"><hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/><hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/><hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/><hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/><hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY"><hp:margin header="0" footer="4251" gutter="0" left="8503" right="7086" top="9921" bottom="7086"/></hp:pagePr><hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/></hp:footNotePr><hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/><hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/><hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/></hp:endNotePr><hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill><hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill></hp:secPr></hp:run></hp:p>'''
    
    xml_items = []
    para_id = 100000000
    
    # 목차 제목 (원본과 동일: paraPrIDRef="15", styleIDRef="1", charPrIDRef="6")
    toc_title = f'<hp:p id="{para_id}" paraPrIDRef="15" styleIDRef="1" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="6"><hp:t>목 차</hp:t></hp:run></hp:p>'
    xml_items.append(toc_title)
    para_id += 1
    
    # 빈 줄 (원본과 동일: paraPrIDRef="14", styleIDRef="4", charPrIDRef="5")
    xml_items.append(f'<hp:p id="{para_id}" paraPrIDRef="14" styleIDRef="4" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="5"/></hp:p>')
    para_id += 1
    
    # 목차 항목들 - 탭과 페이지 번호 포함
    page_num = 1  # 페이지 번호 추정
    for heading in headings:
        level = heading['level']
        text = heading['text']
        
        # 들여쓰기와 탭 너비 (level에 따라 다름)
        if level == 1:
            indent = ''
            tab_width = '38752'  # Ⅰ급
        elif level == 2:
            indent = ''
            tab_width = '34792'  # 1급
        elif level == 3:
            indent = '   '  # 공백 3개
            tab_width = '25000'  # 가급
        elif level == 4:
            indent = '      '  # 공백 6개
            tab_width = '20000'  # 1)급
        else:
            indent = '         '  # 공백 9개
            tab_width = '15000'  # 가)급
        
        # 목차 항목 (원본과 동일: paraPrIDRef="14", styleIDRef="4", charPrIDRef="5")
        toc_entry = f'''<hp:p id="{para_id}" paraPrIDRef="14" styleIDRef="4" pageBreak="0" columnBreak="0" merged="0">'''
        toc_entry += f'''<hp:run charPrIDRef="5"><hp:t>{indent}{escape_xml(text)}<hp:tab width="{tab_width}" leader="3" type="2"/>{page_num}</hp:t></hp:run>'''
        toc_entry += '</hp:p>'
        
        xml_items.append(toc_entry)
        para_id += 1
        
        # 페이지 번호 증가 (간단한 추정)
        if level == 1:
            page_num += 5
        elif level == 2:
            page_num += 2
    
    return xml_header + sec_pr + '\n'.join(xml_items) + '\n</hs:sec>'

# ==================== 부록 처리 함수 ====================

def parse_appendix_markdown(md_text):
    """부록 마크다운 파싱"""
    lines = md_text.split('\n')
    paragraphs = []
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            paragraphs.append(('empty', ''))
        # 부록 제목 감지: "부록 A.", "부록 B." 등
        elif re.match(r'^부록\s+[A-Z]\.', line):
            text = line.strip()
            paragraphs.append(('appendix', text))
        elif line.startswith('# '):
            text = line[2:].strip()
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = line[3:].strip()
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = line[4:].strip()
            paragraphs.append(('heading3', text))
        else:
            paragraphs.append(('body', line))
    
    return paragraphs

# ==================== 메인 함수 ====================

def create_hwpx_with_toc(md_files, appendix_files, output_hwpx):
    """목차 + 본문 + 부록 포함 HWPX 생성"""
    print("="*80)
    print("Markdown → HWPX 변환 (목차 + 본문 + 부록)")
    print("="*80)
    
    # 1. 압축 해제
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_hwpx = os.path.join(script_dir, "report_backup_20251112_020239.hwpx")
    temp_dir = os.path.join(script_dir, "temp_hwpx_toc")
    
    print("\n1단계: 기존 HWPX 압축 해제...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"[OK] 압축 해제 완료")
    
    # 1.5. 표차례와 그림차례 읽기
    print("\n1.5단계: 표차례와 그림차례 읽기...")
    tables_list, figures_list = read_table_and_figure_list(md_files)
    print(f"[OK] 표 {len(tables_list)}개, 그림 {len(figures_list)}개 발견")
    
    # 2. 머메이드 다이어그램 변환
    print("\n2단계: 머메이드 다이어그램 변환...")
    all_md_content = ""
    for chapter_name, md_path in md_files:
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                all_md_content += f.read() + "\n\n"
    
    mermaid_pngs = extract_and_convert_mermaid(all_md_content, "mermaid_diagrams", max_workers=4, figure_list=figures_list)
    print(f"[OK] {len(mermaid_pngs)}개 다이어그램 변환 완료")
    
    # 3. 이미지 복사
    print("\n3단계: 이미지 복사...")
    image_info = copy_images_to_bindata_simple(temp_dir, mermaid_pngs)
    print(f"[OK] {len(image_info)}개 이미지 복사 완료")
    
    # 4. 본문 Markdown 파싱
    print("\n4단계: 본문 Markdown 파싱...")
    all_items = []
    chapter_names = []
    
    for chapter_name, md_path in md_files:
        chapter_names.append(chapter_name)
        if not os.path.exists(md_path):
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md_content = clean_markdown(md_content)
        items = parse_markdown_with_tables(md_content)
        all_items.extend(items)
        
        table_count = sum(1 for item_type, _ in items if item_type == 'table')
        para_count = len(items) - table_count
        print(f"  [OK] {chapter_name}: {para_count}개 문단, {table_count}개 표")
    
    # 5. 부록 파싱
    print("\n5단계: 부록 파싱...")
    appendix_items = []
    for appendix_name, md_path in appendix_files:
        if not os.path.exists(md_path):
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            appendix_content = f.read()
        
        items = parse_appendix_markdown(appendix_content)
        appendix_items.extend(items)
        print(f"  [OK] {appendix_name}: {len(items)}개 항목")
    
    # 6. 목차 생성 (section1.xml) - Markdown 원본에서 번호 유지
    print("\n6단계: 목차 생성...")
    
    # 모든 Markdown에서 제목 추출 (번호 유지)
    all_headings = []
    for chapter_name, md_path in md_files:
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            md_content = clean_markdown(md_content)
            headings = extract_headings_from_markdown_raw(md_content)
            all_headings.extend(headings)
    
    toc_section_xml = create_toc_section_xml(all_headings)
    
    section1_path = os.path.join(temp_dir, 'Contents', 'section1.xml')
    with open(section1_path, 'w', encoding='utf-8') as f:
        f.write(toc_section_xml)
    
    print(f"[OK] {len(all_headings)}개 제목으로 목차 생성 (section1.xml)")
    
    # 7. 본문 XML 생성 (section2.xml)
    print("\n7단계: section2.xml 재생성...")
    section2_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    header = extract_section_header(original_xml)
    
    print(f"  XML 생성 중...")
    xml_items = []
    
    # 7-1. 본문 추가 (목차 없이 바로 본문)
    table_counter = 900000000
    para_id = 500000000
    
    for i, (item_type, content) in enumerate(all_items):
        para_id += 1
        
        if item_type == 'table':
            table_counter += 1
            para_xml = create_table_paragraph_xml(content, para_id, table_counter)
            xml_items.append(para_xml)
        else:
            para_xml = create_paragraph_xml(item_type, content, para_id, image_info)
            xml_items.append(para_xml)
        
        if (i + 1) % 200 == 0:
            print(f"    본문 진행: {i + 1}/{len(all_items)}")
    
    # 7-2. 부록 추가
    if appendix_items:
        # 페이지 브레이크
        page_break = create_paragraph_xml('empty', '', para_id)
        page_break = page_break.replace('pageBreak="0"', 'pageBreak="1"')
        xml_items.append(page_break)
        para_id += 1
        
        for item_type, content in appendix_items:
            para_id += 1
            para_xml = create_paragraph_xml(item_type, content, para_id, image_info)
            xml_items.append(para_xml)
    
    print(f"  [OK] {len(xml_items)}개 항목 XML 생성 완료")
    
    new_xml = header + '\n' + '\n'.join(xml_items) + '\n</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    
    print(f"  [OK] section2.xml 저장")
    
    # 8. HWPX 압축
    print("\n8단계: HWPX 파일 생성...")
    
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
    print(f"[OK] HWPX 생성 완료: {file_size:,} bytes")
    
    shutil.rmtree(temp_dir)
    print(f"[OK] 임시 폴더 정리 완료")
    
    return output_hwpx

def main():
    print("\n" + "="*80)
    print("Markdown -> HWPX (목차 + 본문 + 부록)")
    print("="*80)
    
    # 본문 챕터 (실제 파일명에 맞춤)
    md_chapters = [
        ("Ⅰ. 서론", "../docs/chapters/01-introduction.md"),
        ("Ⅱ. 이론적 배경", "../docs/chapters/02-theoretical-background.md"),
        ("Ⅲ. 시스템 설계", "../docs/chapters/03-system-design.md"),
        ("Ⅳ. 연구 방법", "../docs/chapters/04-research-methods.md"),
        ("Ⅴ. 결과", "../docs/chapters/05-results.md"),
        ("Ⅵ. 논의 및 결론", "../docs/chapters/06-discussion-conclusion.md"),
        ("Ⅶ. 참고문헌", "../docs/chapters/07-references.md"),
    ]
    
    # 부록 (실제 파일명)
    appendix_chapters = [
        ("부록 A", "../docs/appendix/appendix-A-technical-implementation.md"),
        ("부록 B", "../docs/appendix/appendix-B-agent-prompts.md"),
        ("부록 C", "../docs/appendix/appendix-C-student-survey.md"),
        ("부록 D", "../docs/appendix/appendix-D-llm-evaluation.md"),
    ]
    
    output_file = f"report_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        result_file = create_hwpx_with_toc(md_chapters, appendix_chapters, output_file)
        
        print("\n" + "="*80)
        print("[SUCCESS] 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n포함 사항:")
        print("   [OK] 목차 자동 생성")
        print("   [OK] 본문 (8개 챕터)")
        print("   [OK] 표 (깔끔한 테두리)")
        print("   [OK] 머메이드 다이어그램")
        print("   [OK] 부록 (있는 경우)")
        
    except Exception as e:
        print(f"\n[ERROR] 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

