#!/usr/bin/env python3
"""
논문 장절 번호 체계를 한국 학술 논문 표준 형식으로 변환
현재: 1.1, 1.1.1, 1.1.1.1
변경: I, 1, 가, 1)
"""
import re
from pathlib import Path

# 로마 숫자 변환
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

# 한글 가나다 순서
HANGUL = ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하',
          '거', '너', '더', '러', '머', '버', '서', '어', '저', '처', '커', '터', '퍼', '허']

def convert_chapter_numbering(content, chapter_num):
    """
    장 번호 변환
    # 1. 서론 → # I. 서론
    """
    lines = content.split('\n')
    result = []
    
    section_counters = {}  # {level: counter}
    
    for line in lines:
        # 장 제목 (# 1. 서론)
        if re.match(r'^# \d+\. ', line):
            # # 1. 서론 → # I. 서론
            new_line = re.sub(r'^# \d+\. ', f'# {ROMAN[chapter_num - 1]}. ', line)
            result.append(new_line)
            section_counters = {2: 0, 3: 0, 4: 0}  # 리셋
            
        # 절 제목 (## 1.1 ...)
        elif re.match(r'^## \d+\.\d+ ', line):
            section_counters[2] = section_counters.get(2, 0) + 1
            section_counters[3] = 0  # 하위 레벨 리셋
            section_counters[4] = 0
            
            # ## 1.1 연구의 필요성 → ## 1. 연구의 필요성
            title = re.sub(r'^## \d+\.\d+ ', '', line)
            new_line = f'## {section_counters[2]}. {title}'
            result.append(new_line)
            
        # 항 제목 (### 1.1.1 ...)
        elif re.match(r'^### \d+\.\d+\.\d+ ', line):
            section_counters[3] = section_counters.get(3, 0) + 1
            section_counters[4] = 0  # 하위 레벨 리셋
            
            # ### 1.1.1 ... → ### 가. ...
            title = re.sub(r'^### \d+\.\d+\.\d+ ', '', line)
            hangul_idx = section_counters[3] - 1
            if hangul_idx < len(HANGUL):
                new_line = f'### {HANGUL[hangul_idx]}. {title}'
            else:
                new_line = line  # 범위 초과시 원본 유지
            result.append(new_line)
            
        # 목 제목 (#### 1.1.1.1 ...)
        elif re.match(r'^#### \d+\.\d+\.\d+\.\d+ ', line):
            section_counters[4] = section_counters.get(4, 0) + 1
            
            # #### 1.1.1.1 ... → #### 1) ...
            title = re.sub(r'^#### \d+\.\d+\.\d+\.\d+ ', '', line)
            new_line = f'#### {section_counters[4]}) {title}'
            result.append(new_line)
            
        else:
            result.append(line)
    
    return '\n'.join(result)


def process_file(filepath, chapter_num):
    """파일 처리"""
    print(f"\n처리 중: {filepath.name} (Chapter {ROMAN[chapter_num - 1]})")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 변환
    new_content = convert_chapter_numbering(content, chapter_num)
    
    # 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 완료: {filepath.name}")


def main():
    chapters_dir = Path('docs/chapters')
    
    # 처리할 파일과 장 번호 매핑
    files_to_process = [
        ('01-introduction.md', 1),
        ('02-theoretical-background.md', 2),
        ('03-system-design.md', 3),
        ('04-system-implementation.md', 4),
        ('05-mathematical-induction-application.md', 5),
        ('06-research-methods.md', 6),
        ('07-results.md', 7),
        ('08-discussion-conclusion.md', 8),
        ('09-references.md', 9),
    ]
    
    print("=" * 60)
    print("논문 장절 번호 체계 변환 시작")
    print("형식: I. → 1. → 가. → 1)")
    print("=" * 60)
    
    for filename, chapter_num in files_to_process:
        filepath = chapters_dir / filename
        if filepath.exists():
            process_file(filepath, chapter_num)
        else:
            print(f"⚠️  파일 없음: {filepath}")
    
    print("\n" + "=" * 60)
    print("모든 변환 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()

