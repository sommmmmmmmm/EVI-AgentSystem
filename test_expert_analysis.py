"""
Test Expert Analysis System

Tests the qualitative analysis (전문가 의견) system
"""

from tools.real_expert_analysis_tools import RealExpertAnalysisTool


def test_expert_analysis_system():
    """Test the expert analysis system"""
    
    print("="*80)
    print("전문가 의견 시스템 테스트 (Expert Analysis System Test)")
    print("="*80)
    
    tool = RealExpertAnalysisTool()
    
    # Test companies
    test_companies = [
        'Tesla',
        'LG Energy Solution',
        'Samsung SDI',
        'BYD',
        'BMW',
        'GM'
    ]
    
    print("\n" + "="*80)
    print("1. 전문가 컨센서스 테스트 (Expert Consensus Test)")
    print("="*80)
    
    for company in test_companies:
        print(f"\n[{company}]")
        
        # Get expert analyses
        analyses = tool.get_expert_analyses(company)
        print(f"  전문가 의견 개수: {len(analyses)}")
        
        if analyses:
            # Show first analysis
            first = analyses[0]
            print(f"  출처: {first['source']}")
            print(f"  애널리스트: {first.get('analyst', 'Unknown')}")
            print(f"  등급: {first['rating']}")
            print(f"  목표가: {first['target_price']:,}")
            print(f"  상승여력: {first['upside']:+.1f}%")
            print(f"  신뢰도: {first['confidence']:.2f}")
            
            # Calculate consensus
            consensus = tool.calculate_expert_consensus(company)
            print(f"\n  컨센서스 등급: {consensus['consensus_rating']}")
            print(f"  컨센서스 목표가: {consensus['consensus_target_price']:,.0f}")
            print(f"  컨센서스 상승여력: {consensus['consensus_upside']:+.1f}%")
            print(f"  신뢰도 점수: {consensus['confidence_score']:.2f}")
            print(f"  강세 비율: {consensus['bullish_ratio']:.1%}")
            print(f"  약세 비율: {consensus['bearish_ratio']:.1%}")
            print(f"  분석가 수: {consensus['analyst_count']}")
        else:
            print(f"  ⚠️ 전문가 의견 데이터 없음")
    
    print("\n" + "="*80)
    print("2. 리스크 요인 분석 테스트 (Risk Factors Test)")
    print("="*80)
    
    for company in ['Tesla', 'LG Energy Solution', 'BMW']:
        print(f"\n[{company}]")
        risks = tool.get_risk_factors(company)
        
        if risks:
            print(f"  총 리스크 요인: {len(risks)}개")
            print(f"  주요 리스크:")
            for i, risk in enumerate(risks[:3], 1):
                print(f"    {i}. {risk['risk']}")
                print(f"       출처: {risk['source']} (신뢰도: {risk['confidence']:.2f})")
        else:
            print(f"  ⚠️ 리스크 데이터 없음")
    
    print("\n" + "="*80)
    print("3. 성장 동력 분석 테스트 (Growth Drivers Test)")
    print("="*80)
    
    for company in ['Tesla', 'Samsung SDI', 'GM']:
        print(f"\n[{company}]")
        drivers = tool.get_growth_drivers(company)
        
        if drivers:
            print(f"  총 성장 동력: {len(drivers)}개")
            print(f"  주요 성장 동력:")
            for i, driver in enumerate(drivers[:3], 1):
                print(f"    {i}. {driver['driver']}")
                print(f"       출처: {driver['source']} (신뢰도: {driver['confidence']:.2f})")
        else:
            print(f"  ⚠️ 성장 동력 데이터 없음")
    
    print("\n" + "="*80)
    print("4. 정성적 분석 통합 테스트 (Qualitative Analysis Integration)")
    print("="*80)
    
    for company in ['Tesla', 'LG Energy Solution']:
        print(f"\n[{company}]")
        
        # This is what FinancialAnalyzerAgent calls
        analysis = tool.generate_qualitative_analysis(company)
        
        expert = analysis.get('expert_analysis', {})
        print(f"  전문가 컨센서스 점수: {expert.get('expert_consensus_score', 0):.1f}")
        print(f"  전문가 신뢰도: {expert.get('expert_confidence', 0):.2f}")
        print(f"  의견 개수: {expert.get('opinion_count', 0)}")
        
        key_points = expert.get('key_points', [])
        if key_points:
            print(f"  핵심 포인트:")
            for i, point in enumerate(key_points[:3], 1):
                print(f"    {i}. {point}")
        
        risk_factors = expert.get('risk_factors', [])
        if risk_factors:
            print(f"  리스크 요인:")
            for i, risk in enumerate(risk_factors[:3], 1):
                print(f"    {i}. {risk}")
    
    print("\n" + "="*80)
    print("5. 전문가 요약 테스트 (Expert Summary Test)")
    print("="*80)
    
    for company in ['Tesla', 'BYD']:
        print(f"\n[{company}]")
        
        summary = tool.generate_expert_summary(company)
        
        print(f"\n{summary.get('expert_summary', 'No summary available')}")
    
    print("\n" + "="*80)
    print("6. 전문가 출처 가중치 테스트 (Source Credibility Test)")
    print("="*80)
    
    expert_sources = tool.expert_sources
    
    for category, info in expert_sources.items():
        print(f"\n[{category}]")
        print(f"  신뢰도: {info['credibility']}")
        print(f"  가중치: {info['weight']}")
        print(f"  출처 수: {len(info['sources'])}")
        print(f"  출처 예시: {', '.join(info['sources'][:3])}")
    
    print("\n" + "="*80)
    print("✅ 전문가 의견 시스템 테스트 완료!")
    print("="*80)
    
    # Summary statistics
    print("\n📊 데이터베이스 통계:")
    all_companies = list(tool.analysis_database.keys())
    total_analyses = sum(len(analyses) for analyses in tool.analysis_database.values())
    
    print(f"  - 커버리지 기업 수: {len(all_companies)}")
    print(f"  - 총 전문가 의견 수: {total_analyses}")
    print(f"  - 평균 기업당 의견 수: {total_analyses / len(all_companies):.1f}")
    print(f"  - 커버리지 기업: {', '.join(all_companies[:10])}")
    
    # Check if system is working properly
    print("\n🔍 시스템 상태 체크:")
    working_count = 0
    not_working = []
    
    for company in test_companies:
        analyses = tool.get_expert_analyses(company)
        if analyses:
            working_count += 1
        else:
            not_working.append(company)
    
    if working_count == len(test_companies):
        print(f"  ✅ 모든 테스트 기업({len(test_companies)}개)에 대해 전문가 의견 데이터 존재")
    else:
        print(f"  ⚠️ {working_count}/{len(test_companies)}개 기업만 데이터 존재")
        if not_working:
            print(f"  데이터 없는 기업: {', '.join(not_working)}")
    
    print("\n" + "="*80)
    print("테스트 종료")
    print("="*80)


if __name__ == "__main__":
    test_expert_analysis_system()

