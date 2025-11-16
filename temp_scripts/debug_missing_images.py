"""
빠진 이미지 디버깅
"""
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 그림 3-2와 6-3이 빠짐
test_files = [
    ("docs/chapters/03-system-design.md", "3-2"),
    ("docs/chapters/05-research-methods.md", "6-3"),
]

for md_file, target_fig in test_files:
    print("="*80)
    print(f"{md_file} - 그림 {target_fig} 찾기")
    print("="*80)
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 그림 번호로 찾기
    pattern = rf'\[그림[ⅠⅡⅢⅣⅤⅥⅦⅧ]+-{target_fig.split("-")[1]}\]'
    matches = list(re.finditer(pattern, content))
    
    print(f"\n{len(matches)}개 발견:")
    for i, match in enumerate(matches, 1):
        pos = match.start()
        before = content[max(0, pos-50):pos]
        after = content[pos:min(len(content), pos+150)]
        
        print(f"\n  매치 {i} (위치: {pos}):")
        print(f"    앞: ...{before}")
        print(f"    뒤: {after}...")
        
        # 다음 100자에 ```mermaid가 있는지
        next_500 = content[pos:pos+500]
        if '```mermaid' in next_500:
            mermaid_pos = next_500.find('```mermaid')
            print(f"    ✓ mermaid 블록 {mermaid_pos}자 뒤에 있음")
        else:
            print(f"    ✗ mermaid 블록 없음!")

print("\n" + "="*80)
print("결론:")
print("="*80)
print("""
그림 3-2와 6-3이 빠진 이유를 찾아야 합니다.
- Markdown에서 ```mermaid 블록이 실제로 있는지
- [그림X-Y] 캡션이 mermaid 블록 앞 500자 이내에 있는지
""")

