"""
Markdown → HWPX 변환 (최종 수정)
1. 볼드는 일단 제거 (크기 변경 방지)
2. 개요 번호 자동 처리 (중복 제거)
"""
import os
import sys
import re
import zipfile
import shutil
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 정확한 스타일 매핑
STYLE_MAP = {
    'heading1': {'styleIDRef': '5', 'paraPrIDRef': '20', 'charPrIDRef': '14'},  # Ⅰ. 제목
    'heading2': {'styleIDRef': '6', 'paraPrIDRef': '21', 'charPrIDRef': '8'},   # 1. 제목
    'heading3': {'styleIDRef': '7', 'paraPrIDRef': '22', 'charPrIDRef': '15'},  # 가. 제목
    'heading4': {'styleIDRef': '8', 'paraPrIDRef': '23', 'charPrIDRef': '15'},  # 1) 제목
    'heading5': {'styleIDRef': '9', 'paraPrIDRef': '24', 'charPrIDRef': '15'},  # 가) 제목
    'body': {'styleIDRef': '12', 'paraPrIDRef': '17', 'charPrIDRef': '4'},      # 본문
    'list_bullet': {'styleIDRef': '14', 'paraPrIDRef': '18', 'charPrIDRef': '4'},    # ․ 글머리표
    'list_para': {'styleIDRef': '13', 'paraPrIDRef': '19', 'charPrIDRef': '4'},      # ○ 글머리문단
    'numbered_list': {'styleIDRef': '13', 'paraPrIDRef': '19', 'charPrIDRef': '4'},  # 번호 있는 리스트
    'empty': {'styleIDRef': '0', 'paraPrIDRef': '6', 'charPrIDRef': '5'},       # 빈 줄
}

def clean_markdown(text):
    """Markdown 전처리"""
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[.*?\]\]', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def remove_auto_numbering(text, heading_level):
    """
    자동 번호 제거 (한글에서 자동으로 붙이므로)
    예: "가. 수학 교육" → "수학 교육"
    """
    if heading_level == 'heading1':
        # "I. ", "Ⅰ. " 등 제거
        text = re.sub(r'^[IⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s*', '', text)
    elif heading_level == 'heading2':
        # "1. ", "2. " 등 제거
        text = re.sub(r'^\d+\.\s*', '', text)
    elif heading_level == 'heading3':
        # "가. ", "나. " 등 제거
        text = re.sub(r'^[가-힣]\.\s*', '', text)
    elif heading_level == 'heading4':
        # "1) ", "2) " 등 제거
        text = re.sub(r'^\d+\)\s*', '', text)
    elif heading_level == 'heading5':
        # "가) ", "나) " 등 제거
        text = re.sub(r'^[가-힣]\)\s*', '', text)
    
    return text

def parse_markdown_to_paragraphs(md_text):
    """Markdown을 문단 리스트로 파싱"""
    paragraphs = []
    lines = md_text.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            paragraphs.append(('empty', ''))
            continue
        
        if line.startswith('# '):
            text = line[2:].strip()
            text = remove_auto_numbering(text, 'heading1')
            paragraphs.append(('heading1', text))
        elif line.startswith('## '):
            text = line[3:].strip()
            text = remove_auto_numbering(text, 'heading2')
            paragraphs.append(('heading2', text))
        elif line.startswith('### '):
            text = line[4:].strip()
            text = remove_auto_numbering(text, 'heading3')
            paragraphs.append(('heading3', text))
        elif line.startswith('#### '):
            text = line[5:].strip()
            text = remove_auto_numbering(text, 'heading4')
            paragraphs.append(('heading4', text))
        elif line.startswith('##### '):
            text = line[6:].strip()
            text = remove_auto_numbering(text, 'heading5')
            paragraphs.append(('heading5', text))
        elif line.startswith('- '):
            # - 리스트: 짧으면 글머리표, 길면 글머리문단
            text = line[2:].strip()
            # 80자 이상이거나 콜론(:)이 있으면 글머리문단
            if len(text) > 80 or ':' in text[:30]:
                paragraphs.append(('list_para', text))
            else:
                paragraphs.append(('list_bullet', text))
        elif re.match(r'^\d+\.\s', line):
            # 1. 번호 있는 리스트
            text = re.sub(r'^\d+\.\s*', '', line)
            paragraphs.append(('numbered_list', text))
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

def remove_bold_markdown(text):
    """**볼드** 마크다운 제거하고 일반 텍스트로"""
    # **텍스트** → 텍스트
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

