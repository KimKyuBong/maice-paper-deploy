"""
생성된 HWPX 파일 검증
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

hwpx_file = "hwp/report_updated_with_images.hwpx"

print("="*80)
print(f"HWPX 파일 검증: {hwpx_file}")
print("="*80)

# 1. ZIP 구조 확인
print("\n1. ZIP 구조 확인:")
try:
    with zipfile.ZipFile(hwpx_file, 'r') as zf:
        files = zf.namelist()
        print(f"✓ ZIP 파일 정상")
        print(f"  파일 수: {len(files)}개")
        
        # 필수 파일 확인
        required_files = ['mimetype', 'Contents/section2.xml', 'Contents/header.xml']
        for req_file in required_files:
            if req_file in files:
                print(f"  ✓ {req_file}")
            else:
                print(f"  ✗ {req_file} 누락!")
except Exception as e:
    print(f"✗ ZIP 파일 오류: {e}")
    sys.exit(1)

# 2. XML 파싱 검증
print("\n2. XML 파싱 검증:")
try:
    with zipfile.ZipFile(hwpx_file, 'r') as zf:
        xml_content = zf.read('Contents/section2.xml').decode('utf-8')
        
        # XML 파싱 시도
        tree = ET.fromstring(xml_content.encode('utf-8'))
        
        print(f"✓ section2.xml 파싱 성공!")
        print(f"  루트 태그: {tree.tag}")
        print(f"  자식 요소 수: {len(tree)}개")
        
        # 문단 수 확인
        ns = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
        paragraphs = tree.findall('.//hp:p', ns)
        print(f"  문단 수: {len(paragraphs)}개")
        
        # 이미지 수 확인
        pics = tree.findall('.//hp:pic', ns)
        print(f"  이미지 수: {len(pics)}개")
        
        # 표 수 확인
        tables = tree.findall('.//hp:tbl', ns)
        print(f"  표 수: {len(tables)}개")
        
except ET.ParseError as e:
    print(f"✗ XML 파싱 오류: {e}")
    
    # 오류 위치 출력
    import re
    match = re.search(r'line (\d+)', str(e))
    if match:
        line_num = int(match.group(1))
        lines = xml_content.split('\n')
        print(f"\n오류 위치 (line {line_num}):")
        start = max(0, line_num - 3)
        end = min(len(lines), line_num + 2)
        for i in range(start, end):
            prefix = ">>>" if i == line_num - 1 else "   "
            print(f"{prefix} {i+1}: {lines[i][:100]}")
    sys.exit(1)
    
except Exception as e:
    print(f"✗ 기타 오류: {e}")
    sys.exit(1)

# 3. 이미지 파일 확인
print("\n3. 이미지 파일 확인:")
try:
    with zipfile.ZipFile(hwpx_file, 'r') as zf:
        diagram_files = [f for f in zf.namelist() if f.startswith('BinData/diagram')]
        if diagram_files:
            print(f"✓ {len(diagram_files)}개 다이어그램 파일 발견:")
            for df in sorted(diagram_files):
                info = zf.getinfo(df)
                print(f"  - {df} ({info.file_size:,} bytes)")
        else:
            print("⚠ 다이어그램 파일 없음")
except Exception as e:
    print(f"✗ 오류: {e}")

print("\n" + "="*80)
print("✅ 검증 완료!")
print("="*80)
print("\n파일을 한글에서 열어보세요:")
print(f"  {hwpx_file}")

