class User:
    def __init__(self, user_id: str, first_name: str, last_name: str, image_url: str):
        self.user_id, self.first_name, self.last_name, self.image_url = user_id, first_name, last_name, image_url


# TODO: Add more objects

#### Non-DB Objects ####

class ServiceException(Exception):
    def __init__(self, message, status_code=500):
        self.error_message = message
        self.status_code = status_code


class DomainException(ServiceException):
    def __init__(self, message):
        super().__init__(message, 400)
