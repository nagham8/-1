# data/exceptions.py

class BookingError(Exception):
    """Базовый класс для ошибок, связанных с бронированием."""
    pass

class SeatUnavailableError(BookingError):
    """Вызывается при попытке забронировать уже зарезервированное место."""
    pass

class NotFoundError(BookingError):
    """Вызывается, когда сущность (событие/клиент/билет) не найдена."""
    pass

class ValidationError(BookingError):
    """Вызывается при неверном вводе или состоянии."""
    pass

class TicketNotFoundError(BookingError):
    """Вызывается, когда билет не найден."""
    pass
