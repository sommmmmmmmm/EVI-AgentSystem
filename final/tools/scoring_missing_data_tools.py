"""
Scoring Tools with Missing Data Handling

Fixes:
1. Missing values → sector median (not 0)
2. Z-score guard (variance=0 → rank-based)
3. Confidence penalty for missing data
4. Top-N ranking (not strict threshold)
"""

from typing import Dict, Any, List, Optional
import statistics


class ScoringWithMissingData:
    """
    Scoring system that handles missing data gracefully
    """
    
    # Sector medians (example values - should be updated with real data)
    SECTOR_MEDIANS = {
        'Battery': {
            'roe': 0.12,
            'roa': 0.08,
            'operating_margin': 0.10,
            'debt_ratio': 0.35,
            'current_ratio': 1.5,
        },
        'OEM': {
            'roe': 0.15,
            'roa': 0.06,
            'operating_margin': 0.08,
            'debt_ratio': 0.45,
            'current_ratio': 1.2,
        },
        'Component': {
            'roe': 0.10,
            'roa': 0.07,
            'operating_margin': 0.12,
            'debt_ratio': 0.30,
            'current_ratio': 1.8,
        },
        'Unknown': {
            'roe': 0.12,
            'roa': 0.07,
            'operating_margin': 0.10,
            'debt_ratio': 0.40,
            'current_ratio': 1.5,
        }
    }
    
    def __init__(self):
        self.confidence_penalty_per_missing = 0.05  # 5% per missing field
    
    def fill_missing_values(
        self,
        data: Dict[str, Optional[float]],
        sector: str = 'Unknown'
    ) -> Dict[str, Any]:
        """
        Fill missing values with sector median
        
        Args:
            data: Dict with metrics (may have None values)
            sector: Sector name (Battery, OEM, Component, Unknown)
            
        Returns:
            Dict with filled values and metadata
        """
        sector_medians = self.SECTOR_MEDIANS.get(sector, self.SECTOR_MEDIANS['Unknown'])
        
        filled_data = {}
        missing_count = 0
        filled_fields = []
        
        for metric, value in data.items():
            if value is None or (isinstance(value, float) and (value == 0.0 or value != value)):  # None or 0 or NaN
                # Use sector median
                filled_value = sector_medians.get(metric, 0.0)
                filled_data[metric] = filled_value
                missing_count += 1
                filled_fields.append(metric)
            else:
                filled_data[metric] = value
        
        # Calculate confidence penalty
        total_fields = len(data)
        confidence_penalty = missing_count * self.confidence_penalty_per_missing
        confidence = max(0.0, 1.0 - confidence_penalty)
        
        return {
            'data': filled_data,
            'missing_count': missing_count,
            'filled_fields': filled_fields,
            'confidence': confidence,
            'confidence_level': self._get_confidence_level(confidence),
            'note': f"Filled {missing_count}/{total_fields} missing values with sector median"
        }
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level label"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def safe_normalize(
        self,
        values: List[float],
        method: str = 'z_score'
    ) -> List[float]:
        """
        Safe normalization with guards for edge cases
        
        Args:
            values: List of values to normalize
            method: 'z_score' or 'min_max' or 'rank'
            
        Returns:
            Normalized values
        """
        if not values or len(values) < 2:
            return values
        
        if method == 'z_score':
            # Check variance
            try:
                mean = statistics.mean(values)
                stdev = statistics.stdev(values)
                
                # Guard: If std dev is 0 or very small, use rank-based
                if stdev < 1e-6:
                    print(f"   [SCORE] ⚠ Z-score variance ~0, using rank-based normalization")
                    return self.safe_normalize(values, method='rank')
                
                # Z-score normalization
                normalized = [(v - mean) / stdev for v in values]
                return normalized
                
            except statistics.StatisticsError:
                # Fallback to rank
                print(f"   [SCORE] ⚠ Z-score failed, using rank-based normalization")
                return self.safe_normalize(values, method='rank')
        
        elif method == 'min_max':
            min_val = min(values)
            max_val = max(values)
            
            # Guard: If range is 0, return all 0.5
            if max_val - min_val < 1e-6:
                print(f"   [SCORE] ⚠ Min-max range ~0, returning neutral values")
                return [0.5] * len(values)
            
            # Min-max normalization
            normalized = [(v - min_val) / (max_val - min_val) for v in values]
            return normalized
        
        elif method == 'rank':
            # Rank-based normalization (1 to N)
            sorted_indices = sorted(range(len(values)), key=lambda i: values[i])
            ranks = [0.0] * len(values)
            for rank, idx in enumerate(sorted_indices):
                ranks[idx] = rank / (len(values) - 1)  # Normalize to 0-1
            return ranks
        
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def score_with_confidence(
        self,
        company_data: Dict[str, Any],
        sector: str = 'Unknown'
    ) -> Dict[str, Any]:
        """
        Score company with confidence tracking
        
        Args:
            company_data: Dict with financial metrics (may have None/missing values)
            sector: Company sector
            
        Returns:
            Score dict with confidence
        """
        # Extract financial metrics
        metrics = {
            'roe': company_data.get('roe'),
            'roa': company_data.get('roa'),
            'operating_margin': company_data.get('operating_margin'),
            'debt_ratio': company_data.get('debt_ratio'),
            'current_ratio': company_data.get('current_ratio'),
        }
        
        # Fill missing values
        filled_result = self.fill_missing_values(metrics, sector=sector)
        filled_metrics = filled_result['data']
        
        # Calculate score (weighted average)
        weights = {
            'roe': 0.25,
            'roa': 0.20,
            'operating_margin': 0.25,
            'debt_ratio': 0.15,  # Lower is better, so will invert
            'current_ratio': 0.15,
        }
        
        # Normalize each metric to 0-100 scale
        scores = {}
        
        # ROE: Higher is better (15%+ = 100, 0% = 0)
        scores['roe'] = min(filled_metrics['roe'] / 0.15 * 100, 100)
        
        # ROA: Higher is better (10%+ = 100, 0% = 0)
        scores['roa'] = min(filled_metrics['roa'] / 0.10 * 100, 100)
        
        # Operating Margin: Higher is better (15%+ = 100, 0% = 0)
        scores['operating_margin'] = min(filled_metrics['operating_margin'] / 0.15 * 100, 100)
        
        # Debt Ratio: Lower is better (30% = 100, 70%+ = 0)
        debt_ratio = filled_metrics['debt_ratio']
        if debt_ratio <= 0.30:
            scores['debt_ratio'] = 100
        elif debt_ratio >= 0.70:
            scores['debt_ratio'] = 0
        else:
            scores['debt_ratio'] = 100 - (debt_ratio - 0.30) / 0.40 * 100
        
        # Current Ratio: Higher is better (1.5+ = 100, <1.0 = 0)
        current_ratio = filled_metrics['current_ratio']
        if current_ratio >= 1.5:
            scores['current_ratio'] = 100
        elif current_ratio < 1.0:
            scores['current_ratio'] = 0
        else:
            scores['current_ratio'] = (current_ratio - 1.0) / 0.5 * 100
        
        # Weighted total
        total_score = sum(scores[metric] * weight for metric, weight in weights.items())
        
        return {
            'company_name': company_data.get('company_name', 'Unknown'),
            'sector': sector,
            'total_score': round(total_score, 1),
            'component_scores': {k: round(v, 1) for k, v in scores.items()},
            'filled_metrics': filled_metrics,
            'missing_count': filled_result['missing_count'],
            'filled_fields': filled_result['filled_fields'],
            'confidence': filled_result['confidence'],
            'confidence_level': filled_result['confidence_level'],
            'note': filled_result['note']
        }
    
    def rank_companies(
        self,
        companies: List[Dict[str, Any]],
        top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank companies by score (Top-N approach, not strict threshold)
        
        Args:
            companies: List of scored company dicts
            top_n: Number of top companies to return (None = all)
            
        Returns:
            Ranked list with rank field added
        """
        # Sort by total_score descending
        sorted_companies = sorted(
            companies,
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )
        
        # Add rank
        for i, company in enumerate(sorted_companies, 1):
            company['rank'] = i
            
            # Add tier based on rank
            if i <= max(len(companies) // 5, 1):
                company['tier'] = 'top'
            elif i <= len(companies) // 2:
                company['tier'] = 'mid'
            else:
                company['tier'] = 'low'
        
        # Return top N if specified
        if top_n:
            return sorted_companies[:top_n]
        else:
            return sorted_companies


def test_scoring_missing_data():
    """Test scoring with missing data handling"""
    
    print("="*70)
    print("Scoring with Missing Data Test")
    print("="*70)
    
    scorer = ScoringWithMissingData()
    
    # Test 1: Complete data
    print("\n[Test 1] Complete Data")
    company1 = {
        'company_name': 'Tesla',
        'roe': 0.18,
        'roa': 0.10,
        'operating_margin': 0.12,
        'debt_ratio': 0.25,
        'current_ratio': 1.8
    }
    
    result1 = scorer.score_with_confidence(company1, sector='OEM')
    print(f"  Score: {result1['total_score']}")
    print(f"  Confidence: {result1['confidence']:.2f} ({result1['confidence_level']})")
    print(f"  Missing: {result1['missing_count']}")
    
    # Test 2: Partial data
    print("\n[Test 2] Partial Data (Missing 2 fields)")
    company2 = {
        'company_name': 'BYD',
        'roe': 0.14,
        'roa': None,  # Missing
        'operating_margin': 0.09,
        'debt_ratio': None,  # Missing
        'current_ratio': 1.5
    }
    
    result2 = scorer.score_with_confidence(company2, sector='OEM')
    print(f"  Score: {result2['total_score']}")
    print(f"  Confidence: {result2['confidence']:.2f} ({result2['confidence_level']})")
    print(f"  Missing: {result2['missing_count']}")
    print(f"  Filled: {result2['filled_fields']}")
    print(f"  Note: {result2['note']}")
    
    # Test 3: Mostly missing data
    print("\n[Test 3] Mostly Missing Data (4/5 missing)")
    company3 = {
        'company_name': 'Startup EV',
        'roe': 0.05,
        'roa': None,
        'operating_margin': None,
        'debt_ratio': None,
        'current_ratio': None
    }
    
    result3 = scorer.score_with_confidence(company3, sector='OEM')
    print(f"  Score: {result3['total_score']}")
    print(f"  Confidence: {result3['confidence']:.2f} ({result3['confidence_level']})")
    print(f"  Missing: {result3['missing_count']}")
    
    # Test 4: Safe normalization
    print("\n[Test 4] Safe Normalization")
    
    # Case 1: Normal variance
    values1 = [10, 20, 30, 40, 50]
    norm1 = scorer.safe_normalize(values1, method='z_score')
    print(f"  Normal variance: {values1}")
    print(f"  Z-score: {[round(v, 2) for v in norm1]}")
    
    # Case 2: Zero variance
    values2 = [50, 50, 50, 50, 50]
    norm2 = scorer.safe_normalize(values2, method='z_score')
    print(f"  Zero variance: {values2}")
    print(f"  Z-score (fallback): {[round(v, 2) for v in norm2]}")
    
    # Test 5: Ranking
    print("\n[Test 5] Company Ranking (Top-N)")
    companies = [result1, result2, result3]
    
    ranked = scorer.rank_companies(companies, top_n=2)
    print(f"  Top 2:")
    for company in ranked:
        print(f"    {company['rank']}. {company['company_name']:15s} Score: {company['total_score']:5.1f} "
              f"(Confidence: {company['confidence']:.2f}, Tier: {company['tier']})")
    
    print("\n" + "="*70)
    print("✓ All tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_scoring_missing_data()

