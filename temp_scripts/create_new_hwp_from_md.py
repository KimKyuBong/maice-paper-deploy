"""
Markdown 파일들을 기존 HWP 스타일로 새 HWP 문서 생성
1. 기존 HWP에서 스타일 추출
2. 새 HWP 생성
3. 스타일 적용
4. Markdown 내용을 스타일과 함께 삽입
"""
import pyhwpx
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 스타일 매핑
STYLE_MAPPING = {
    'heading1': 'Ⅰ. 제목',     # # I. 서론
    'heading2': '1. 제목',      # ## 1. 연구의 필요성
    'heading3': '가. 제목',     # ### 가. 수학 교육
    'heading4': '1) 제목',      # #### 1) 소제목
    'heading5': '가) 제목',     # ##### 가) 더 작은 제목
    'body': '본문',             # 일반 텍스트
    'list': '․ 글머리표',       # - 리스트
}

def extract_styles_from_hwp(hwp_path, style_output_path):
    """기존 HWP에서 스타일 추출"""
    print("="*80)
    print("1단계: 기존 HWP에서 스타일 추출")
    print("="*80)
    
    hwp = pyhwpx.Hwp()
    hwp.open(hwp_path)
    
    # 스타일 내보내기
    result = hwp.export_style(style_output_path)
    print(f"스타일 추출 결과: {result}")
    print(f"스타일 파일 저장: {style_output_path}")
    
    # 스타일 목록 확인
    styles = hwp.get_style_dict()
    print(f"\n총 {len(styles)}개 스타일 추출됨:")
    
    for style in styles[:15]:
        if isinstance(style, dict):
            print(f"  - {style.get('Name', 'N/A')} (ID: {style.get('Id', 'N/A')})")
    
    hwp.quit()
    
    return os.path.exists(style_output_path)

def clean_markdown(text):
    """Markdown 메타데이터 제거"""
    # YAML front matter 제거
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # 링크 제거
    text = re.sub(r'\[\[.*?\]\]', '', text)
    # HTML 주석 제거
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # 불필요한 공백 제거
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    return text.strip()

def parse_markdown_line(line):
    """
    Markdown 줄을 파싱하여 (텍스트, 스타일, 서식) 반환
    """
    line = line.rstrip()
    
    if not line:
        return ('', 'newline', {})
    
    # 제목 파싱
    if line.startswith('# '):
        return (line[2:].strip(), 'heading1', {'bold': False})
    elif line.startswith('## '):
        return (line[3:].strip(), 'heading2', {'bold': False})
    elif line.startswith('### '):
        return (line[4:].strip(), 'heading3', {'bold': False})
    elif line.startswith('#### '):
        return (line[5:].strip(), 'heading4', {'bold': False})
    elif line.startswith('##### '):
        return (line[6:].strip(), 'heading5', {'bold': False})
    
    # 리스트
    elif line.startswith('- '):
        text = line[2:].strip()
        return (text, 'list', {})
    
    # 일반 텍스트
    else:
        return (line, 'body', {})

def parse_inline_formatting(text):
    """
    인라인 서식 (볼드, 이탤릭 등) 파싱
    Returns: [(text, is_bold), ...]
    """
    parts = []
    
    # 볼드 처리: **text**
    segments = re.split(r'(\*\*.*?\*\*)', text)
    
    for segment in segments:
        if segment.startswith('**') and segment.endswith('**'):
            # 볼드
            parts.append((segment[2:-2], True))
        elif segment:
            # 일반
            parts.append((segment, False))
    
    return parts

