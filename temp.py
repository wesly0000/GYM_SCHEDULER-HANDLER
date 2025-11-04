from pushbullet import Pushbullet
import datetime
import json
import os
import api
import time

# --- Workout Splits ---
WORKOUTS = {
    4: ["Chest & Triceps", "Back & Biceps", "Shoulders & Abs", "Legs"],
    6: ["Chest", "Back", "Shoulders", "Arms", "Legs", "Abs & Cardio"]
}

SETTINGS_FILE = "gym_settings.json"


def load_last_mode():
    """Load last workout mode (4 or 6)"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f).get("mode", 4)
    return 4


def save_mode(mode):
    """Save current workout mode"""
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"mode": mode}, f)


def get_today_workout(days):
    """Return today's workout or rest day"""
    today = datetime.datetime.now().weekday()  # 0=Mon ... 6=Sun

    if days == 4:
        # Alternate rest/work pattern (Tue, Thu, Sat, Mon next)
        workout_days = [1, 3, 5, 0]
        if today in workout_days:
            index = workout_days.index(today)
            return WORKOUTS[4][index]
        else:
            return None

    elif days == 6:
        # Sunday rest
        if today == 6:
            return None
        else:
            return WORKOUTS[6][today]

    return None


def send_notif(pb, title, message):
    """Send a Pushbullet notification"""
    pb.push_note(title, message)
    print("Sent:", message)


def check_pushes(pb, last_seen_time):
    """Check new messages after last_seen_time"""
    pushes = pb.get_pushes(modified_after=last_seen_time)
    if pushes:
        # Get the latest message only
        latest = pushes[0]
        body = latest.get("body", "").strip().lower()
        timestamp = latest.get("modified", 0)
        return body, timestamp
    return None, last_seen_time


def main():
    API_KEY = api.API_KEY[0]
    pb = Pushbullet(API_KEY)

    mode = load_last_mode()
    print(f"Last mode: {mode}-day plan")

    # Get timestamp of latest push to start from
    last_time = time.time()

    print("Listening for Pushbullet messages... (Ctrl+C to stop)")
    while True:
        body, new_time = check_pushes(pb, last_time)

        if body:
            if body in ["4", "6"]:
                mode = int(body)
                save_mode(mode)
                send_notif(pb, "Gym Notifier", f"✅ Plan updated to {mode}-day workout schedule!")

            elif body == "workout":
                workout = get_today_workout(mode)
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                if workout:
                    msg = f"🏋️ Gym Workout ({mode}-Day Plan)\nToday's Workout: {workout}\nTime: {current_time}"
                else:
                    msg = f"😴 Rest Day Today!\n(Plan: {mode}-Day Routine)\nTime: {current_time}"
                send_notif(pb, "Gym Notifier", msg)

            else:
                print("Ignored:", body)

            last_time = new_time

        time.sleep(5)  # Check every 5 seconds


if __name__ == "__main__":
    main()
