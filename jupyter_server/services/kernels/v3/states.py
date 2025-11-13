from enum import Enum, EnumMeta


class StrContainerEnumMeta(EnumMeta):
    def __contains__(cls, item):
        for name, member in cls.__members__.items():
            if item == name or item == member.value:
                return True
        return False


class StrContainerEnum(str, Enum, metaclass=StrContainerEnumMeta):
    """A Enum object that enables search for items
    in a normal Enum object based on key and value.
    """


class ExecutionStates(StrContainerEnum):
    BUSY = "busy"
    IDLE = "idle"
    STARTING = "starting"
    UNKNOWN = "unknown"
    DEAD = "dead"
