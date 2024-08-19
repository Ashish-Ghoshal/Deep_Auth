import uuid


class User:
    def __init__(
        self,
        name: str,
        username: str,
        email: str,
        phone: str,
        pass1: str,
        pass2: str,
        uid: str = None,
    ):
        self.name = name
        self.username = username
        self.email = email
        self.phone = phone
        self.pass1 = pass1
        self.pass2 = pass2
        self.uid = uid or str(uuid.uuid4()) + str(uuid.uuid4())[:4]

    def as_dict(self) -> dict:
        return self.__dict__

    def __repr__(self) -> str:
        return str(self.as_dict())
