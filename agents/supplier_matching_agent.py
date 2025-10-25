"""
Supplier Matching Agent -       
     OEM  
"""

from typing import Dict, Any, List
from config.settings import config, SUPPLIER_RELATIONSHIP_MAPPING
from datetime import datetime
import re
from tools.supplier_scoring_tools import SupplierScorer  # 🆕 공급망 스코어링 도구


class SupplierMatchingAgent:
    """     """
    
    def __init__(self, web_search_tool, llm_tool):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        self.supplier_scorer = SupplierScorer()  # 🆕 공급망 스코어링

    def match_suppliers(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """     """
        try:
            print("    ...")
            
            categorized_keywords = state.get('categorized_keywords', {})
            
            # 1.     
            discovered_suppliers = self._discover_suppliers_via_web_search(
                categorized_keywords, state
            )
            
            # 2.   
            all_suppliers = self._merge_with_database(discovered_suppliers)
            
            # 3.    
            relationship_analysis = self._analyze_supplier_relationships(
                all_suppliers, state
            )
            
            # 4.  
            structured_result = self._structure_supplier_result(
                relationship_analysis, state
            )
            
            print(f"[OK]    -  {len(structured_result)}  ")
            
            # 신규 발견 기업 수 계산 (웹 검색으로 발견된 기업)
            new_discoveries = len([s for s in structured_result if s.get('discovery_source') == 'web_search'])
            
            return {
                'suppliers': structured_result,
                'discovery_summary': {
                    'total_suppliers': len(structured_result),
                    'new_discoveries': new_discoveries,
                    'existing_suppliers': len(structured_result) - new_discoveries,
                    'high_confidence': len([s for s in structured_result if s.get('overall_confidence', 0) > 0.7]),
                    'medium_confidence': len([s for s in structured_result if 0.4 <= s.get('overall_confidence', 0) <= 0.7]),
                    'low_confidence': len([s for s in structured_result if s.get('overall_confidence', 0) < 0.4])
                }
            }
            
        except Exception as e:
            print(f"[FAIL]   : {e}")
            return {
                'suppliers': [],
                'discovery_summary': {
                    'total_suppliers': 0,
                    'high_confidence': 0,
                    'medium_confidence': 0,
                    'low_confidence': 0
                }
            }

    def _discover_suppliers_via_web_search(self, categorized_keywords: Dict[str, List[str]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """    """
        discovered_suppliers = []
        
        # 키워드 필터링 함수
        def is_valid_search_keyword(keyword: str) -> bool:
            """검색에 사용할 수 있는 유효한 키워드인지 검사"""
            if not keyword or not keyword.strip():
                return False
            if keyword.strip() in ['-', '_', '/', '\\', '|', '.', ',', '&']:
                return False
            if len(keyword.strip()) < 2:
                return False
            if keyword.strip().isdigit():
                return False
            # 특수문자만으로 이루어진 경우
            if not any(c.isalnum() for c in keyword):
                return False
            return True
        
        # 키워드 필터링 적용
        filtered_keywords = {}
        for category, keywords in categorized_keywords.items():
            valid_keywords = [k for k in keywords if is_valid_search_keyword(k)]
            if valid_keywords:
                filtered_keywords[category] = valid_keywords
        
        print(f"     : {categorized_keywords}")
        print(f"        : {filtered_keywords}")
        
        #      ()
        if not filtered_keywords or all(not keywords for keywords in filtered_keywords.values()):
            print("   [WARNING]      ")
            print("   [INFO]        ")
            return discovered_suppliers
        
        categorized_keywords = filtered_keywords
        
        for category, keywords in categorized_keywords.items():
            if not keywords:
                continue
                
            print(f"     '{category}'  ...")
            
            for keyword in keywords:
                print(f"     '{keyword}'  ...")
                
                #    
                suppliers = self._find_suppliers_by_keyword(keyword, category, state)
                
                if suppliers:
                    print(f"   [OK]  '{keyword}' {len(suppliers)}  ")
                    discovered_suppliers.extend(suppliers)
                else:
                    print(f"   [OK]  '{keyword}' 0  ")
        
        #   (    )
        unique_suppliers = []
        seen_names = set()

        for supplier in discovered_suppliers:
            name = supplier.get('name', '').strip()
            # , ,  1
            if name and len(name) > 1 and not name.startswith('_') and name not in seen_names:
                unique_suppliers.append(supplier)
                seen_names.add(name)

        print(f"     {len(discovered_suppliers)}   ( )")
        print(f"       {len(unique_suppliers)} ")

        return unique_suppliers

    def _search_suppliers_web(self, keyword: str, category: str) -> List[Dict[str, Any]]:
        """웹 검색으로 공급업체 발견"""
        suppliers = []
        
        # API 한도 최적화: 1개 쿼리만 사용
        search_queries = [
            f"{keyword} supplier EV electric vehicle"
        ]
        
        for query in search_queries:
            try:
                print(f"      '{query}' 검색 중...")
                results = self.web_search_tool.search(query, num_results=1)  # API 한도 최적화: 1개로 축소
                
                for result in results:
                    title = result.get('title', '').lower()
                    content = result.get('content', '').lower()
                    
                    # 회사명 추출 (OEM/공급업체 분류 포함)
                    company_infos = self._extract_company_names(title, content)
                    
                    for company_info in company_infos:
                        if isinstance(company_info, dict):
                            company_name = company_info['name']
                            company_type = company_info['type']
                            
                            if company_name and len(company_name) > 2:
                                # OEM은 공급업체 목록에서 제외
                                if company_type == 'oem':
                                    print(f"   [FILTER] {company_name}는 OEM이므로 공급업체 목록에서 제외")
                                    continue
                                
                                supplier = {
                                    'name': company_name,
                                    'category': category,
                                    'company_type': company_type,
                                    'confidence': 0.6,  # 웹 검색은 중간 신뢰도
                                    'source': 'web_search',
                                    'query': query,
                                    'url': result.get('url', '')
                                }
                                suppliers.append(supplier)
                        else:
                            # 기존 문자열 형태인 경우 (호환성)
                            company_name = company_info
                            if company_name and len(company_name) > 2:
                                supplier = {
                                    'name': company_name,
                                    'category': category,
                                    'company_type': 'supplier',
                                    'confidence': 0.6,
                                    'source': 'web_search',
                                    'query': query,
                                    'url': result.get('url', '')
                                }
                                suppliers.append(supplier)
                
                print(f"    [OK] '{query}'에서 {len(results)}개 결과 처리")
                
            except Exception as e:
                print(f"    [WARNING] '{query}' 검색 실패: {e}")
                continue
        
        return suppliers

    def _extract_company_names(self, title: str, content: str) -> List[str]:
        """제목과 내용에서 회사명 추출"""
        company_names = []
        text = f"{title} {content}".lower()
        
        # 알려진 EV OEM (완성체 제조사) 리스트
        known_oems = [
            'tesla', 'byd', 'bmw', 'mercedes', 'mercedes-benz', 'volkswagen', 'audi', 'ford', 'gm', 
            'hyundai', 'kia', 'nio', 'rivian', 'lucid', 'xpeng', 'li auto', 'geely', 'great wall', 
            'dongfeng', 'changan', 'porsche', 'jaguar', 'land rover', 'volvo', 'polestar'
        ]
        
        # 알려진 EV 공급업체 리스트
        known_suppliers = [
            'lg', 'samsung', 'sdi', 'sk', 'catl', 'panasonic', 'bosch', 'continental', 'magna',
            'hyundai mobis', 'mando', 'ls cable', 'hyosung', 'posco', 'lg chem', 'lg energy solution',
            'samsung sdi', 'sk innovation', 'sk on', 'lg electronics', 'magna international',
            'continental ag', 'bosch', 'denso', 'valeo', 'aptiv', 'zffriedrichshafen'
        ]
        
        # 모든 알려진 회사명 (OEM + 공급업체)
        known_companies = known_oems + known_suppliers
        
        for company in known_companies:
            if company in text:
                # 적절한 형태로 변환
                if ' ' in company:
                    # 공백이 있는 경우 (예: "hyundai mobis" -> "Hyundai Mobis")
                    formatted_name = ' '.join(word.capitalize() for word in company.split())
                else:
                    # 단일 단어인 경우 (예: "tesla" -> "Tesla")
                    formatted_name = company.capitalize()
                
                # OEM vs 공급업체 분류
                company_type = 'oem' if company in known_oems else 'supplier'
                company_names.append({
                    'name': formatted_name,
                    'type': company_type,
                    'original': company
                })
        
        # 일반적인 회사명 패턴 (대문자 + 공백) - 더 엄격한 필터링
        import re
        # 2-4단어로 구성된 회사명만 추출 (단일 단어 제외)
        patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', text)
        
        # 의미있는 회사명만 필터링
        meaningful_patterns = []
        for pattern in patterns:
            # 너무 일반적인 단어들 제외
            if not any(word.lower() in ['the', 'and', 'or', 'for', 'with', 'from', 'this', 'that', 'news', 'report', 'article'] 
                      for word in pattern.split()):
                if len(pattern) > 5:  # 최소 길이 체크
                    # 일반 패턴은 기본적으로 공급업체로 분류 (OEM은 이미 위에서 처리됨)
                    meaningful_patterns.append({
                        'name': pattern,
                        'type': 'supplier',
                        'original': pattern.lower()
                    })
        
        company_names.extend(meaningful_patterns[:3])  # 최대 3개만
        
        # 중복 제거 (이름 기준)
        unique_names = []
        seen = set()
        for company_info in company_names:
            if isinstance(company_info, dict):
                name = company_info['name']
                if name and name.strip() and name not in seen:
                    unique_names.append(company_info)
                    seen.add(name)
            else:
                # 기존 문자열 형태인 경우 (호환성)
                if company_info and company_info.strip() and company_info not in seen:
                    unique_names.append({
                        'name': company_info.strip(),
                        'type': 'supplier',
                        'original': company_info.lower()
                    })
                    seen.add(company_info)
        
        return unique_names

    def _find_suppliers_by_keyword(self, keyword: str, category: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """키워드로 공급업체 검색 - 웹 검색 + 데이터베이스"""
        suppliers = []
        
        # 1. 웹 검색으로 공급업체 발견
        web_suppliers = self._search_suppliers_web(keyword, category)
        if web_suppliers:
            suppliers.extend(web_suppliers)
        
        # 2. 데이터베이스에서 매칭
        ev_suppliers_db = {
            # 2  ()
            '': [
                {'name': 'LG', 'category': '', 'confidence': 0.9},
                {'name': 'SDI', 'category': '', 'confidence': 0.9},
                {'name': 'SK', 'category': '', 'confidence': 0.8},
                {'name': 'CATL', 'category': '', 'confidence': 0.9},
                {'name': 'BYD', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7}
            ],
            '': [
                {'name': 'LG', 'category': '', 'confidence': 0.9},
                {'name': 'SDI', 'category': '', 'confidence': 0.9},
                {'name': 'SK', 'category': '', 'confidence': 0.8}
            ],
            '': [
                {'name': 'LG', 'category': '', 'confidence': 0.9},
                {'name': 'SDI', 'category': '', 'confidence': 0.9},
                {'name': 'SK', 'category': '', 'confidence': 0.8}
            ],
            'BMS': [
                {'name': 'LG', 'category': 'BMS', 'confidence': 0.8},
                {'name': 'SDI', 'category': 'BMS', 'confidence': 0.8},
                {'name': '', 'category': 'BMS', 'confidence': 0.7}
            ],
            
            #   
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.9},
                {'name': '', 'category': '', 'confidence': 0.8}
            ],
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.9}
            ],
            
            #  
            '': [
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': 'LS', 'category': '', 'confidence': 0.6},
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': 'ABB', 'category': '', 'confidence': 0.8}
            ],
            '': [
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': 'LS', 'category': '', 'confidence': 0.6},
                {'name': '', 'category': '', 'confidence': 0.8}
            ],
            
            # 
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': 'LG', 'category': '', 'confidence': 0.6}
            ],
            '': [
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.6}
            ],
            '': [
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.6}
            ],
            
            #   
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.9},
                {'name': '', 'category': '', 'confidence': 0.8}
            ],
            'ADAS': [
                {'name': '', 'category': 'ADAS', 'confidence': 0.8},
                {'name': '', 'category': 'ADAS', 'confidence': 0.7},
                {'name': '', 'category': 'ADAS', 'confidence': 0.9}
            ],
            
            #  
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': '', 'category': '', 'confidence': 0.7}
            ],
            '': [
                {'name': '', 'category': '', 'confidence': 0.8},
                {'name': 'SK', 'category': '', 'confidence': 0.7},
                {'name': '', 'category': '', 'confidence': 0.8}
            ]
        }
        
        #   
        for db_keyword, supplier_list in ev_suppliers_db.items():
            if (keyword in db_keyword or 
                db_keyword in keyword or 
                keyword.lower() in db_keyword.lower()):
                
                for supplier in supplier_list:
                    #   
                    confidence = supplier['confidence']
                    if category == '_':
                        confidence *= 1.0
                    elif category == '_':
                        confidence *= 0.9
                    elif category == '_':
                        confidence *= 0.8
                    
                    suppliers.append({
                        'name': supplier['name'],
                        'category': supplier['category'],
                        'keyword': keyword,
                        'confidence': confidence,
                        'source': 'database'
                    })
        
        return suppliers

    def _merge_with_database(self, discovered_suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """데이터베이스와 병합 (실제 데이터만 사용)"""
        # 웹에서 발견된 공급업체만 사용 (가짜 데이터 제거)
        return discovered_suppliers

    def _analyze_supplier_relationships(self, suppliers: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ OEM   """
        analyzed_suppliers = []
        
        for supplier in suppliers:
            #   (    )
            relationship = self._determine_relationship(supplier)
            
            analyzed_supplier = {
                **supplier,
                'relationship': relationship,
                'overall_confidence': supplier.get('confidence', 0.5)
            }
            
            analyzed_suppliers.append(analyzed_supplier)
        
        return analyzed_suppliers

    def _determine_relationship(self, supplier: Dict[str, Any]) -> Dict[str, Any]:
        """ OEM   """
        #    (    )
        relationship_types = ['', '', '', '']
        
        return {
            'type': relationship_types[0],  # : 
            'confidence': 0.5,
            'description': f"{supplier.get('name', '')} "
        }

    def _structure_supplier_result(self, suppliers: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """공급업체 결과 구조화"""
        structured_suppliers = []
        
        print(f"   [DEBUG] 구조화할 공급업체 수: {len(suppliers)}")
        
        for i, supplier in enumerate(suppliers, 1):
            # 기본 정보 추출
            raw_name = supplier.get('name', '')
            company_type = supplier.get('company_type', 'supplier')
            print(f"   [DEBUG] 공급업체 {i}: raw_name='{raw_name}', type='{company_type}' (길이: {len(raw_name)})")
            
            # 빈 문자열이나 None 처리
            if not raw_name or not raw_name.strip():
                name = f'Supplier_{i}'
                print(f"   [WARNING] 공급업체 {i} 이름이 비어있음, '{name}'으로 대체")
            else:
                name = raw_name.strip()
            
            category = supplier.get('category', 'Unknown')
            products = supplier.get('products', [])
            confidence = supplier.get('confidence', 0.5)
            source = supplier.get('source', 'Database')
            
            # OEM vs 공급업체에 따른 제품 정보 설정
            if company_type == 'oem':
                products = ['Electric Vehicles', 'EV Systems']
                category = 'oem'
            else:
                # 제품 정보가 비어있는 경우 기본값 설정
                if not products:
                    products = [f"{category} components", f"{category} systems"]
            
            # OEM 관계 정보
            oem_relationships = supplier.get('oem_relationships', [])
            if not oem_relationships:
                oem_relationships = []
            
            # 발견 소스 결정
            if company_type == 'oem':
                discovery_source = 'Web Search (OEM Discovery)'
            else:
                discovery_source = 'Web Search (New Discovery)' if source == 'web_search' else 'Database'
            
            structured_supplier = {
                'name': name,
                'category': category,
                'products': products,
                'oem_relationships': 1 if company_type == 'oem' else len(oem_relationships),
                'confidence_score': confidence,
                'discovery_source': discovery_source,
                'supplier_id': f"SUP_{i:03d}",
                'analysis_date': datetime.now().isoformat(),
                'company_type': company_type
            }
            
            structured_suppliers.append(structured_supplier)
            print(f"   [OK] 공급업체 {i} 구조화 완료: {name} ({company_type})")
        
        return structured_suppliers