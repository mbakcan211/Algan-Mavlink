import time
import argparse
from pymavlink import mavutil
from generated_build.python import algan_uav

parser = argparse.ArgumentParser(description='Send custom MAVLink messages.')
parser.add_argument('--device', default='udpin:127.0.0.1:14550', help='Device path (e.g., /dev/ttyUSB0) or connection string')
parser.add_argument('--baud', type=int, default=57600, help='Baud rate for serial connection')
args = parser.parse_args()

# Connect to the vehicle (SITL or SiK Radio)
connection = mavutil.mavlink_connection(args.device, baud=args.baud)

# Initialize the MAVLink instance with the connection
mav = algan_uav.MAVLink(connection)

print("Waiting for heartbeat from PX4...")
connection.wait_heartbeat()
print("Heartbeat received! Sending RFD_TEST messages...")

# Send custom RFD_TEST message with fixed random number data
# Field: RANDOM_DEGER (uint8_t)

try:
    mav.rfd_test_send(RANDOM_DEGER=int(input("RFD_TEST RANDOM_DEGER = ")))
    print("Message SENT!")
except Exception as e:
    print(f"mav.rf_test_send HATA --->> {e}")

time.sleep(1)