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
        'days_ago': 30,  # 최근 30일 이내 뉴스만 수집 (더 많은 결과 확보)
        'max_news_articles': 10,  # 최대 10개 뉴스 기사로 제한
        'keywords': ['EV', 'electric vehicle', 'battery', 'charging'],  # 영어 키워드로 변경
        'target_audience': 'individual investors',  # 영어로 변경
        'language': 'en'  # 영어 보고서 생성
    }
    
    print("[설정 정보]")
    print(f"   - 보고서 월: {config['report_month']}")
    print(f"   - 뉴스 수집 기간: 최근 {config['days_ago']}일")
    print(f"   - 최대 뉴스 기사 수: {config['max_news_articles']}개")
    print(f"   - 키워드: {', '.join(config['keywords'])}")
    print(f"   - 대상 독자: {config['target_audience']}")
    print()
    
    # ==========================================
    # 2.  
    # ==========================================
    
    print("[  ...]")
    
    # Web Search ( web_search  )
    web_search = WebSearchTool()
    
    # OpenAI API
    openai_api_key = os.getenv('OPENAI_API_KEY', 'sk-proj-your-key-here')
    llm = OpenAILLM(openai_api_key)
    
    # DART API
    dart_api_key = os.getenv('DART_API_KEY', 'f9cc57c302b3717900443947647ca55800eb6e8a')
    dart = DARTTool(dart_api_key)
    
    print("   [OK] Web Search  ")
    print("   [OK] OpenAI API  ")
    if dart_api_key:
        print("   [OK] DART API  ")
    print()
    
    # ==========================================
    # 3.  State 
    # ==========================================
    
    initial_state = create_initial_state(config)
    
    # ==========================================
    # 4.  
    # ==========================================
    
    print("[  ...]")
    
    workflow = create_workflow(
        web_search_tool=web_search,
        llm_tool=llm,
        dart_tool=dart
    )
    
    print("   [OK] LangGraph   ")
    print()
    
    # ==========================================
    # 5. 
    # ==========================================
    
    print("[  !]")
    print("="*70)
    
    try:
        #  
        final_state = workflow.invoke(initial_state)
        
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