def create_paragraph_xml(style_type, text, para_id):
    """
    HWP 문단 XML 생성
    - 정확한 paraPrIDRef, styleIDRef, charPrIDRef 사용
    - 볼드는 제거 (크기 변경 방지)
    """
    style_info = STYLE_MAP.get(style_type, STYLE_MAP['body'])
    
    style_id = style_info['styleIDRef']
    para_pr = style_info['paraPrIDRef']
    char_pr = style_info['charPrIDRef']
    
    # 볼드 마크다운 제거
    text = remove_bold_markdown(text) if text else ''
    
    # XML 이스케이프
    escaped_text = escape_xml(text)
    
    # run 생성
    if text:
        run = f'<hp:run charPrIDRef="{char_pr}"><hp:t>{escaped_text}</hp:t></hp:run>'
    else:
        run = f'<hp:run charPrIDRef="{char_pr}"/>'
    
    # 문단 XML
    para_xml = f'<hp:p id="{para_id}" paraPrIDRef="{para_pr}" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">{run}</hp:p>'
    
    return para_xml

def extract_section_header(xml_content):
    """섹션 XML 헤더 추출"""
    first_para_pos = xml_content.find('<hp:p')
    
    if first_para_pos == -1:
        close_tag_pos = xml_content.rfind('</hs:sec>')
        return xml_content[:close_tag_pos]
    
    return xml_content[:first_para_pos]

def create_hwpx_final(md_files, output_hwpx):
    """최종 HWPX 생성"""
    print("="*80)
    print("Markdown → HWPX 변환 (최종)")
    print("="*80)
    
    # 1. 기존 HWPX 압축 해제
    template_hwpx = "hwp/report_backup_20251112_020239.hwpx"
    temp_dir = "hwp/temp_hwpx_final"
    
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
        
        # 샘플 확인
        for style, text in paragraphs[:3]:
            text_preview = text[:40] if text else '(빈 줄)'
            print(f"      {style:12s}: {text_preview}")
    
    print(f"\n총 {len(all_paragraphs)}개 문단 파싱 완료")
    
    # 3. section2.xml 재생성
    print("\n3단계: section2.xml 재생성...")
    section2_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    
    with open(section2_path, 'r', encoding='utf-8') as f:
        original_xml = f.read()
    
    header = extract_section_header(original_xml)
    print(f"  ✓ 헤더 추출 ({len(header):,}자)")
    
    # 문단 XML 생성
    print(f"  문단 XML 생성 중...")
    new_paragraphs = []
    
    for i, (style_type, text) in enumerate(all_paragraphs):
        para_id = 500000000 + i
        para_xml = create_paragraph_xml(style_type, text, para_id)
        new_paragraphs.append(para_xml)
        
        if (i + 1) % 200 == 0:
            print(f"    진행: {i + 1}/{len(all_paragraphs)}")
    
    print(f"  ✓ {len(new_paragraphs)}개 문단 XML 생성 완료")
    
    # 조합
    new_xml = header + '\n' + '\n'.join(new_paragraphs) + '\n</hs:sec>'
    
    with open(section2_path, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    
    print(f"  ✓ section2.xml 저장 ({len(new_xml):,}자)")
    
    # 4. HWPX 압축
    print("\n4단계: HWPX 파일 생성...")
    
    if os.path.exists(output_hwpx):
        os.remove(output_hwpx)
    
    # mimetype 먼저 (무압축)
    with zipfile.ZipFile(output_hwpx, 'w', zipfile.ZIP_STORED) as zf:
        mimetype_path = os.path.join(temp_dir, 'mimetype')
        if os.path.exists(mimetype_path):
            zf.write(mimetype_path, 'mimetype')
    
    # 나머지 파일들
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
    print("📝 Markdown → HWPX 변환기 (전체 챕터)")
    print("="*80)
    print("\n수정 사항:")
    print("  1. 개요 번호 자동 처리 (가., 1. 등 제거 - 중복 방지)")
    print("  2. 볼드 마크다운 제거 (크기 변경 방지)")
    print("  3. 글머리문단/글머리표 구분")
    
    # 전체 챕터
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
    
    output_file = f"hwp/report_all_chapters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        result_file = create_hwpx_final(md_chapters, output_file)
        
        print("\n" + "="*80)
        print("✅ 변환 완료!")
        print("="*80)
        print(f"\n생성 파일: {result_file}")
        print("\n🔍 확인 사항:")
        print("   1. 파일이 정상적으로 열리는지")
        print("   2. '가. 가. ...' 중복이 사라졌는지")
        print("   3. 볼드 텍스트 크기가 일반 텍스트와 동일한지")
        print("   4. 전체 스타일이 원본과 일치하는지")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

