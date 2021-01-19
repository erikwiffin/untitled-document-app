from dataclasses import asdict

from sqlalchemy.types import JSON, TypeDecorator


class ListOf(TypeDecorator):

    impl = JSON

    def __init__(self, dc, *args, **kwargs):
        TypeDecorator.__init__(self, *args, **kwargs)
        self.dc = dc

    def process_bind_param(self, value, dialect):
        return [asdict(row) for row in value]

    def process_result_value(self, value, dialect):
        return [self.dc(**row) for row in value]


class OneOf(TypeDecorator):

    impl = JSON

    def __init__(self, dc, *args, **kwargs):
        TypeDecorator.__init__(self, *args, **kwargs)
        self.dc = dc

    def process_bind_param(self, value, dialect):
        return asdict(value)

    def process_result_value(self, value, dialect):
        return self.dc(**value)
