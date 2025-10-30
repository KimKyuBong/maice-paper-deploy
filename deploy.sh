#!/bin/bash

# MAICE 논문 빠른 배포 스크립트

set -e  # 에러 발생 시 중단

echo "================================================"
echo "🚀 MAICE 논문 배포 시작"
echo "================================================"
echo ""

# 현재 시간
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 1. Git 변경사항 커밋
echo "📝 1/3: Git 변경사항 커밋 중..."
git add .

# 커밋 메시지 (파라미터로 받거나 기본값 사용)
COMMIT_MSG="${1:-Update: $TIMESTAMP}"
git commit -m "$COMMIT_MSG" || echo "변경사항이 없습니다."
git push

echo "✅ Git 푸시 완료"
echo ""

# 2. 가상환경 활성화 및 MkDocs 빌드
echo "🔨 2/3: MkDocs 빌드 중..."
if [ -d "venv_mkdocs" ]; then
    source venv_mkdocs/bin/activate
else
    echo "⚠️  가상환경이 없습니다. 먼저 setup_mkdocs.sh를 실행하세요."
    exit 1
fi

mkdocs build --clean
echo "✅ 빌드 완료"
echo ""

# 3. GitHub Pages 배포
echo "🌐 3/3: GitHub Pages에 배포 중..."
mkdocs gh-deploy --force

echo ""
echo "================================================"
echo "✅ 배포 완료!"
echo "================================================"
echo ""
echo "🌐 사이트 URL을 확인하세요:"
echo "   https://YOUR_USERNAME.github.io/maice-paper/"
echo ""
echo "💡 변경사항이 반영되는 데 1-2분 정도 걸릴 수 있습니다."
echo ""

