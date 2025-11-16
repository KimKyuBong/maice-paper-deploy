"""
HWP 논문 챕터별 업데이트 스크립트
Markdown 내용을 기존 HWP 문서에 삽입하되, 양식과 스타일 유지
"""
import pyhwpx
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def clean_markdown(text):
    """Markdown 메타데이터 및 특수 문법 제거"""
    # YAML front matter 제거
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    
    # 링크 제거 (예: [[chapters/02-theoretical-background]])
    text = re.sub(r'\[\[.*?\]\]', '', text)
    
    # 주석 제거 (<!-- -->)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    return text.strip()

def convert_markdown_to_hwp_content(md_text):
    """
    Markdown 텍스트를 HWP에 삽입할 구조화된 데이터로 변환
    Returns: [(text, style_info), ...]
    """
    lines = md_text.split('\n')
    content = []
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            content.append(('', 'newline'))
            continue
        
        # 제목 파싱
        if line.startswith('# '):
            # 대제목 (I. 서론)
            text = line[2:].strip()
            content.append((text, 'heading1'))
        elif line.startswith('## '):
            # 중제목 (1. 연구의 필요성)
            text = line[3:].strip()
            content.append((text, 'heading2'))
        elif line.startswith('### '):
            # 소제목 (가. 수학 교육에서...)
            text = line[4:].strip()
            content.append((text, 'heading3'))
        
        # 리스트
        elif line.startswith('- '):
            text = line[2:].strip()
            # 볼드 처리
            if '**' in text:
                parts = re.split(r'\*\*(.*?)\*\*', text)
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # 일반 텍스트
                        if part:
                            content.append((part, 'list_item'))
                    else:  # 볼드 텍스트
                        content.append((part, 'list_item_bold'))
            else:
                content.append((text, 'list_item'))
        
        # 일반 단락
        else:
            # 볼드 처리
            if '**' in line:
                parts = re.split(r'\*\*(.*?)\*\*', line)
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # 일반 텍스트
                        if part:
                            content.append((part, 'normal'))
                    else:  # 볼드 텍스트
                        content.append((part, 'bold'))
            else:
                content.append((line, 'normal'))
    
    return content

def update_chapter_in_hwp(hwp_path, chapter_title, md_content):
    """
    HWP 문서에서 특정 챕터를 찾아 내용 업데이트
    
    Args:
        hwp_path: HWP 파일 경로
        chapter_title: 챕터 제목 (예: "Ⅰ. 서 론")
        md_content: Markdown 내용
    """
    print(f"\n{'='*80}")
    print(f"챕터 업데이트: {chapter_title}")
    print(f"{'='*80}\n")
    
    # Markdown 전처리
    md_content = clean_markdown(md_content)
    print(f"✓ Markdown 전처리 완료 (길이: {len(md_content):,}자)")
    
    # 구조화된 콘텐츠 생성
    content_items = convert_markdown_to_hwp_content(md_content)
    print(f"✓ 콘텐츠 파싱 완료 ({len(content_items)}개 항목)")
    
    # HWP 열기
    hwp = pyhwpx.Hwp()
    hwp.open(hwp_path)
    print(f"✓ HWP 파일 열기 완료")
    
    # 챕터 찾기
    hwp.Run("MoveDocBegin")
    found = hwp.find(chapter_title)
    
    if not found:
        print(f"✗ 챕터를 찾을 수 없습니다: {chapter_title}")
        hwp.quit()
        return False
    
    print(f"✓ 챕터 위치 찾기 완료")
    
    # 현재 위치에서 다음 챕터까지 선택
    # (여기서는 간단히 제목만 교체하는 방식으로 시작)
    
    # 제목 다음 줄로 이동
    hwp.Run("MoveLineEnd")
    hwp.BreakPara()
    
    # 기존 내용 삭제를 위해 다음 대제목까지 선택
    # 안전을 위해 현재는 내용 추가만 수행
    
    print(f"\n내용 삽입 시작...")
    inserted_count = 0
    
    for text, style in content_items:
        if not text and style == 'newline':
            hwp.BreakPara()
            continue
        
        if style == 'heading1':
            # 대제목은 이미 존재하므로 건너뜀
            continue
        elif style == 'heading2':
            hwp.insert_text(text)
            hwp.set_font(Height=14, Bold=True)
            hwp.BreakPara()
        elif style == 'heading3':
            hwp.insert_text(text)
            hwp.set_font(Height=12, Bold=True)
            hwp.BreakPara()
        elif style == 'list_item':
            hwp.insert_text(f"- {text}")
            hwp.set_font(Height=10, Bold=False)
            hwp.BreakPara()
        elif style == 'list_item_bold':
            hwp.set_font(Height=10, Bold=True)
            hwp.insert_text(text)
            hwp.set_font(Bold=False)
        elif style == 'bold':
            hwp.set_font(Height=10, Bold=True)
            hwp.insert_text(text)
            hwp.set_font(Bold=False)
        elif style == 'normal':
            hwp.insert_text(text)
            hwp.set_font(Height=10, Bold=False)
            hwp.BreakPara()
        
        inserted_count += 1
        if inserted_count % 20 == 0:
            print(f"  진행: {inserted_count}/{len(content_items)} 항목...")
    
    print(f"✓ 내용 삽입 완료 ({inserted_count}개 항목)")
    
    # 저장
    output_path = hwp_path.replace('.hwpx', '_updated.hwpx')
    result = hwp.save(output_path)
    print(f"\n저장 결과: {result}")
    print(f"저장 경로: {output_path}")
    
    hwp.quit()
    
    return True

def test_chapter_1():
    """서론(1장) 테스트"""
    hwp_path = os.path.abspath("hwp/report.hwpx")
    md_path = os.path.abspath("docs/chapters/01-introduction.md")
    
    print("="*80)
    print("서론(1장) 업데이트 테스트")
    print("="*80)
    
    # Markdown 읽기
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 업데이트 실행
    success = update_chapter_in_hwp(
        hwp_path=hwp_path,
        chapter_title="Ⅰ. 서 론",
        md_content=md_content
    )
    
    if success:
        print("\n" + "="*80)
        print("✅ 서론 업데이트 테스트 성공!")
        print("="*80)
        print("\nhwp/report_updated.hwpx 파일을 열어서 확인해주세요.")
        print("문제가 없다면 전체 챕터 업데이트를 진행하겠습니다.")
    else:
        print("\n" + "="*80)
        print("❌ 서론 업데이트 실패")
        print("="*80)
    
    return success

if __name__ == "__main__":
    try:
        test_chapter_1()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

