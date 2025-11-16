"""
PNG 파일이 실제로 컬러인지 확인
"""
import sys
from PIL import Image
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

png_file = "docs/diagrams/output/png/figure3-1-pipeline.png"

img = Image.open(png_file)

print("="*80)
print(f"파일: {png_file}")
print("="*80)
print(f"모드: {img.mode}")
print(f"크기: {img.size}")

# RGB 값 확인
pixels = np.array(img)

if img.mode == 'RGB':
    # R, G, B 각각 다른지 확인
    r = pixels[:,:,0]
    g = pixels[:,:,1]
    b = pixels[:,:,2]
    
    # 모든 픽셀이 R=G=B이면 그레이스케일
    is_gray = np.all(r == g) and np.all(g == b)
    
    if is_gray:
        print("\n⚠️ RGB 모드이지만 실제로는 그레이스케일 (흑백)!")
        print("   → 모든 픽셀의 R=G=B")
    else:
        print("\n✓ 실제 컬러 이미지")
        print(f"   R 범위: {r.min()}-{r.max()}")
        print(f"   G 범위: {g.min()}-{g.max()}")
        print(f"   B 범위: {b.min()}-{b.max()}")
    
    # 몇 개 픽셀 샘플 확인
    print("\n샘플 픽셀 (처음 5개):")
    for i in range(min(5, pixels.shape[0])):
        for j in range(min(5, pixels.shape[1])):
            r, g, b = pixels[i, j]
            print(f"  ({i},{j}): R={r}, G={g}, B={b}")

elif img.mode == 'L':
    print("\n⚠️ 그레이스케일 모드 (흑백)")
else:
    print(f"\n모드: {img.mode}")

print("\n" + "="*80)
print("결론:")
print("="*80)

if img.mode == 'RGB':
    is_gray = np.all(pixels[:,:,0] == pixels[:,:,1]) and np.all(pixels[:,:,1] == pixels[:,:,2])
    if is_gray:
        print("→ PNG 파일 자체가 흑백입니다!")
        print("→ Mermaid 다이어그램 생성 시 컬러 옵션을 확인해야 합니다.")
    else:
        print("→ PNG는 컬러입니다. 다른 원인을 찾아야 합니다.")

