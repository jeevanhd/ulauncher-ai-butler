def run(text: str, minutes: int) -> dict:
    # TODO: schedule real notify-send via threading.Timer or systemd-run --user --on-active
    return {"summary": f"Reminder set for {minutes}m", "detail": text}
