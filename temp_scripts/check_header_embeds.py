import sys, zipfile, re
sys.stdout.reconfigure(encoding='utf-8')

zf = zipfile.ZipFile('hwp/report_backup_20251112_020239.hwpx', 'r')
header = zf.read('Contents/header.xml').decode('utf-8')

print("header.xml 크기:", len(header))
print("'binData' 포함:", 'binData' in header)
print("'BinData' 포함:", 'BinData' in header)  
print("'embed' 포함:", 'embed' in header)
print("'image1' 참조:", 'image1' in header)

# image 또는 binData 관련 태그 찾기
patterns = [
    r'<hh:binData[^>]*>',
    r'<hh:embedBinary[^>]*>',
    r'binaryItemIDRef="image\d+"'
]

for pattern in patterns:
    matches = re.findall(pattern, header)
    if matches:
        print(f"\n패턴 '{pattern}': {len(matches)}개")
        for m in matches[:3]:
            print(f"  {m[:100]}")