def create_new_hwp_with_styles(style_file, chapters, output_path):
    """
    새 HWP 문서 생성 및 스타일 적용
    
    Args:
        style_file: 추출한 스타일 파일 경로
        chapters: [(chapter_title, md_content), ...] 챕터 목록
        output_path: 출력 HWP 파일 경로
    """
    print("\n" + "="*80)
    print("2단계: 새 HWP 문서 생성 및 내용 삽입")
    print("="*80)
    
    hwp = pyhwpx.Hwp()
    print("✓ 새 문서 생성 완료")
    
    # 스타일 가져오기
    print(f"\n스타일 가져오기: {style_file}")
    result = hwp.import_style(style_file)
    print(f"스타일 가져오기 결과: {result}")
    
    # 가져온 스타일 확인
    imported_styles = hwp.get_style_dict()
    print(f"✓ {len(imported_styles)}개 스타일 적용됨")
    
    # 각 챕터 삽입
    total_lines = 0
    
    for chapter_num, (chapter_title, md_content) in enumerate(chapters, 1):
        print(f"\n--- 챕터 {chapter_num}: {chapter_title} ---")
        
        # Markdown 전처리
        md_content = clean_markdown(md_content)
        lines = md_content.split('\n')
        
        print(f"  총 {len(lines)}줄 처리 중...")
        
        for line_num, line in enumerate(lines, 1):
            text, style_type, formatting = parse_markdown_line(line)
            
            if style_type == 'newline':
                hwp.BreakPara()
                continue
            
            # 스타일 적용
            hwp_style = STYLE_MAPPING.get(style_type, '본문')
            
            try:
                hwp.set_style(hwp_style)
            except Exception as e:
                print(f"  경고: 스타일 '{hwp_style}' 적용 실패: {e}")
            
            # 인라인 서식 처리
            inline_parts = parse_inline_formatting(text)
            
            for part_text, is_bold in inline_parts:
                if part_text:
                    hwp.insert_text(part_text)
                    if is_bold:
                        # 볼드 적용 (텍스트 입력 후 선택하여 적용)
                        pass  # 현재 간단히 처리
            
            hwp.BreakPara()
            total_lines += 1
            
            if line_num % 50 == 0:
                print(f"    진행: {line_num}/{len(lines)} 줄...")
        
        print(f"  ✓ 챕터 {chapter_num} 완료 ({len(lines)}줄)")
        
        # 챕터 사이 페이지 구분 (선택적)
        if chapter_num < len(chapters):
            hwp.BreakPara()
            hwp.BreakPara()
    
    print(f"\n✓ 전체 {total_lines}줄 삽입 완료")
    
    # 저장
    print(f"\n문서 저장 중: {output_path}")
    save_result = hwp.save(output_path)
    print(f"저장 결과: {save_result}")
    
    if save_result and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✓ 파일 생성 완료: {output_path} ({file_size:,} bytes)")
    
    hwp.quit()
    
    return save_result

def main():
    """메인 실행 함수"""
    print("="*80)
    print("Markdown → HWP 변환 (기존 스타일 유지)")
    print("="*80)
    
    # 파일 경로
    original_hwp = os.path.abspath("hwp/report.hwpx")
    style_file = os.path.abspath("hwp/extracted_styles.style")
    output_hwp = os.path.abspath("hwp/report_new.hwpx")
    
    # 1단계: 스타일 추출
    if not extract_styles_from_hwp(original_hwp, style_file):
        print("\n❌ 스타일 추출 실패!")
        return False
    
    # 2단계: Markdown 파일 읽기
    print("\n" + "="*80)
    print("Markdown 파일 읽기")
    print("="*80)
    
    chapters = []
    chapter_files = [
        ("Ⅰ. 서론", "docs/chapters/01-introduction.md"),
        ("Ⅱ. 이론적 배경", "docs/chapters/02-theoretical-background.md"),
        ("Ⅲ. 시스템 설계", "docs/chapters/03-system-design.md"),
        ("Ⅳ. 시스템 구현", "docs/chapters/04-system-implementation.md"),
        ("Ⅴ. 연구 방법", "docs/chapters/05-research-methods.md"),
        ("Ⅵ. 결과", "docs/chapters/06-results.md"),
        ("Ⅶ. 논의 및 결론", "docs/chapters/07-discussion-conclusion.md"),
        ("Ⅷ. 참고문헌", "docs/chapters/08-references.md"),
    ]
    
    for title, file_path in chapter_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                chapters.append((title, content))
                print(f"  ✓ {title}: {len(content):,}자")
        else:
            print(f"  ⚠ 파일 없음: {file_path}")
    
    print(f"\n총 {len(chapters)}개 챕터 로드 완료")
    
    # 3단계: 새 HWP 생성
    success = create_new_hwp_with_styles(style_file, chapters, output_hwp)
    
    if success:
        print("\n" + "="*80)
        print("✅ 새 HWP 문서 생성 완료!")
        print("="*80)
        print(f"\n생성된 파일: {output_hwp}")
        print("\n파일을 열어서 확인해주세요!")
    else:
        print("\n" + "="*80)
        print("❌ 문서 생성 실패")
        print("="*80)
    
    return success

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

