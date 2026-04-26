
import csv
import math
import random
import time
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


LOG_FILE = "telemetry_log.csv"
SAMPLE_RATE_HZ = 50
WINDOW_SECONDS = 10
MAX_POINTS = SAMPLE_RATE_HZ * WINDOW_SECONDS


def generate_telemetry(start_time):
    """
    Generate dummy rocket hopper telemetry.
    This is a visual demo model, not a physics-accurate rocket model.
    """
    t = time.time() - start_time

    # Simple hop-like altitude profile with noise
    altitude = max(0, 80 * math.sin(t / 8) + random.uniform(-1.5, 1.5))

    # Approximate vertical velocity
    velocity = 10 * math.cos(t / 8) + random.uniform(-0.7, 0.7)

    # Approximate acceleration
    acceleration = -1.2 * math.sin(t / 8) + random.uniform(-0.2, 0.2)

    # Orientation
    pitch = 5 * math.sin(t * 0.9)
    roll = 3 * math.sin(t * 0.55)
    yaw = 10 * math.sin(t * 0.25)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "mission_time": round(t, 3),
        "altitude": round(altitude, 3),
        "velocity": round(velocity, 3),
        "acceleration": round(acceleration, 3),
        "pitch": round(pitch, 3),
        "roll": round(roll, 3),
        "yaw": round(yaw, 3),
    }


def main():
    # Rolling buffers for dashboard
    times = deque(maxlen=MAX_POINTS)
    altitudes = deque(maxlen=MAX_POINTS)
    velocities = deque(maxlen=MAX_POINTS)
    accelerations = deque(maxlen=MAX_POINTS)
    pitches = deque(maxlen=MAX_POINTS)
    rolls = deque(maxlen=MAX_POINTS)
    yaws = deque(maxlen=MAX_POINTS)

    # CSV logging
    csv_file = open(LOG_FILE, "w", newline="")
    fieldnames = [
        "timestamp",
        "mission_time",
        "altitude",
        "velocity",
        "acceleration",
        "pitch",
        "roll",
        "yaw",
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    start_time = time.time()

    # Dashboard style
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(13, 8))
    fig.canvas.manager.set_window_title("Rocket Hopper Telemetry Dashboard")

    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.1])

    ax_alt = fig.add_subplot(gs[0, 0])
    ax_vel = fig.add_subplot(gs[0, 1])
    ax_acc = fig.add_subplot(gs[1, 0])
    ax_ori = fig.add_subplot(gs[1, 1])
    ax_status = fig.add_subplot(gs[2, :])

    fig.suptitle("Rocket Hopper Telemetry Dashboard", fontsize=18, fontweight="bold")

    # Different colors for each signal
    line_alt, = ax_alt.plot([], [], color="#00E5FF", linewidth=2, label="Altitude (m)")
    line_vel, = ax_vel.plot([], [], color="#76FF03", linewidth=2, label="Velocity (m/s)")
    line_acc, = ax_acc.plot([], [], color="#FFEA00", linewidth=2, label="Acceleration (m/s²)")
    line_pitch, = ax_ori.plot([], [], color="#FF4081", linewidth=2, label="Pitch (deg)")
    line_roll, = ax_ori.plot([], [], color="#B388FF", linewidth=2, label="Roll (deg)")
    line_yaw, = ax_ori.plot([], [], color="#FF9100", linewidth=2, label="Yaw (deg)")

    axes = [ax_alt, ax_vel, ax_acc, ax_ori]
    for ax in axes:
        ax.set_facecolor("#111827")
        ax.grid(True, color="#374151", alpha=0.7)
        ax.legend(loc="upper right")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#6B7280")

    ax_alt.set_title("Altitude", fontweight="bold")
    ax_vel.set_title("Vertical Velocity", fontweight="bold")
    ax_acc.set_title("Acceleration", fontweight="bold")
    ax_ori.set_title("Orientation", fontweight="bold")

    ax_alt.set_ylabel("m")
    ax_vel.set_ylabel("m/s")
    ax_acc.set_ylabel("m/s²")
    ax_ori.set_ylabel("deg")

    ax_acc.set_xlabel("Mission Time (s)")
    ax_ori.set_xlabel("Mission Time (s)")

    # Status panel
    ax_status.set_facecolor("#020617")
    ax_status.axis("off")
    status_text = ax_status.text(
        0.02,
        0.65,
        "",
        transform=ax_status.transAxes,
        fontsize=13,
        family="monospace",
        color="#E5E7EB",
        verticalalignment="top",
    )

    def update(_):
        data = generate_telemetry(start_time)
        writer.writerow(data)
        csv_file.flush()

        times.append(data["mission_time"])
        altitudes.append(data["altitude"])
        velocities.append(data["velocity"])
        accelerations.append(data["acceleration"])
        pitches.append(data["pitch"])
        rolls.append(data["roll"])
        yaws.append(data["yaw"])

        x = list(times)

        line_alt.set_data(x, list(altitudes))
        line_vel.set_data(x, list(velocities))
        line_acc.set_data(x, list(accelerations))
        line_pitch.set_data(x, list(pitches))
        line_roll.set_data(x, list(rolls))
        line_yaw.set_data(x, list(yaws))

        if len(x) > 1:
            xmin, xmax = min(x), max(x)
            for ax in axes:
                ax.set_xlim(xmin, xmax)

            ax_alt.set_ylim(max(0, min(altitudes) - 5), max(10, max(altitudes) + 5))
            ax_vel.set_ylim(min(velocities) - 2, max(velocities) + 2)
            ax_acc.set_ylim(min(accelerations) - 1, max(accelerations) + 1)
            ax_ori.set_ylim(
                min(min(pitches), min(rolls), min(yaws)) - 3,
                max(max(pitches), max(rolls), max(yaws)) + 3,
            )

        status_text.set_text(
            f"MISSION TIME : {data['mission_time']:>8.2f} s\n"
            f"ALTITUDE     : {data['altitude']:>8.2f} m\n"
            f"VELOCITY     : {data['velocity']:>8.2f} m/s\n"
            f"ACCELERATION : {data['acceleration']:>8.2f} m/s²\n"
            f"PITCH / ROLL / YAW : "
            f"{data['pitch']:>6.2f}° / {data['roll']:>6.2f}° / {data['yaw']:>6.2f}°\n"
            f"LOG FILE     : {LOG_FILE}"
        )

        return (
            line_alt,
            line_vel,
            line_acc,
            line_pitch,
            line_roll,
            line_yaw,
            status_text,
        )

    interval_ms = int(1000 / SAMPLE_RATE_HZ)
    ani = FuncAnimation(fig, update, interval=interval_ms, blit=False)

    try:
        plt.tight_layout()
        plt.show()
    finally:
        csv_file.close()


if __name__ == "__main__":
    main()
