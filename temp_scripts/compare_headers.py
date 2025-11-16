"""
example.hwpx vs 원본 파일의 header.xml, content.hpf 비교
"""
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

files = {
    'example': 'hwp/example.hwpx',
    '원본': 'hwp/report_backup_20251112_020239.hwpx'
}

for name, path in files.items():
    print("="*80)
    print(f"{name}: {path}")
    print("="*80)
    
    with zipfile.ZipFile(path, 'r') as zf:
        file_list = zf.namelist()
        
        # Contents 폴더 파일 목록
        contents_files = [f for f in file_list if f.startswith('Contents/')]
        print(f"\nContents 파일 ({len(contents_files)}개):")
        for f in sorted(contents_files):
            info = zf.getinfo(f)
            print(f"  {f}: {info.file_size:,} bytes")
        
        # content.hpf 확인
        if 'Contents/content.hpf' in file_list:
            content_hpf = zf.read('Contents/content.hpf')
            print(f"\n✓ content.hpf 존재 ({len(content_hpf)} bytes)")
            print(f"  내용 (처음 200자):")
            try:
                decoded = content_hpf.decode('utf-8')
                print(f"    {decoded[:200]}")
            except:
                print(f"    (바이너리 데이터)")
        else:
            print(f"\n✗ content.hpf 없음")
        
        # header.xml 크기
        if 'Contents/header.xml' in file_list:
            header = zf.read('Contents/header.xml').decode('utf-8')
            print(f"\n✓ header.xml: {len(header):,} bytes")
            
            # 섹션 개수 확인
            import re
            sections = re.findall(r'<hh:sec[^>]*>', header)
            print(f"  섹션 정의: {len(sections)}개")

