from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _get(d: dict, key: str, default=None):
    return d.get(key, default) if isinstance(d, dict) else default


@dataclass
class Address:
    name: str = ""
    email: str = ""
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Address":
        return cls(name=_get(d, "name", ""), email=_get(d, "email", ""), raw=d)


@dataclass
class Attachment:
    filename: str = ""
    content_type: str = ""
    size: int = 0
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Attachment":
        return cls(
            filename=_get(d, "filename", ""),
            content_type=_get(d, "content_type", ""),
            size=_get(d, "size", 0),
            raw=d,
        )


@dataclass
class Folder:
    name: str = ""
    attributes: list = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Folder":
        return cls(
            name=_get(d, "name", ""),
            attributes=list(_get(d, "attributes", []) or []),
            raw=d,
        )


@dataclass
class MessageHeader:
    uid: int = 0
    subject: str = ""
    from_: list = field(default_factory=list)
    to: list = field(default_factory=list)
    date: str = ""
    flags: list = field(default_factory=list)
    seen: bool = False
    size: int = 0
    preview: str = ""
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict) -> "MessageHeader":
        return cls(
            uid=_get(d, "uid", 0),
            subject=_get(d, "subject", ""),
            from_=[Address.from_dict(a) for a in (_get(d, "from", []) or [])],
            to=[Address.from_dict(a) for a in (_get(d, "to", []) or [])],
            date=_get(d, "date", ""),
            flags=list(_get(d, "flags", []) or []),
            seen=bool(_get(d, "seen", False)),
            size=_get(d, "size", 0),
            preview=_get(d, "preview", ""),
            raw=d,
        )


@dataclass
class Message(MessageHeader):
    text: str = ""
    html: str = ""
    attachments: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        header = MessageHeader.from_dict(d)
        return cls(
            **{k: getattr(header, k) for k in header.__dataclass_fields__},
            text=_get(d, "text", ""),
            html=_get(d, "html", ""),
            attachments=[Attachment.from_dict(a) for a in (_get(d, "attachments", []) or [])],
        )


@dataclass
class SendResult:
    status: str = ""
    raw: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict) -> "SendResult":
        return cls(status=_get(d, "status", ""), raw=d)


@dataclass
class AttachmentContent:
    data: bytes
    content_type: str = ""
    filename: str = ""
