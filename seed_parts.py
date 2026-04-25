#!/usr/bin/env python3
"""
One-time script to populate the parts database with Yamaha XMAX 400 parts.
Run once after initial setup: python seed_parts.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database_manager import ScooterDB

XMAX_400_PARTS = [
    # (Part_Number, Description, Category, Price_Euro, Image_URL)
    ("B6T-E3440-00", "V-Belt (Transmission)", "Drivetrain", 52.00, "No Image"),
    ("B6T-E3450-00", "Clutch Weight Set (18g)", "Drivetrain", 38.00, "No Image"),
    ("B6T-13440-00", "Air Filter Element", "Engine", 22.00, "No Image"),
    ("B6T-13441-00", "Air Filter Element (Secondary)", "Engine", 18.00, "No Image"),
    ("5VU-13440-20", "Air Filter OEM", "Engine", 25.00, "No Image"),
    ("B6T-E3560-00", "Oil Filter Element", "Engine", 8.50, "No Image"),
    ("90445-10126", "Oil Drain Bolt Washer", "Engine", 1.20, "No Image"),
    ("B6T-E4621-00", "Front Brake Pads Set", "Brakes", 28.00, "No Image"),
    ("B6T-F5805-00", "Rear Brake Pads Set", "Brakes", 24.00, "No Image"),
    ("90890-01294", "Front Brake Disc", "Brakes", 65.00, "No Image"),
    ("B6T-25806-00", "Rear Brake Disc", "Brakes", 58.00, "No Image"),
    ("NGK-CR7E-00", "Spark Plug NGK CR7E", "Electrical", 6.50, "No Image"),
    ("YTZ10S-BS-00", "Battery YTZ10S 12V 8.6Ah", "Electrical", 72.00, "No Image"),
    ("B6T-84710-00", "Headlight Assembly LED", "Electrical", 185.00, "No Image"),
    ("B6T-F3806-00", "Brake Light Switch", "Electrical", 11.00, "No Image"),
    ("B6T-82519-00", "Turn Signal Bulb 12V 10W", "Electrical", 2.50, "No Image"),
    ("B6T-E2210-00", "Engine Oil Seal Set", "Engine", 15.00, "No Image"),
    ("B6T-11601-00", "Piston Ring Set", "Engine", 42.00, "No Image"),
    ("B6T-12453-00", "Cylinder Head Gasket", "Engine", 19.00, "No Image"),
    ("B6T-E3540-00", "Transmission Oil Seal", "Drivetrain", 7.50, "No Image"),
    ("B6T-2510W-00", "Front Fork Oil Seal Kit", "Suspension", 32.00, "No Image"),
    ("B6T-23350-00", "Front Fork Spring", "Suspension", 45.00, "No Image"),
    ("B6T-22110-00", "Rear Shock Absorber", "Suspension", 125.00, "No Image"),
    ("B6T-14591-00", "Coolant Reservoir Hose", "Cooling", 12.00, "No Image"),
    ("B6T-12459-00", "Thermostat", "Cooling", 38.00, "No Image"),
    ("B6T-12461-00", "Thermostat Gasket", "Cooling", 5.50, "No Image"),
    ("B6T-14720-00", "Radiator Cap", "Cooling", 9.00, "No Image"),
    ("B6T-27411-00", "Front Wheel Bearing Set", "Wheels", 22.00, "No Image"),
    ("B6T-25380-00", "Rear Wheel Bearing Set", "Wheels", 28.00, "No Image"),
    ("3FA-F4181-00", "Air Valve Cap Set (4pcs)", "Wheels", 3.50, "No Image"),
]


def main():
    print(f"Connecting to database: {config.DB_PATH}")
    db = ScooterDB(config.DB_PATH, config.DATA_FILE)
    try:
        db.seed_parts(XMAX_400_PARTS)
        print(f"Done. Seeded {len(XMAX_400_PARTS)} parts.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
