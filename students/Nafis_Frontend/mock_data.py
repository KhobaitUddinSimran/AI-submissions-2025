# mock_data.py
import time


def generate_mock_tick(
    tick_count: int,
    start_time: float,
    initial_temp_f: float,
    drift_rate_f: float,
    high_threshold_f: float,
    low_threshold_f: float,
):
    """
    Generates one deterministic mock sensor reading (Fahrenheit).
    Designed for SCADA-style demos with realistic state transitions.
    """

    current_time = time.time()
    simulation_time = current_time - start_time

    # -------------------------------------------------
    # 1. TEMPERATURE MODEL (REALISTIC & DEMO-FRIENDLY)
    # -------------------------------------------------

    # Phase 1: Warm-up (0–10 sec)
    if simulation_time <= 10:
        temperature = initial_temp_f + (simulation_time * 1.2)

    # Phase 2: Normal operation (10–40 sec)
    elif simulation_time <= 40:
        temperature = initial_temp_f + 12 + ((simulation_time - 10) * 0.05)

    # Phase 3: Degradation drift (after 40 sec)
    else:
        temperature = (
            initial_temp_f
            + 12
            + (30 * 0.05)
            + ((simulation_time - 40) * drift_rate_f)
        )

    temperature = round(temperature, 2)

    # -------------------------------------------------
    # 2. STATE LOGIC (FIXED & REALISTIC)
    # -------------------------------------------------

    if temperature >= high_threshold_f + 10:
        state = "CRITICAL"
    elif temperature >= high_threshold_f:
        state = "ALERT_HIGH"
    elif temperature <= low_threshold_f:
        state = "ALERT_LOW"
    else:
        state = "NORMAL"

    # -------------------------------------------------
    # 3. RETURN SCHEMA (LOCKED & CONSISTENT)
    # -------------------------------------------------

    return {
        "timestamp": current_time,
        "simulation_time": round(simulation_time, 1),
        "temperature_f": temperature,
        "state": state
    }
