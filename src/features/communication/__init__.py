"""Outbound communication channels such as email delivery."""

from .email_notifier import send_mail

__all__ = ["send_mail"]