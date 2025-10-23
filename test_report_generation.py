"""
보고서 생성 테스트 스크립트 (API 키 불필요)
Mock 데이터를 사용하여 전체 시스템 테스트
"""

import os
import sys
from datetime import datetime
from workflow.graph import create_workflow
from workflow.state import create_initial_state
from mock_tools import create_mock_tools
import json

# UTF-8 인코딩 설정 (Windows cp949 에러 방지)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    """
    Mock 툴을 사용한 보고서 생성 테스트
    """
    
    print("="*70)
    print("🧪 보고서 생성 테스트 (Mock Mode)")
    print("="*70)
    print()
    print("⚠️  주의: 실제 API를 호출하지 않고 Mock 데이터를 사용합니다.")
    print("   실제 데이터가 아닌 테스트용 샘플 데이터입니다.")
    print()
    
    # ==========================================
    # 1. 설정
    # ==========================================
    
    config = {
        'report_month': datetime.now().strftime('%Y-%m'),
        'days_ago': 30,
        'max_news_articles': 20,  # 테스트용으로 축소
        'max_disclosures_per_company': 5,
        'max_sec_filings_per_company': 5,
        'keywords': ['EV', 'electric vehicle', 'battery', 'charging'],
        'target_audience': 'individual investors',
        'language': 'en',
        'mock_mode': True  # Mock 모드 활성화
    }
    
    print("[설정 정보]")
    print(f"   - 보고서 월: {config['report_month']}")
    print(f"   - 모드: Mock Testing Mode")
    print(f"   - 키워드: {', '.join(config['keywords'])}")
    print()
    
    # ==========================================
    # 2. Mock 툴 생성
    # ==========================================
    
    print("[Mock 툴 초기화...]")
    
    tools = create_mock_tools()
    web_search = tools['web_search']
    llm = tools['llm']
    dart = tools['dart']
    
    print("   [OK] Mock Web Search Tool ✓")
    print("   [OK] Mock LLM Tool ✓")
    print("   [OK] Mock DART Tool ✓")
    print()
    
    # ==========================================
    # 3. 초기 State 생성
    # ==========================================
    
    print("[초기 State 생성...]")
    initial_state = create_initial_state(config)
    
    # 테스트용 공급업체 추가 (Mock 데이터)
    initial_state['suppliers'] = [
        {
            'company': 'LG에너지솔루션',
            'category': 'Battery',
            'tier': 1,
            'products': ['배터리 셀', '배터리 팩', 'BMS'],
            'relationships': [
                {'oem': '테슬라', 'type': 'supply'},
                {'oem': '현대자동차', 'type': 'supply'},
                {'oem': 'GM', 'type': 'supply'}
            ],
            'overall_confidence': 0.95,
            'source': 'database'
        },
        {
            'company': 'Samsung SDI',
            'category': 'Battery',
            'tier': 1,
            'products': ['원통형 배터리', '각형 배터리', 'ESS'],
            'relationships': [
                {'oem': 'BMW', 'type': 'supply'},
                {'oem': 'Ford', 'type': 'supply'}
            ],
            'overall_confidence': 0.92,
            'source': 'database'
        },
        {
            'company': 'SK온',
            'category': 'Battery',
            'tier': 1,
            'products': ['NCM 배터리', '파우치형 배터리'],
            'relationships': [
                {'oem': '현대자동차', 'type': 'supply'},
                {'oem': 'Volkswagen', 'type': 'supply'}
            ],
            'overall_confidence': 0.88,
            'source': 'web_search'
        }
    ]
    
    print(f"   [OK] 분석 대상 기업: {len(initial_state['suppliers'])}개")
    for supplier in initial_state['suppliers']:
        print(f"       - {supplier['company']} ({supplier['category']})")
    print()
    
    # ==========================================
    # 4. 워크플로우 생성
    # ==========================================
    
    print("[워크플로우 생성...]")
    
    workflow = create_workflow(
        web_search_tool=web_search,
        llm_tool=llm,
        dart_tool=dart
    )
    
    print("   [OK] LangGraph 워크플로우 생성 완료 ✓")
    print()
    
    # ==========================================
    # 5. 워크플로우 실행
    # ==========================================
    
    print("[워크플로우 실행 시작!]")
    print("="*70)
    print()
    
    try:
        # 워크플로우 실행
        final_state = workflow.invoke(initial_state)
        
        # ==========================================
        # 6. 결과 출력
        # ==========================================
        
        print("\n" + "="*70)
        print("📊 실행 결과")
        print("="*70)
        
        print(f"\n[메시지 로그]")
        for msg in final_state['messages'][-5:]:  # 마지막 5개만
            print(f"   {msg}")
        
        if final_state['errors']:
            print(f"\n[⚠️  오류 발생: {len(final_state['errors'])}건]")
            for i, error in enumerate(final_state['errors'], 1):
                print(f"   {i}. {error['agent']}: {error['error'][:100]}...")
        
        print(f"\n[수집된 데이터]")
        print(f"   - 뉴스 기사: {len(final_state.get('news_articles', []))}건")
        print(f"   - 키워드: {len(final_state.get('keywords', []))}개")
        print(f"   - 공급업체: {len(final_state.get('suppliers', []))}개")
        
        # 재무 분석 결과
        if final_state.get('financial_analysis'):
            print(f"\n[재무 분석 결과]")
            fa = final_state['financial_analysis']
            print(f"   - 분석 기업 수: {len([k for k in fa.keys() if k not in ['analysis_weights', 'top_picks', 'analysis_metadata']])}개")
            
            if fa.get('top_picks'):
                print(f"   - Top Picks: {len(fa['top_picks'])}개")
                for i, pick in enumerate(fa['top_picks'][:3], 1):
                    print(f"      {i}. {pick.get('company', 'N/A')} (점수: {pick.get('investment_score', 0):.2f})")
        
        # 리스크 분석 결과
        if final_state.get('risk_analysis'):
            print(f"\n[리스크 분석 결과]")
            ra = final_state['risk_analysis']
            if ra.get('risk_summary'):
                summary = ra['risk_summary']
                print(f"   - 분석 기업 수: {summary.get('total_companies', 0)}개")
                print(f"   - Critical Risk: {summary.get('critical_risk', 0)}개")
                print(f"   - High Risk: {summary.get('high_risk', 0)}개")
                print(f"   - Medium Risk: {summary.get('medium_risk', 0)}개")
                print(f"   - Low Risk: {summary.get('low_risk', 0)}개")
        
        # 출처 관리
        if final_state.get('source_manager'):
            citations_count = len(final_state['source_manager'].citations)
            print(f"\n[출처 정보]")
            print(f"   - 총 인용 출처: {citations_count}개")
            
            if citations_count > 0:
                confidence_summary = final_state['source_manager'].get_citations_summary()
                print(f"   - 평균 신뢰도: {confidence_summary.get('average_confidence', 0):.2f}")
                print(f"   - 평균 신뢰성: {confidence_summary.get('average_reliability', 0):.2f}")
        
        # ==========================================
        # 7. 보고서 저장
        # ==========================================
        
        if final_state.get('final_report'):
            print("\n[📝 보고서 저장 중...]")
            
            output_dir = "outputs/mock_test"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # JSON 저장
            json_path = f"{output_dir}/mock_report_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                # final_report를 JSON으로 저장
                report_data = {
                    'metadata': {
                        'generated_at': timestamp,
                        'mode': 'mock_test',
                        'config': config
                    },
                    'report': final_state['final_report'],
                    'statistics': {
                        'companies_analyzed': len(final_state.get('suppliers', [])),
                        'news_articles': len(final_state.get('news_articles', [])),
                        'errors': len(final_state.get('errors', []))
                    }
                }
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"   [OK] JSON 저장: {json_path}")
            
            # Markdown 저장
            md_path = f"{output_dir}/mock_report_{timestamp}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# Investment Analysis Report (Mock Test)\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Mode**: Mock Testing (샘플 데이터 사용)\n\n")
                f.write("---\n\n")
                
                for section_name, section_content in final_state['final_report'].items():
                    if not section_content.strip().startswith('#'):
                        f.write(f"## {section_name}\n\n")
                    f.write(section_content)
                    f.write("\n\n---\n\n")
            print(f"   [OK] Markdown 저장: {md_path}")
            
            print("\n[✅ 보고서 생성 완료!]")
            print(f"    저장 위치: {output_dir}/")
            print(f"    파일명: mock_report_{timestamp}.*")
            
        else:
            print("\n[⚠️  보고서 미생성]")
            print("     보고서가 생성되지 않았습니다.")
        
        # ==========================================
        # 8. 테스트 요약
        # ==========================================
        
        print("\n" + "="*70)
        print("🎉 테스트 완료!")
        print("="*70)
        print()
        print("✅ Mock 모드로 성공적으로 실행되었습니다.")
        print("✅ 실제 API 키 없이 전체 프로세스를 테스트할 수 있습니다.")
        print()
        print("💡 다음 단계:")
        print("   1. outputs/mock_test/ 폴더에서 생성된 보고서 확인")
        print("   2. 실제 API 키를 설정하여 main.py 실행")
        print("   3. 결과 비교 및 검증")
        print()
        
    except Exception as e:
        print(f"\n[❌ 오류 발생: {e}]")
        import traceback
        traceback.print_exc()
        
        print("\n디버깅 정보:")
        print(f"   - 오류 타입: {type(e).__name__}")
        print(f"   - 오류 메시지: {str(e)}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

