#!/usr/bin/env python3
"""
Quick start script for Blissful Abodes Hotel Booking System
"""

import os
import sys
from app import app, init_db


def main():
    # Environment variables are no longer used
    # Application uses hardcoded defaults

    print("\n" + "=" * 60)
    print("BLISSFUL ABODES - Hotel Booking System")
    print("=" * 60)
    print("\nStarting server...")

    # Initialize database
    print("Initializing database...")
    init_db()

    print("\n" + "-" * 60)
    print("SERVER IS READY!")
    print("-" * 60)
    print(f"\n🌐 Website URL: http://localhost:5000")
    print("\n👤 TEST ACCOUNTS:")
    print("   Guest:  guest@example.com / password123")
    print("   Staff:  staff@example.com / password123")
    print("   Admin:  admin@example.com / password123")
    print("\n📋 FEATURES:")
    print("   • Home page with room browsing")
    print("   • User registration and login")
    print("   • Room booking system")
    print("   • Guest dashboard")
    print("   • Staff dashboard")
    print("   • Admin dashboard")
    print("   • Real-time notifications")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
