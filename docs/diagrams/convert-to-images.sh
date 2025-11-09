#!/bin/bash

# 머메이드 다이어그램을 논문용 이미지로 변환하는 스크립트
# 사용법: ./convert-to-images.sh

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   MAICE 논문용 다이어그램 변환 스크립트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# mmdc 명령어 확인
if ! command -v mmdc &> /dev/null; then
    echo -e "${RED}❌ mermaid-cli가 설치되어 있지 않습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "  npm install -g @mermaid-js/mermaid-cli"
    echo ""
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p output/svg
mkdir -p output/png

echo -e "${GREEN}✓ mermaid-cli 확인 완료${NC}"
echo ""

# 변환할 파일 목록
files=(
    "figure3-1-pipeline:그림 3.1 질문 처리 파이프라인"
    "figure3-2-architecture:그림 3.2 3계층 아키텍처"
    "figure3-3-sequence:그림 3.3 질문 처리 시퀀스"
    "figure3-4-gating:그림 3.4 3단계 게이팅"
    "figure3-5-clarification:그림 3.5 명료화 프로세스"
    "figure3-6-ocr:그림 3.6 OCR 시스템"
)

echo -e "${BLUE}📊 다이어그램 변환 시작...${NC}"
echo ""

# 각 파일 변환
for item in "${files[@]}"; do
    IFS=':' read -r filename description <<< "$item"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "📄 ${description}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # SVG 변환 (벡터, 최고 품질)
    echo -n "  SVG 변환 중... "
    if mmdc -i "${filename}.mmd" -o "output/svg/${filename}.svg" -t neutral -b transparent 2>/dev/null; then
        echo -e "${GREEN}✓ 완료${NC}"
    else
        echo -e "${RED}✗ 실패${NC}"
    fi
    
    # PNG 변환 (고해상도, 300 DPI 기준)
    echo -n "  PNG 변환 중 (고해상도)... "
    if mmdc -i "${filename}.mmd" -o "output/png/${filename}.png" -t neutral -b white -w 3000 2>/dev/null; then
        echo -e "${GREEN}✓ 완료${NC}"
    else
        echo -e "${RED}✗ 실패${NC}"
    fi
    
    echo ""
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 모든 다이어그램 변환 완료!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📁 출력 위치:"
echo "  - SVG (벡터): ./output/svg/"
echo "  - PNG (래스터): ./output/png/"
echo ""
echo "💡 권장사항:"
echo "  - LaTeX 논문: SVG 파일 사용 권장"
echo "  - Word 논문: PNG 파일 사용 가능"
echo "  - 인쇄물: SVG 또는 고해상도 PNG 사용"
echo ""












