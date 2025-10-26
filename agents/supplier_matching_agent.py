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
        
        # 중복 제거 (기업명 정규화 후 비교)
        unique_suppliers = []
        seen_normalized_names = set()
        
        def normalize_company_name(name: str) -> str:
            """기업명 정규화 (중복 제거용)"""
            if not name:
                return ""
            
            # 소문자 변환
            normalized = name.lower().strip()
            
            # 공통 접미사 제거
            suffixes = [' international', ' inc', ' inc.', ' corp', ' corp.', ' ltd', ' ltd.', 
                       ' co', ' co.', ' company', ' group', ' holdings', ' ag']
            for suffix in suffixes:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)].strip()
            
            # 공백, 하이픈, 점 제거
            normalized = normalized.replace(' ', '').replace('-', '').replace('.', '')
            
            return normalized

        for supplier in discovered_suppliers:
            name = supplier.get('name', '').strip()
            
            # 빈 이름이나 너무 짧은 이름 제외
            if not name or len(name) <= 1 or name.startswith('_'):
                continue
            
            # 정규화된 이름으로 중복 체크
            normalized_name = normalize_company_name(name)
            
            if normalized_name and normalized_name not in seen_normalized_names:
                unique_suppliers.append(supplier)
                seen_normalized_names.add(normalized_name)
                print(f"   [OK] 공급업체 추가: {name} (정규화: {normalized_name})")
            else:
                print(f"   [SKIP] 중복 제거: {name} (정규화: {normalized_name})")

        print(f"     {len(discovered_suppliers)}개 발견 (중복 포함)")
        print(f"       {len(unique_suppliers)}개 (중복 제거 후)")

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
                                # OEM과 공급업체 모두 포함 (type 필드로 구분)
                                supplier = {
                                    'name': company_name,
                                    'category': category,
                                    'type': company_type,  # 'oem' 또는 'supplier'
                                    'confidence': 0.6,  # 웹 검색은 중간 신뢰도
                                    'source': 'web_search',
                                    'query': query,
                                    'url': result.get('url', '')
                                }
                                suppliers.append(supplier)
                                print(f"   [OK] {company_name} 추가 (type: {company_type})")
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
        """키워드로 공급업체 검색 - 웹 검색만 사용 (하드코딩 DB 제거)"""
        suppliers = []
        
        # 웹 검색으로만 공급업체 발견 (가짜 데이터 생성 방지)
        web_suppliers = self._search_suppliers_web(keyword, category)
        if web_suppliers:
            suppliers.extend(web_suppliers)
            print(f"   [OK] '{keyword}' 웹 검색: {len(web_suppliers)}개 공급업체 발견")
        else:
            print(f"   [INFO] '{keyword}' 웹 검색: 공급업체 없음")
        
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
            
            # 동적 신뢰도 계산
            dynamic_confidence = self._calculate_dynamic_confidence(supplier, relationship)
            
            analyzed_supplier = {
                **supplier,
                'relationship': relationship,
                'overall_confidence': dynamic_confidence
            }
            
            analyzed_suppliers.append(analyzed_supplier)
        
        return analyzed_suppliers

    def _generate_products_from_category(self, company_name: str, category: str) -> List[str]:
        """
        회사명과 카테고리 기반으로 의미있는 제품 정보 생성
        
        Args:
            company_name: 회사명
            category: 카테고리
            
        Returns:
            제품 리스트
        """
        # 회사명 기반 제품 매핑
        company_lower = company_name.lower()
        
        if 'lg' in company_lower or 'samsung' in company_lower or 'sk' in company_lower:
            if 'energy' in company_lower or 'sdi' in company_lower:
                return ['Lithium-ion Batteries', 'Battery Cells', 'Energy Storage Systems']
            elif 'chem' in company_lower:
                return ['Battery Materials', 'Cathode Materials', 'Electrolytes']
            else:
                return ['EV Components', 'Battery Systems', 'Power Electronics']
        
        elif 'catl' in company_lower or 'panasonic' in company_lower:
            return ['Lithium-ion Batteries', 'Battery Packs', 'Energy Storage']
        
        elif 'bosch' in company_lower or 'continental' in company_lower or 'denso' in company_lower:
            return ['Powertrain Systems', 'Electric Motors', 'Power Electronics']
        
        elif 'magna' in company_lower:
            return ['EV Platforms', 'Body Systems', 'Powertrain Components']
        
        # 카테고리 기반 제품 매핑
        category_lower = category.lower()
        
        if 'battery' in category_lower:
            return ['Battery Cells', 'Battery Packs', 'BMS']
        elif 'motor' in category_lower or 'powertrain' in category_lower:
            return ['Electric Motors', 'Inverters', 'Gearboxes']
        elif 'semiconductor' in category_lower or 'chip' in category_lower:
            return ['Power Semiconductors', 'MCU', 'Sensors']
        elif 'material' in category_lower:
            return ['Battery Materials', 'Cathode/Anode Materials', 'Separators']
        elif 'charging' in category_lower:
            return ['Charging Stations', 'DC Fast Chargers', 'Charging Cables']
        else:
            # 기본값: 카테고리 이름 활용
            return [f'{category} Components', f'{category} Systems']
    
    def _calculate_dynamic_confidence(self, supplier: Dict[str, Any], relationship: Dict[str, Any]) -> float:
        """
        동적 신뢰도 계산 - 출처 수, 관계 신뢰도, 카테고리 기반
        
        Args:
            supplier: 공급업체 정보
            relationship: OEM 관계 정보
            
        Returns:
            신뢰도 점수 (0.0-1.0)
        """
        base_confidence = supplier.get('confidence', 0.5)
        
        # 1. 관계 신뢰도 보너스 (0.0-0.2)
        relationship_confidence = relationship.get('confidence', 0.0)
        relationship_bonus = relationship_confidence * 0.2
        
        # 2. 출처 다양성 보너스 (0.0-0.15)
        all_relationships = relationship.get('all_relationships', [])
        source_diversity = min(len(all_relationships) / 3.0, 1.0) * 0.15
        
        # 3. 카테고리 명확성 보너스 (0.0-0.1)
        category = supplier.get('category', '')
        category_bonus = 0.1 if category and category not in ['Unknown', 'unknown', ''] else 0.0
        
        # 4. 제품 정보 보너스 (0.0-0.05)
        products = supplier.get('products', [])
        product_bonus = 0.05 if products and len(products) > 0 else 0.0
        
        # 총 신뢰도 계산 (최대 1.0)
        total_confidence = base_confidence + relationship_bonus + source_diversity + category_bonus + product_bonus
        
        return round(min(total_confidence, 1.0), 2)
    
    def _determine_relationship(self, supplier: Dict[str, Any]) -> Dict[str, Any]:
        """웹 검색으로 OEM과의 관계 추론"""
        supplier_name = supplier.get('name', '')
        
        # 웹 검색으로 OEM 관계 찾기
        try:
            # 주요 EV OEM 리스트
            major_oems = ['Tesla', 'BYD', 'BMW', 'Mercedes', 'Volkswagen', 'Ford', 'GM', 
                         'Hyundai', 'Kia', 'Nio', 'Rivian', 'Lucid']
            
            relationships = []
            
            # 각 OEM과의 관계 검색 (API 한도 고려하여 상위 3개만)
            for oem in major_oems[:3]:
                query = f"{supplier_name} supplier {oem} partnership"
                try:
                    results = self.web_search_tool.search(query, num_results=1)
                    
                    if results:
                        content = results[0].get('content', '').lower()
                        title = results[0].get('title', '').lower()
                        text = f"{title} {content}"
                        
                        # 관계 유형 판단
                        if any(word in text for word in ['supply', 'supplier', 'partnership', 'contract', 'deal']):
                            rel_type = 'supply'
                            confidence = 0.8
                        elif any(word in text for word in ['cooperate', 'collaboration', 'joint']):
                            rel_type = 'cooperation'
                            confidence = 0.7
                        elif any(word in text for word in ['compete', 'rival', 'competition']):
                            rel_type = 'competition'
                            confidence = 0.6
                        else:
                            rel_type = 'unclear'
                            confidence = 0.3
                        
                        relationships.append({
                            'oem': oem,
                            'type': rel_type,
                            'confidence': confidence,
                            'source': results[0].get('url', '')
                        })
                        
                except Exception as e:
                    print(f"    [WARNING] {supplier_name}-{oem} 관계 검색 실패: {e}")
                    continue
            
            # 가장 신뢰도 높은 관계 반환
            if relationships:
                best_rel = max(relationships, key=lambda x: x['confidence'])
                return {
                    'type': best_rel['type'],
                    'confidence': best_rel['confidence'],
                    'description': f"{supplier_name}는 {best_rel['oem']}와 {best_rel['type']} 관계",
                    'all_relationships': relationships
                }
            else:
                return {
                    'type': 'unclear',
                    'confidence': 0.3,
                    'description': f"{supplier_name}의 OEM 관계 정보 부족",
                    'all_relationships': []
                }
                
        except Exception as e:
            print(f"    [ERROR] {supplier_name} 관계 분석 실패: {e}")
            return {
                'type': 'unclear',
                'confidence': 0.3,
                'description': f"{supplier_name}의 관계 분석 실패",
                'all_relationships': []
            }

    def _is_listed_company(self, company_name: str) -> tuple[bool, str]:
        """
        기업이 상장사인지 확인
        
        Returns:
            (is_listed, ticker_symbol)
        """
        # 알려진 상장사 티커 매핑
        LISTED_COMPANIES = {
            # 한국
            'LG에너지솔루션': '373220.KS', 'LG Energy Solution': '373220.KS',
            '삼성SDI': '006400.KS', 'Samsung SDI': '006400.KS',
            'SK이노베이션': '096770.KS', 'SK Innovation': '096770.KS',
            '현대자동차': '005380.KS', 'Hyundai': '005380.KS', 'Hyundai Motor': '005380.KS',
            '기아': '000270.KS', 'Kia': '000270.KS',
            '에코프로비엠': '247540.KQ', 'Ecopro': '247540.KQ',
            '포스코퓨처엠': '003670.KS', 'Posco': '003670.KS',
            'LG화학': '051910.KS', 'LG Chem': '051910.KS',
            'LG전자': '066570.KS', 'LG Electronics': '066570.KS',
            
            # 미국
            'Tesla': 'TSLA', '테슬라': 'TSLA',
            'Ford': 'F', '포드': 'F',
            'GM': 'GM', 'General Motors': 'GM',
            'Rivian': 'RIVN', 'Lucid': 'LCID',
            'Albemarle': 'ALB',
            
            # 중국
            'BYD': '002594.SZ',
            'CATL': '300750.SZ',
            'Nio': 'NIO', 'Xpeng': 'XPEV', 'Li Auto': 'LI',
            
            # 유럽
            'BMW': 'BMW.DE',
            'Volkswagen': 'VOW.DE', 'VW': 'VOW.DE',
            'Mercedes': 'MBG.DE', 'Mercedes-Benz': 'MBG.DE',
            'Porsche': 'P911.DE',
            
            # 일본
            'Panasonic': '6752.T', '파나소닉': '6752.T',
            'Toyota': '7203.T', '도요타': '7203.T',
        }
        
        # 정확한 매칭
        if company_name in LISTED_COMPANIES:
            return True, LISTED_COMPANIES[company_name]
        
        # 부분 매칭 (예: "LG에너지솔루션 주식회사" → "LG에너지솔루션")
        for listed_name, ticker in LISTED_COMPANIES.items():
            if listed_name.lower() in company_name.lower() or company_name.lower() in listed_name.lower():
                return True, ticker
        
        return False, ''
    
    def _structure_supplier_result(self, suppliers: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """공급업체 결과 구조화 (상장사 우선 필터링)"""
        structured_suppliers = []
        
        print(f"   [DEBUG] 구조화할 공급업체 수: {len(suppliers)}")
        
        # 🆕 상장사 필터링 (투자 보고서이므로 투자 가능한 기업만)
        listed_suppliers = []
        unlisted_suppliers = []
        
        for supplier in suppliers:
            company_name = supplier.get('name', '')
            is_listed, ticker = self._is_listed_company(company_name)
            
            supplier['is_listed'] = is_listed
            supplier['ticker'] = ticker
            
            if is_listed:
                listed_suppliers.append(supplier)
            else:
                unlisted_suppliers.append(supplier)
        
        print(f"   [FILTER] 상장사: {len(listed_suppliers)}개 / 비상장사: {len(unlisted_suppliers)}개")
        print(f"   [STRATEGY] 투자 보고서 → 상장사 우선 분석")
        
        # 상장사를 먼저 처리 (투자 가능)
        priority_suppliers = listed_suppliers + unlisted_suppliers[:5]  # 비상장사는 최대 5개만
        
        for i, supplier in enumerate(priority_suppliers, 1):
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
            
            # 🆕 상장사 정보 추가
            is_listed = supplier.get('is_listed', False)
            ticker = supplier.get('ticker', '')
            
            # 🆕 상장사는 신뢰도 증가 (투자 가능성)
            if is_listed:
                confidence = min(confidence + 0.2, 1.0)
            
            # OEM vs 공급업체에 따른 제품 정보 설정
            if company_type == 'oem':
                products = ['Electric Vehicles', 'EV Systems']
                category = 'oem'
            else:
                # 제품 정보가 비어있는 경우 카테고리 기반 의미있는 제품 생성
                if not products:
                    products = self._generate_products_from_category(name, category)
            
            # OEM 관계 정보
            oem_relationships = supplier.get('oem_relationships', [])
            if not oem_relationships:
                oem_relationships = []
            
            # 발견 소스 결정
            if company_type == 'oem':
                discovery_source = 'Web Search (OEM Discovery)'
            else:
                discovery_source = 'Web Search (New Discovery)' if source == 'web_search' else 'Database'
            
            # 🆕 상장사 태그 추가
            investable_tag = '📈 투자가능' if is_listed else ''
            
            structured_supplier = {
                'name': name,
                'category': category,
                'products': products,
                'oem_relationships': 1 if company_type == 'oem' else len(oem_relationships),
                'confidence_score': confidence,
                'discovery_source': discovery_source,
                'supplier_id': f"SUP_{i:03d}",
                'analysis_date': datetime.now().isoformat(),
                'company_type': company_type,
                'is_listed': is_listed,  # 🆕 상장 여부
                'ticker': ticker,  # 🆕 티커 심볼
                'investable': is_listed,  # 🆕 투자 가능 여부
                'investable_tag': investable_tag  # 🆕 표시용 태그
            }
            
            structured_suppliers.append(structured_supplier)
            print(f"   [OK] 공급업체 {i} 구조화 완료: {name} ({company_type})")
        
        return structured_suppliers