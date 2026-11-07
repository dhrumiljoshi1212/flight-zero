class FlightZeroError(Exception):
    """Base class for expected application errors."""


class FlightNotFound(FlightZeroError): pass
class SeatNotFound(FlightZeroError): pass
class SeatAlreadyBooked(FlightZeroError): pass
class ReservationNotFound(FlightZeroError): pass
class ReservationAlreadyCancelled(FlightZeroError): pass
class DataFormatError(FlightZeroError): pass
