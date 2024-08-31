"""Dataclasses for the Fluora API."""

from dataclasses import dataclass


@dataclass
class FluoraState:  # pylint: disable=R0902
    """Represents the state of a Fluora Plant."""

    model: str = ""
    rssi: int = 0
    mac_address: str = ""

    audio_filter: float = 0.0
    audio_release: float = 0.0
    audio_gain: float = 0.0
    audio_attack: float = 0.0

    light_sensor_enabled: bool = False

    main_light: bool = False
    brightness: float = 0.0

    animation_mode: int = 0
    active_animation: str = ""
    animation_bloom: float = 0.0
    animation_speed: float = 0.0
    animation_size: float = 0.0

    palette_saturation: float = 0.0
    palette_hue: float = 0.0
