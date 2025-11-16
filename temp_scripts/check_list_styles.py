"""
원본에서 글머리문단(13)과 글머리표(14) 사용 확인
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("글머리 스타일 분석")
print("="*80)

with open('hwp/analyze_original/Contents/section2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# styleIDRef="13" (글머리문단) 사용 예시
print("\n1. styleIDRef=\"13\" (○ 글머리문단) 사용 예시:")
print("-"*80)

pattern13 = r'<hp:p[^>]*styleIDRef="13"[^>]*>(.*?)</hp:p>'
matches13 = re.findall(pattern13, content, re.DOTALL)

for i, match in enumerate(matches13[:5], 1):
    text = re.findall(r'<hp:t>(.*?)</hp:t>', match)
    text_str = ''.join(text)[:100]
    print(f"{i}. {text_str}")

print(f"\n총 {len(matches13)}개 사용")

# styleIDRef="14" (글머리표) 사용 예시
print("\n\n2. styleIDRef=\"14\" (․ 글머리표) 사용 예시:")
print("-"*80)

pattern14 = r'<hp:p[^>]*styleIDRef="14"[^>]*>(.*?)</hp:p>'
matches14 = re.findall(pattern14, content, re.DOTALL)

for i, match in enumerate(matches14[:5], 1):
    text = re.findall(r'<hp:t>(.*?)</hp:t>', match)
    text_str = ''.join(text)[:100]
    print(f"{i}. {text_str}")

print(f"\n총 {len(matches14)}개 사용")

# paraPrIDRef 확인
print("\n\n3. paraPrIDRef 확인:")
print("-"*80)

# styleIDRef="13" 의 paraPrIDRef
pattern13_para = r'<hp:p[^>]*paraPrIDRef="(\d+)"[^>]*styleIDRef="13"'
para_refs_13 = set(re.findall(pattern13_para, content))
print(f"styleIDRef=\"13\" 의 paraPrIDRef: {para_refs_13}")

# styleIDRef="14" 의 paraPrIDRef
pattern14_para = r'<hp:p[^>]*paraPrIDRef="(\d+)"[^>]*styleIDRef="14"'
para_refs_14 = set(re.findall(pattern14_para, content))
print(f"styleIDRef=\"14\" 의 paraPrIDRef: {para_refs_14}")

print("\n\n" + "="*80)
print("결론:")
print("="*80)
print("""
Markdown의 "- 리스트" 는:
  → styleIDRef="14" (․ 글머리표) 사용
  → paraPrIDRef를 확인하여 정확히 매핑 필요
""")

