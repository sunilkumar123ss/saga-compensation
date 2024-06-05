"""Synchronous saga execution with explicit compensation outcomes."""
import argparse
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Step:
    name: str
    execute: object
    compensate: object
