#EX-2 receiver code
import ustruct as struct
import utime, time
from machine import Pin, SPI
from NRF24L01 import NRF24L01
from micropython import const

_RX_POLL_DELAY = const(15)

cfg = {"spi": -1, "miso": 17, "mosi": 16, "sck": 4, "csn": 2, "ce": 15}

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

nrf = None


def call_back(*argc):
    # print(argc)
    print("有数据...")
    if nrf.any():
        while nrf.any():
            buf = nrf.recv()
            (millis, ) = struct.unpack("i", buf)
            print("received:", millis)
            utime.sleep_ms(_RX_POLL_DELAY)


def slave():
    global nrf
    
    p5 = Pin(5, Pin.IN)
    p5.irq(trigger=Pin.IRQ_FALLING, handler=call_back)
    
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)

    spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=4)


    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.stop_listening()
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

    while True:
        print("waiting ....")
        time.sleep(1)


slave()
