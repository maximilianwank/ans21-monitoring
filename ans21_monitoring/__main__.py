import time
import sys
import logging
from ans21_monitoring.camera import take_picture
from ans21_monitoring.image_analysis import count_bright_spots


def main():
    """
    Main loop for monitoring bright spots.
    Takes a picture every 5 seconds and prints the count.
    """
    print("Starting monitoring process... Press Ctrl+C to stop.")

    try:
        while True:
            try:
                # Capture image
                image = take_picture()

                # Analyze image
                count = count_bright_spots(image)

                # Output result
                print(f"Bright spots detected: {count}")

            except Exception as e:
                print(f"Error: {e}")

            # Wait for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")


if __name__ == "__main__":
    main()
