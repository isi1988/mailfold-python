from __future__ import annotations

from typing import Optional


class MailfoldError(Exception):
    """Base class for all errors raised by the Mailfold SDK."""


class MailfoldAPIError(MailfoldError):
    """Raised when the Mailfold API returns a non-2xx response.

    Exposes the HTTP status code, the server-provided "error" message, and
    (when the server sent one, e.g. on 429 rate limiting) the Retry-After
    value in seconds.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        retry_after: Optional[int] = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.retry_after = retry_after
        super().__init__(f"Mailfold API error ({status_code}): {message}")


class MailfoldConnectionError(MailfoldError):
    """Raised when the request could not reach the server at all."""
