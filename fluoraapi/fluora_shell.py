"""Fluora Interactive Command Shell."""

import signal
from cmd import Cmd

from fluoraapi import fluoraapi as api
from fluoraapi.dataclasses import FluoraState
from fluoraapi.enums import AnimationModeManual


class CommandShell(Cmd):
    """Command interpreter for managing the laser."""

    PLANT_IP = "192.168.4.172"
    PLANT_PORT = 6767
    SERVER_IP = "192.168.4.229"
    SERVER_PORT = 12345

    plant = api.FluoraAPI(PLANT_IP, PLANT_PORT, SERVER_IP, SERVER_PORT)

    def exit_shell(self, sig=None, frame=None):
        """Exits the program cleanly."""
        del sig, frame
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
        print([e.name for e in AnimationModeManual])

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
        self.plant.reboot()

    def do_power(self, argstring: int):
        """Turn Light On/Off

        $ power <0|1>
        """
        try:
            self.plant.power(int(argstring))
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
        else:
            brightness: float = float(argstring)
            try:
                self.plant.brightness_set(brightness)
            except ConnectionError as error:
                print(f"Connection error: {error}")
            except ValueError as error:
                print(f"Value error: {error}")

    def do_animation(self, argstring: str):
        """Run pre-programmed effect."""
        arg_tuple = self._parse_argstring(argstring)
        if len(arg_tuple) != 1:
            print("Usage: animation <animation_name>")
            print("list_animations for possible values")
            return
        effect: str = arg_tuple[0].upper()
        try:
            self.plant.animation_set_manual(effect)
        except ConnectionError as error:
            print(f"Connection problem: {error}")
        except ValueError as error:
            print(f"Effect problem: {error}")
        except LookupError as error:
            print(f"Animation problem: {error}")

    def do_print_state(self, argstring: str):
        """Print the current state of the plant."""
        del argstring
        if self.plant.plant_state is None:
            print("No state data available")
        else:
            state: FluoraState = self.plant.plant_state
            print(state)


if __name__ == "__main__":
    prompt = CommandShell()
    signal.signal(signal.SIGINT, prompt.exit_shell)  # type: ignore
    prompt.prompt = "fluora_shell $ "
    prompt.cmdloop("Started Fluora interactive shell")
    prompt.cmdloop("Started Fluora interactive shell")
