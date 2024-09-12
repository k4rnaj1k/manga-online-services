from os import getenv
import time
import stomp
import signal
import sys


# Listener class to handle incoming messages and errors
class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print(f"Received an error: {frame.body}")

    def on_message(self, frame):
        print(f"Received a message: {frame.body}")


# Define connection parameters
stomp_server = getenv("BROKER_HOST", default="localhost")
stomp_port = getenv("BROKER_PORT", default=61613)
username = getenv("BROKER_USERNAME", default="admin")
password = getenv("BROKER_PASSWORD", default="admin")

# Create connection object
conn = None


def connect_and_subscribe():
    global conn
    conn = stomp.Connection([(stomp_server, stomp_port)])
    conn.set_listener("", MyListener())
    conn.connect(username, password, wait=True)
    conn.subscribe(destination="/queue/manga", id=1, ack="auto")

    print("Connected to the STOMP server and subscribed to /queue/manga")


# Function to gracefully handle container shutdown
def signal_handler(sig, frame):
    print("Signal received, disconnecting...")
    if conn:
        conn.disconnect()
    sys.exit(0)


# Attach signal handler to terminate when the container is stopped/killed
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main loop to keep the connection alive and handle reconnection
while True:
    try:
        if not conn or not conn.is_connected():
            print("Attempting to connect to STOMP server...")
            connect_and_subscribe()

        # Send a message every 10 seconds to keep the connection alive (optional)
        print("Sent heartbeat message")

        # Sleep for a while to wait for incoming messages
        time.sleep(10)

    except Exception as e:
        print(f"Error occurred: {e}, reconnecting...")
        time.sleep(5)  # Wait a bit before trying to reconnect

