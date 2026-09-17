class Entity:
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(f'{key}={value}' for key, value in vars(self).items())})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.__class__ is other.__class__ and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.__class__, self.__dict__))
