"""
Markdown → HWPX 변환 (표 + PNG 이미지)
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
    'table_caption': {'styleIDRef': '12', 'paraPrIDRef': '4', 'charPrIDRef': '4'},  # 가운데 정렬 (원본 사용)
    'figure_caption': {'styleIDRef': '12', 'paraPrIDRef': '4', 'charPrIDRef': '4'},  # 가운데 정렬 (원본 사용)
}

# 새 borderFill XML 정의
# ID 52: C1용 (좌 NONE, 우 SOLID, 아래 굵게)
NEW_BORDER_FILL_C1 = '''<hh:borderFill id="52" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">
<hh:slash type="NONE" Crooked="0" isCounter="0"/>
<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>
<hh:leftBorder type="NONE" width="0.12 mm" color="#5D5D5D"/>
<hh:rightBorder type="SOLID" width="0.12 mm" color="#5D5D5D"/>
<hh:topBorder type="SOLID" width="0.12 mm" color="#5D5D5D"/>
<hh:bottomBorder type="SOLID" width="0.7 mm" color="#5D5D5D"/>
<hh:diagonal type="SLASH" width="0.1 mm" color="#000000"/>
</hh:borderFill>'''

# 가운데 정렬 paraPr (표/그림 캡션용)
NEW_PARA_PR_CENTER = '''<hh:paraPr id="60" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" suppressLineNumbers="0" checked="0" textDir="LTR">
<hh:align horizontal="CENTER" vertical="BASELINE"/>
<hh:heading type="NONE" idRef="0" level="0"/>
<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD" widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>
<hh:autoSpacing eAsianEng="0" eAsianNum="0"/>
<hp:switch>
<hp:case hp:required-namespace="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">
<hh:margin><hc:intent value="0" unit="HWPUNIT"/><hc:left value="0" unit="HWPUNIT"/><hc:right value="0" unit="HWPUNIT"/><hc:prev value="0" unit="HWPUNIT"/><hc:next value="0" unit="HWPUNIT"/></hh:margin>
<hh:lineSpacing type="PERCENT" value="160" unit="HWPUNIT"/>
</hp:case>
<hp:default>
<hh:margin><hc:intent value="0" unit="HWPUNIT"/><hc:left value="0" unit="HWPUNIT"/><hc:right value="0" unit="HWPUNIT"/><hc:prev value="0" unit="HWPUNIT"/><hc:next value="0" unit="HWPUNIT"/></hh:margin>
<hh:lineSpacing type="PERCENT" value="160" unit="HWPUNIT"/>
</hp:default>
</hp:switch>
<hh:border borderFillIDRef="0" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" connect="0" ignoreMargin="0"/>
</hh:paraPr>'''

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
            page.wait_for_timeout(2000)  # 렌더링 대기
            
            # SVG 요소 찾기
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
        # Ⅰ., I., VII. 등 로마자 형식 제거 (라틴 I, V, X + 유니코드 로마자)
        text = re.sub(r'^[IVXⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s*', '', text)
    elif heading_level == 'heading2':
        # 1., 2.1., 2.1.2. 등 모든 점-숫자 패턴 제거
        text = re.sub(r'^\d+(?:\.\d+)*\.\s*', '', text)
    elif heading_level == 'heading3':
        # 가., 나., ... 형식 제거
        text = re.sub(r'^[가-힣]\.\s*', '', text)
    elif heading_level == 'heading4':
        # 1), 2), ... 또는 1., 2., 2.1. 등 형식 모두 제거
        text = re.sub(r'^\d+(?:\.\d+)*[\.\)]\s*', '', text)
    elif heading_level == 'heading5':
        # 가), 나), ... 또는 가., 나., ... 형식 모두 제거
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
    """
    셀 위치별 borderFillIDRef 반환
    
    A1 A2 A3 (헤더)
    B1 B2 B3 (데이터)
    C1 C2 C3 (맨아래)
    """
    is_header = (row_idx == 0)
    is_last_row = (row_idx == total_rows - 1)
    is_first_col = (col_idx == 0)
    is_last_col = (col_idx == total_cols - 1)
    
    if is_header:
        # 헤더 행 (A): 상하 솔리드(굵게)
        if is_first_col:
            return "19"  # A1: 좌 없음, 우 실선
        elif is_last_col:
            return "17"  # A3: 좌 실선, 우 없음
        else:
            return "12"  # A2: 좌우 실선
    elif is_last_row:
        # 맨아래 행 (C): 하 솔리드(굵게)
        if is_first_col:
            return "16"  # C1: 좌 없음, 우 실선, 하 굵게
        elif is_last_col:
            return "15"  # C3: 우 없음, 하 굵게
        else:
            return "10"  # C2: 좌우 실선, 하 굵게
    else:
        # 데이터 행 중간 (B): 상하 일반 선 (0.12mm)
        if is_first_col:
            return "9"   # B1: 좌 없음, 우 실선, 상하 일반
        elif is_last_col:
            return "8"   # B3: 우 없음, 좌 실선, 상하 일반
        else:
            return "7"   # B2: 좌우 실선, 상하 일반

def create_table_cell_xml(text, row, col, total_rows, total_cols, is_header=False):
    escaped_text = escape_xml(text)
    border_fill_id = get_border_fill_id(row, col, total_rows, total_cols)
    header_attr = "1" if is_header else "0"
    style_id = "20"
    char_pr_id = "16"  # 맑은 고딕 9pt
    
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
<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="CENTER" vertOffset="0" horzOffset="0"/>
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
    # 먼저 머메이드 블록을 마커로 교체 (역순으로!)
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    mermaid_replacements = []
    
    for match in re.finditer(mermaid_pattern, md_text, re.DOTALL):
        start_pos = match.start()
        context_before = md_text[max(0, start_pos - 500):start_pos]
        
        # [그림X-Y] 찾기 (가장 가까운 = 마지막 매치)
        caption_matches = list(re.finditer(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', context_before))
        
        if caption_matches:
            # 가장 가까운 캡션 = 마지막 매치
            caption_match = caption_matches[-1]
            
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            roman = caption_match.group(1)
            num = caption_match.group(2)
            chapter_num = roman_map.get(roman, '?')
            figure_num = f"{chapter_num}-{num}"
            
            marker = f"[MERMAID_IMAGE:{figure_num}]"
            mermaid_replacements.append((match.start(), match.end(), marker))
    
    # 역순으로 교체 (뒤에서부터)
    for start, end, marker in reversed(mermaid_replacements):
        md_text = md_text[:start] + marker + md_text[end:]
    
    # 일반 코드 블록도 마커로 교체 (```python, ```bash 등, mermaid 제외)
    code_block_pattern = r'```(?!mermaid)([a-z]*)\n(.*?)\n```'
    code_replacements = []
    
    for match in re.finditer(code_block_pattern, md_text, re.DOTALL):
        # mermaid가 아닌 코드 블록만 처리
        marker = f"[CODE_BLOCK_{len(code_replacements)}]"
        code_replacements.append((match.start(), match.end(), marker, match.group(0)))
    
    # 역순으로 교체
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
        
        # 머메이드 이미지 마커 확인
        if line.startswith('[MERMAID_IMAGE:'):
            figure_num = line[15:-1]  # [MERMAID_IMAGE:3-1] → 3-1
            paragraphs.append(('mermaid_image', figure_num))
            i += 1
            continue
        
        # 코드 블록 마커 확인 (복원하지 않고 빈 줄로 처리)
        if line.startswith('[CODE_BLOCK_'):
            paragraphs.append(('empty', ''))
            i += 1
            continue
        
        line = lines[i].rstrip()
        
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
        elif re.match(r'^\[표[ⅠⅡⅢⅣⅤⅥⅦⅧ]+-\d+\]', line) or re.match(r'^\*\*\[표[ⅠⅡⅢⅣⅤⅥⅦⅧ]+-\d+\]', line):
            # 표 캡션 (볼드 마크 제거)
            text = re.sub(r'^\*\*|\*\*$', '', line)  # **캡션** → 캡션
            paragraphs.append(('table_caption', text))
        elif re.match(r'^\[그림[ⅠⅡⅢⅣⅤⅥⅦⅧ]+-\d+\]', line) or re.match(r'^\*\*\[그림[ⅠⅡⅢⅣⅤⅥⅦⅧ]+-\d+\]', line):
            # 그림 캡션 (볼드 마크 제거)
            text = re.sub(r'^\*\*|\*\*$', '', line)  # **캡션** → 캡션
            paragraphs.append(('figure_caption', text))
        else:
            paragraphs.append(('body', line))
        
        i += 1
    
    # 캡션 순서 조정
    paragraphs = adjust_caption_order(paragraphs)
    
    return paragraphs

def adjust_caption_order(paragraphs):
    """
    캡션과 표/그림의 순서 조정:
    - 표 캡션: 표 앞에 유지
    - 그림 캡션: 그림 뒤로 이동
    """
    adjusted = []
    i = 0
    
    while i < len(paragraphs):
        style_type, content = paragraphs[i]
        
        # 그림 캡션이 그림 앞에 있는 경우 → 그림 뒤로 이동
        if style_type == 'figure_caption' and i + 1 < len(paragraphs):
            next_type, next_content = paragraphs[i + 1]
            if next_type == 'mermaid_image':
                # 순서 바꾸기: 그림 → 캡션
                adjusted.append(paragraphs[i + 1])  # 그림 먼저
                adjusted.append(paragraphs[i])       # 캡션 나중
                i += 2
                continue
        
        # 표 캡션 바로 다음에 빈 줄이 있고 그 다음에 표가 있는 경우
        if style_type == 'table_caption' and i + 2 < len(paragraphs):
            next1_type, _ = paragraphs[i + 1]
            next2_type, _ = paragraphs[i + 2]
            if next1_type == 'empty' and next2_type == 'table':
                # 캡션 → 빈 줄 제거 → 표
                adjusted.append(paragraphs[i])       # 캡션
                adjusted.append(paragraphs[i + 2])   # 표 (빈 줄 건너뛰기)
                i += 3
                continue
        
        # 표 캡션 바로 다음에 표가 있는 경우 (빈 줄 없음)
        if style_type == 'table_caption' and i + 1 < len(paragraphs):
            next_type, _ = paragraphs[i + 1]
            if next_type == 'table':
                # 캡션 → 표
                adjusted.append(paragraphs[i])       # 캡션
                adjusted.append(paragraphs[i + 1])   # 표
                i += 2
                continue
        
        # 일반 요소
        adjusted.append(paragraphs[i])
        i += 1
    
    return adjusted

def remove_bold_markdown(text):
    """볼드 제거"""
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def remove_all_markdown_formatting(text):
    """모든 Markdown 포맷 제거 (볼드, 이탤릭 등)"""
    # 볼드
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # 이탤릭
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # 코드
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def create_paragraph_xml(style_type, text, para_id, image_info=None):
    # 머메이드 이미지 처리
    if style_type == 'mermaid_image' and image_info and text in image_info:
        img_data = image_info[text]
        return create_image_paragraph_xml(img_data)
    
    style_info = STYLE_MAP.get(style_type, STYLE_MAP['body'])
    
    style_id = style_info['styleIDRef']
    para_pr = style_info['paraPrIDRef']
    char_pr = style_info['charPrIDRef']
    
    # 이미 parse 단계에서 모든 포맷 제거됨, XML 이스케이프만 수행
    escaped_text = escape_xml(text) if text else ''
    
    run = f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>' if text else f'<hp:run charPrIDRef="{char_pr}"/>'
    
    return f'<hp:p id="{para_id}" paraPrIDRef="{para_pr}" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">{run}</hp:p>'

def create_image_paragraph_xml(img_data):
    """PNG 이미지 문단 XML (example.hwpx 방식)"""
    image_id = img_data['id']
    img_w = img_data['img_width']
    img_h = img_data['img_height']
    display_w = img_data['display_width']
    display_h = img_data['display_height']
    
    # 스케일 계산
    scale_x = display_w / img_w if img_w > 0 else 1
    scale_y = display_h / img_h if img_h > 0 else 1
    
    pic_xml = f'<hp:pic id="{2000000000 + image_id}" zOrder="{10 + image_id}" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="{927519913 + image_id}" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{display_w}" height="{display_h}"/><hp:curSz width="{display_w}" height="{display_h}"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{display_w//2}" centerY="{display_h//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="{scale_x}" e2="0" e3="0" e4="0" e5="{scale_y}" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image{image_id}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{img_w}" y="0"/><hc:pt2 x="{img_w}" y="{img_h}"/><hc:pt3 x="0" y="{img_h}"/></hp:imgRect><hp:imgClip left="0" right="{img_w}" top="0" bottom="{img_h}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{img_w}" dimheight="{img_h}"/><hp:effects/><hp:sz width="{display_w}" widthRelTo="ABSOLUTE" height="{display_h}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="CENTER" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic>'
    
    # 이미지를 감싸는 문단도 가운데 정렬 (paraPrIDRef="4")
    return f'<hp:p id="0" paraPrIDRef="4" styleIDRef="12" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="4">{pic_xml}<hp:t/></hp:run><hp:linesegarray><hp:lineseg textpos="0" vertpos="6440" vertsize="1100" textheight="1100" baseline="935" spacing="880" horzpos="0" horzsize="43936" flags="1441792"/></hp:linesegarray></hp:p>'

def create_table_paragraph_xml(table_data, para_id, table_id):
    table_xml = create_table_xml(table_data, table_id)
    
    # 표를 감싸는 문단도 가운데 정렬 (paraPrIDRef="4")
    para_xml = f'<hp:p id="{para_id}" paraPrIDRef="4" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
    para_xml += f'<hp:run charPrIDRef="4">{table_xml}<hp:t/></hp:run>'
    para_xml += '</hp:p>'
    
    return para_xml

def add_custom_borderfills_to_header(header_xml_path):
    """header.xml에 새 borderFill 및 paraPr 추가"""
    with open(header_xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. </hh:borderFills> 태그 찾기 및 borderFill 추가
    close_tag = '</hh:borderFills>'
    pos = content.find(close_tag)
    
    if pos != -1:
        # 새 borderFill 삽입
        content = content[:pos] + NEW_BORDER_FILL_C1 + '\n' + content[pos:]
    
    # 2. </hh:paraPrs> 태그 찾기 및 paraPr 추가
    close_tag_para = '</hh:paraPrs>'
    pos_para = content.find(close_tag_para)
    
    if pos_para != -1:
        # 새 paraPr 삽입 (가운데 정렬)
        content = content[:pos_para] + NEW_PARA_PR_CENTER + '\n' + content[pos_para:]
    
    # 저장
    with open(header_xml_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return pos != -1 and pos_para != -1

def extract_section_header(xml_content):
    first_para_pos = xml_content.find('<hp:p')
    
    if first_para_pos == -1:
        close_tag_pos = xml_content.rfind('</hs:sec>')
        return xml_content[:close_tag_pos]
    
    return xml_content[:first_para_pos]

def copy_images_to_bindata_simple(temp_dir, mermaid_pngs):
    """PNG 이미지를 BinData에 복사하고 content.hpf에 등록"""
    bindata_dir = os.path.join(temp_dir, "BinData")
    
    image_info = {}
    image_id = 39  # 기존 image1-38 다음부터
    
    # content.hpf 업데이트를 위한 항목들
    hpf_items = []
    
    for figure_num, src_path in sorted(mermaid_pngs.items()):
        if not os.path.exists(src_path):
            print(f"  [WARNING] PNG 파일을 찾을 수 없음: {src_path}")
            continue
        
        # PNG 그대로 복사 (소문자 .png)
        dst_filename = f"image{image_id}.png"
        dst_path = os.path.join(bindata_dir, dst_filename)
        shutil.copy2(src_path, dst_path)
        
        # 해시 계산
        with open(dst_path, 'rb') as f:
            data = f.read()
            hash_md5 = hashlib.md5(data).digest()
            hashkey = base64.b64encode(hash_md5).decode('ascii')
        
        # 크기 계산
        img = Image.open(src_path)
        width_px, height_px = img.size
        dpi = img.info.get('dpi', (96, 96))[0]
        
        # 이미지 실제 크기
        img_width_hwp = int(width_px / dpi * 7200)
        img_height_hwp = int(height_px / dpi * 7200)
        
        # 표시 크기 (A4 너비 80% 이하로)
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
        
        # content.hpf 항목 생성
        hpf_item = f'<opf:item id="image{image_id}" href="BinData/{dst_filename}" media-type="image/png" isEmbeded="1" hashkey="{hashkey}"/>'
        hpf_items.append(hpf_item)
        
        print(f"  [OK] {figure_num} -> {dst_filename}")
        
        image_id += 1
    
    # content.hpf 업데이트
    if hpf_items:
        hpf_path = os.path.join(temp_dir, "Contents", "content.hpf")
        with open(hpf_path, 'r', encoding='utf-8') as f:
            hpf_content = f.read()
        
        # </opf:manifest> 앞에 모든 이미지 항목 삽입
        manifest_end = hpf_content.find('</opf:manifest>')
        if manifest_end != -1:
            all_items = '\n'.join(hpf_items)
            hpf_content = hpf_content[:manifest_end] + all_items + '\n' + hpf_content[manifest_end:]
            
            with open(hpf_path, 'w', encoding='utf-8') as f:
                f.write(hpf_content)
            
            print(f"  [OK] content.hpf에 {len(hpf_items)}개 이미지 등록")
    
    return image_info

def parse_appendix_markdown(md_text):
    """부록 마크다운 파싱 (표와 머메이드 포함)"""
    # 머메이드 블록 마커로 교체
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    mermaid_replacements = []
    
    for match in re.finditer(mermaid_pattern, md_text, re.DOTALL):
        start_pos = match.start()
        context_before = md_text[max(0, start_pos - 500):start_pos]
        
        caption_match = re.search(r'\[그림([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', context_before)
        
        if caption_match:
            roman_map = {'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5', 'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8'}
            roman = caption_match.group(1)
            num = caption_match.group(2)
            chapter_num = roman_map.get(roman, '?')
            figure_num = f"{chapter_num}-{num}"
            
            marker = f"[MERMAID_IMAGE:{figure_num}]"
            mermaid_replacements.append((match.start(), match.end(), marker))
    
    for start, end, marker in reversed(mermaid_replacements):
        md_text = md_text[:start] + marker + md_text[end:]
    
    # 코드 블록 마커로 교체
    code_block_pattern = r'```[a-z]*\n(.*?)\n```'
    code_replacements = []
    
    for match in re.finditer(code_block_pattern, md_text, re.DOTALL):
        marker = f"[CODE_BLOCK_{len(code_replacements)}]"
        code_replacements.append((match.start(), match.end(), marker, match.group(0)))
    
    for start, end, marker, original in reversed(code_replacements):
        md_text = md_text[:start] + marker + md_text[end:]
    
    # 표 추출
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
        
        # 머메이드 이미지 마커
        if line.startswith('[MERMAID_IMAGE:'):
            figure_num = line[15:-1]
            paragraphs.append(('mermaid_image', figure_num))
            i += 1
            continue
        
        # 코드 블록 마커
        if line.startswith('[CODE_BLOCK_'):
            paragraphs.append(('empty', ''))
            i += 1
            continue
        
        if not line:
            paragraphs.append(('empty', ''))
        elif line.startswith('# '):
            text = line[2:].strip()
            text = remove_all_markdown_formatting(text)
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = line[3:].strip()
            text = remove_all_markdown_formatting(text)
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = line[4:].strip()
            text = remove_all_markdown_formatting(text)
            paragraphs.append(('heading3', text))
        elif line.startswith('#### '):
            text = line[5:].strip()
            text = remove_all_markdown_formatting(text)
            paragraphs.append(('heading4', text))
        elif line.startswith('##### '):
            text = line[6:].strip()
            text = remove_all_markdown_formatting(text)
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

def create_hwpx_clean(md_files, appendix_files, output_hwpx):
    print("="*80)
    print("Markdown → HWPX 변환 (표 + 이미지)")
    print("="*80)
    
    # 1. 압축 해제
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_hwpx = os.path.join(script_dir, "report_backup_20251112_020239.hwpx")
    temp_dir = os.path.join(script_dir, "temp_hwpx_clean")
    
    print("\n1단계: 기존 HWPX 압축 해제...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"[OK] 압축 해제 완료")
    
    # 1.4 표차례와 그림차례 읽기
    print("\n1.4단계: 표차례와 그림차례 읽기...")
    tables_list, figures_list = read_table_and_figure_list(md_files)
    print(f"[OK] 표 {len(tables_list)}개, 그림 {len(figures_list)}개 발견")
    
    # 1.5 머메이드 다이어그램 변환
    print("\n1.5단계: 머메이드 다이어그램 변환...")
    all_md_content = ""
    for chapter_name, md_path in md_files:
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                all_md_content += f.read() + "\n\n"
    
    mermaid_pngs = extract_and_convert_mermaid(all_md_content, "mermaid_diagrams", max_workers=4, figure_list=figures_list)
    print(f"[OK] {len(mermaid_pngs)}개 다이어그램 변환 완료")
    
    # 1.6 이미지 복사
    print("\n1.6단계: 이미지 복사...")
    image_info = copy_images_to_bindata_simple(temp_dir, mermaid_pngs)
    print(f"[OK] {len(image_info)}개 이미지 복사 완료")
    
    # 2. header.xml에 새 borderFill 추가 (필요 없음 - 기존 ID 사용)
    # print("\n1.5단계: 새 borderFill 정의 추가...")
    # 모두 기존 ID 사용
    
    # 3. Markdown 읽기
    print("\n2단계: Markdown 파싱...")
    all_items = []
    
    for chapter_name, md_path in md_files:
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
    
    total_tables = sum(1 for item_type, _ in all_items if item_type == 'table')
    total_paras = len(all_items) - total_tables
    print(f"\n총 {total_paras}개 문단, {total_tables}개 표")
    
    # 3.5. 부록 파싱
    print("\n3.5단계: 부록 파싱...")
    appendix_items = []
    for appendix_name, md_path in appendix_files:
        if not os.path.exists(md_path):
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            appendix_content = f.read()
        
        appendix_content = clean_markdown(appendix_content)
        items = parse_appendix_markdown(appendix_content)
        appendix_items.extend(items)
        
        table_count = sum(1 for item_type, _ in items if item_type == 'table')
        para_count = len(items) - table_count
        print(f"  [OK] {appendix_name}: {para_count}개 문단, {table_count}개 표")
    
    # 4. XML 생성
    print("\n4단계: section2.xml 재생성...")
    section2_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    header = extract_section_header(original_xml)
    
    print(f"  XML 생성 중...")
    xml_items = []
    table_counter = 900000000
    para_id = 500000000
    
    # 4-1. 본문 처리
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
    
    # 4-2. 부록 처리
    if appendix_items:
        print(f"  부록 XML 생성 중...")
        # 페이지 브레이크 추가
        page_break = create_paragraph_xml('empty', '', para_id)
        page_break = page_break.replace('pageBreak="0"', 'pageBreak="1"')
        xml_items.append(page_break)
        para_id += 1
        
        for i, (item_type, content) in enumerate(appendix_items):
            para_id += 1
            
            if item_type == 'table':
                table_counter += 1
                para_xml = create_table_paragraph_xml(content, para_id, table_counter)
                xml_items.append(para_xml)
            else:
                para_xml = create_paragraph_xml(item_type, content, para_id, image_info)
                xml_items.append(para_xml)
            
            if (i + 1) % 200 == 0:
                print(f"    부록 진행: {i + 1}/{len(appendix_items)}")
    
    print(f"  [OK] {len(xml_items)}개 항목 XML 생성 완료")
    
    new_xml = header + '\n' + '\n'.join(xml_items) + '\n</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    
    print(f"  [OK] section2.xml 저장")
    
    # 5. HWPX 압축
    print("\n5단계: HWPX 파일 생성...")
    
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
    print("Markdown -> HWPX (깔끔한 표)")
    print("="*80)
    print("\n표 테두리 정책:")
    print("  [OK] 맨 둘레만 실선")
    print("  [OK] 중간 셀은 좌우 테두리 없음")
    
    # 스크립트 위치 기준 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    chapters_dir = os.path.join(project_root, "docs", "chapters")
    appendix_dir = os.path.join(project_root, "docs", "appendix")
    
    md_chapters = [
        ("Ⅰ. 서론", os.path.join(chapters_dir, "01-introduction.md")),
        ("Ⅱ. 이론적 배경", os.path.join(chapters_dir, "02-theoretical-background.md")),
        ("Ⅲ. 시스템 설계", os.path.join(chapters_dir, "03-system-design.md")),
        ("Ⅳ. 연구 방법", os.path.join(chapters_dir, "04-research-methods.md")),
        ("Ⅴ. 결과", os.path.join(chapters_dir, "05-results.md")),
        ("Ⅵ. 논의 및 결론", os.path.join(chapters_dir, "06-discussion-conclusion.md")),
        ("Ⅶ. 참고문헌", os.path.join(chapters_dir, "07-references.md")),
    ]
    
    # 부록
    appendix_chapters = [
        ("부록 A", os.path.join(appendix_dir, "appendix-A-technical-implementation.md")),
        ("부록 B", os.path.join(appendix_dir, "appendix-B-agent-prompts.md")),
        ("부록 C", os.path.join(appendix_dir, "appendix-C-student-survey.md")),
        ("부록 D", os.path.join(appendix_dir, "appendix-D-llm-evaluation.md")),
    ]
    
    output_file = os.path.join(script_dir, f"report_with_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx")
    
    try:
        result_file = create_hwpx_clean(md_chapters, appendix_chapters, output_file)
        
        print("\n" + "="*80)
        print("[SUCCESS] 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n포함 사항:")
        print("   [OK] 표 테두리 (둘레만 실선)")
        print("   [OK] 머메이드 다이어그램 자동 변환")
        print("   [OK] 부록 4개 포함")
        
    except Exception as e:
        print(f"\n[ERROR] 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

