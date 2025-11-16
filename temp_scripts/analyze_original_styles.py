"""
원본 백업 파일에서 서론 부분의 정확한 스타일 추출
"""
import zipfile
import sys
import re
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

backup_file = "hwp/report_backup_20251112_020239.hwpx"

print("="*80)
print("원본 백업 파일 서론 스타일 분석")
print("="*80)

# 압축 해제
extract_dir = "hwp/analyze_original"
import os
import shutil

if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)

with zipfile.ZipFile(backup_file, 'r') as zf:
    zf.extractall(extract_dir)

print(f"\n✓ 압축 해제: {extract_dir}")

# section 파일들 찾기
section_files = []
for i in range(10):
    section_path = f"{extract_dir}/Contents/section{i}.xml"
    if os.path.exists(section_path):
        section_files.append((i, section_path))

print(f"\n발견된 섹션: {len(section_files)}개")

# 각 섹션에서 "서 론" 찾기
print("\n" + "="*80)
print("'서 론' 텍스트가 포함된 섹션 찾기")
print("="*80)

for section_num, section_path in section_files:
    with open(section_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '서 론' in content or '서론' in content:
        print(f"\n✓ section{section_num}.xml에서 '서론' 발견!")
        
        # 서론 관련 문단 추출
        print("\n서론 부분 XML 구조:")
        print("-"*80)
        
        # 간단한 정규식으로 문단 추출
        pattern = r'<hp:p id="(\d+)" paraPrIDRef="(\d+)" styleIDRef="(\d+)"[^>]*>(.*?)</hp:p>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        # 서론 관련 문단만 필터
        intro_paragraphs = []
        found_intro = False
        
        for match in matches:
            para_id, para_pr, style_id, content_part = match
            
            # 텍스트 추출 (간단히)
            text_match = re.findall(r'<hp:t>(.*?)</hp:t>', content_part)
            text = ''.join(text_match)
            
            if '서 론' in text or '서론' in text:
                found_intro = True
            
            if found_intro:
                intro_paragraphs.append({
                    'id': para_id,
                    'paraPrIDRef': para_pr,
                    'styleIDRef': style_id,
                    'text': text[:100]
                })
                
                if len(intro_paragraphs) >= 30:  # 처음 30개만
                    break
        
        print(f"\n서론 부분 문단 {len(intro_paragraphs)}개:")
        for i, para in enumerate(intro_paragraphs[:20], 1):
            print(f"\n{i}. ID={para['id']}, paraPr={para['paraPrIDRef']}, style={para['styleIDRef']}")
            print(f"   텍스트: {para['text']}")
        
        # 스타일별 통계
        print("\n\n" + "="*80)
        print("스타일 ID 사용 통계 (서론 부분)")
        print("="*80)
        
        style_counts = {}
        for para in intro_paragraphs:
            style_id = para['styleIDRef']
            text_preview = para['text'][:50]
            
            if style_id not in style_counts:
                style_counts[style_id] = []
            style_counts[style_id].append(text_preview)
        
        for style_id, texts in sorted(style_counts.items()):
            print(f"\nstyleIDRef=\"{style_id}\" ({len(texts)}회 사용):")
            for text in texts[:3]:
                print(f"  - {text}")

# header.xml에서 스타일 정의 확인
print("\n\n" + "="*80)
print("header.xml에서 스타일 이름 확인")
print("="*80)

header_path = f"{extract_dir}/Contents/header.xml"
with open(header_path, 'r', encoding='utf-8') as f:
    header_content = f.read()

# 스타일 태그 찾기
style_pattern = r'<hh:style id="(\d+)" type="PARA" name="([^"]*)" engName="([^"]*)"'
styles = re.findall(style_pattern, header_content)

print("\n문단 스타일 목록:")
for style_id, korean_name, eng_name in styles[:20]:
    print(f"  ID {style_id:2s}: {korean_name:20s} ({eng_name})")

print("\n\n" + "="*80)
print("분석 완료!")
print("="*80)

