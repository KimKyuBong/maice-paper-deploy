import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

files = {
    '원본': 'hwp/report_backup_20251112_020239.hwpx',
    'test_image39': 'hwp/test_image39.hwpx',
    'report_clean_tables': 'hwp/report_clean_tables_20251112_034443.hwpx'
}

for name, path in files.items():
    with zipfile.ZipFile(path, 'r') as zf:
        bindata = [f for f in zf.namelist() if f.startswith('BinData/')]
        print(f"\n{name}: {len(bindata)}개 파일")
        
        if name == 'test_image39':
            # image39가 있는지 확인
            if 'BinData/image39.BMP' in bindata:
                print("  ✓ image39.BMP 존재")
            else:
                print("  ✗ image39.BMP 없음!")

