class AnalysisDataError(Exception):
    """Raised when a request is valid but the underlying session has no usable data for the requested analysis."""
