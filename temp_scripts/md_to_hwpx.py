"""
Markdown을 HWP XML로 변환하고 새 HWPX 파일 생성
1. Markdown 파싱
2. HWP XML 생성 (스타일 유지)
3. 기존 HWPX 구조에 삽입
4. ZIP으로 압축 → .hwpx
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
    # YAML front matter 제거
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # 링크 제거
    text = re.sub(r'\[\[.*?\]\]', '', text)
    # HTML 주석 제거
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text.strip()

def parse_markdown_to_paragraphs(md_text):
    """
    Markdown을 문단 리스트로 파싱
    Returns: [(style_type, text, is_bold), ...]
    """
    paragraphs = []
    lines = md_text.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            continue
        
        # 제목 파싱
        if line.startswith('# '):
            text = line[2:].strip()
            paragraphs.append(('heading1', text, False))
        elif line.startswith('## '):
            text = line[3:].strip()
            paragraphs.append(('heading2', text, False))
        elif line.startswith('### '):
            text = line[4:].strip()
            paragraphs.append(('heading3', text, False))
        
        # 리스트
        elif line.startswith('- '):
            text = line[2:].strip()
            # 볼드 처리
            if '**' in text:
                paragraphs.append(('list', text, True))
            else:
                paragraphs.append(('list', text, False))
        
        # 일반 텍스트
        else:
            if '**' in line:
                paragraphs.append(('body', line, True))
            else:
                paragraphs.append(('body', line, False))
    
    return paragraphs

def create_hwp_paragraph_xml(style_type, text, para_id=0):
    """
    HWP XML 문단 생성
    """
    style_id = STYLE_MAP.get(style_type, '12')  # 기본값은 본문
    
    # 볼드 처리
    parts = []
    if '**' in text:
        segments = re.split(r'(\*\*.*?\*\*)', text)
        for seg in segments:
            if seg.startswith('**') and seg.endswith('**'):
                parts.append((seg[2:-2], True))
            elif seg:
                parts.append((seg, False))
    else:
        parts = [(text, False)]
    
    # XML 생성
    para_xml = f'<hp:p id="{para_id}" paraPrIDRef="6" styleIDRef="{style_id}" pageBreak="0" columnBreak="0" merged="0">'
    
    for text_part, is_bold in parts:
        if text_part:
            # 볼드면 다른 charPrIDRef 사용
            char_pr = "8" if is_bold else "4"
            para_xml += f'<hp:run charPrIDRef="{char_pr}"><hp:t>{text_part}</hp:t></hp:run>'
    
    para_xml += '</hp:p>\n'
    
    return para_xml

def generate_section_xml(paragraphs):
    """
    전체 섹션 XML 생성
    """
    # XML 헤더
    xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" 
         xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" 
         xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" 
         xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core">
'''
    
    # 각 문단 추가
    for i, (style_type, text, _) in enumerate(paragraphs, start=1000):
        para_xml = create_hwp_paragraph_xml(style_type, text, para_id=i)
        xml_content += para_xml
    
    xml_content += '</hs:sec>'
    
    return xml_content

def create_hwpx_from_markdown(md_files, output_hwpx):
    """
    Markdown 파일들로부터 새 HWPX 생성
    
    Args:
        md_files: [(chapter_name, md_file_path), ...]
        output_hwpx: 출력 HWPX 파일 경로
    """
    print("="*80)
    print("Markdown → HWPX 변환")
    print("="*80)
    
    # 1. 기존 HWPX 템플릿 복사
    template_hwpx = "hwp/report.hwpx"
    temp_dir = "hwp/temp_hwpx_build"
    
    print("\n1단계: 기존 HWPX 구조 복사...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    with zipfile.ZipFile(template_hwpx, 'r') as zf:
        zf.extractall(temp_dir)
    print(f"✓ 압축 해제 완료: {temp_dir}")
    
    # 2. Markdown 읽기 및 XML 생성
    print("\n2단계: Markdown 파싱 및 XML 생성...")
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
    
    # 3. 새 section XML 생성
    print("\n3단계: 새 section XML 생성...")
    new_section_xml = generate_section_xml(all_paragraphs)
    
    # section2.xml에 쓰기 (본문)
    section_path = os.path.join(temp_dir, 'Contents', 'section2.xml')
    with open(section_path, 'w', encoding='utf-8') as f:
        f.write(new_section_xml)
    
    print(f"✓ section2.xml 생성 완료 ({len(new_section_xml):,}자)")
    
    # 4. ZIP으로 압축하여 HWPX 생성
    print("\n4단계: HWPX 파일 생성...")
    
    if os.path.exists(output_hwpx):
        os.remove(output_hwpx)
    
    with zipfile.ZipFile(output_hwpx, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)
    
    file_size = os.path.getsize(output_hwpx)
    print(f"✓ HWPX 생성 완료: {output_hwpx} ({file_size:,} bytes)")
    
    # 5. 임시 폴더 정리
    shutil.rmtree(temp_dir)
    print(f"✓ 임시 폴더 정리 완료")
    
    return output_hwpx

def main():
    """메인 실행"""
    print("\n" + "="*80)
    print("📝 Markdown 논문 → HWPX 변환기")
    print("="*80)
    
    # Markdown 파일 목록
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
    
    # 출력 파일
    output_file = f"hwp/report_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hwpx"
    
    try:
        # 변환 실행
        result_file = create_hwpx_from_markdown(md_chapters, output_file)
        
        print("\n" + "="*80)
        print("✅ 변환 완료!")
        print("="*80)
        print(f"\n생성된 파일: {result_file}")
        print("\n📂 파일을 열어서 확인해주세요!")
        print("   스타일이 올바르게 적용되었는지 확인하세요.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

