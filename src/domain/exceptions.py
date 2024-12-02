class NotFoundException(Exception):
    def __init__(self, detail: str = "Not found."):
        self.detail = detail

class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Unauthorized. Provided credentials or token have expired or invalid."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

class AccessDeniedException(Exception):
    def __init__(self, detail: str = "Access denied."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

class SourceTimeoutException(Exception):
    def __init__(self, detail: str = "Source timeout exceeded."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

class SourceUnavailableException(Exception):
    def __init__(self, detail: str = "Source is not available."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

class ConflictException(Exception):
    def __init__(self, detail: str = "Conflict."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

class UnhandledException(Exception):
    def __init__(self, detail: str = "Unknown error occurred."):
        self.detail = detail

    @classmethod
    def get_default_detail(cls):
        return cls().detail

