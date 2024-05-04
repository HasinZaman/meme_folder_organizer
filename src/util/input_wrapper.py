from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class Img:
    key: str
    meta_data: Optional[Dict[str, str]] = None

@dataclass
class Video:
    key: str
    meta_data: Optional[Dict[str, str]] = None

@dataclass
class Text:
    key: str
    meta_data: Optional[Dict[str, str]] = None

