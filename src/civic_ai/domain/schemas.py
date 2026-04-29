from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Department:
    key: str
    name: str
    keywords: List[str]
    knowledge: List[str]


@dataclass
class RouteResult:
    department_key: str
    department_name: str
    confidence: float
    matched_keywords: List[str]
    secondary_department_key: Optional[str] = None
    secondary_department_name: Optional[str] = None