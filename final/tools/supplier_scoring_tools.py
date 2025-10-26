"""
Supplier Scoring Tools with Two-Tier System

Fixes:
1. Two-tier buckets: Discovery (0.4-0.69) / Verified (≥0.7)
2. Evidence extraction with repair
3. Multi-source bonus
4. Recency bonus
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re


class SupplierScorer:
    """
    Supplier relationship scorer with two-tier confidence system
    """
    
    # Confidence thresholds
    VERIFIED_THRESHOLD = 0.70  # High confidence
    DISCOVERY_THRESHOLD = 0.40  # Medium confidence
    
    # Source weights
    SOURCE_WEIGHTS = {
        'official_announcement': 1.0,
        'company_report': 0.9,
        'news_article': 0.7,
        'industry_report': 0.8,
        'analyst_report': 0.85,
        'social_media': 0.4,
        'unknown': 0.3
    }
    
    def __init__(self):
        self.recency_window_days = 365  # 1 year
    
    def calculate_recency_bonus(self, date_str: str) -> float:
        """
        Calculate recency bonus (0.0 - 0.2)
        
        Args:
            date_str: Date string (YYYY-MM-DD or similar)
            
        Returns:
            Bonus score (0.0 to 0.2)
        """
        try:
            # Parse date
            if not date_str:
                return 0.0
            
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S']:
                try:
                    date = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            else:
                return 0.0
            
            # Calculate days ago
            days_ago = (datetime.now() - date).days
            
            # Linear decay
            if days_ago < 0:
                return 0.2  # Future date (should not happen)
            elif days_ago <= 30:
                return 0.2  # Within 1 month = max bonus
            elif days_ago <= 90:
                return 0.15  # Within 3 months
            elif days_ago <= 180:
                return 0.1  # Within 6 months
            elif days_ago <= 365:
                return 0.05  # Within 1 year
            else:
                return 0.0  # Older than 1 year
                
        except Exception as e:
            print(f"   [SCORE] ⚠ Date parsing failed: {e}")
            return 0.0
    
    def calculate_multi_source_bonus(self, evidence_count: int) -> float:
        """
        Calculate multi-source bonus (0.0 - 0.15)
        
        Args:
            evidence_count: Number of evidence sources
            
        Returns:
            Bonus score
        """
        if evidence_count >= 5:
            return 0.15
        elif evidence_count >= 3:
            return 0.10
        elif evidence_count >= 2:
            return 0.05
        else:
            return 0.0
    
    def extract_evidence_from_text(
        self,
        text: str,
        supplier_name: str,
        oem_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extract evidence mentions from text
        
        Args:
            text: Text to extract from
            supplier_name: Supplier company name
            oem_name: OEM company name
            
        Returns:
            List of evidence dicts
        """
        evidence = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            # Check if both companies mentioned
            if (supplier_name.lower() in sentence.lower() and 
                oem_name.lower() in sentence.lower()):
                
                # Extract date if present
                date_match = re.search(r'\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b', sentence)
                date_str = date_match.group(1) if date_match else None
                
                # Determine source type from keywords
                source_type = 'news_article'  # Default
                if any(word in sentence.lower() for word in ['announced', 'official', 'press release']):
                    source_type = 'official_announcement'
                elif any(word in sentence.lower() for word in ['report', 'filing', '10-K', '10-Q']):
                    source_type = 'company_report'
                elif any(word in sentence.lower() for word in ['analyst', 'rating', 'recommendation']):
                    source_type = 'analyst_report'
                
                evidence.append({
                    'text': sentence.strip(),
                    'date': date_str,
                    'source_type': source_type,
                    'url': None  # To be filled by caller
                })
        
        return evidence
    
    def score_relationship(
        self,
        supplier_name: str,
        oem_name: str,
        relationship_type: str,
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Score supplier-OEM relationship
        
        Args:
            supplier_name: Supplier company name
            oem_name: OEM company name
            relationship_type: Type (e.g., 'battery_supplier', 'motor_supplier')
            evidence: List of evidence dicts with keys: source_type, date, text, url
            
        Returns:
            Scoring result with confidence, tier, and details
        """
        if not evidence:
            return {
                'confidence': 0.0,
                'tier': 'unverified',
                'base_score': 0.0,
                'recency_bonus': 0.0,
                'multi_source_bonus': 0.0,
                'total_score': 0.0,
                'evidence_count': 0,
                'reason': 'No evidence provided'
            }
        
        # Calculate base score from source types
        base_score = 0.0
        for ev in evidence:
            source_type = ev.get('source_type', 'unknown')
            weight = self.SOURCE_WEIGHTS.get(source_type, 0.3)
            base_score += weight
        
        # Average base score (normalize to 0-1)
        base_score = min(base_score / len(evidence), 1.0)
        
        # Calculate recency bonus (use most recent evidence)
        recency_bonus = 0.0
        for ev in evidence:
            date_str = ev.get('date')
            if date_str:
                bonus = self.calculate_recency_bonus(date_str)
                recency_bonus = max(recency_bonus, bonus)
        
        # Calculate multi-source bonus
        multi_source_bonus = self.calculate_multi_source_bonus(len(evidence))
        
        # Total confidence
        confidence = base_score + recency_bonus + multi_source_bonus
        confidence = min(confidence, 1.0)  # Cap at 1.0
        
        # Determine tier
        if confidence >= self.VERIFIED_THRESHOLD:
            tier = 'verified'
        elif confidence >= self.DISCOVERY_THRESHOLD:
            tier = 'discovery'
        else:
            tier = 'unverified'
        
        return {
            'supplier_name': supplier_name,
            'oem_name': oem_name,
            'relationship_type': relationship_type,
            'confidence': round(confidence, 2),
            'tier': tier,
            'base_score': round(base_score, 2),
            'recency_bonus': round(recency_bonus, 2),
            'multi_source_bonus': round(multi_source_bonus, 2),
            'total_score': round(confidence, 2),
            'evidence_count': len(evidence),
            'evidence': evidence,
            'reason': f"{tier.capitalize()} based on {len(evidence)} source(s)"
        }
    
    def filter_by_tier(
        self,
        relationships: List[Dict[str, Any]],
        min_tier: str = 'discovery'
    ) -> List[Dict[str, Any]]:
        """
        Filter relationships by minimum tier
        
        Args:
            relationships: List of relationship dicts with 'tier' field
            min_tier: Minimum tier ('verified', 'discovery', or 'unverified')
            
        Returns:
            Filtered relationships
        """
        tier_order = {'verified': 3, 'discovery': 2, 'unverified': 1}
        min_level = tier_order.get(min_tier, 1)
        
        filtered = []
        for rel in relationships:
            tier = rel.get('tier', 'unverified')
            if tier_order.get(tier, 0) >= min_level:
                filtered.append(rel)
        
        return filtered
    
    def generate_summary(
        self,
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics
        
        Args:
            relationships: List of scored relationships
            
        Returns:
            Summary dict
        """
        verified = [r for r in relationships if r.get('tier') == 'verified']
        discovery = [r for r in relationships if r.get('tier') == 'discovery']
        unverified = [r for r in relationships if r.get('tier') == 'unverified']
        
        return {
            'total': len(relationships),
            'verified': len(verified),
            'discovery': len(discovery),
            'unverified': len(unverified),
            'avg_confidence': round(sum(r.get('confidence', 0) for r in relationships) / len(relationships), 2) if relationships else 0.0,
            'verified_relationships': verified,
            'discovery_relationships': discovery
        }


def test_supplier_scorer():
    """Test the supplier scorer"""
    
    print("="*70)
    print("Supplier Scorer Test")
    print("="*70)
    
    scorer = SupplierScorer()
    
    # Test 1: Single high-quality evidence
    print("\n[Test 1] Official Announcement (Recent)")
    evidence1 = [{
        'source_type': 'official_announcement',
        'date': '2024-10-01',
        'text': 'LG Energy Solution signed battery supply agreement with Tesla',
        'url': 'https://example.com/news1'
    }]
    
    result1 = scorer.score_relationship(
        supplier_name='LG Energy Solution',
        oem_name='Tesla',
        relationship_type='battery_supplier',
        evidence=evidence1
    )
    
    print(f"  Confidence: {result1['confidence']}")
    print(f"  Tier: {result1['tier']}")
    print(f"  Base: {result1['base_score']}, Recency: {result1['recency_bonus']}, Multi: {result1['multi_source_bonus']}")
    
    # Test 2: Multiple sources
    print("\n[Test 2] Multiple Sources")
    evidence2 = [
        {
            'source_type': 'official_announcement',
            'date': '2024-09-15',
            'text': 'Samsung SDI partners with BMW for battery supply',
            'url': 'https://example.com/news2'
        },
        {
            'source_type': 'company_report',
            'date': '2024-09-20',
            'text': 'BMW mentions Samsung SDI as key battery supplier in Q3 report',
            'url': 'https://example.com/report'
        },
        {
            'source_type': 'news_article',
            'date': '2024-10-01',
            'text': 'Industry sources confirm Samsung SDI-BMW battery deal',
            'url': 'https://example.com/news3'
        }
    ]
    
    result2 = scorer.score_relationship(
        supplier_name='Samsung SDI',
        oem_name='BMW',
        relationship_type='battery_supplier',
        evidence=evidence2
    )
    
    print(f"  Confidence: {result2['confidence']}")
    print(f"  Tier: {result2['tier']}")
    print(f"  Evidence count: {result2['evidence_count']}")
    print(f"  Multi-source bonus: {result2['multi_source_bonus']}")
    
    # Test 3: Weak evidence
    print("\n[Test 3] Weak Evidence")
    evidence3 = [{
        'source_type': 'social_media',
        'date': '2023-01-15',  # Old
        'text': 'Rumor about BYD supplying batteries to Ford',
        'url': 'https://twitter.com/example'
    }]
    
    result3 = scorer.score_relationship(
        supplier_name='BYD',
        oem_name='Ford',
        relationship_type='battery_supplier',
        evidence=evidence3
    )
    
    print(f"  Confidence: {result3['confidence']}")
    print(f"  Tier: {result3['tier']}")
    print(f"  Reason: {result3['reason']}")
    
    # Test 4: Summary
    print("\n[Test 4] Summary Statistics")
    all_relationships = [result1, result2, result3]
    summary = scorer.generate_summary(all_relationships)
    
    print(f"  Total: {summary['total']}")
    print(f"  Verified: {summary['verified']}")
    print(f"  Discovery: {summary['discovery']}")
    print(f"  Unverified: {summary['unverified']}")
    print(f"  Avg Confidence: {summary['avg_confidence']}")
    
    # Test 5: Filtering
    print("\n[Test 5] Filter by Tier")
    verified_only = scorer.filter_by_tier(all_relationships, min_tier='verified')
    print(f"  Verified only: {len(verified_only)} relationships")
    
    discovery_plus = scorer.filter_by_tier(all_relationships, min_tier='discovery')
    print(f"  Discovery+: {len(discovery_plus)} relationships")
    
    print("\n" + "="*70)
    print("✓ All tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_supplier_scorer()

