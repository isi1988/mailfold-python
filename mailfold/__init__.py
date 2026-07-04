from .client import Client
from .errors import MailfoldAPIError, MailfoldConnectionError, MailfoldError
from .models import (
    Address,
    Attachment,
    AttachmentContent,
    Folder,
    Message,
    MessageHeader,
    SendResult,
)

__version__ = "0.1.0"

__all__ = [
    "Client",
    "MailfoldError",
    "MailfoldAPIError",
    "MailfoldConnectionError",
    "Address",
    "Attachment",
    "AttachmentContent",
    "Folder",
    "Message",
    "MessageHeader",
    "SendResult",
]
