#!/usr/bin/env python3
"""Advanced usage example for pyfluora with threading demonstration."""

import time
import threading
import logging
from fluoraapi import FluoraAPI, FluoraClient, FluoraStateServer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def monitor_state(api: FluoraAPI, duration: int = 30):
    """Monitor and print state changes for a specified duration."""
    print(f"Monitoring state for {duration} seconds...")

    start_time = time.time()
    last_brightness = None
    last_animation = None

    while time.time() - start_time < duration:
        state = api.plant_state
        if state:
            # Only print when values change
            if state.brightness != last_brightness:
                print(f"  Brightness changed: {state.brightness:.2f}")
                last_brightness = state.brightness

            if state.active_animation != last_animation:
                print(f"  Animation changed: {state.active_animation}")
                last_animation = state.active_animation

        time.sleep(1)

    print("State monitoring complete")


def demo_standalone_components():
    """Demonstrate using client and server separately."""
    print("\nStandalone Components Demo")
    print("-" * 30)

    # Use separate client and server
    client = FluoraClient(("192.168.4.172", 6767))
    server = FluoraStateServer(("192.168.4.229", 12345))

    try:
        # Start server in background
        server.server_start()
        print("Started standalone UDP server")

        # Send commands with separate client
        print("Sending commands with standalone client...")
        client.power(1)
        time.sleep(1)

        client.brightness_set(0.6)
        time.sleep(1)

        client.animation_set("HUECYCLE")
        time.sleep(2)

        # Check received state
        state = server.fluora_state
        print(
            f"Received state - Brightness: {state.brightness}, Main light: {state.main_light}"
        )

    except OSError as e:
        print(f"Network error: {e}")
    finally:
        server.server_stop()
        print("Stopped standalone server")


def demo_threaded_control():
    """Demonstrate controlling multiple aspects in separate threads."""
    print("\nThreaded Control Demo")
    print("-" * 20)

    def brightness_cycle(api: FluoraAPI):
        """Cycle brightness in a separate thread."""
        for i in range(5):
            brightness = 0.2 + (i * 0.2)  # 0.2 to 1.0
            api.brightness_set(brightness)
            print(f"  Thread: Set brightness to {brightness:.1f}")
            time.sleep(3)

    def animation_cycle(api: FluoraAPI):
        """Cycle animations in a separate thread."""
        animations = ["LEAFSWIRL", "SNAKES", "RAINBOW", "TWINKLE"]
        for anim in animations:
            api.animation_set(anim)
            print(f"  Thread: Set animation to {anim}")
            time.sleep(4)

    try:
        client = ("192.168.1.172", 6767)
        server = ("0.0.0.0", 12345)
        with FluoraAPI(client, server) as api:
            api.power(1)  # Make sure it's on

            # Start threads for different controls
            brightness_thread = threading.Thread(target=brightness_cycle, args=(api,))
            animation_thread = threading.Thread(target=animation_cycle, args=(api,))
            monitor_thread = threading.Thread(target=monitor_state, args=(api, 15))

            # Start all threads
            brightness_thread.start()
            animation_thread.start()
            monitor_thread.start()

            # Wait for all threads to complete
            brightness_thread.join()
            animation_thread.join()
            monitor_thread.join()

    except OSError as e:
        print(f"Network error: {e}")


def main():
    """Run all demonstrations."""
    print("Advanced pyfluora Usage Examples")
    print("=" * 40)

    try:
        demo_standalone_components()  # Demo 1: Standalone components
        time.sleep(2)
        demo_threaded_control()  # Demo 2: Threaded control

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except OSError as e:
        print(f"Network error - check that plant IP is correct: {e}")

    print("\nAdvanced examples completed!")


if __name__ == "__main__":
    main()
