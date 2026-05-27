"""ROS2 node that converts LiDAR scans into velocity commands."""

from __future__ import annotations

import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

from obstacle_avoidance.avoidance_logic import (
    AvoidanceConfig,
    ScanSummary,
    choose_motion,
    summarize_scan,
)


class ObstacleAvoidanceNode(Node):
    """Subscribe to LaserScan data and publish reactive Twist commands."""

    def __init__(self) -> None:
        super().__init__("obstacle_avoidance_node")

        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("obstacle_distance", 0.55)
        self.declare_parameter("caution_distance", 0.85)
        self.declare_parameter("forward_speed", 0.20)
        self.declare_parameter("slow_speed", 0.08)
        self.declare_parameter("turn_speed", 0.65)
        self.declare_parameter("front_window_degrees", 60.0)
        self.declare_parameter("scan_timeout_seconds", 1.0)

        self.config = AvoidanceConfig(
            obstacle_distance=self.get_parameter("obstacle_distance").value,
            caution_distance=self.get_parameter("caution_distance").value,
            forward_speed=self.get_parameter("forward_speed").value,
            slow_speed=self.get_parameter("slow_speed").value,
            turn_speed=self.get_parameter("turn_speed").value,
            front_window_degrees=self.get_parameter("front_window_degrees").value,
        )

        self.scan_timeout_seconds = float(
            self.get_parameter("scan_timeout_seconds").value
        )
        self.last_scan_time = None
        self.last_state = None

        scan_topic = self.get_parameter("scan_topic").value
        cmd_vel_topic = self.get_parameter("cmd_vel_topic").value

        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.scan_sub = self.create_subscription(
            LaserScan,
            scan_topic,
            self.scan_callback,
            10,
        )
        self.watchdog_timer = self.create_timer(0.2, self.stop_if_scan_stale)

        self.get_logger().info(
            f"Obstacle avoidance ready: scan={scan_topic}, cmd_vel={cmd_vel_topic}"
        )

    def scan_callback(self, scan: LaserScan) -> None:
        """Process a LiDAR scan and publish the selected motion command."""

        self.last_scan_time = self.get_clock().now()

        summary = summarize_scan(
            scan.ranges,
            scan.angle_min,
            scan.angle_increment,
            scan.range_min,
            scan.range_max if scan.range_max > 0.0 else math.inf,
            self.config,
        )
        command = choose_motion(summary, self.config)

        self.publish_twist(command.linear_x, command.angular_z)
        self.log_state_change(command.state, summary)

    def publish_twist(self, linear_x: float, angular_z: float) -> None:
        """Publish a Twist command."""

        twist = Twist()
        twist.linear.x = float(linear_x)
        twist.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(twist)

    def stop_if_scan_stale(self) -> None:
        """Stop the robot if scan data stops arriving."""

        if self.last_scan_time is None:
            return

        elapsed = (self.get_clock().now() - self.last_scan_time).nanoseconds / 1e9
        if elapsed <= self.scan_timeout_seconds:
            return

        self.publish_twist(0.0, 0.0)
        if self.last_state != "scan_timeout":
            self.get_logger().warn("No recent /scan data; publishing stop command.")
            self.last_state = "scan_timeout"

    def log_state_change(self, state: str, summary: ScanSummary) -> None:
        """Log control state changes without flooding the terminal."""

        if state == self.last_state:
            return

        self.get_logger().info(
            "state=%s front=%.2f left=%.2f right=%.2f"
            % (state, summary.front, summary.left, summary.right)
        )
        self.last_state = state


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_twist(0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

