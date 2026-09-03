def analyze_traffic(
    vehicle_count,
    average_movement,
    waterlogging=False,
    road_obstruction=False,
    accident=False,
    pedestrian_activity=False
):

    reasons = []

    # -------------------------------
    # Traffic level
    # -------------------------------

    if vehicle_count >= 20 and average_movement < 0.35:
        traffic_level = "HIGH"

    elif vehicle_count >= 10:
        traffic_level = "MEDIUM"

    else:
        traffic_level = "LOW"

    # -------------------------------
    # Find possible reasons
    # -------------------------------

    if vehicle_count >= 20:
        reasons.append("High vehicle density")

    if average_movement < 0.35:
        reasons.append("Low vehicle movement")

    if waterlogging:
        reasons.append("Waterlogging")

    if road_obstruction:
        reasons.append("Road obstruction")

    if accident:
        reasons.append("Possible accident")

    if pedestrian_activity:
        reasons.append("High pedestrian crossing activity")

    # -------------------------------
    # Default
    # -------------------------------

    if not reasons:
        reasons.append("No significant cause detected")

    return {
        "traffic_level": traffic_level,
        "reasons": reasons
    }