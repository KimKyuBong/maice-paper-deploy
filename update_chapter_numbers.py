"""
MD 파일의 표/그림 번호를 파일명에 맞게 자동 업데이트
03-research-methods.md → Ⅲ장
04-system-design.md → Ⅳ장
"""
import os
import re

# 파일명과 장 번호 매핑
file_to_chapter = {
    '01-introduction.md': 'Ⅰ',
    '02-theoretical-background.md': 'Ⅱ',
    '03-research-methods.md': 'Ⅲ',
    '04-system-design.md': 'Ⅳ',
    '05-results.md': 'Ⅴ',
    '06-discussion-conclusion.md': 'Ⅵ',
    '07-references.md': 'Ⅶ',
}

def update_file_numbers(filepath, correct_roman):
    """파일 내부의 표/그림 번호를 올바른 장 번호로 변경"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # [표X-Y] 패턴 찾기
    def replace_table(match):
        prefix = match.group(1)  # '표' 또는 '그림'
        old_roman = match.group(2)
        item_num = match.group(3)
        # 올바른 로마자로 교체
        return f'[{prefix}{correct_roman}-{item_num}]'
    
    # 표와 그림 번호 변경
    content = re.sub(r'\[(표|그림)([ⅠⅡⅢⅣⅤⅥⅦⅧ]+)-(\d+)\]', replace_table, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# 모든 장 파일 처리
chapters_dir = 'docs/chapters'
updated_count = 0

for filename, roman_num in file_to_chapter.items():
    filepath = os.path.join(chapters_dir, filename)
    if os.path.exists(filepath):
        if update_file_numbers(filepath, roman_num):
            print(f'[OK] {filename} -> {roman_num}장으로 업데이트')
            updated_count += 1
        else:
            print(f'     {filename} -> 변경 없음 (이미 올바름)')

print(f'\n총 {updated_count}개 파일 업데이트 완료!')

