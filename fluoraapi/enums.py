"""Enums for the Fluora API."""

from enum import Enum


class OSCPathNames(Enum):
    """OSC path names for the Fluora plant API."""

    POWER = "/SyYOTiXjQBjW"
    LIGHT_SENSOR = "/S53upLXAu7vg"
    REBOOT = "/pixelair/engine/reboot"
    BRIGHTNESS = "/Uv7aMFw5P2lX"

    # Animation modes - calling these with an int val will switch the mode as well
    ANIMATION_MODE = "/iwaaMkVzOfUM"

    ANIMATION_AUTO = "/Ps4hvrg9cWFd"
    ANIMATION_MANUAL = "/tdU63ENxy4UG"
    ANIMATION_SCENE = "/EpUwZA1GSPjO"
    ANIMATION_WHAT = "/yduArlhwq8kw"

    # Dashboard controls
    COLOR_MANUAL = "/VdV1IeK61BuM"

    SIZE_MANUAL = "/Vd7XP0X61BuM"  # manual
    SIZE_SCENE = "/Ve3ZSfSgP54T"

    SPEED_MANUAL = "/Vd72e0D61BuM"  # manual
    SPEED_SCENE = "/Ve3ZSfSgP54T"

    # Color palette controls
    HUE_AUTO = "/Ps4hvrg9cWFd"  # auto
    HUE_MANUAL = "/ThWnxs65l0sj"  # manual
    HUE_WHAT = "/Vd7Xz0X61BuM"
    HUE_SCENE = "/Ve3ZSfSgP54T"

    SATURATION_AUTO = "/wzLQUAQLcWky"  # auto
    SATURATION_MANUAL = "/UH9E69aUREEb"
    SATURATION_SCENE = "/y687U4Zgymsj"  # manual

    # Sound reactive controls
    AUDIO_GAIN = "/HwBeJeS0ufSp"
    AUDIO_ATTACK = "HwBeGOxYN5Sp"
    AUDIO_RELEASE = "/HwBeogt1MBDp"
    AUDIO_FILTER = "/HwBeiitcOaSp"


class AnimationMode(Enum):
    """Animation modes of the Fluora plant."""

    AUTO = 0
    SCENE = 1
    MANUAL = 2


class AnimationModeManualNew(Enum):
    """Animation names and number for manual mode."""

    TWINKLE = 1
    LEAFSWIRL = 1  # leaf
    MIRAGE = 1
    RAINBOW = 1
    RAINBOWBLOOM = 1  # leaf
    RAINBOWSWIRL = 1  # leaf
    SNAKES = 1  # leaf
    HUECYCLE = 1
    GRADIENT = 1
    HUEEQ = 1  # SR # leaf
    BOOMCLAP = 1  # SR  # leaf
    STEMEQ = 1  # SR    # leaf
    LEAFEQ = 1  # SR    # leaf
    LEAFFADE = 1  # leaf
    SWEEP = 1
    PULSE = 1
    LAMP = 1
    SOLIDCOLOR = 1
    STARSPANGLEDBANNER = 1
    STARSPANGLEDSPARKLE = 1
    HALLOWEENFADE = 1
    HALLOWEENTWINKLE = 1
    HOLIDAYFADE = 1
    HOLIDAYRIPPLE = 1
    HOLIDAYTWINKLE = 1


class AnimationModeManual(Enum):
    """Animation names and number for manual mode."""

    LEAFSWIRL = 1
    SNAKES = 2
    STEMEQ = 3  # SR
    HUEEQ = 4  # SR
    BOOMCLAP = 5  # SR
    HUECYCLE = 6
    RAINBOW = 7
    RAINBOWBLOOM = 8
    TWINKLE = 9
    LEAFFADE = 10
    STEMFADE = 11
    SOLIDCOLOR = 12
    SWEEP = 13
    PULSE = 14


class AnimationsSoundReactive(Enum):
    """Sound reactive animations."""

    STEMEQ = 3
    HUEEQ = 4
    BOOMCLAP = 5


class AnimationModeAuto(Enum):
    """Animation names and number for auto mode."""

    TWINKLE = 0
    SNAKES = 1
    RAINBOWSWIRL = 2
    SWEEP = 3
    LEAFFADE = 4
    LEAFSWIRL = 5


class AnimationModeScene(Enum):
    """Animation names and number for scene mode."""

    PARTY = 0
    CHILL = 1  # works
    FOCUS = 2
    BEDTIME = 3
    AWAKEN = 4  # works


class FluoraAnimations(Enum):
    """Animation names for the Fluora LED plant
    0-99 - reserved for system - Auto mode
    100-199 - manual mode animations - subtract 100 to get the actual value
    200-299 - scene mode animations - subtract 200 to get the actual value
    """

    # system reserved
    AUTO = 0
    # manual mode animations
    LEAFSWIRL = 101
    SNAKES = 102
    STEMEQ = 103  # SR
    HUEEQ = 104  # SR
    BOOMCLAP = 105  # SR
    HUECYCLE = 106
    RAINBOW = 107
    RAINBOWBLOOM = 108
    TWINKLE = 109
    LEAFFADE = 110
    STEMFADE = 111
    SOLIDCOLOR = 112
    SWEEP = 113
    PULSE = 114
    # scene mode animations
    PARTY = 200
    CHILL = 201
    FOCUS = 202
    BEDTIME = 203
    AWAKEN = 204
