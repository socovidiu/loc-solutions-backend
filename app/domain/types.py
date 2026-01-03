from __future__ import annotations
from dataclasses import dataclass
from typing import NewType
from uuid import UUID


JobId = NewType("JobId", UUID)       
Locale = NewType("Locale", str)
Provider = NewType("Provider", str)
