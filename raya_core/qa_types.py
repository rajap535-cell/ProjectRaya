# qa_types.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class QAResult:
    question: str
    answer: str
    confidence: float
    source: Optional[str] = None
