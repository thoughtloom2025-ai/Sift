from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, resource: str):
        super().__init__(status_code=404, detail=f"{resource} not found")


class ConflictError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=409, detail=message)


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(status_code=401, detail=message)


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=message)


class BadRequestError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
