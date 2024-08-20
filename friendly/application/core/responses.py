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
