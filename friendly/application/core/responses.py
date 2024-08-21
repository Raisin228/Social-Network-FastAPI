UNAUTHORIZED = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {"detail": "Authentication is required to access the requested resource"}
            }
        }
    }
}

FORBIDDEN = {
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "The server understood the request, but it refuses to execute it due to restrictions on "
                              "client access to the specified resource"}
            }
        }
    }
}

CONFLICT = {
    409: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": {"detail": "Cannot be executed due to conflicting resource access"}
            }
        }
    }
}
