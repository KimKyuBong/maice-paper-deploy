#!/bin/bash

# MAICE 논문 MkDocs 프로젝트 설정 스크립트
# 이 스크립트는 MkDocs 프로젝트를 자동으로 설정합니다.

set -e  # 에러 발생 시 중단

echo "================================================"
echo "MAICE 논문 MkDocs 프로젝트 설정 시작"
echo "================================================"
echo ""

# 1. Python 가상환경 생성 (선택사항)
echo "📦 1/5: Python 가상환경 설정..."
if [ ! -d "venv_mkdocs" ]; then
    python3 -m venv venv_mkdocs
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 사용"
fi

# 가상환경 활성화
source venv_mkdocs/bin/activate

echo ""

# 2. MkDocs 및 필요한 패키지 설치
echo "📦 2/5: MkDocs 및 플러그인 설치..."
pip install --upgrade pip
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-git-revision-date-localized-plugin
pip install mkdocs-print-site-plugin
pip install pymdown-extensions
echo "✅ 패키지 설치 완료"

echo ""

# 3. 필요한 디렉토리 구조 생성
echo "📁 3/5: 디렉토리 구조 생성..."
mkdir -p docs/javascripts
mkdir -p docs/stylesheets
mkdir -p docs/assets/images
mkdir -p docs/assets/templates

echo "✅ 디렉토리 생성 완료"

echo ""

# 4. 기존 파일들이 올바른 위치에 있는지 확인
echo "🔍 4/5: 파일 구조 확인..."

if [ ! -d "chapters" ]; then
    echo "⚠️  경고: chapters 폴더를 찾을 수 없습니다."
else
    echo "✅ chapters 폴더 확인"
fi

if [ ! -f "mkdocs.yml" ]; then
    echo "⚠️  경고: mkdocs.yml 파일을 찾을 수 없습니다."
else
    echo "✅ mkdocs.yml 파일 확인"
fi

echo ""

# 5. 로컬 서버 실행 안내
echo "🚀 5/5: 설정 완료!"
echo ""
echo "================================================"
echo "다음 단계:"
echo "================================================"
echo ""
echo "1. 로컬에서 미리보기:"
echo "   $ source venv_mkdocs/bin/activate"
echo "   $ mkdocs serve"
echo "   브라우저에서 http://127.0.0.1:8000 접속"
echo ""
echo "2. 정적 사이트 빌드:"
echo "   $ mkdocs build"
echo "   (site/ 폴더에 빌드 결과 생성)"
echo ""
echo "3. GitHub Pages 배포:"
echo "   $ mkdocs gh-deploy"
echo "   (자동으로 gh-pages 브랜치에 배포)"
echo ""
echo "================================================"
echo "📚 자세한 가이드는 MKDOCS_GUIDE.md를 참조하세요"
echo "================================================"

# requirements.txt 생성
echo ""
echo "📝 requirements.txt 생성 중..."
cat > requirements_mkdocs.txt << EOF
mkdocs>=1.5.0
mkdocs-material>=9.5.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
mkdocs-print-site-plugin>=2.3.0
pymdown-extensions>=10.7.0
EOF
echo "✅ requirements_mkdocs.txt 생성 완료"

echo ""
echo "🎉 설정이 완료되었습니다!"
echo ""

