"""
정상 파일과 문제 파일 비교
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

# 정상 파일 (가장 최근 생성된 clean_tables 파일)
good_file = "hwp/report_clean_tables_20251112_032609.hwpx"
# 문제 파일
bad_file = "hwp/report_updated_with_images.hwpx"

print("="*80)
print("HWPX 파일 비교")
print("="*80)

# 1. ZIP 구조 비교
print("\n1. ZIP 파일 구조 비교:")
print("-"*80)

with zipfile.ZipFile(good_file, 'r') as zf_good:
    good_files = set(zf_good.namelist())
    print(f"정상 파일: {len(good_files)}개 파일")
    
with zipfile.ZipFile(bad_file, 'r') as zf_bad:
    bad_files = set(zf_bad.namelist())
    print(f"문제 파일: {len(bad_files)}개 파일")

# 추가된 파일
added = bad_files - good_files
if added:
    print(f"\n추가된 파일 ({len(added)}개):")
    for f in sorted(added)[:20]:
        print(f"  + {f}")

# 누락된 파일
removed = good_files - bad_files
if removed:
    print(f"\n누락된 파일 ({len(removed)}개):")
    for f in sorted(removed)[:20]:
        print(f"  - {f}")

# 2. section2.xml 비교
print("\n" + "="*80)
print("2. section2.xml 구조 비교:")
print("-"*80)

with zipfile.ZipFile(good_file, 'r') as zf:
    good_xml = zf.read('Contents/section2.xml').decode('utf-8')
    
with zipfile.ZipFile(bad_file, 'r') as zf:
    bad_xml = zf.read('Contents/section2.xml').decode('utf-8')

print(f"정상 파일 크기: {len(good_xml):,} bytes")
print(f"문제 파일 크기: {len(bad_xml):,} bytes")

# 첫 1000자 비교
print("\n정상 파일 시작 (처음 500자):")
print(good_xml[:500])

print("\n문제 파일 시작 (처음 500자):")
print(bad_xml[:500])

# XML 파싱 시도
print("\n" + "="*80)
print("3. XML 파싱 테스트:")
print("-"*80)

try:
    tree_good = ET.fromstring(good_xml.encode('utf-8'))
    print("✓ 정상 파일: XML 파싱 성공")
    print(f"  루트 태그: {tree_good.tag}")
    print(f"  자식 수: {len(tree_good)}")
except Exception as e:
    print(f"✗ 정상 파일: XML 파싱 실패 - {e}")

try:
    tree_bad = ET.fromstring(bad_xml.encode('utf-8'))
    print("✓ 문제 파일: XML 파싱 성공")
    print(f"  루트 태그: {tree_bad.tag}")
    print(f"  자식 수: {len(tree_bad)}")
except Exception as e:
    print(f"✗ 문제 파일: XML 파싱 실패 - {e}")
    print(f"\n오류 위치 주변 내용:")
    # 오류 위치 찾기
    import re
    match = re.search(r'line (\d+)', str(e))
    if match:
        line_num = int(match.group(1))
        lines = bad_xml.split('\n')
        start = max(0, line_num - 3)
        end = min(len(lines), line_num + 2)
        for i in range(start, end):
            prefix = ">>>" if i == line_num - 1 else "   "
            print(f"{prefix} {i+1}: {lines[i][:100]}")

# 4. 네임스페이스 비교
print("\n" + "="*80)
print("4. 네임스페이스 선언 비교:")
print("-"*80)

import re

def extract_namespaces(xml_str):
    """XML에서 네임스페이스 추출"""
    ns_pattern = r'xmlns:?(\w*)\s*=\s*"([^"]*)"'
    matches = re.findall(ns_pattern, xml_str[:2000])
    return matches

good_ns = extract_namespaces(good_xml)
bad_ns = extract_namespaces(bad_xml)

print("정상 파일 네임스페이스:")
for prefix, uri in good_ns:
    print(f"  {prefix or 'default'}: {uri}")

print("\n문제 파일 네임스페이스:")
for prefix, uri in bad_ns:
    print(f"  {prefix or 'default'}: {uri}")

