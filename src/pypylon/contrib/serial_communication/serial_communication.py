"""Basler Serial Communication"""

import logging
import time
from typing import Generator, Optional, Union

import serial

from pypylon import pylon as py
from pypylon.pylon import InvalidArgumentException, RuntimeException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def timeout_generator(timeout_s: Union[float, None],
                      min_interval_s: Union[float, None] = 0.1,
                      raise_error: bool = False) -> Generator[bool, None, None]:
    """Timeout Generator to handle time-checks easy in a for-loop

    :param timeout_s: timeout in seconds
    :param min_interval_s: the minimum interval between checks - could be used to avoid heavy load during busy waiting
    :param raise_error: if true, raises a timeout error instead yield a "False" at the end
    :return: True until there is time left, false otherwise
    """
    if timeout_s is None:
        # Never timeout
        while True:
            yield True

    end_time = time.perf_counter() + timeout_s
    last_call = time.perf_counter()
    if timeout_s > 0:
        yield True  # return min one true for every call with a minimum timeout

    while time.perf_counter() < end_time:
        if min_interval_s > 0:
            # force a minimum interval
            time.sleep(max(min_interval_s - (time.perf_counter() - last_call), 0))
        last_call = time.perf_counter()
        yield True
    if raise_error:
        # Write (nearly) the time until the timeout,
        # if the condition check is very slow, this could be a hint
        raise TimeoutError(f"Timed out after {time.perf_counter() - end_time + timeout_s:.3f} seconds")

    yield False


