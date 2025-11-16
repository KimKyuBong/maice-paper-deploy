"""
Markdown → HWPX 변환 (v3: 문자열 기반 안전 처리)
"""
import os
import sys
import re
import zipfile
import shutil
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
            paragraphs.append(('heading1', line[2:].strip()))
        elif line.startswith('## '):
            paragraphs.append(('heading2', line[3:].strip()))
        elif line.startswith('### '):
            paragraphs.append(('heading3', line[4:].strip()))
        elif line.startswith('- '):
            paragraphs.append(('list', line[2:].strip()))
        else:
            paragraphs.append(('body', line))
    
    return paragraphs

def escape_xml(text):
    """XML 특수 문자 이스케이프"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

def parse_inline_formatting(text):
    """인라인 서식 파싱"""
    parts = []
    segments = re.split(r'(\*\*.*?\*\*)', text)
    
    for seg in segments:
        if seg.startswith('**') and seg.endswith('**'):
            parts.append((seg[2:-2], True))
        elif seg:
            parts.append((seg, False))
    
    return parts

def create_paragraph_xml(style_type, text, para_id):
    """HWP 문단 XML 생성"""
    style_id = STYLE_MAP.get(style_type, '12')
    parts = parse_inline_formatting(text)
    
    runs = []
    for text_part, is_bold in parts:
        if text_part:
            char_pr = "8" if is_bold else "4"
            escaped_text = escape_xml(text_part)
            runs.append(f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>')
    
    para = f'<hp:p id="{para_id}" paraPrIDRef="6" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">{"".join(runs)}</hp:p>'
    
    return para

def extract_section_header(template_xml_content):
    """기존 section XML에서 헤더 부분만 추출"""
    # 첫 번째 <hp:p> 태그 찾기
    first_para_pos = template_xml_content.find('<hp:p')
    
    if first_para_pos == -1:
        # 문단이 없다면 닫는 태그 직전까지
        close_tag_pos = template_xml_content.rfind('</hs:sec>')
        header = template_xml_content[:close_tag_pos]
    else:
        header = template_xml_content[:first_para_pos]
    
    return header

def create_hwpx_safe(md_files, output_hwpx, test_mode=True):
    """안전한 HWPX 생성"""
    print("="*80)
    print("Markdown → HWPX 변환 (v3: 문자열 기반)")
    print("="*80)
    
    # 1. 기존 HWPX 압축 해제
    template_hwpx = "hwp/report.hwpx"
    temp_dir = "hwp/temp_hwpx_safe"
    
    print("\n1단계: 기존 HWPX 압축 해제...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"✓ 압축 해제 완료")
    
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
    
    print(f"\n총 {len(all_paragraphs)}개 문단 파싱 완료")
    
    # 3. section2.xml 재생성
    print("\n3단계: section2.xml 재생성...")
    section2_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    # 기존 section2.xml 읽기
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    # 헤더 추출
    header = extract_section_header(original_xml)
    print(f"  ✓ 헤더 추출 ({len(header):,}자)")
    
    # 새 문단들 생성
    print(f"  문단 생성 중...")
    new_paragraphs = []
    for i, (style_type, text) in enumerate(all_paragraphs, start=2000000000):
        para_xml = create_paragraph_xml(style_type, text, para_id=i)
        new_paragraphs.append(para_xml)
        
        if (i - 2000000000 + 1) % 100 == 0:
            print(f"    진행: {i - 2000000000 + 1}/{len(all_paragraphs)}")
    
    print(f"  ✓ {len(new_paragraphs)}개 문단 XML 생성 완료")
    
    # 조합
    new_xml = header + '\n' + '\n'.join(new_paragraphs) + '\n</hs:sec>'
    
    # 저장
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    
    print(f"  ✓ section2.xml 저장 ({len(new_xml):,}자)")
    
    # 4. HWPX 압축
    print("\n4단계: HWPX 파일 생성...")
    
    if os.path.exists(output_hwpx):
        os.remove(output_hwpx)
    
    # mimetype 파일을 먼저 무압축으로 추가 (HWPX 표준)
    with zipfile.ZipFile(output_hwpx, 'w', zipfile.ZIP_STORED) as zf:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zf.write(mimetype_path, 'mimetype')
    
    # 나머지 파일들 압축 추가
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
    
    # 5. 정리
    shutil.rmtree(temp_dir)
    print(f"✓ 임시 폴더 정리 완료")
    
    return output_hwpx

def main():
    print("\n" + "="*80)
    print("📝 Markdown → HWPX 변환기 v3 (안전 버전)")
    print("="*80)
    
    # 테스트: 서론만
    md_chapters = [
        ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
    ]
    
    output_file = f"hwp/report_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        result_file = create_hwpx_safe(md_chapters, output_file)
        
        print("\n" + "="*80)
        print("✅ 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n🔍 파일을 열어서 확인해주세요:")
        print("   1. 파일이 정상적으로 열리는지")
        print("   2. 스타일이 올바르게 적용되었는지")
        print("   3. 내용이 제대로 표시되는지")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

