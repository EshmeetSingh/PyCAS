def unsupported(reason):
    """
    Construct a standardized error object.

    All unsupported operations return this structure so that
    dispatchers can fail loudly and consistently.
    """
    return {
        "error": True,
        "reason": reason
    }