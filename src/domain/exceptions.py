from domain.base import DomainBase


class ServiceException(Exception, DomainBase):
    def __init__(self, message, status_code=500):
        self.error_message = message
        self.status_code = status_code


class DomainException(ServiceException):
    def __init__(self, message):
        super().__init__(message, 400)
