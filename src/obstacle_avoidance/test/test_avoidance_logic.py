import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from obstacle_avoidance.avoidance_logic import (  # noqa: E402
    AvoidanceConfig,
    ScanSummary,
    choose_motion,
    sector_min_distance,
)


def test_clear_path_moves_forward():
    config = AvoidanceConfig()
    command = choose_motion(ScanSummary(front=2.0, left=2.0, right=2.0), config)

    assert command.state == "clear"
    assert command.linear_x == config.forward_speed
    assert command.angular_z == 0.0


def test_front_obstacle_turns_toward_more_open_side():
    config = AvoidanceConfig()
    command = choose_motion(ScanSummary(front=0.3, left=1.5, right=0.7), config)

    assert command.state == "turn_left"
    assert command.linear_x == 0.0
    assert command.angular_z > 0.0


def test_caution_distance_slows_and_steers():
    config = AvoidanceConfig(caution_distance=1.0, obstacle_distance=0.4)
    command = choose_motion(ScanSummary(front=0.75, left=0.6, right=1.4), config)

    assert command.state == "caution_right"
    assert command.linear_x == config.slow_speed
    assert command.angular_z < 0.0


def test_sector_min_distance_handles_wrapped_scan_angles():
    ranges = [1.2, 0.4, 2.0, 3.0]
    angle_min = math.radians(315.0)
    angle_increment = math.radians(15.0)

    distance = sector_min_distance(
        ranges,
        angle_min,
        angle_increment,
        math.radians(-30.0),
        math.radians(15.0),
    )

    assert distance == 0.4

