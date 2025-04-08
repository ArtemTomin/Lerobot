#!/usr/bin/env python3
"""
SO100 Robot Follower Arm Direct Controller

This script directly controls the SO100 follower arm using the most basic approach.
"""

import time
import os
import sys
import numpy as np
from pathlib import Path

from lerobot.common.robot_devices.robots.utils import make_robot_from_config
from lerobot.common.robot_devices.robots.configs import So100RobotConfig

def main():
    # Initialize robot config
    robot_config = So100RobotConfig()
    
    # Empty the leader_arms dict to prevent connection attempts
    robot_config.leader_arms = {}
    
    # Set specific port for the follower arm
    follower_port = '/dev/tty.usbmodem58FA0819211'
    
    # Update the port in the follower arm config
    if 'main' in robot_config.follower_arms:
        robot_config.follower_arms['main'].port = follower_port
    
    print("Creating robot object...")
    robot = make_robot_from_config(robot_config)
    
    print("Connecting to robot...")
    if not robot.is_connected:
        robot.connect()
        
    print("Robot connected successfully!")
    
    # Get access to the motor bus directly
    motor_bus = robot.follower_arms["main"]
    
    # Set up parameters
    joint_names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
    joint_positions = {}
    
    # Get initial positions
    print("\nReading initial positions...")
    for joint in joint_names:
        try:
            pos = motor_bus.read("Present_Position", joint)
            if isinstance(pos, np.ndarray):
                if pos.size > 0:
                    joint_positions[joint] = float(pos.item())
                else:
                    joint_positions[joint] = 0.0
            else:
                joint_positions[joint] = float(pos)
            print(f"{joint}: {joint_positions[joint]}")
        except Exception as e:
            print(f"Error reading {joint}: {str(e)}")
            joint_positions[joint] = 0.0
    
    # Menu system
    step_size = 300.0
    selected_joint = joint_names[0]
    
    print("\nSimple Joint Controller")
    print("======================")
    print("Commands:")
    print("  j NUMBER - select joint (1-6)")
    print("  + - move current joint up/forward")
    print("  - - move current joint down/backward")
    print("  s NUMBER - set step size")
    print("  r - read all positions")
    print("  q - quit")
    
    try:
        while True:
            print(f"\nSelected joint: {selected_joint}")
            print(f"Current position: {joint_positions[selected_joint]}")
            print(f"Step size: {step_size}")
            
            # Get command
            cmd = input("Enter command (j/+/-/s/r/q): ").strip().lower()
            
            if cmd == 'q':
                break
                
            elif cmd.startswith('j'):
                try:
                    parts = cmd.split()
                    if len(parts) > 1:
                        idx = int(parts[1]) - 1
                        if 0 <= idx < len(joint_names):
                            selected_joint = joint_names[idx]
                            print(f"Selected joint: {selected_joint}")
                        else:
                            print(f"Invalid joint number. Use 1-{len(joint_names)}")
                    else:
                        print("Usage: j NUMBER")
                except ValueError:
                    print("Invalid joint number format")
                    
            elif cmd == '+':
                try:
                    current_pos = joint_positions[selected_joint]
                    target_pos = current_pos + step_size
                    print(f"Moving {selected_joint} from {current_pos} to {target_pos}")
                    
                    # Send the move command
                    motor_bus.write("Goal_Position", target_pos, selected_joint)
                    print("Command sent. Waiting...")
                    
                    time.sleep(0.5)  # Wait for movement
                    
                    # Read new position
                    pos = motor_bus.read("Present_Position", selected_joint)
                    if isinstance(pos, np.ndarray):
                        if pos.size > 0:
                            joint_positions[selected_joint] = float(pos.item())
                        else:
                            joint_positions[selected_joint] = 0.0
                    else:
                        joint_positions[selected_joint] = float(pos)
                    
                    print(f"New position: {joint_positions[selected_joint]}")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif cmd == '-':
                try:
                    current_pos = joint_positions[selected_joint]
                    target_pos = current_pos - step_size
                    print(f"Moving {selected_joint} from {current_pos} to {target_pos}")
                    
                    # Send the move command
                    motor_bus.write("Goal_Position", target_pos, selected_joint)
                    print("Command sent. Waiting...")
                    
                    time.sleep(0.5)  # Wait for movement
                    
                    # Read new position
                    pos = motor_bus.read("Present_Position", selected_joint)
                    if isinstance(pos, np.ndarray):
                        if pos.size > 0:
                            joint_positions[selected_joint] = float(pos.item())
                        else:
                            joint_positions[selected_joint] = 0.0
                    else:
                        joint_positions[selected_joint] = float(pos)
                    
                    print(f"New position: {joint_positions[selected_joint]}")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif cmd.startswith('s'):
                try:
                    parts = cmd.split()
                    if len(parts) > 1:
                        new_step = float(parts[1])
                        if new_step > 0:
                            step_size = new_step
                            print(f"Step size set to {step_size}")
                        else:
                            print("Step size must be positive")
                    else:
                        print("Usage: s NUMBER")
                except ValueError:
                    print("Invalid step size format")
                    
            elif cmd == 'r':
                print("\nReading all positions...")
                for joint in joint_names:
                    try:
                        pos = motor_bus.read("Present_Position", joint)
                        if isinstance(pos, np.ndarray):
                            if pos.size > 0:
                                joint_positions[joint] = float(pos.item())
                            else:
                                joint_positions[joint] = 0.0
                        else:
                            joint_positions[joint] = float(pos)
                        print(f"{joint}: {joint_positions[joint]}")
                    except Exception as e:
                        print(f"Error reading {joint}: {str(e)}")
                        
            else:
                print("Unknown command")
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        
    finally:
        # Disconnect the robot
        if robot.is_connected:
            print("Disconnecting robot...")
            robot.disconnect()
            print("Robot disconnected")

if __name__ == "__main__":
    main() 