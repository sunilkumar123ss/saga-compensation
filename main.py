"""Synchronous saga execution with explicit compensation outcomes."""
import argparse
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Step:
    name: str
    execute: object
    compensate: object

def run(steps):
    if not isinstance(steps, list):
        raise ValueError('Steps must be a list')
    seen = set()
    for step in steps:
        if not isinstance(step, Step) or not isinstance(step.name, str) or (not step.name) or (step.name in seen) or (not callable(step.execute)) or (not callable(step.compensate)):
            raise ValueError('Unique named steps need execute and compensate callbacks')
        seen.add(step.name)
    completed = []
    events = []
    for step in steps:
        try:
            value = step.execute()
        except Exception as error:
            events.append({'step': step.name, 'action': 'failed', 'error': str(error)})
            failed_compensations = []
            for (previous, result) in reversed(completed):
                try:
                    previous.compensate(result)
                    events.append({'step': previous.name, 'action': 'compensated'})
                except Exception as compensation_error:
                    failed_compensations.append(previous.name)
                    events.append({'step': previous.name, 'action': 'compensation_failed', 'error': str(compensation_error)})
            return {'status': 'compensation_incomplete' if failed_compensations else 'compensated', 'failed_step': step.name, 'failed_compensations': failed_compensations, 'events': events}
        completed.append((step, value))
        events.append({'step': step.name, 'action': 'completed'})
    return {'status': 'complete', 'events': events}
