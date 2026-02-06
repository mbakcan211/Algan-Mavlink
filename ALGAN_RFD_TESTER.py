import time
import argparse
from pymavlink import mavutil
from generated_build.python import algan_uav

class AlganRfdTester:
    def __init__(self, device, baud, interval=0.1):
        self.device = device
        self.baud = baud
        self.interval = interval
        self.connection = None
        self.mav = None
        self.counter = 0
        self.is_connected = False
        self.last_heartbeat_time = 0  # Manual tracker

    def connect(self):
        """Attempts to establish a connection and wait for a heartbeat."""
        try:
            print(f"Attempting to connect to {self.device}...")
            # autoreconnect=True helps with socket persistence
            self.connection = mavutil.mavlink_connection(
                self.device, 
                baud=self.baud, 
                autoreconnect=True
            )
            
            print("Waiting for heartbeat...")
            hb = self.connection.wait_heartbeat(timeout=5)
            
            if hb:
                self.mav = algan_uav.MAVLink(self.connection)
                self.is_connected = True
                self.last_heartbeat_time = time.time() # Initialize time
                print(f"Heartbeat received from System {self.connection.target_system}!")
                return True
            else:
                print("Heartbeat timeout. Retrying...")
                return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_rfd_test(self):
        """Encapsulates the sending logic with overflow protection."""
        if not self.is_connected:
            return False

        try:
            uint8_val = self.counter % 256
            self.mav.rfd_test_send(RANDOM_DEGER=uint8_val)
            self.counter += 1
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            self.is_connected = False 
            return False

    def check_link_health(self):
        """
        Non-blocking check for incoming heartbeats to update link status.
        """
        # Look for any message (non-blocking)
        msg = self.connection.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            self.last_heartbeat_time = time.time()

        # If we haven't heard a heartbeat in over 5 seconds, the link is dead
        if time.time() - self.last_heartbeat_time > 5:
            print("Link timed out (No heartbeat for 5s).")
            self.is_connected = False

    def run(self):
        """Main loop: Connect -> Send -> Monitor Health."""
        print("Starting Algan RFD Tester...")
        try:
            while True:
                if not self.is_connected:
                    if self.connect():
                        continue
                    else:
                        time.sleep(2)
                        continue

                # 1. Update link health by checking for incoming heartbeats
                self.check_link_health()

                # 2. If still connected, send our custom data
                if self.is_connected:
                    self.send_rfd_test()
                    time.sleep(self.interval)
                else:
                    print("Lost connection. Reconnecting...")

        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Production-ready MAVLink sender.')
    parser.add_argument('--device', default='udpin:127.0.0.1:14550', help='Device path')
    parser.add_argument('--baud', type=int, default=57600, help='Baud rate')
    parser.add_argument('--hz', type=float, default=10, help='Frequency in Hz')
    
    args = parser.parse_args()
    interval = 1.0 / args.hz
    
    tester = AlganRfdTester(args.device, args.baud, interval)
    tester.run()