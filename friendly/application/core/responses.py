SUCCESS = {
    200: {
        "description": "OK",
        "content": {"application/json": {"example": {"detail": "successful request"}}},
    }
}

FOUND = {
    302: {
        "description": "Redirects to Google OAuth login page",
        "content": {"application/json": {"example": {"detail": "successful request"}}},
    }
}

BAD_REQUEST = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"detail": "the server detected a syntactic/logical error in the client's request"}
            }
        },
    }
}

UNAUTHORIZED = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": {"detail": "Authentication is required to access the requested resource"}}
        },
    }
}

FORBIDDEN = {
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "The server understood the request, but it refuses to execute it due to restrictions on "
                    "client access to the specified resource"
                }
            }
        },
    }
}

NOT_FOUND = {
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {"detail": "The requested resource could not be found but may be available in the future."}
            }
        },
    }
}

CONFLICT = {
    409: {
        "description": "Conflict",
        "content": {
            "application/json": {"example": {"detail": "Cannot be executed due to conflicting resource access."}}
        },
    }
}

REQUEST_ENTITY_TOO_LARGE = {
    413: {
        "description": "Request Entity Too Large",
        "content": {
            "application/json": {
                "example": {"detail": "The uploaded files are too large. The size should not exceed 20MB."}
            }
        },
    }
}

UNPROCESSABLE_ENTITY = {
    422: {
        "description": "Unprocessable Entity",
        "content": {
            "application/json": {"example": {"detail": [{"loc": ["string", 0], "msg": "string", "type": "string"}]}}
        },
    }
}
