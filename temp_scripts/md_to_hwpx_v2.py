"""
Markdown → HWPX 변환 (v2: 기존 구조 정확히 유지)
전략: 기존 section XML 템플릿 사용하고 문단만 교체
"""
import os
import sys
import re
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 스타일 ID 매핑
STYLE_MAP = {
    'heading1': '5',   # Ⅰ. 제목
    'heading2': '6',   # 1. 제목
    'heading3': '7',   # 가. 제목
    'body': '12',      # 본문
    'list': '14',      # 글머리표
}

def clean_markdown(text):
    """Markdown 전처리"""
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[.*?\]\]', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def parse_markdown_to_paragraphs(md_text):
    """Markdown을 문단 리스트로 파싱"""
    paragraphs = []
    lines = md_text.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            continue
        
        if line.startswith('# '):
            text = line[2:].strip()
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = line[3:].strip()
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = line[4:].strip()
            paragraphs.append(('heading3', text))
        elif line.startswith('- '):
            text = line[2:].strip()
            paragraphs.append(('list', text))
        else:
            paragraphs.append(('body', line))
    
    return paragraphs

def escape_xml(text):
    """XML 특수 문자 이스케이프"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def parse_inline_formatting(text):
    """인라인 서식 파싱 (볼드)"""
    parts = []
    segments = re.split(r'(\*\*.*?\*\*)', text)
    
    for seg in segments:
        if seg.startswith('**') and seg.endswith('**'):
            parts.append((seg[2:-2], True))
        elif seg:
            parts.append((seg, False))
    
    return parts

def create_paragraph_xml(style_type, text, para_id):
    """HWP 문단 XML 생성 (더 정확한 구조)"""
    style_id = STYLE_MAP.get(style_type, '12')
    
    # 인라인 서식 파싱
    parts = parse_inline_formatting(text)
    
    # 문단 시작
    para_lines = []
    para_lines.append(f'<hp:p id="{para_id}" paraPrIDRef="6" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">')
    
    # run 추가
    for text_part, is_bold in parts:
        if text_part:
            char_pr = "8" if is_bold else "4"
            escaped_text = escape_xml(text_part)
            para_lines.append(f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>')
    
    para_lines.append('</hp:p>')
    
    return ''.join(para_lines)

def create_section_xml_from_template(paragraphs, template_path):
    """
    기존 section XML을 템플릿으로 사용하여 새 XML 생성
    """
    print("\n  템플릿 읽기...")
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # XML 파싱
    try:
        root = ET.fromstring(template_content)
    except Exception as e:
        print(f"  ⚠ XML 파싱 오류: {e}")
        # 파싱 실패 시 직접 문자열 처리
        return create_simple_section_xml(paragraphs, template_content)
    
    # 네임스페이스 추출
    namespaces = dict([node for _, node in ET.iterparse(
        template_path, events=['start-ns']
    )])
    
    # 기존 문단 모두 제거
    for elem in root.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
        parent = root.find('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}p/..')
        if parent is not None:
            parent.remove(elem)
    
    # 새 문단 추가
    print(f"  {len(paragraphs)}개 문단 생성 중...")
    
    # XML 헤더 재생성
    xml_header = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
    
    # 루트 태그 시작 부분 추출
    root_start = template_content.split('>')[0] + '>'
    
    # 새 문단들 생성
    new_paragraphs = []
    for i, (style_type, text) in enumerate(paragraphs, start=2000000000):
        para_xml = create_paragraph_xml(style_type, text, para_id=i)
        new_paragraphs.append(para_xml)
    
    # 조합
    new_xml = xml_header + root_start + '\n'
    new_xml += '\n'.join(new_paragraphs)
    new_xml += '\n</hs:sec>'
    
    return new_xml

def create_simple_section_xml(paragraphs, template_content):
    """간단한 방식: 헤더만 가져오고 문단 추가"""
    # 템플릿에서 헤더 부분만 추출
    header_end = template_content.find('<hp:p')
    if header_end == -1:
        # 문단이 없으면 닫는 태그 찾기
        header_end = template_content.rfind('</hs:sec>')
    
    header = template_content[:header_end]
    
    # 새 문단들
    new_paragraphs = []
    for i, (style_type, text) in enumerate(paragraphs, start=2000000000):
        para_xml = create_paragraph_xml(style_type, text, para_id=i)
        new_paragraphs.append(para_xml)
    
    # 조합
    new_xml = header + '\n'
    new_xml += '\n'.join(new_paragraphs)
    new_xml += '\n</hs:sec>'
    
    return new_xml

def create_hwpx_v2(md_files, output_hwpx):
    """v2: 더 안전한 HWPX 생성"""
    print("="*80)
    print("Markdown → HWPX 변환 (v2: 안전 버전)")
    print("="*80)
    
    # 1. 기존 HWPX 압축 해제
    template_hwpx = "hwp/report.hwpx"
    temp_dir = "hwp/temp_hwpx_v2"
    
    print("\n1단계: 기존 HWPX 압축 해제...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"✓ 압축 해제: {temp_dir}")
    
    # 2. Markdown 읽기
    print("\n2단계: Markdown 파싱...")
    all_paragraphs = []
    
    for chapter_name, md_path in md_files:
        if not os.path.exists(md_path):
            print(f"  ⚠ 파일 없음: {md_path}")
            continue
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md_content = clean_markdown(md_content)
        paragraphs = parse_markdown_to_paragraphs(md_content)
        all_paragraphs.extend(paragraphs)
        
        print(f"  ✓ {chapter_name}: {len(paragraphs)}개 문단")
    
    print(f"\n총 {len(all_paragraphs)}개 문단")
    
    # 3. section2.xml 교체 (템플릿 기반)
    print("\n3단계: section2.xml 생성...")
    template_section = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    new_section_xml = create_section_xml_from_template(
        all_paragraphs, 
        template_section
    )
    
    # 저장
    with open(template_section, 'w', encoding='utf-8') as f:
        f.write(new_section_xml)
    
    print(f"✓ section2.xml 교체 완료 ({len(new_section_xml):,}자)")
    
    # 4. HWPX 재압축
    print("\n4단계: HWPX 재압축...")
    
    if os.path.exists(output_hwpx):
        os.remove(output_hwpx)
    
    with zipfile.ZipFile(output_hwpx, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)
    
    file_size = os.path.getsize(output_hwpx)
    print(f"✓ HWPX 생성: {output_hwpx} ({file_size:,} bytes)")
    
    # 5. 정리
    shutil.rmtree(temp_dir)
    
    return output_hwpx

def main():
    print("\n" + "="*80)
    print("📝 Markdown → HWPX 변환기 v2")
    print("="*80)
    
    md_chapters = [
        ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
        # 우선 서론만 테스트
    ]
    
    output_file = f"hwp/report_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        result_file = create_hwpx_v2(md_chapters, output_file)
        
        print("\n" + "="*80)
        print("✅ 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n파일을 열어서 손상되지 않았는지 확인해주세요!")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

