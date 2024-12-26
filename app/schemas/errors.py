from pydantic import BaseModel


class HTTPException(BaseModel):
    detail: str


class HTTPBadRequest(HTTPException):
    pass


class HTTPUnauthorized(HTTPException):
    pass


class HTTPPaymentRequired(HTTPException):
    pass


class HTTPForbidden(HTTPException):
    pass


class HTTPNotFound(HTTPException):
    pass


class HTTPConflict(HTTPException):
    pass


class HTTPTooManyRequests(HTTPException):
    pass


_400 = {"description": "Bad Request", "model": HTTPBadRequest}

_401 = {
    "description": "Unauthorized",
    "model": HTTPUnauthorized,
    "headers": {
        "WWW-Authenticate": {
            "description": "Authentication type",
            "type": "string",
        },
    },
}

_402 = {"description": "Payment Required", "model": HTTPPaymentRequired}

_403 = {"description": "Forbidden", "model": HTTPForbidden}

_404 = {"description": "Not Found", "model": HTTPNotFound}

_409 = {"description": "Conflict", "model": HTTPConflict}

_429 = {
    "description": "Too Many Requests",
    "model": HTTPTooManyRequests,
    "headers": {
        "Retry-After": {
            "description": "Time to wait before retrying",
            "type": "integer",
        }
    },
}
