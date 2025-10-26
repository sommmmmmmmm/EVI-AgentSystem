"""

"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from workflow.graph import create_workflow
from workflow.state import create_initial_state
from tools.web_tools import WebSearchTool
from tools.llm_tools import OpenAILLM
from tools.dart_tools import DARTTool
from tools.sec_edgar_tools import SECEdgarTool  # 🆕 SEC EDGAR tool 추가
from tools.report_converter import ReportConverter
import json

# UTF-8   (Windows cp949  )
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# .env
load_dotenv()


def main():
    """
      
    """
    
    print("="*70)
    print("        ")
    print("="*70)
    print()
    
    # ==========================================
    # 1. 
    # ==========================================
    
    config = {
        'report_month': datetime.now().strftime('%Y-%m'),
        'days_ago': 30,  # 최근 30일 이내 뉴스만 수집
        'max_news_articles': 100,  # 최대 100개 뉴스 기사로 증가 (신뢰도 향상)
        'max_disclosures_per_company': 10,  # 기업당 최대 공시 수
        'max_sec_filings_per_company': 8,  # SEC 기업당 최대 공시 수
        'keywords': ['EV', 'electric vehicle', 'battery', 'charging'],  # 영어 키워드로 변경
        'target_audience': 'individual investors',  # 영어로 변경
        'language': 'en',  # 영어 보고서 생성
        
        # 데이터 수집 전략 (웹 서치 실패 대비)
        'relaxed_mode': True,  # 에러 시에도 계속 진행 (기준 완화)
        'fallback_enabled': True,  # 웹 서치 실패 시 fallback 전략 사용
        'default_companies_enabled': True  # 기본 기업 리스트 사용 여부
    }
    
    print("[설정 정보]")
    print(f"   - 보고서 월: {config['report_month']}")
    print(f"   - 뉴스 수집 기간: 최근 {config['days_ago']}일")
    print(f"   - 최대 뉴스 기사 수: {config['max_news_articles']}개")
    print(f"   - 키워드: {', '.join(config['keywords'])}")
    print(f"   - 대상 독자: {config['target_audience']}")
    print(f"   - Relaxed Mode: {'활성화' if config.get('relaxed_mode') else '비활성화'}")
    print(f"   - Fallback 전략: {'활성화' if config.get('fallback_enabled') else '비활성화'}")
    print()
    
    # ==========================================
    # 2.  
    # ==========================================
    
    print("[  ...]")
    
    # Web Search ( web_search  )
    web_search = WebSearchTool()
    
    # OpenAI API
    openai_api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-your-key-here')
    llm = OpenAILLM(openai_api_key, model='gpt-4o-mini')  # 비용 절감: GPT-4o-mini 사용
    
    # DART API (한국 기업)
    dart_api_key = os.getenv('DART_API_KEY', 'f9cc57c302b3717900443947647ca55800eb6e8a')
    dart = DARTTool(dart_api_key)
    
    # SEC EDGAR API (미국 기업) - 🆕 추가
    sec = SECEdgarTool()
    
    print("   [OK] Web Search 도구 초기화")
    print("   [OK] OpenAI API 초기화")
    if dart_api_key:
        print("   [OK] DART API 초기화 (한국 기업)")
    print("   [OK] SEC EDGAR 초기화 (미국 기업)")
    print()
    
    # ==========================================
    # 3.  State 
    # ==========================================
    
    initial_state = create_initial_state(config)
    
    # ==========================================
    # 4.  
    # ==========================================
    
    print("[워크플로우 생성 중...]")
    
    workflow = create_workflow(
        web_search_tool=web_search,
        llm_tool=llm,
        dart_tool=dart,
        sec_tool=sec  # 🆕 SEC tool 전달
    )
    
    print("   [OK] LangGraph 워크플로우 생성 완료")
    print()
    
    # ==========================================
    # 5. 
    # ==========================================
    
    print("[  !]")
    print("="*70)
    
    try:
        # 워크플로우 실행 (LangGraph 버전 호환성 문제로 수동 실행)
        # LangGraph의 checkpoint 버그를 회피하기 위해 각 에이전트를 직접 호출
        from agents.market_trend_agent import MarketTrendAgent
        from agents.supplier_matching_agent import SupplierMatchingAgent
        from agents.financial_analyzer_agent import FinancialAnalyzerAgent
        from agents.risk_assessment_agent_improved import RiskAssessmentAgent
        from agents.investment_strategy_agent import InvestmentStrategyAgent
        from agents.report_generator_agent import ReportGeneratorAgent
        
        # 에이전트 초기화
        market_agent = MarketTrendAgent(web_search, llm, dart)
        supplier_agent = SupplierMatchingAgent(web_search, llm)
        financial_agent = FinancialAnalyzerAgent(web_search, llm, dart, sec_tool=sec)
        risk_agent = RiskAssessmentAgent(web_search, llm)
        strategy_agent = InvestmentStrategyAgent(web_search, llm)
        report_agent = ReportGeneratorAgent(llm)
        
        final_state = initial_state
        
        # 1. MarketTrendAgent
        print("[현재 노드: market_trend_node]")
        print("="*60)
        result = market_agent.analyze_market_trends(final_state)
        final_state['news_articles'] = result.get('news_articles', [])
        final_state['disclosure_data'] = result.get('disclosure_data', [])
        final_state['keywords'] = result.get('keywords', [])
        final_state['categorized_keywords'] = result.get('categorized_keywords', {})
        final_state['market_trends'] = result.get('market_trends', [])
        discovered = result.get('discovered_companies', [])
        if discovered:
            final_state['suppliers'].extend(discovered)
        
        # 2. SupplierMatchingAgent
        print("\n[현재 노드: supplier_matching_node]")
        print("="*60)
        result = supplier_agent.match_suppliers(final_state)
        final_state['suppliers'] = result.get('suppliers', [])
        
        # 3. FinancialAnalyzerAgent
        print("\n[현재 노드: financial_analysis_node]")
        print("="*60)
        result = financial_agent.analyze_financials(final_state)
        final_state['financial_analysis'] = result.get('financial_analysis', {})
        
        # 4. RiskAssessmentAgent
        print("\n[현재 노드: risk_assessment_node]")
        print("="*60)
        result = risk_agent.analyze_risks(final_state)
        final_state['risk_assessment'] = result.get('risk_assessment', {})
        
        # 5. InvestmentStrategyAgent
        print("\n[현재 노드: investment_strategy_node]")
        print("="*60)
        result = strategy_agent.develop_investment_strategy(final_state)
        final_state['investment_strategy'] = result.get('investment_strategy', {})
        final_state['investment_opportunities'] = result.get('investment_opportunities', [])
        final_state['portfolio_recommendation'] = result.get('portfolio_recommendation', {})
        
        # 6. ReportGeneratorAgent
        print("\n[현재 노드: report_generation_node]")
        print("="*60)
        result = report_agent.generate_report(final_state)
        final_state['final_report'] = result.get('final_report', {})
        final_state['glossary'] = result.get('glossary', {})
        final_state['investor_guide'] = result.get('investor_guide', {})
        
        # ==========================================
        # 6.  
        # ==========================================
        
        print("\n" + "="*70)
        print("[ ]")
        print("="*70)
        
        print(f"\n[ ]")
        for msg in final_state['messages']:
            print(f"   {msg}")
        
        if final_state['errors']:
            print(f"\n[ : {len(final_state['errors'])}]")
            for i, error in enumerate(final_state['errors'], 1):
                print(f"   {i}. {error['agent']}: {error['error'][:100]}...")
        
        print(f"\n[ ]")
        print(f"   -  : {len(final_state['news_articles'])}")
        print(f"   - : {len(final_state['keywords'])}")
        print(f"   - : {len(final_state['suppliers'])}")
        print(f"   -  : {len(final_state['source_manager'].citations)}")
        
        #   
        if final_state['source_manager'].citations:
            confidence_summary = final_state['source_manager'].get_citations_summary()
            print(f"   -  : {confidence_summary['average_confidence']:.2f}")
            print(f"   -  : {confidence_summary['average_reliability']:.2f}")
        
        # ==========================================
        # 7.  
        # ==========================================
        
        if final_state['final_report']:
            print("\n[  ...]")
            
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # JSON 
            json_path = f"{output_dir}/report_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_state['final_report'], f, 
                         ensure_ascii=False, indent=2)
            print(f"   [OK] JSON: {json_path}")
            
            # Markdown
            md_path = f"{output_dir}/report_{timestamp}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                for section_name, section_content in final_state['final_report'].items():
                    # section_content에 이미 제목이 있는지 확인
                    if not section_content.strip().startswith('#'):
                        f.write(f"# {section_name}\n\n")
                    f.write(section_content)
                    f.write("\n\n---\n\n")
            print(f"   [OK] Markdown: {md_path}")

            # HTML과 PDF 변환
            try:
                print("   HTML/PDF 변환 중...")
                converter = ReportConverter()
                converter.convert_markdown_file(md_path, generate_pdf=True)
            except Exception as e:
                print(f"   [WARNING] HTML/PDF 변환 실패: {e}")

            print("\n[보고서 생성 완료!]")
            print(f"    저장 위치: {output_dir}/")
        
        else:
            print("\n[  ]")
            print("     .")
        
    except Exception as e:
        print(f"\n[  : {e}]")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()