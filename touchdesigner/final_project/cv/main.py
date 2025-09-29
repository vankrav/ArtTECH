#!/usr/bin/env python3
"""
ArUco Marker Position Detector
Real-time detection of ArUco markers with position and orientation estimation
"""

import cv2
import numpy as np
import sys
import time

class ArucoDetector:
    def __init__(self, camera_id=0, marker_size=0.05):
        """
        Initialize the ArUco detector

        Args:
            camera_id (int): Camera device ID
            marker_size (float): Size of the marker in meters
        """
        # ArUco dictionary and detector parameters
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()

        # Camera setup
        self.camera_id = camera_id
        self.cap = None

        # Marker size (side length in meters)
        self.marker_size = marker_size

        # Camera matrix and distortion coefficients (you may need to calibrate your camera)
        # These are placeholder values - replace with your camera's calibrated values
        self.camera_matrix = np.array([
            [800, 0, 320],
            [0, 800, 240],
            [0, 0, 1]
        ], dtype=np.float32)

        self.dist_coeffs = np.zeros((4, 1), dtype=np.float32)

        # Colors for visualization
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'purple': (255, 0, 255),
            'cyan': (255, 255, 0)
        }

    def initialize_camera(self):
        """Initialize the camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera {self.camera_id}")

            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            print(f"Camera initialized successfully (ID: {self.camera_id})")
            return True

        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False

    def detect_markers(self, frame):
        """
        Detect ArUco markers in the frame

        Args:
            frame: Input image frame

        Returns:
            tuple: (corners, ids, rejected) - detected marker corners, IDs, and rejected candidates
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.parameters
        )

        return corners, ids, rejected

    def estimate_pose(self, corners, ids):
        """
        Estimate pose of detected markers

        Args:
            corners: Detected marker corners
            ids: Marker IDs

        Returns:
            tuple: (rvecs, tvecs) - rotation and translation vectors
        """
        if ids is None or len(ids) == 0:
            return None, None

        # Estimate pose for each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, self.marker_size, self.camera_matrix, self.dist_coeffs
        )

        return rvecs, tvecs

    def draw_markers(self, frame, corners, ids, rvecs, tvecs):
        """
        Draw detected markers and pose information on the frame

        Args:
            frame: Input/output frame
            corners: Marker corners
            ids: Marker IDs
            rvecs: Rotation vectors
            tvecs: Translation vectors
        """
        if ids is None or len(ids) == 0:
            return frame

        # Draw detected markers
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Draw pose information for each marker
        for i in range(len(ids)):
            # Get color for this marker (cycle through colors)
            color_idx = ids[i][0] % len(self.colors)
            color_name = list(self.colors.keys())[color_idx]
            color = self.colors[color_name]

            # Draw coordinate axes
            cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs,
                            rvecs[i], tvecs[i], self.marker_size * 0.5)

            # Draw marker ID
            corner = corners[i][0]
            center_x = int(np.mean(corner[:, 0]))
            center_y = int(np.mean(corner[:, 1]))

            cv2.putText(frame, f"ID: {ids[i][0]}", (center_x - 30, center_y - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw position information
            position_text = f"X: {tvecs[i][0][0]:.2f} Y: {tvecs[i][0][1]:.2f} Z: {tvecs[i][0][2]:.2f}"
            cv2.putText(frame, position_text, (center_x - 50, center_y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        return frame

    def print_marker_info(self, corners, ids, rvecs, tvecs):
        """
        Print detailed information about detected markers

        Args:
            corners: Marker corners
            ids: Marker IDs
            rvecs: Rotation vectors
            tvecs: Translation vectors
        """
        if ids is None or len(ids) == 0:
            print("No markers detected")
            return

        print(f"\n=== Detected {len(ids)} markers ===")
        for i in range(len(ids)):
            marker_id = ids[i][0]
            tvec = tvecs[i][0]
            rvec = rvecs[i][0]

            print(f"Marker ID: {marker_id}")
            print(f"  Position (X, Y, Z): {tvec[0]:.3f}, {tvec[1]:.3f}, {tvec[2]:.3f}")
            print(f"  Rotation (rX, rY, rZ): {rvec[0]:.3f}, {rvec[1]:.3f}, {rvec[2]:.3f}")

            # Calculate distance from camera
            distance = np.linalg.norm(tvec)
            print(f"  Distance from camera: {distance:.3f} meters")

    def run(self):
        """Main detection loop"""
        if not self.initialize_camera():
            return

        print("Starting ArUco marker detection...")
        print("Press 'q' to quit, 'p' to print marker info")

        try:
            frame_count = 0
            consecutive_failures = 0
            max_consecutive_failures = 10

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    consecutive_failures += 1
                    print(f"Failed to grab frame (attempt {consecutive_failures}/{max_consecutive_failures})")

                    if consecutive_failures >= max_consecutive_failures:
                        print("❌ Too many consecutive frame grab failures. Checking camera...")
                        self.diagnose_camera()
                        print("💡 Try restarting the camera or check camera permissions")
                        break

                    # Wait a bit before retrying
                    cv2.waitKey(100)
                    continue

                # Reset failure counter on successful frame grab
                consecutive_failures = 0
                frame_count += 1

                # Detect markers
                corners, ids, rejected = self.detect_markers(frame)

                # Estimate pose
                rvecs, tvecs = self.estimate_pose(corners, ids)

                # Draw results on frame
                frame = self.draw_markers(frame, corners, ids, rvecs, tvecs)

                # Display frame
                cv2.imshow('ArUco Marker Detection', frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    self.print_marker_info(corners, ids, rvecs, tvecs)

        except KeyboardInterrupt:
            print("\nDetection stopped by user")

        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()

    def diagnose_camera(self):
        """
        Diagnose camera issues
        """
        print("\n🔍 Camera Diagnostics:")
        print("-" * 30)

        # Check if camera object exists
        if self.cap is None:
            print("❌ Camera object is None")
            return

        # Check if camera is opened
        if not self.cap.isOpened():
            print("❌ Camera is not opened")
            print("💡 Try:")
            print("   - Restarting the application")
            print("   - Checking camera permissions")
            print("   - Testing with different camera ID")
            return

        # Try to get camera properties
        try:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)

            print(f"📊 Camera properties:")
            print(f"   - Width: {width}")
            print(f"   - Height: {height}")
            print(f"   - FPS: {fps}")

            if width == 0 or height == 0:
                print("❌ Camera properties are invalid")
                print("💡 This might indicate camera driver issues")

        except Exception as e:
            print(f"❌ Error getting camera properties: {e}")

        # Test available camera IDs
        print("
🔎 Checking available cameras:")
        for i in range(5):
            try:
                test_cap = cv2.VideoCapture(i)
                if test_cap.isOpened():
                    print(f"   ✅ Camera {i}: Available")
                    test_cap.release()
                else:
                    print(f"   ❌ Camera {i}: Not available")
            except:
                print(f"   ❌ Camera {i}: Error")
                break

        print("
💡 Troubleshooting tips:")
        print("   1. Close other applications using the camera")
        print("   2. Try a different camera ID (0, 1, 2, etc.)")
        print("   3. Check camera permissions in System Preferences")
        print("   4. Restart your computer")
        print("   5. Try an external camera if using built-in")

def main():
    """Main function"""
    detector = ArucoDetector(camera_id=0)
    detector.run()

if __name__ == "__main__":
    main()
