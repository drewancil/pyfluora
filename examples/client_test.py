#!/usr/bin/env python3
"""Basic client test."""

import time
import logging
from fluoraapi import FluoraAPI

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)


def main():
    """Demonstrate basic usage of the FluoraAPI."""

    client = ("192.168.1.172", 6767)
    server = ("0.0.0.0", 12345)

    print("Fluora LED Plant Control Example")
    print("=" * 35)

    # Method 1: Manual server management
    print("\n1. Manual server management:")
    api = FluoraAPI(client, server)

    try:
        # Start the server to receive state updates
        api.start_server()
        print("Started UDP server for state updates")

        # Give the server a moment to start
        time.sleep(1)

        print("Turning plant on...")
        api.power(1)
        time.sleep(2)

        api.brightness_set(0.1)
        time.sleep(2)

        print("Setting rainbow animation...")
        api.animation_set("RAINBOW")
        time.sleep(2)

        state = api.plant_state
        if state:
            print("\nCurrent state:")
            print(f"  Brightness: {state.brightness}")
            print(f"  Main light on: {state.main_light}")
            print(f"  Animation: {state.animation_name}")
        else:
            print("No state received yet")

    except Exception as e:  # pylint: disable=W0718
        print(f"Error: {e}")
    finally:
        # Always stop the server
        api.stop_server()
        print("Stopped UDP server")

    print("\n" + "=" * 50)

    # Method 2: Using context manager (recommended)
    print("\n2. Using context manager (recommended):")

    try:
        with FluoraAPI(client, server) as api:
            print("Server automatically started")

            # Cycle through some brightness levels
            for brightness in [0.2, 0.5, 0.8, 1.0]:
                print(f"Setting brightness to {int(brightness * 100)}%...")
                api.brightness_set(brightness)
                time.sleep(2)

            # Try different animations
            animations = ["TWINKLE", "PULSE", "SWEEP"]
            for anim in animations:
                print(f"Setting animation to {anim}...")
                api.animation_set(anim)
                time.sleep(3)

            print("Server will automatically stop when exiting context")

    except Exception as e:  # pylint: disable=W0718
        print(f"Error: {e}")

    print("\nExample completed!")


if __name__ == "__main__":
    main()
