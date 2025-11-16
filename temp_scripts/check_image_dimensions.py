"""
생성된 HWPX의 이미지 크기 확인
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
import re

sys.stdout.reconfigure(encoding='utf-8')

hwpx = "hwp/report_with_images_20251112_033511.hwpx"

with zipfile.ZipFile(hwpx, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    # 각 이미지의 크기 정보 추출
    pic_pattern = r'<hp:pic [^>]*binaryItemIDRef="(diagram\d+)"[^>]*>.*?<hp:orgSz width="(\d+)" height="(\d+)"/>.*?</hp:pic>'
    
    matches = re.findall(pic_pattern, xml, re.DOTALL)
    
    print("="*80)
    print("이미지 크기 정보")
    print("="*80)
    
    for ref, width, height in matches:
        print(f"\n{ref}:")
        print(f"  width: {width} HWP units")
        print(f"  height: {height} HWP units")
        
        # HWP units to pixels (대략)
        # 1 inch = 7200 HWP units, 96 DPI 기준
        width_px = int(width) * 96 / 7200
        height_px = int(height) * 96 / 7200
        print(f"  약 {width_px:.0f} x {height_px:.0f} pixels")
        
        if int(width) == 0 or int(height) == 0:
            print("  ⚠️ 크기가 0입니다!")

print("\n" + "="*80)
print("원본 이미지와 비교")
print("="*80)

# 원본 파일의 첫 이미지
original = "hwp/report_backup_20251112_020239.hwpx"
with zipfile.ZipFile(original, 'r') as zf:
    xml = zf.read('Contents/section2.xml').decode('utf-8')
    
    match = re.search(r'<hp:pic [^>]*binaryItemIDRef="(image\d+)"[^>]*>.*?<hp:orgSz width="(\d+)" height="(\d+)"/>', xml, re.DOTALL)
    
    if match:
        ref, width, height = match.groups()
        print(f"\n원본 첫 이미지 ({ref}):")
        print(f"  width: {width} HWP units")
        print(f"  height: {height} HWP units")
        
        width_px = int(width) * 96 / 7200
        height_px = int(height) * 96 / 7200
        print(f"  약 {width_px:.0f} x {height_px:.0f} pixels")

