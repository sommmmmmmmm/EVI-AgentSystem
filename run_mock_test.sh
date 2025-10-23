#!/bin/bash

# Mock 테스트 실행 스크립트
# API 키 없이 보고서 생성 시스템 테스트

echo "========================================================================"
echo "🧪 EVI-AgentSystem Mock 테스트 시작"
echo "========================================================================"
echo ""

# 현재 디렉토리 확인
if [ ! -f "test_report_generation.py" ]; then
    echo "❌ 오류: test_report_generation.py 파일을 찾을 수 없습니다."
    echo "   올바른 디렉토리에서 실행했는지 확인하세요."
    echo "   현재 위치: $(pwd)"
    exit 1
fi

# Python 버전 확인
echo "📌 Python 버전 확인..."
python3 --version || python --version

echo ""
echo "📌 필요한 패키지 확인..."
python3 -c "import langchain" 2>/dev/null || python -c "import langchain" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  경고: langchain이 설치되지 않았습니다."
    echo "   다음 명령어로 설치하세요:"
    echo "   pip install -r requirements.txt"
    echo ""
    read -p "   계속 진행하시겠습니까? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "========================================================================"
echo "🚀 Mock 테스트 실행 중..."
echo "========================================================================"
echo ""

# Mock 툴 테스트 먼저 실행
echo "1️⃣ Mock Tools 단독 테스트..."
python3 mock_tools.py 2>/dev/null || python mock_tools.py 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Mock Tools 정상 작동"
    echo ""
else
    echo ""
    echo "⚠️ Mock Tools 테스트 실패 (계속 진행)"
    echo ""
fi

# 전체 시스템 테스트
echo "2️⃣ 전체 시스템 테스트..."
echo "   (시간이 1-2분 소요될 수 있습니다)"
echo ""

python3 test_report_generation.py || python test_report_generation.py

echo ""
echo "========================================================================"
echo "✅ 테스트 완료!"
echo "========================================================================"
echo ""
echo "📁 생성된 파일 확인:"
echo "   outputs/mock_test/ 디렉토리를 확인하세요"
echo ""

# 생성된 파일 목록 표시
if [ -d "outputs/mock_test" ]; then
    echo "생성된 파일:"
    ls -lh outputs/mock_test/ | tail -n +2
    echo ""
fi

echo "💡 다음 단계:"
echo "   1. outputs/mock_test/ 폴더에서 생성된 보고서 확인"
echo "   2. JSON/Markdown 파일 내용 검토"
echo "   3. 실제 API 키 설정 후 main.py 실행"
echo ""

