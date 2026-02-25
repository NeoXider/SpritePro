"""Custom exceptions for SpritePro library."""


class SpriteProError(Exception):
    """Base exception for all SpritePro errors."""

    pass


class ResourceError(SpriteProError):
    """Exception raised for resource loading errors (textures, sounds, etc.)."""

    pass


class SceneError(SpriteProError):
    """Exception raised for scene-related errors."""

    pass


class TweenError(SpriteProError):
    """Exception raised for tween/animation errors."""

    pass


class ConfigurationError(SpriteProError):
    """Exception raised for configuration/invalid parameter errors."""

    pass


class PhysicsError(SpriteProError):
    """Exception raised for physics simulation errors."""

    pass


class NetworkError(SpriteProError):
    """Exception raised for networking errors."""

    pass


class AudioError(SpriteProError):
    """Exception raised for audio playback errors."""

    pass


class ValidationError(SpriteProError):
    """Exception raised for validation errors in public API."""

    pass


class PoolError(SpriteProError):
    """Exception raised for object pool errors."""

    pass