# pylint: disable=too-many-instance-attributes
class BaslerSerial(serial.SerialBase):
    """
    A class to manage the Serial Communication for a Basler camera.

    This class facilitates the configuration and operation of the Serial interface
    on a Basler camera, providing methods to send and receive data over the serial interface,
    configure the camera's serial settings (such as baud rate, data bits, parity, stop bits),
    and monitor the status of the camera"""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def __init__(self,
                 *args,
                 camera: py.InstantCamera,
                 rx_line: str = "Line2",
                 tx_line: str = "Line3",
                 baudrate: int = 115200,
                 bytesize: int = 8,
                 parity: str = "None",
                 stop_bits: int = 1,
                 timeout: float = 1.0,
                 timeout_interval: float = 0.1,
                 ):

        """Initializes the BaslerSerial instance and configures the camera settings.

        :param camera: The Basler camera that will be used for communication.
        :param rx_line: The reception line to use (default "Line2").
        :param tx_line: The transmit line to use (default "Line3").
        :param baudrate: The baud rate for communication (default 115200).
        :param bytesize: The number of data bits for (default 8).
        :param parity: The parity setting for communication (default "None").
        :param stop_bits: The number of stop bits for (default 1).
        :param timeout: The timeout duration in seconds for operations (default 1.0).
        :param timeout_interval: The interval in seconds between retries during timeout (default 0.1).
        """

        self.camera = camera
        self._rx_source = rx_line
        self._tx_sink = tx_line

        port = f"Basler_{camera.GetDeviceInfo().GetSerialNumber()}"

        # ruff: noqa: B026
        super().__init__(port=port,
                         baudrate=baudrate,
                         bytesize=bytesize,
                         parity=parity,
                         stopbits=stop_bits,
                         timeout=timeout,
                         *args)

        self._timeout = timeout  #
        self._timeout_interval = timeout_interval
        self._input_buffer = bytearray()
        self.open()
        # reset buffers inside the camera on initialization
        self.reset_input_buffer()
        self.reset_output_buffer()

    def open(self):
        """Open the Camera

        Although the camera is opened during initialization, this method can be called
        to verify that the camera is open to avoid any unexpected behavior."""
        if not self.camera.IsOpen():
            self.camera.Open()
            logger.debug(f"Camera opened: {self.camera.GetDeviceInfo().GetSerialNumber()}")
        if not self.is_open:
            self._reconfigure_port()
            self.is_open = True

    def __enter__(self):
        """Enter context: ensure camera is open."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context: flush serial."""
        self.flush()

    def close(self, close_camera=False):
        """Since normally the camera remains open throughout its lifecycle, this method does not perform
        any actions by default. Set close_camera to "True", if the connection termination should really close the camera
        """
        if not (close_camera or self.camera.IsOpen()):
            return
        self.camera.Close()

    def flush(self):
        """Block until TX-Buffer is empty"""
        for _ in timeout_generator(self._timeout, self._timeout_interval, raise_error=True):
            if self.camera.BslSerialTxFifoEmpty.Value:
                break

    def _reconfigure_port(self):
        """Reconfigure the port settings based on the current configuration."""
        logger.debug("Reconfiguring port")
        self.configure_line(self._rx_source, self._tx_sink, touch_rx_line=False)
        self.configure_frame(self._baudrate, self._bytesize, self._parity, self._stopbits)

    def configure_line(self, rx_source: str, tx_sink: str, touch_rx_line: bool = True):
        """Camera setup for the uart hardware lines.

        :param rx_source: source of the uart signal (input line)
        :param tx_sink: sink of the uart signal (output line)
        :param touch_rx_line: change the line settings to input and not inverted, if true
        :return: None
        """
        available_sources = self.camera.BslSerialRxSource.Symbolics
        if rx_source in available_sources:
            self.camera.BslSerialRxSource.Value = rx_source
        else:
            raise ValueError(f"RX Source not supported: {rx_source}")

        if rx_source in self.camera.LineSelector.Symbolics and touch_rx_line:
            self.camera.LineSelector.Value = rx_source
            self.camera.LineMode.Value = "Input"
            self.camera.LineInverter.Value = False

        if tx_sink in self.camera.LineSelector.Symbolics:
            self.camera.LineSelector.Value = tx_sink
            try:
                self.camera.LineMode.Value = "Output"
                self.camera.LineSource.Value = "SerialTx"
                self.camera.LineInverter.Value = False
            except InvalidArgumentException as e:
                raise ValueError(f"Line is not supported as Serial-TX: {tx_sink}") from e

        self._rx_source = rx_source
        self._tx_sink = tx_sink
        logger.debug(f"Configured RX Source: {rx_source}, TX Sink: {tx_sink}")

    def configure_frame(self, baud_rate: int, data_bits: int, parity: str, stop_bits: int):
        """Set up the timing of the camera UART feature.

        :param baud_rate: Integer Value of the baud rate, like: 9600, 115200
        :param data_bits: Integer Value of Payload Bits (7 or 8)
        :param parity: String Value of Parity setting (Odd, Even, None)
        :param stop_bits: Integer Value of the Stop bits (1,2)
        :return: None
        """
        baud_rate_node = self.camera.BslSerialBaudRate
        data_bit_node = self.camera.BslSerialNumberOfDataBits
        parity_node = self.camera.BslSerialParity
        stop_bit_node = self.camera.BslSerialNumberOfStopBits

        # convert from serial to camera settings
        if parity in serial.PARITY_NAMES:
            parity = serial.PARITY_NAMES[parity]
        if parity.upper() not in ["ODD", "EVEN", "NONE"]:
            raise ValueError(f"The Camera Serial only supports: 'Odd', 'Even', or 'None' parity, is {parity}.")

        try:
            baud_rate_node.Value = f"Baud{baud_rate}"
            data_bit_node.Value = f"Bits{data_bits}"
            parity_node.Value = parity.capitalize()
            stop_bit_node.Value = f"Bits{stop_bits}"
        except InvalidArgumentException as in_arg_ex:
            raise AssertionError("Configuration is not possible, Invalid Argument:" + str(in_arg_ex)) from in_arg_ex

        self._baudrate = baud_rate
        self._bytesize = data_bits

        # store the parity in the serial.SerialBase format
        self._parity = {v: k for k, v in serial.PARITY_NAMES.items()}[parity]
        self._stopbits = stop_bits
        logger.debug(f"Configured Serial Frame: Baudrate: {baud_rate}, Data Bits: {data_bits}, \
                     Parity: {parity}, Stop Bits: {stop_bits}")

    @property
    def out_waiting(self) -> int:
        """Return 1 if there are bytes left to be sent, exact number is unknown"""
        return 1 if self.camera.BslSerialTxFifoEmpty.Value else 0

    @property
    def in_waiting(self) -> int:
        """Performing a read, add it to the internal buffer and return the count of waiting bytes"""
        self.receive()
        return len(self._input_buffer)

    def reset(self):
        """Clean the camera uart by resetting the status register
        and read all remaining bytes.

        :return: None
        """
        logger.debug("Camera Serial Reset started")
        self._input_buffer = bytearray()

        self.camera.BslSerialTxBreak.Value = False
        self.camera.BslSerialReceive.Execute()

        for _ in timeout_generator(self._timeout, self._timeout_interval, raise_error=True):
            if self.camera.BslSerialTransferLength.Value == 0 and self.camera.BslSerialTxFifoEmpty.Value:
                break
            self.camera.BslSerialReceive.Execute()

        # wait until last byte is transmitted
        # (Start + 8-Bit Data + Parity + 2 Stop) / 1200 = 10ms
        # wait 50ms to be sure
        time.sleep(0.05)

        self.camera.BslSerialRxBreakReset.Execute()

        buffer_size = self.camera.BslSerialTransferBuffer.GetLength()
        self.camera.BslSerialTransferBuffer.Set(b"\x00" * buffer_size)
        self.camera.BslSerialTransferLength.Value = 0

        # update BslSerialTxFifoOverflow Status
        self.camera.BslSerialTransmit.Execute()
        if self.camera.BslSerialTxFifoOverflow.Value:
            raise AssertionError("BslSerialTxFifoOverflow is not reset")
        logger.debug("Camera Serial Reset done")

    def check_status(self, assert_ok=True) -> list:
        """Check the camera uart status register.
        Every value except 0 is an unexpected behaviour.

        :param assert_ok: raise an assert error if any bit is set
        :return: a list with the occurred issues (if no assert error was thrown)
        """
        error_list: list = []

        if self.camera.BslSerialTxFifoOverflow.Value:
            error_list.append("TX_FIFO_OVERFLOW")
        if self.camera.BslSerialRxFifoOverflow.Value:
            error_list.append("RX_FIFO_OVERFLOW")

        if self.camera.BslSerialRxParityError.Value:
            error_list.append("RX_PARITY_ERROR")
        if self.camera.BslSerialRxStopBitError.Value:
            error_list.append("RX_STOP_BIT_ERROR")

        if self.camera.BslSerialRxBreak.Value:
            error_list.append("BREAK_ON_RX")

        logger.debug(f"Camera Serial Status checked: {error_list}")
        # pylint: disable=C1801
        if assert_ok and len(error_list) != 0:
            raise AssertionError(f"Serial Error detected: {error_list}")
        return error_list

    def single_send(self, data: bytes, block: bool = True):
        """Sends a single chunk of data over Serial Communication

        :param data: The data to send, in the form of a bytes object.
        :param block: If True, the method will block until the transmission is complete.
        :return: The number of bytes transmitted.
        :raises ValueError: If the data length exceeds the camera's maximum transfer length.
        :raises RuntimeException: If there is an error writing to the transfer buffer.
        """

        assert isinstance(data, bytes)

        data_len = len(data)
        if data_len == 0:
            return 0
        if data_len > self.camera.BslSerialTransferLength.Max:
            raise ValueError(f"Could only send {self.camera.BslSerialTransferLength.Max} bytes at one call!")

        self.camera.BslSerialTransferLength.Value = data_len

        ireg_special_value = bytearray(data)

        if self.camera.IsGigE():
            # GigE needs 4 byte blocks in i-register
            miss_bytes = 4 - (data_len % 4)
            if miss_bytes != 4:
                ireg_special_value.extend(b"\x00" * miss_bytes)
        try:
            self.camera.BslSerialTransferBuffer.Set(bytes(ireg_special_value))
        except RuntimeException as exception:
            raise AssertionError("Error writing to Transfer Buffer") from exception

        self.camera.BslSerialTransmit.Execute()

        if block:
            self.flush()
        return data_len

    def receive(self):
        """Perform Readout of the Camera RX Buffer.

        :return: None
        """
        self.camera.BslSerialReceive.Execute()
        rec_bytes = self.camera.BslSerialTransferLength.Value
        self._input_buffer.extend(self.camera.BslSerialTransferBuffer.GetAll()[:rec_bytes])

    def write(self, data: Union[bytes, bytearray, memoryview], block: bool = True):
        """
        Writes bytes data to the camera's Serial interface.

        This method writes the provided data in multiple slices if necessary
        """
        data = bytes(data)
        data_len = len(data)
        if data_len == 0:
            return 0

        max_single_slice = self.camera.BslSerialTransferLength.Max

        data_to_send = bytearray(data)
        slices = (data_len + max_single_slice - 1) // max_single_slice

        # it's not possible to buffer the data,
        # if there is more then one slice, force waiting!
        if slices > 1 and not block:
            logger.warning(f"Forced blocking during write, due to camera tx-buffer limit of {max_single_slice} bytes!")
            block = True

        send_count = 0
        for i in range(slices):
            send_count += self.single_send(bytes(data_to_send[i * max_single_slice:(i + 1) * max_single_slice]),
                                           block=block)
        return send_count

    def _consume_n_bytes(self, n: Optional[int] = None) -> bytearray:
        """Consume exactly n bytes from the input buffer (or less if not available)."""
        if n is None:
            n = len(self._input_buffer)
        result = self._input_buffer[:n]
        self._input_buffer = self._input_buffer[n:]
        return result

    def read(self, size: int = 1) -> bytes:
        """Reads a specific number of bytes from the camera's RX-Buffer.

        This method reads from the internal buffer, waiting for new data if necessary.
        It also handles timeouts if the requested number of bytes is not available within the timeout period.

        :param size: The number of bytes to read from the buffer (default is 1).
        :return: The requested bytes from the buffer, or fewer if the timeout occurs.
        """
        for _ in timeout_generator(self._timeout):  # no interval here, reading is critical in time
            if len(self._input_buffer) < size:
                self.receive()
                continue
            return bytes(self._consume_n_bytes(size))
        return bytes(self._consume_n_bytes())


    def reset_input_buffer(self):
        """Resets the input buffer on host and on camera"""

        self._input_buffer = bytearray()
        while self.camera.BslSerialTransferLength.Value:
            self.camera.BslSerialReceive.Execute()
        logger.debug("Camera Serial Input Buffer reset done")

    def reset_output_buffer(self):
        """Flush the output buffer on camera

        Since there is no buffer on host side, that is all
        """
        self.flush()

    def update_break_state(self):
        """Update the break state of the serial communication."""
        self.camera.BslSerialTxBreak.Value = self.break_condition
