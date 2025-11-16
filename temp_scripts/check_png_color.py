"""
PNG 파일 색상 모드 확인
"""
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

png_files = [
    "docs/diagrams/output/png/figure3-1-pipeline.png",
    "docs/diagrams/output/png/figure3-2-architecture.png",
    "docs/diagrams/output/png/figure6-1-research-design.png",
]

print("="*80)
print("PNG 파일 색상 정보")
print("="*80)

for png_file in png_files:
    img = Image.open(png_file)
    print(f"\n{png_file.split('/')[-1]}:")
    print(f"  모드: {img.mode}")
    print(f"  크기: {img.size}")
    
    if img.mode == 'L':
        print(f"  ⚠️ 그레이스케일 (흑백) 이미지!")
    elif img.mode == 'RGB':
        print(f"  ✓ 컬러 이미지")
    elif img.mode == 'RGBA':
        print(f"  ✓ 컬러 + 투명도")

