"""
HWPX 파일 구조 분석
HWPX는 ZIP 압축된 XML 기반 포맷
"""
import zipfile
import os
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = "hwp/report.hwpx"

print("="*80)
print("HWPX 파일 구조 분석")
print("="*80)

print(f"\n파일: {hwpx_path}")
print(f"크기: {os.path.getsize(hwpx_path):,} bytes")

# HWPX를 ZIP으로 열기
print("\n" + "="*80)
print("1. HWPX 내부 파일 목록")
print("="*80)

with zipfile.ZipFile(hwpx_path, 'r') as zf:
    file_list = zf.namelist()
    
    print(f"\n총 {len(file_list)}개 파일:\n")
    
    # 파일 분류
    xml_files = []
    image_files = []
    other_files = []
    
    for filename in sorted(file_list):
        size = zf.getinfo(filename).file_size
        
        if filename.endswith('.xml'):
            xml_files.append((filename, size))
            print(f"  📄 {filename:50} ({size:,} bytes)")
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_files.append((filename, size))
            print(f"  🖼️  {filename:50} ({size:,} bytes)")
        else:
            other_files.append((filename, size))
            print(f"  📦 {filename:50} ({size:,} bytes)")
    
    print(f"\n요약:")
    print(f"  - XML 파일: {len(xml_files)}개")
    print(f"  - 이미지: {len(image_files)}개")
    print(f"  - 기타: {len(other_files)}개")
    
    # 2. 주요 XML 파일 분석
    print("\n" + "="*80)
    print("2. 주요 XML 파일 내용 미리보기")
    print("="*80)
    
    # header.xml 분석
    if 'header.xml' in file_list:
        print("\n📄 header.xml (문서 메타데이터)")
        print("-"*80)
        with zf.open('header.xml') as f:
            content = f.read().decode('utf-8')
            print(content[:1000])
            if len(content) > 1000:
                print(f"\n... (총 {len(content):,}자 중 1000자만 표시)")
    
    # settings.xml 분석
    if 'settings.xml' in file_list:
        print("\n\n📄 settings.xml (문서 설정)")
        print("-"*80)
        with zf.open('settings.xml') as f:
            content = f.read().decode('utf-8')
            print(content[:1000])
            if len(content) > 1000:
                print(f"\n... (총 {len(content):,}자 중 1000자만 표시)")
    
    # Contents 폴더 내 파일들
    content_files = [f for f in file_list if f.startswith('Contents/')]
    if content_files:
        print("\n\n📁 Contents/ 폴더 (본문 내용)")
        print("-"*80)
        for cf in sorted(content_files)[:10]:
            size = zf.getinfo(cf).file_size
            print(f"  - {cf} ({size:,} bytes)")
        if len(content_files) > 10:
            print(f"  ... (총 {len(content_files)}개 파일)")
        
        # section0.xml 내용 확인 (주요 본문)
        section0_path = 'Contents/section0.xml'
        if section0_path in file_list:
            print(f"\n📄 {section0_path} (첫 번째 섹션 내용)")
            print("-"*80)
            with zf.open(section0_path) as f:
                content = f.read().decode('utf-8')
                print(content[:1500])
                if len(content) > 1500:
                    print(f"\n... (총 {len(content):,}자 중 1500자만 표시)")
    
    # 3. 스타일 정보 찾기
    print("\n\n" + "="*80)
    print("3. 스타일 관련 파일 찾기")
    print("="*80)
    
    style_files = [f for f in file_list if 'style' in f.lower()]
    if style_files:
        print("\n스타일 관련 파일:")
        for sf in style_files:
            size = zf.getinfo(sf).file_size
            print(f"  - {sf} ({size:,} bytes)")
            
            # 내용 미리보기
            with zf.open(sf) as f:
                content = f.read().decode('utf-8')
                print(f"\n    내용 미리보기:")
                print("    " + "-"*70)
                preview = content[:800].replace('\n', '\n    ')
                print(f"    {preview}")
                if len(content) > 800:
                    print(f"    ... (총 {len(content):,}자)")
    else:
        print("\n⚠️ 'style' 이름의 파일을 찾을 수 없습니다.")
        print("스타일 정보는 다른 XML 파일에 포함되어 있을 수 있습니다.")
    
    # 4. 압축 풀어서 저장
    extract_path = "hwp/extracted_hwpx"
    print(f"\n\n" + "="*80)
    print(f"4. HWPX 압축 해제")
    print("="*80)
    print(f"\n압축 해제 위치: {extract_path}/")
    
    os.makedirs(extract_path, exist_ok=True)
    zf.extractall(extract_path)
    
    print(f"✓ {len(file_list)}개 파일 압축 해제 완료")
    print(f"\n→ {extract_path}/ 폴더를 확인하여 XML 파일들을 직접 볼 수 있습니다.")

print("\n" + "="*80)
print("분석 완료!")
print("="*80)

