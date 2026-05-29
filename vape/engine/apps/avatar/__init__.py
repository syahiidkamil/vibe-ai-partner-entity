"""Avatar domain layer — plugin-agnostic interface for avatar rendering."""

from engine.apps.avatar.avatar_app import AvatarApp, AvatarPlugin, AvatarShell

__all__ = ["AvatarApp", "AvatarPlugin", "AvatarShell"]
