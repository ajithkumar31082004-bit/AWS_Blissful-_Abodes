"""
Show Room-to-Image Mapping
Displays which images are assigned to which rooms in the database
"""

from db import get_all_rooms
from collections import defaultdict

def show_room_images():
    """Display all rooms with their assigned images"""

    print("\n" + "="*80)
    print("ROOM IMAGE MAPPING VISUALIZATION")
    print("="*80 + "\n")

    # Get all rooms
    rooms = get_all_rooms()

    if not rooms:
        print("❌ No rooms found in database!")
        print("Run: python populate_rooms.py")
        return

    # Group rooms by type
    rooms_by_type = defaultdict(list)
    image_usage = defaultdict(int)

    for room in rooms:
        room_type = room.get('room_type', 'unknown')
        rooms_by_type[room_type].append(room)

        # Count image usage
        image = room.get('image', 'no-image')
        image_usage[image] += 1

    # Display by room type
    type_names = {
        'single': '🛏️  SINGLE BED ROOMS',
        'double': '🛏️🛏️  DOUBLE BED ROOMS',
        'family': '👨‍👩‍👧‍👦  FAMILY SUITES',
        'couple': '💑  COUPLE/ROMANTIC ROOMS',
        'vip': '👑  VIP/PRESIDENTIAL SUITES'
    }

    for room_type in ['single', 'double', 'family', 'couple', 'vip']:
        rooms_list = rooms_by_type.get(room_type, [])

        if not rooms_list:
            continue

        print(f"\n{type_names.get(room_type, room_type.upper())}")
        print("-" * 80)

        for idx, room in enumerate(rooms_list[:10], 1):  # Show first 10
            room_name = room.get('name', 'Unknown')
            image = room.get('image', 'no-image')
            price = room.get('price', 0)
            location = room.get('location', 'Unknown')

            # Extract just the filename
            if '/' in image:
                image_file = image.split('/')[-1]
            else:
                image_file = image

            print(f"{idx:2}. {room_name:25} → {image_file:20} ₹{price:>7,} | {location}")

        if len(rooms_list) > 10:
            print(f"    ... and {len(rooms_list) - 10} more rooms")

    # Display image usage statistics
    print("\n" + "="*80)
    print("IMAGE USAGE STATISTICS")
    print("="*80 + "\n")

    # Group by image type
    image_types = {
        '1bed': [],
        '2bed': [],
        'family': [],
        'couple': [],
        'vip': []
    }

    for image, count in sorted(image_usage.items()):
        if 'no-image' in image or 'default' in image:
            continue

        # Categorize
        for key in image_types.keys():
            if key in image:
                image_types[key].append((image, count))
                break

    for img_type, images in image_types.items():
        if not images:
            continue

        print(f"\n{img_type.upper()} Images ({len(images)} unique):")
        for image, count in images:
            # Extract filename
            if '/' in image:
                filename = image.split('/')[-1]
            else:
                filename = image

            bar = '█' * min(count, 50)
            print(f"  {filename:20} → Used by {count:2} rooms {bar}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Rooms: {len(rooms)}")
    print(f"Unique Images: {len([img for img in image_usage.keys() if 'no-image' not in img])}")
    print(f"Single Rooms: {len(rooms_by_type['single'])}")
    print(f"Double Rooms: {len(rooms_by_type['double'])}")
    print(f"Family Suites: {len(rooms_by_type['family'])}")
    print(f"Couple Rooms: {len(rooms_by_type['couple'])}")
    print(f"VIP Suites: {len(rooms_by_type['vip'])}")

    # Check for local vs external images
    local_images = sum(1 for r in rooms if r.get('image', '').startswith('/static'))
    external_images = sum(1 for r in rooms if r.get('image', '').startswith('http'))

    print(f"\n📁 Local Images: {local_images} rooms")
    print(f"🌐 External URLs: {external_images} rooms")

    if local_images > 0:
        print("\n✅ SUCCESS: Rooms are using local static images!")
    else:
        print("\n⚠️  WARNING: No rooms using local images. Check populate_rooms.py")

    print("\n" + "="*80 + "\n")


def show_image_files():
    """Show available image files in static/images directory"""
    import os
    from pathlib import Path

    print("\n" + "="*80)
    print("AVAILABLE IMAGE FILES")
    print("="*80 + "\n")

    # Find the static/images directory
    script_dir = Path(__file__).parent
    images_dir = script_dir / 'static' / 'images'

    if not images_dir.exists():
        print(f"❌ Directory not found: {images_dir}")
        return

    # Get all image files
    image_files = {}
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
        for file in images_dir.glob(ext):
            filename = file.name
            size_kb = file.stat().st_size / 1024

            # Categorize
            if filename.startswith('1bed'):
                category = 'Single Bed'
            elif filename.startswith('2bed'):
                category = 'Double Bed'
            elif filename.startswith('family'):
                category = 'Family Suite'
            elif filename.startswith('couple'):
                category = 'Couple Room'
            elif filename.startswith('vip'):
                category = 'VIP Suite'
            else:
                category = 'Other'

            if category not in image_files:
                image_files[category] = []

            image_files[category].append((filename, size_kb))

    # Display by category
    total_files = 0
    total_size = 0

    for category in ['Single Bed', 'Double Bed', 'Family Suite', 'Couple Room', 'VIP Suite', 'Other']:
        if category not in image_files:
            continue

        files = sorted(image_files[category])
        print(f"\n{category} ({len(files)} files):")
        print("-" * 80)

        for filename, size_kb in files:
            total_files += 1
            total_size += size_kb
            print(f"  📸 {filename:30} ({size_kb:7.1f} KB)")

    print("\n" + "="*80)
    print(f"Total Files: {total_files}")
    print(f"Total Size: {total_size/1024:.1f} MB")
    print("="*80 + "\n")


def main():
    """Main function"""
    print("\n🏨 Blissful Abodes - Room Image Mapping Tool\n")

    # Show database room-to-image mapping
    show_room_images()

    # Show available image files
    show_image_files()

    print("\n💡 TIP: To update images, modify populate_rooms.py and re-run it.")
    print("📖 For more info, see: IMAGE_DOWNLOAD_GUIDE.md or ROOM_IMAGES_SUMMARY.md\n")


if __name__ == '__main__':
    main()
