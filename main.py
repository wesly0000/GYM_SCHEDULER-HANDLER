from pushbullet import Pushbullet
import datetime
import time
import json
import os
import api 

# --- Workout Splits ---
WORKOUTS = {
    4: ["Chest & Triceps & Abs", "Back & Biceps", "Shoulders & Chest", "Legs & Arms"],
    6: ["Chest & Biceps", "Back & Triceps", "Shoulders & Chest", "Legs & Triceps", "Shoulders & Biceps", "Back & Abs"]
}

SETTINGS_FILE = "gym_settings.json"


def load_last_mode():
    """Load last workout mode (4 or 6 days) from file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return data.get("mode", 4)
    return 4  # default mode


def save_mode(mode):
    """Save current mode"""
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"mode": mode}, f)


def get_latest_command(pb):
    """Check for latest Pushbullet text from yourself"""
    pushes = pb.get_pushes(limit=3)
    for push in pushes:
        if "body" in push:
            body = push["body"].strip()
            if body in ["4", "6"]:
                return int(body)
    return None


def get_today_workout(days):
    """Return today's workout or rest day"""
    today = datetime.datetime.now().weekday()  # Monday = 0
    if today >= days:
        return None
    return WORKOUTS[days][today]


def send_notif(pb, workout, mode):
    """Send Pushbullet notification"""
    try:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        if workout:
            msg = f"🏋️ Gym Workout ({mode}-Day Plan)\nToday's Workout: {workout}\nTime: {current_time}"
        else:
            msg = f"😴 Rest day today!\n(Plan: {mode}-Day Routine)"
        pb.push_note("Gym Notifier", msg)
        print("Notification sent:", msg)
    except Exception as e:
        print("Error while sending:", e)


def main():
    API_KEY = api.API_KEY[0]  # using your first key
    pb = Pushbullet(API_KEY)

    # Load or get new mode
    mode = load_last_mode()
    print(f"Loaded previous mode: {mode}-day plan")

    new_mode = get_latest_command(pb)
    if new_mode:
        mode = new_mode
        save_mode(mode)
        pb.push_note("Gym Notifier", f"✅ Plan updated to {mode}-day workout schedule!")
        print(f"Updated plan to {mode}-day routine")

    # Determine today’s workout
    workout = get_today_workout(mode)
    send_notif(pb, workout, mode)


if __name__ == "__main__":
    main()
