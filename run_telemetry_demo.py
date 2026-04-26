"""
Single-file Rocket Hopper Telemetry Demo
Run with: python run_telemetry_demo.py

What it does:
- Simulates vehicle telemetry at ~50 Hz
- Simulates packet drops and jitter
- Logs received packets to CSV
- Shows live plots for altitude, velocity, and pitch
"""

import csv
import math
import random
import socket
import json
import threading
import time
from collections import deque
from queue import Queue, Empty
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

HOST = "127.0.0.1"
PORT = 5005
DATA_RATE_HZ = 50
PACKET_DROP_PROBABILITY = 0.03
MAX_JITTER_SECONDS = 0.015
LOG_FILE = Path("telemetry_log.csv")

running = True
plot_queue = Queue()
log_queue = Queue()


def make_packet(start_time: float, sequence: int) -> dict:
    now = time.time()
    t = now - start_time

    # Simple rocket-hop-like trajectory
    altitude = max(0.0, 60.0 * math.sin(math.pi * min(t, 12.0) / 12.0))
    velocity = 60.0 * (math.pi / 12.0) * math.cos(math.pi * min(t, 12.0) / 12.0)
    acceleration = -60.0 * (math.pi / 12.0) ** 2 * math.sin(math.pi * min(t, 12.0) / 12.0)

    # Add small sensor-like noise
    altitude += random.uniform(-0.3, 0.3)
    velocity += random.uniform(-0.2, 0.2)
    acceleration += random.uniform(-0.1, 0.1)

    return {
        "sequence": sequence,
        "timestamp": now,
        "mission_time": t,
        "altitude": altitude,
        "vertical_velocity": velocity,
        "acceleration": acceleration,
        "pitch": 5.0 * math.sin(t),
        "roll": 2.0 * math.sin(0.7 * t),
        "yaw": 10.0 * math.sin(0.3 * t),
    }


def vehicle_simulator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    sequence = 0
    period = 1.0 / DATA_RATE_HZ

    while running:
        packet = make_packet(start_time, sequence)
        sequence += 1

        # Simulate occasional packet loss
        if random.random() > PACKET_DROP_PROBABILITY:
            # Simulate network jitter
            time.sleep(random.uniform(0.0, MAX_JITTER_SECONDS))
            sock.sendto(json.dumps(packet).encode("utf-8"), (HOST, PORT))

        time.sleep(period)

    sock.close()


def ground_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)

    while running:
        try:
            raw, _addr = sock.recvfrom(4096)
            packet = json.loads(raw.decode("utf-8"))
            plot_queue.put(packet)
            log_queue.put(packet)
        except socket.timeout:
            continue
        except Exception as exc:
            print(f"Receiver error: {exc}")

    sock.close()


def csv_logger():
    fields = [
        "sequence",
        "timestamp",
        "mission_time",
        "altitude",
        "vertical_velocity",
        "acceleration",
        "pitch",
        "roll",
        "yaw",
    ]

    with LOG_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        while running or not log_queue.empty():
            try:
                packet = log_queue.get(timeout=0.5)
                writer.writerow({key: packet.get(key) for key in fields})
                f.flush()
            except Empty:
                continue


def main():
    global running

    receiver_thread = threading.Thread(target=ground_receiver, daemon=True)
    logger_thread = threading.Thread(target=csv_logger, daemon=True)
    vehicle_thread = threading.Thread(target=vehicle_simulator, daemon=True)

    receiver_thread.start()
    logger_thread.start()
    vehicle_thread.start()

    times = deque(maxlen=500)
    altitudes = deque(maxlen=500)
    velocities = deque(maxlen=500)
    pitches = deque(maxlen=500)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Rocket Hopper Telemetry Demo")

    line_alt, = ax1.plot([], [], label="Altitude (m)")
    line_vel, = ax2.plot([], [], label="Vertical Velocity (m/s)")
    line_pitch, = ax3.plot([], [], label="Pitch (deg)")

    ax1.set_ylabel("Altitude")
    ax2.set_ylabel("Velocity")
    ax3.set_ylabel("Pitch")
    ax3.set_xlabel("Mission Time (s)")

    for ax in (ax1, ax2, ax3):
        ax.grid(True)
        ax.legend(loc="upper right")

    def update(_frame):
        while True:
            try:
                packet = plot_queue.get_nowait()
                times.append(packet["mission_time"])
                altitudes.append(packet["altitude"])
                velocities.append(packet["vertical_velocity"])
                pitches.append(packet["pitch"])
            except Empty:
                break

        if not times:
            return line_alt, line_vel, line_pitch

        line_alt.set_data(times, altitudes)
        line_vel.set_data(times, velocities)
        line_pitch.set_data(times, pitches)

        for ax, values in ((ax1, altitudes), (ax2, velocities), (ax3, pitches)):
            ax.relim()
            ax.autoscale_view()

        ax3.set_xlim(max(0, times[-1] - 10), max(10, times[-1]))
        return line_alt, line_vel, line_pitch

    ani = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)

    print("Telemetry demo running.")
    print("Close the plot window to stop.")
    print(f"Logging to: {LOG_FILE.resolve()}")

    try:
        plt.show()
    finally:
        running = False
        time.sleep(0.5)


if __name__ == "__main__":
    main()
