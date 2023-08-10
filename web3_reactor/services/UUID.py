from uuid import UUID as _UUID, uuid1 as uuid1_, uuid4 as uuid4_, uuid5 as uuid5_, uuid3 as uuid3_


class UUID(_UUID):
    def __repr__(self):
        return f"<UUID {hex(self.fields[0])}>"

    def __str__(self):
        return hex(self.fields[0])


def uuid1():
    return UUID(uuid1_().hex)


uuid = uuid1


def uuid4():
    return UUID(uuid4_().hex)


def uuid5(namespace: UUID, name: str):
    return UUID(uuid5_(namespace, name).hex)


def uuid3(namespace: UUID, name: str):
    return UUID(uuid3_(namespace, name).hex)


__all__ = (
    "UUID",
    "uuid",
    "uuid1",
    "uuid3",
    "uuid4",
    "uuid5",
)
