"""Basler Serial Communication"""
import serial

from .serial_communication import BaslerSerial


def basler_cam_uart(camera, *args, **kwargs):
    """Create a BaslerSerial instance"""
    return BaslerSerial(camera, *args, **kwargs)

serial.protocol_handler_packages.append("serial_communication")
