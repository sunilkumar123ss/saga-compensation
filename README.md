# Saga compensation runner

Compensate completed steps in reverse order after a later operation fails.

Educational implementation with synthetic examples.

## Run

Python 3.9 or newer; standard library only. From this directory:

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

The default example uses synthetic data and needs no credentials, installation, or network connection. The script also works by absolute path from another working directory.

## Behavior

A step provides a name, forward callback, and compensation callback. Successful steps retain their result for compensation. Failure stops forward execution, then attempts every completed compensation in reverse order; compensation failures are captured without skipping earlier steps.

## Use in Python

```python
from main import Step, run

reservations = []
def reserve():
    reservations.append('example-id')
    return 'example-id'
def cancel(reservation_id):
    reservations.remove(reservation_id)

result = run([Step('reserve', reserve, cancel)])
assert result['status'] == 'complete'
```

## Design limits

Callbacks are trusted local functions, and this runner is synchronous and in-memory. A forward callback must be atomic or recover its own partial failure: the failing step is not automatically compensated. Compensation may itself fail and is not equivalent to a database rollback. Real side effects need idempotency and durable recovery.

## Verification

The unit tests cover successful operations, failure paths, and invariants. These are local correctness checks, not production performance or security certification.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
