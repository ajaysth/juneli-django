from datetime import datetime, timezone

def time_decay_weighted_score(events, now=None, half_life_hours=24):
    """
    events: queryset or list of EngagementEvent objects (must have .timestamp)
    now: current time (default: now)
    half_life_hours: how quickly the weight decays (smaller = more recent events matter more)
    """
    if now is None:
        now = datetime.now(timezone.utc)
    score = 0
    for event in events:
        hours_ago = (now - event.timestamp).total_seconds() / 3600
        weight = 0.5 ** (hours_ago / half_life_hours)
        score += weight
    return score