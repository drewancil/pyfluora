"""Dataclasses for the Fluora API."""

from dataclasses import dataclass
from fluoraapi.enums import AnimationMode


@dataclass
class FluoraState:  # pylint: disable=R0902
    """Represents the state of a Fluora Plant."""

    nickname: str = ""
    audio_filter: float = 0.0
    audio_release: float = 0.0
    audio_gain: float = 0.0
    audio_attack: float = 0.0

    light_sensor_enabled: bool = False
    brightness: float = 0.0
    main_light: bool = False

    mode: AnimationMode = AnimationMode.AUTO
    animation_name: str = ""  # todo: use enum
    animation_index: int = -1
    animation_speed: float = 0.0
    animation_size: float = 0.0

    saturation: float = 0.0
    hue: float = 0.0
