"""
Reset and Repopulate Rooms with Images
This script clears existing rooms and creates new ones with proper image assignments
"""

from db import mock_rooms, add_room
from populate_rooms import populate_rooms

def reset_rooms():
    """Clear existing rooms and repopulate with images"""

    print("\n" + "="*80)
    print("RESETTING ROOM DATABASE")
    print("="*80 + "\n")

    # Show current state
    print(f"Current rooms in database: {len(mock_rooms)}")

    if len(mock_rooms) == 0:
        print("✓ Database is already empty. Proceeding with population...\n")
    else:
        # Clear all rooms
        print(f"\n🗑️  Clearing {len(mock_rooms)} existing rooms...")
        mock_rooms.clear()
        print("✓ All rooms cleared!\n")

    # Repopulate with new image assignments
    print("📥 Populating rooms with local images...\n")
    populate_rooms()

    # Verify results
    print("\n" + "="*80)
    print("RESET COMPLETE")
    print("="*80)
    print(f"✓ Total rooms in database: {len(mock_rooms)}")

    # Count rooms with images
    rooms_with_images = sum(1 for r in mock_rooms if r.get('image') and r['image'] != 'no-image')
    local_images = sum(1 for r in mock_rooms if r.get('image', '').startswith('/static'))

    print(f"✓ Rooms with images: {rooms_with_images}")
    print(f"✓ Using local images: {local_images}")

    if local_images > 0:
        print("\n🎉 SUCCESS! Rooms are now using local static images!")
    else:
        print("\n⚠️  WARNING: Rooms are not using local images. Check populate_rooms.py")

    print("\n" + "="*80 + "\n")

    # Show sample rooms
    print("Sample rooms with images:\n")

    room_types = ['single', 'double', 'family', 'couple', 'vip']
    for room_type in room_types:
        matching_rooms = [r for r in mock_rooms if r.get('room_type') == room_type]
        if matching_rooms:
            sample = matching_rooms[0]
            image_file = sample.get('image', 'no-image').split('/')[-1]
            print(f"  {room_type.capitalize():10} → {sample['name']:25} → {image_file}")

    print("\n✨ Ready to use! Start the app with: python run.py\n")

if __name__ == '__main__':
    reset_rooms()
