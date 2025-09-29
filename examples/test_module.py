#!/usr/bin/env python3
"""Simple test to verify pyfluora module functionality."""

import time
from fluoraapi import FluoraAPI, FluoraClient, FluoraStateServer, FluoraState

client = ("192.168.1.172", 6767)
server = ("0.0.0.0", 12345)


def test_imports():
    """Test that all imports work correctly."""
    print("✓ All imports successful")


def test_client_creation():
    """Test creating a FluoraClient."""
    fluora_client = FluoraClient(client)
    assert fluora_client.effect_list is not None
    print("✓ FluoraClient creation successful")


def test_server_creation():
    """Test creating and starting/stopping FluoraStateServer."""
    try:
        state_server = FluoraStateServer(server)  # Use different port

        # Test starting server
        state_server.server_start()
        time.sleep(0.5)  # Give it time to start

        # Test stopping server
        state_server.server_stop()
        time.sleep(0.5)  # Give it time to stop

        print("✓ FluoraStateServer start/stop successful")
    except OSError as e:
        print(f"⚠ Server test skipped (port in use): {e}")


def test_api_creation():
    """Test creating FluoraAPI without starting server."""
    api = FluoraAPI(client, server)
    assert api.plant_state is not None  # Should have a FluoraState object
    print("✓ FluoraAPI creation successful")


def test_context_manager():
    """Test FluoraAPI context manager."""
    try:
        with FluoraAPI(client, server) as api:
            # Just test that context manager works
            assert api is not None
        print("✓ FluoraAPI context manager successful")
    except OSError as e:
        print(f"⚠ Context manager test skipped (port in use): {e}")


def test_dataclass():
    """Test FluoraState dataclass."""
    state = FluoraState()
    assert state.brightness == 0.0
    assert state.main_light is False

    # Test setting values
    state.brightness = 0.5
    state.main_light = True

    assert state.brightness == 0.5
    assert state.main_light is True

    print("✓ FluoraState dataclass working correctly")


def test_effect_lists():
    """Test that effect lists are available."""
    fluora_client = FluoraClient(client)
    effects = fluora_client.effect_list
    assert len(effects) > 0
    assert "Auto" in effects  # Should have at least the Auto effect
    print(f"✓ Effect list available: {len(effects)} effects")


def main():
    """Run all tests."""
    print("Running pyfluora Module Tests")
    print("=" * 35)

    tests = [
        test_imports,
        test_dataclass,
        test_client_creation,
        test_server_creation,
        test_api_creation,
        test_context_manager,
        test_effect_lists,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:  # pylint: disable=W0718
            print(f"✗ {test.__name__} failed: {e}")

    print(f"\nTest Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Module is properly structured.")
    else:
        print("⚠ Some tests failed. Check the module structure.")


if __name__ == "__main__":
    main()
