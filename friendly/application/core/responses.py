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
