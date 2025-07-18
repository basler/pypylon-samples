"""Tests for pypylon contrib serial_communication module."""

import pytest


def test_serial_communication_module_import():
    """Test that serial_communication module and classes can be imported."""
    from pypylon.contrib.serial_communication.serial_communication import BaslerSerial, timeout_generator

    assert BaslerSerial is not None
    assert timeout_generator is not None


def test_timeout_generator_basic():
    """Test basic timeout_generator functionality."""
    from pypylon.contrib.serial_communication.serial_communication import timeout_generator

    # Test with short timeout
    results = []
    for is_active in timeout_generator(0.001):
        results.append(is_active)
        if len(results) > 10:  # Safety break
            break

    assert len(results) > 0
    assert results[0] is True  # First yield should be True
    assert results[-1] is False  # Last yield should be False


def test_timeout_generator_none_timeout():
    """Test timeout_generator with None (never timeout)."""
    from pypylon.contrib.serial_communication.serial_communication import timeout_generator

    count = 0
    for is_active in timeout_generator(None):
        assert is_active is True
        count += 1
        if count >= 3:  # Just test a few
            break

    assert count == 3


def test_timeout_generator_raise_error():
    """Test timeout_generator with raise_error=True."""
    from pypylon.contrib.serial_communication.serial_communication import timeout_generator

    with pytest.raises(TimeoutError):
        for _ in timeout_generator(0.001, raise_error=True):
            pass


def test_basler_serial_inheritance():
    """Test BaslerSerial inherits from serial.SerialBase."""
    import serial

    from pypylon.contrib.serial_communication.serial_communication import BaslerSerial

    assert issubclass(BaslerSerial, serial.SerialBase)
