"""Pure Python LiDAR processing and reactive obstacle avoidance logic."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, NamedTuple


class MotionCommand(NamedTuple):
    """A small ROS-independent representation of a velocity command."""

    linear_x: float
    angular_z: float
    state: str


class ScanSummary(NamedTuple):
    """Minimum distances in the sectors used by the reactive controller."""

    front: float
    left: float
    right: float


@dataclass(frozen=True)
class AvoidanceConfig:
    """Tunable values for reactive obstacle avoidance."""

    obstacle_distance: float = 0.55
    caution_distance: float = 0.85
    forward_speed: float = 0.20
    slow_speed: float = 0.08
    turn_speed: float = 0.65
    front_window_degrees: float = 60.0


def normalize_angle(angle: float) -> float:
    """Normalize an angle to the range [-pi, pi]."""

    return math.atan2(math.sin(angle), math.cos(angle))


def angle_in_window(angle: float, start_angle: float, end_angle: float) -> bool:
    """Return True if angle is inside a possibly wrapped angular window."""

    epsilon = 1e-12
    angle = normalize_angle(angle)
    start_angle = normalize_angle(start_angle)
    end_angle = normalize_angle(end_angle)

    if start_angle <= end_angle:
        return start_angle - epsilon <= angle <= end_angle + epsilon

    return angle >= start_angle - epsilon or angle <= end_angle + epsilon


def valid_distance(
    reading: float,
    range_min: float = 0.0,
    range_max: float = math.inf,
) -> float | None:
    """Return a usable LiDAR distance or None if the reading is invalid."""

    if not math.isfinite(reading):
        return None
    if reading < range_min:
        return None
    if math.isfinite(range_max) and reading > range_max:
        return None
    return reading


def sector_min_distance(
    ranges: Iterable[float],
    angle_min: float,
    angle_increment: float,
    start_angle: float,
    end_angle: float,
    range_min: float = 0.0,
    range_max: float = math.inf,
) -> float:
    """Find the nearest valid obstacle inside an angular sector."""

    distances = []

    for index, reading in enumerate(ranges):
        angle = angle_min + index * angle_increment

        if not angle_in_window(angle, start_angle, end_angle):
            continue

        distance = valid_distance(reading, range_min, range_max)
        if distance is not None:
            distances.append(distance)

    if not distances:
        return math.inf

    return min(distances)


def summarize_scan(
    ranges: Iterable[float],
    angle_min: float,
    angle_increment: float,
    range_min: float,
    range_max: float,
    config: AvoidanceConfig,
) -> ScanSummary:
    """Extract the front, left, and right distances used by the controller."""

    ranges = list(ranges)
    half_front = math.radians(config.front_window_degrees / 2.0)

    front = sector_min_distance(
        ranges,
        angle_min,
        angle_increment,
        -half_front,
        half_front,
        range_min,
        range_max,
    )
    left = sector_min_distance(
        ranges,
        angle_min,
        angle_increment,
        half_front,
        math.radians(90.0),
        range_min,
        range_max,
    )
    right = sector_min_distance(
        ranges,
        angle_min,
        angle_increment,
        math.radians(-90.0),
        -half_front,
        range_min,
        range_max,
    )

    return ScanSummary(front=front, left=left, right=right)


def choose_motion(summary: ScanSummary, config: AvoidanceConfig) -> MotionCommand:
    """Choose a velocity command from nearby obstacle distances."""

    turn_left = summary.left >= summary.right

    if summary.front < config.obstacle_distance:
        angular_z = config.turn_speed if turn_left else -config.turn_speed
        state = "turn_left" if turn_left else "turn_right"
        return MotionCommand(linear_x=0.0, angular_z=angular_z, state=state)

    if summary.front < config.caution_distance:
        angular_z = config.turn_speed * 0.45 if turn_left else -config.turn_speed * 0.45
        state = "caution_left" if turn_left else "caution_right"
        return MotionCommand(
            linear_x=config.slow_speed,
            angular_z=angular_z,
            state=state,
        )

    return MotionCommand(linear_x=config.forward_speed, angular_z=0.0, state="clear")
