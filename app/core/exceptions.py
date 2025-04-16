from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """
    Исключение для случаев, когда ресурс не найден.
    """
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class AuthError(HTTPException):
    """
    Исключение для ошибок аутентификации и авторизации.
    """
    def __init__(self, detail: str = "Не удалось подтвердить учетные данные"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedError(HTTPException):
    """
    Исключение для случаев, когда у пользователя недостаточно прав.
    """
    def __init__(self, detail: str = "Недостаточно прав"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestError(HTTPException):
    """
    Исключение для неверных запросов.
    """
    def __init__(self, detail: str = "Неверный запрос"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )