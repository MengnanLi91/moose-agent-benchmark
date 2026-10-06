"""Evaluator infrastructure failures for protected MOOSE gates."""


class GateInfrastructureError(RuntimeError):
    """Raised when the evaluator cannot produce trustworthy gate results."""
