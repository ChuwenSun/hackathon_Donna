# exceptions.py
class ReservationError(Exception):
    """Base class for all reservation-related errors."""

    pass


class DateUnavailableException(ReservationError):
    """Exception raised when the selected date is not available."""

    pass


class TimeUnavailableException(ReservationError):
    """Exception raised when the selected time is not available."""

    pass


class UnexpectedScriptError(ReservationError):
    """Exception raised for unexpected script errors."""

    pass


class OpenTableOptionNotFoundException(Exception):
    pass


class EmailInputNotAvailableException(Exception):
    pass


class FinalReserveBtnNotAvailableException(Exception):
    pass


class TimeSlotsNotFoundException(Exception):
    def __init__(self, message):
        # Store the variables
        self.message = message
        super().__init__(message)

    def __str__(self):
        # Customize the string representation of the exception
        return f"TimeSlotsNotFoundException: ({self.message})"
