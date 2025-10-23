"""
Supplier Matching Agent -       
     OEM  
"""

from typing import Dict, Any, List
from config.settings import config, SUPPLIER_RELATIONSHIP_MAPPING
from datetime import datetime
import re


class SupplierMatchingAgent:
    """     """
    
    def __init__(self, web_search_tool, llm_tool):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool

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
            
            return {
                'suppliers': structured_result,
                'discovery_summary': {
                    'total_suppliers': len(structured_result),
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
        
        print(f"     : {categorized_keywords}")
        
        #      ()
        if not categorized_keywords or all(not keywords for keywords in categorized_keywords.values()):
            print("   [WARNING]      ")
            categorized_keywords = {
                '_': ['', '', ''],
                '_': ['', '', 'BMS'],
                '_': ['', '', '']
            }
            print(f"      : {categorized_keywords}")
        
        print(f"        : {categorized_keywords}")
        
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
                    
                    # 회사명 추출 (간단한 패턴 매칭)
                    company_names = self._extract_company_names(title, content)
                    
                    for company_name in company_names:
                        if company_name and len(company_name) > 2:
                            supplier = {
                                'name': company_name,
                                'category': category,
                                'confidence': 0.6,  # 웹 검색은 중간 신뢰도
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
        text = f"{title} {content}"
        
        # 알려진 EV 관련 회사명 패턴
        known_companies = [
            'tesla', 'byd', 'bmw', 'mercedes', 'volkswagen', 'audi', 'ford', 'gm', 'hyundai', 'kia',
            'lg', 'samsung', 'sdi', 'sk', 'catl', 'panasonic', 'bosch', 'continental', 'magna',
            'hyundai mobis', 'mando', 'ls cable', 'hyosung', 'posco', 'lg chem'
        ]
        
        for company in known_companies:
            if company in text:
                company_names.append(company.upper())
        
        # 일반적인 회사명 패턴 (대문자 + 공백)
        import re
        patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        company_names.extend(patterns[:5])  # 최대 5개만
        
        return list(set(company_names))  # 중복 제거

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
        
        for i, supplier in enumerate(suppliers, 1):
            # 기본 정보 추출
            name = supplier.get('name', f'Supplier_{i}')
            category = supplier.get('category', 'Unknown')
            products = supplier.get('products', [])
            confidence = supplier.get('confidence', 0.5)
            source = supplier.get('source', 'Database')
            
            # 제품 정보가 비어있는 경우 기본값 설정
            if not products:
                products = [f"{category} components", f"{category} systems"]
            
            # OEM 관계 정보
            oem_relationships = supplier.get('oem_relationships', [])
            if not oem_relationships:
                oem_relationships = []
            
            structured_supplier = {
                'name': name,
                'category': category,
                'products': products,
                'oem_relationships': oem_relationships,
                'confidence_score': confidence,
                'discovery_source': source,
                'supplier_id': f"SUP_{i:03d}",
                'analysis_date': datetime.now().isoformat()
            }
            
            structured_suppliers.append(structured_supplier)
        
        return structured_suppliers