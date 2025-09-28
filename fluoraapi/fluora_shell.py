"""Fluora Interactive Command Shell."""

import logging
import pprint
import signal
import sys
from cmd import Cmd

from .dataclasses import FluoraState  # relative import
from .fluoraapi import FluoraAPI  # relative import

PLANT_IP = "192.168.4.172"
PLANT_PORT = 6767
SVR_ADDRESS_WITH_PORT = ("0.0.0.0", 12345)


class CommandShell(Cmd):
    """Command interpreter for managing the Fluora plant.."""

    def __init__(self):
        super().__init__()
        self._configure_logging()

        self.api = FluoraAPI(
            PLANT_IP,
            PLANT_PORT,
            SVR_ADDRESS_WITH_PORT,
            api_callback=self._handle_api_update,
        )
        self.api.start_server()

    def _handle_api_update(self, state: dict) -> None:
        """Handle updates from the Fluora API."""
        print("\nAPI update received: %s", state)

    def _configure_logging(self):
        """Set up logging for the application."""
        timeform = "%d %b %Y %H:%M:%S"
        loglevel = logging.DEBUG
        logform = "%(asctime)s %(levelname)-7s %(funcName)16s() %(message)s"

        logging.basicConfig(
            level=loglevel,
            datefmt=timeform,
            format=logform,
            stream=sys.stdout,
            force=True,
        )

        root = logging.getLogger()
        logging.debug("Logging handlers configured: %s", root.handlers)

    def exit_shell(self, sig=None, frame=None):
        """Exits the program cleanly."""
        del sig, frame
        try:
            self.api.stop_server()
        except Exception:  # pylint: disable=W0703
            pass
        print("Exited Fluora interactive shell")
        raise SystemExit

    def _parse_argstring(self, argstring):
        """Convert a series of zero or more argument to an argument tuple."""
        return tuple(map(str, argstring.split()))

    def do_list_animations(self, argstring):
        """Prints a list of all animations available
        $ list_animations
        """
        del argstring
        print(self.api.available_animations())
        # print([e.name for e in AnimationModeManual])

    def do_quit(self, argstring):
        """Quits the program
        $ quit
        """
        del argstring
        self.exit_shell()

    def do_reboot(self, argstring):
        """Reboot the plant
        $ reboot
        """
        del argstring
        print("Reboot of plant requested")
        self.api.reboot()

    def do_power(self, argstring: int):
        """Turn Light On/Off

        $ power <0|1>
        """
        try:
            self.api.power(int(argstring))
        except ConnectionError as error:
            print(f"Connection error: {error}")
        except ValueError as error:
            print(f"Value error: {error}")

    def do_custom(self, argstring: str) -> None:
        """Send a custom command to the plant

        $ custom <route> <value>
        """
        arg_tuple = self._parse_argstring(argstring)
        if len(arg_tuple) != 2:
            print("Usage: custom <route> <value>")
            return
        route: str = arg_tuple[0]
        try:
            value: float = float(arg_tuple[1])
        except ValueError:
            print("Value must be a number")
            return
        try:
            self.api.custom_command(route, value)  # pylint: disable=W0212
        except ConnectionError as error:
            print(f"Connection error: {error}")
        except ValueError as error:
            print(f"Value error: {error}")

    def do_brightness(self, argstring: float):
        """Change the brightness of the plant

        $ brightness [0-1]
        """
        if float(argstring) < 0.00 or float(argstring) > 1.00:
            print("Size out of bounds [0-1]")
            return
        else:
            brightness: float = float(argstring)
            try:
                self.api.brightness_set(brightness)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_animation_mode(self, argstring: str):
        """Set the animation mode

        $ set_mode <mode>
        """
        arg_tuple = self._parse_argstring(argstring)
        if len(arg_tuple) != 1:
            print("Usage: set_mode <mode>")
            print("list_modes for possible values")
            return
        mode: str = arg_tuple[0].upper()
        try:
            self.api.animation_set_mode(mode)
        except ConnectionError as error:
            print(f"Connection problem: {error}")
        except ValueError as error:
            print(f"Mode problem: {error}")
        except LookupError as error:
            print(f"Animation problem: {error}")

    def do_animation(self, argstring: str):
        """Run pre-programmed effect."""
        arg_tuple = self._parse_argstring(argstring)
        if len(arg_tuple) != 1:
            print("Usage: animation <animation_name>")
            print("list_animations for possible values")
            return
        effect: str = arg_tuple[0].upper()
        try:
            self.api.animation_set(effect)
        except ConnectionError as error:
            print(f"Connection problem: {error}")
        except ValueError as error:
            print(f"Effect problem: {error}")
        except LookupError as error:
            print(f"Animation problem: {error}")

    def do_palette_hue(self, argstring: float):
        """Change the palette hue of the plant

        $ palette_hue [0-1]
        """
        if float(argstring) < 0.00 or float(argstring) > 1.00:
            print("Size out of bounds [0-1]")
            return
        else:
            hue: float = float(argstring)
            try:
                self.api.palette_hue_set(hue)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_palette_saturation(self, argstring: float):
        """Change the palette saturation of the plant

        $ palette_saturation [0-1]
        """
        if float(argstring) < 0.00 or float(argstring) > 1.00:
            print("Size out of bounds [0-1]")
            return
        else:
            saturation: float = float(argstring)
            try:
                self.api.palette_saturation_set(saturation)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_animation_speed(self, argstring: float):
        """Change the animation speed of the plant

        $ animation_speed [0-1]
        """
        if float(argstring) < 0.00 or float(argstring) > 1.00:
            print("Size out of bounds [0-1]")
            return
        else:
            speed: float = float(argstring)
            try:
                self.api.animation_speed_set(speed)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_animation_size(self, argstring: float):
        """Change the animation size of the plant

        $ animation_size [0-1]
        """
        if float(argstring) < 0.00 or float(argstring) > 1.00:
            print("Size out of bounds [0-1]")
            return
        else:
            size: float = float(argstring)
            try:
                self.api.animation_size_set(size)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_print_state(self, argstring: str):
        """Print the current state of the plant."""
        del argstring
        if self.api.plant_state is None:
            print("No state data available")
        else:
            state: FluoraState = self.api.plant_state
            print("\n-------- Current plant state -----------")
            pprint.pprint(state)
            print("\n")


if __name__ == "__main__":
    prompt = CommandShell()
    signal.signal(signal.SIGINT, prompt.exit_shell)  # type: ignore
    prompt.prompt = "fluora_shell $ "
    prompt.cmdloop("\n------- Fluora Interactive Shell (help for commands) -------\n")
