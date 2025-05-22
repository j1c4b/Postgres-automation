#!/usr/bin/env python3
"""
PostgreSQL Docker Container Manager

This script automates starting, stopping, and restarting a PostgreSQL
Docker container.
"""

import subprocess
import argparse
import sys
import time

class PostgresDockerManager:
    def __init__(self, container_name="jacob_postgres"):
        """Initialize the manager with the container name."""
        # Store the container name for later use in all methods
        self.container_name = container_name
        print(f"PostgreSQL Docker Manager initialized for container: {self.container_name}")

    def get_container_logs(self, lines=5):
        try:
            result = subprocess.check_output(
                ['docker', 'logs', '--tail', str(lines), self.container_name],
                stderr=subprocess.STDOUT
            ).decode()
            return result
        except subprocess.CalledProcessError:
            return "Error retrieving logs."
        

    def get_health_status(self):
        """Get the health status of the PostgreSQL container."""
        try:
            result = subprocess.check_output(
                ['docker', 'inspect', '--format', '{{.State.Health.Status}}', self.container_name],
                stderr=subprocess.STDOUT
            ).decode().strip()
            return result
        except subprocess.CalledProcessError:
            return None

    
    def get_container_status(self):
        """Get the current status of the container."""
        status = None  # Initialize status to ensure it's accessible outside the try block
        try:
            # Run docker ps command to list containers with name filter
            # -a flag shows all containers (including stopped ones)
            # --filter filters by container name
            # --format extracts only the Status field from output
            result = subprocess.run(
                # ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.State.Status}}"],
                ['docker', 'inspect', '--format', '{{.State.Status}}', "jacob_postgres"],
                capture_output=True,  # Capture stdout and stderr
                text=True,            # Return strings rather than bytes
                check=True            # Raise exception if command fails
            )
            
            # Remove any whitespace from the result
            status = result.stdout.strip()

        except subprocess.CalledProcessError as e:
        # Handle any errors that occur when running the docker command
            print(f"Error checking container status: {e}")
            return "error"

    # Determine container state based on the command output
        if not status:
            return "not_found"  # Empty result means no container with this name
        elif status == "running":
            # Check if the container is healthy
            health_status = self.get_health_status()
            if health_status == "healthy":
                return "running and healthy"  # "Up X minutes/hours" means container is running and healthy
            elif health_status == "unhealthy":
                return "unhealthy" # Container is running but unhealthy
        else:
            return "stopped"  # Any other status (like "Exited") means stopped

    def start(self):
        """Start the PostgreSQL container."""
        # First check the current status of the container
        status = self.get_container_status()

        # Handle different container states
        if status == "not_found":
            # Can't start a container that doesn't exist
            print(f"Container '{self.container_name}' not found.Please create it first.")
            return False
        elif status == "running and healthy":
            # No need to start if it's already running
            print(f"Container '{self.container_name}' is already running and healthy")
            print(f"Container '{self.container_name}' not found. Please create it first.")
        try:
            # Container exists but is stopped, so we can start it
            print(f"Starting container '{self.container_name}'...")
            # Execute docker start command
            subprocess.run(["docker", "start", self.container_name], check=True)
            print(f"Container '{self.container_name}' started successfully.")
            return True
        except subprocess.CalledProcessError as e:
            # Handle any errors during the start process
            print(f"Failed to start container: {e}")
            return False

    def stop(self):
        """Stop the PostgreSQL container."""
        # First check the current status of the container
        status = self.get_container_status()

        # Handle different container states
        if status == "not_found":
            # Can't stop a container that doesn't exist
            print(f"Container '{self.container_name}' not found.")
            return False
        elif status == "stopped":
            # No need to stop if it's already stopped
            print(f"Container '{self.container_name}' is already stopped.")
            return True

        try:
            # Container is running, so we can stop it
            print(f"Stopping container '{self.container_name}'...")
            # Execute docker stop command
            subprocess.run(["docker", "stop", self.container_name], check=True)
            print(f"Container '{self.container_name}' stopped successfully.")
            return True
        except subprocess.CalledProcessError as e:
            # Handle any errors during the stop process
            print(f"Failed to stop container: {e}")
            return False

    def restart(self):
        """Restart the PostgreSQL container."""
        # First check the current status of the container
        status = self.get_container_status()

        if status == "not_found":
            # Can't restart a container that doesn't exist
            print(f"Container '{self.container_name}' not found.Please create it first.")
            return False

        try:
            # Container exists (either running or stopped), so we can restart it
            # Docker restart will start a stopped container or restarta running one
            print(f"Restarting container '{self.container_name}'...")
            # Execute docker restart command
            subprocess.run(["docker", "restart", self.container_name],check=True)
            print(f"Container '{self.container_name}' restarted successfully.")
            return True
        except subprocess.CalledProcessError as e:
            # Handle any errors during the restart process
            print(f"Failed to restart container: {e}")
            return False

    def show_status(self):
        """Display detailed status of the container."""
        # First check the current status of the container
        status = self.get_container_status()

        if status == "not_found":
            # Can't show details of a container that doesn't exist
            print(f"Container '{self.container_name}' not found.")
            return

        try:
            # Container exists, so gather detailed information

            # Get detailed container information using docker inspect
            container_info = subprocess.run(
                ["docker", "inspect", self.container_name],
                capture_output=True,
                text=True,
                check=True
            )

            # Get process status and port information
            ps_info = subprocess.run(
                ["docker", "ps", "-a", "--filter",f"name={self.container_name}", "--format", "{{.Status}} |{{.Ports}}"],
                capture_output=True,
                text=True,
                check=True
            )

            # Display basic status information
            print(f"Container '{self.container_name}' status:")
            print(f"State: {status.upper()}")
            print(f"Details: {ps_info.stdout.strip()}")

            # If the container is running and healthy, show recent logs to helpwith troubleshooting
            if status == "running and healthy":
                try:
                    # Get the last 5 lines from the container logs
                    logs = self.get_container_logs(10)

                    print("\nRecent logs:")
                    print(logs)
                except subprocess.CalledProcessError:
                    # Silently ignore errors when fetching logs
                    pass

        except subprocess.CalledProcessError as e:
            # Handle any errors during status retrieval
            print(f"Error retrieving container details: {e}")

def main():
    # Create argument parser for command line arguments
    parser = argparse.ArgumentParser(description="Manage PostgreSQLDocker Container")

    # Define the required action argument with choices
    parser.add_argument("action", choices=["start", "stop", "restart","status"],
                        help="Action to perform on the PostgreSQL container")

    # Define optional container name argument
    parser.add_argument("--name", default="jacob_postgres",
                        help="The name of the PostgreSQL container(default: postgres)")

    # Parse the command line arguments
    args = parser.parse_args()

    # Create an instance of the manager with the specified container name
    manager = PostgresDockerManager(container_name=args.name)

    # Execute the requested action
    if args.action == "start":
        manager.start()
    elif args.action == "stop":
        manager.stop()
    elif args.action == "restart":
        manager.restart()
    elif args.action == "status":
        manager.show_status()

if __name__ == "__main__":
    main()
