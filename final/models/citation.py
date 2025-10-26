"""
Citation  -     
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class SourceType(str, Enum):
    """  """
    NEWS_ARTICLE = "news_article"
    FINANCIAL_DATA = "financial_data"
    COMPANY_DISCLOSURE = "company_disclosure"
    DISCLOSURE = "disclosure"  #   
    MARKET_DATA = "market_data"
    POLICY_DOCUMENT = "policy_document"
    RESEARCH_REPORT = "research_report"
    WEB_SEARCH = "web_search"
    API_DATA = "api_data"
    CALCULATION = "calculation"
    ANALYSIS = "analysis"


class Citation(BaseModel):
    """
       Citation 
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType
    data_source: str
    title: str
    url: Optional[str] = None
    publication_date: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class SourceManager:
    """
       SourceManager 
    """
    
    def __init__(self):
        self.citations: List[Citation] = []
        self._citation_index: Dict[str, Citation] = {}
    
    def add_citation(self, 
                    source_type: SourceType,
                    data_source: str,
                    title: str,
                    url: Optional[str] = None,
                    publication_date: Optional[datetime] = None,
                    raw_data: Optional[Dict[str, Any]] = None,
                    confidence_score: float = 0.5,
                    reliability_score: float = 0.5,
                    tags: List[str] = None,
                    description: Optional[str] = None) -> Citation:
        """
          
        
        Args:
            source_type:  
            data_source:  
            title: 
            url: URL
            publication_date: 
            raw_data:  
            confidence_score:  
            reliability_score:  
            tags:  
            description: 
            
        Returns:
             Citation 
        """
        citation = Citation(
            source_type=source_type,
            data_source=data_source,
            title=title,
            url=url,
            publication_date=publication_date,
            raw_data=raw_data,
            confidence_score=confidence_score,
            reliability_score=reliability_score,
            tags=tags or [],
            description=description
        )
        
        self.citations.append(citation)
        self._citation_index[citation.id] = citation
        
        return citation
    
    def get_citation(self, citation_id: str) -> Optional[Citation]:
        """ID  """
        return self._citation_index.get(citation_id)
    
    def get_citations_by_type(self, source_type: SourceType) -> List[Citation]:
        """  """
        return [c for c in self.citations if c.source_type == source_type]
    
    def get_citations_by_tag(self, tag: str) -> List[Citation]:
        """  """
        return [c for c in self.citations if tag in c.tags]
    
    def get_high_confidence_citations(self, threshold: float = 0.7) -> List[Citation]:
        """  """
        return [c for c in self.citations if c.confidence_score >= threshold]
    
    def get_citations_summary(self) -> Dict[str, Any]:
        """  """
        if not self.citations:
            return {
                'total_citations': 0,
                'by_type': {},
                'by_source': {},
                'average_confidence': 0.0,
                'average_reliability': 0.0
            }
        
        #  
        by_type = {}
        for citation in self.citations:
            source_type = citation.source_type if isinstance(citation.source_type, str) else citation.source_type.value
            by_type[source_type] = by_type.get(source_type, 0) + 1
        
        #  
        by_source = {}
        for citation in self.citations:
            data_source = citation.data_source
            by_source[data_source] = by_source.get(data_source, 0) + 1
        
        #   
        avg_confidence = sum(c.confidence_score for c in self.citations) / len(self.citations)
        avg_reliability = sum(c.reliability_score for c in self.citations) / len(self.citations)
        
        return {
            'total_citations': len(self.citations),
            'by_type': by_type,
            'by_source': by_source,
            'average_confidence': avg_confidence,
            'average_reliability': avg_reliability
        }
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """
           (get_citations_summary )
        main.py   
        """
        return self.get_citations_summary()
    
    def generate_references_section(self) -> str:
        """
           ( )
            .
        """
        if not self.citations:
            return "## References\n\nNo citations available."
        
        references = ["## References\n"]
        
        #   
        by_type = {}
        for citation in self.citations:
            source_type = citation.source_type if isinstance(citation.source_type, str) else citation.source_type.value
            if source_type not in by_type:
                by_type[source_type] = []
            by_type[source_type].append(citation)
        
        #    
        for source_type, citations in sorted(by_type.items()):
            type_title = source_type.replace('_', ' ').title()
            references.append(f"\n### {type_title} ({len(citations)} sources)\n")
            
            for i, citation in enumerate(citations, 1):
                ref = f"{i}. **{citation.title or 'Untitled'}**"
                
                if citation.url:
                    ref += f"\n   - URL: {citation.url}"
                
                if citation.publication_date:
                    date_str = citation.publication_date.strftime('%Y-%m-%d') if isinstance(citation.publication_date, datetime) else str(citation.publication_date)
                    ref += f"\n   - Date: {date_str}"
                
                if citation.data_source:
                    ref += f"\n   - Source: {citation.data_source}"
                
                ref += f"\n   - Confidence: {citation.confidence_score:.2f}"
                
                if citation.description:
                    ref += f"\n   - Description: {citation.description}"
                
                references.append(ref + "\n")
        
        #   
        summary = self.get_citations_summary()
        references.append(f"\n### Summary Statistics\n")
        references.append(f"- Total Citations: {summary['total_citations']}")
        references.append(f"- Average Confidence: {summary['average_confidence']:.2f}")
        references.append(f"- Average Reliability: {summary['average_reliability']:.2f}")
        
        return "\n".join(references)
    
    def clear(self):
        """  """
        self.citations.clear()
        self._citation_index.clear()
    
    def __len__(self):
        return len(self.citations)
    
    def __iter__(self):
        return iter(self.citations)