# Architecture Notes

## Data Flow

```text
LaserScan message
    |
    v
Sector extraction
    |
    v
Minimum front, left, and right distances
    |
    v
Reactive controller
    |
    v
Twist velocity command
```

The ROS2 node is intentionally thin. It reads parameters, subscribes to
`sensor_msgs/LaserScan`, calls pure Python control logic, then publishes
`geometry_msgs/Twist`.

## Why Separate The Logic?

`avoidance_logic.py` does not import ROS. This makes the robot behavior easy to
unit test and easy to explain in an interview. The ROS node handles integration;
the logic module handles decisions.

## LiDAR Sectors

The controller divides the scan into three angular sectors:

| Sector | Default angle range | Used for |
| --- | --- | --- |
| Front | -30 to +30 degrees | Stop or slow down near obstacles |
| Left | +30 to +90 degrees | Choose turn direction |
| Right | -90 to -30 degrees | Choose turn direction |

Angles are normalized to `[-pi, pi]`, so scans that report angles from `0` to
`2*pi` still work.

## Control States

| State | Meaning |
| --- | --- |
| `clear` | Move forward normally |
| `caution_left` | Slow forward motion and steer left |
| `caution_right` | Slow forward motion and steer right |
| `turn_left` | Stop forward motion and rotate left |
| `turn_right` | Stop forward motion and rotate right |

This is reactive navigation, not full path planning. It is a strong first step
because it teaches sensor processing, control outputs, and real-time debugging.

