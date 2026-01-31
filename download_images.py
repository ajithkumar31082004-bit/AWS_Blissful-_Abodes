"""
Download high-quality hotel room images from Unsplash (free to use)
This script downloads images for different room types and saves them to static/images folder
"""

import requests
import os
import time
from pathlib import Path

# Unsplash image collections for different room types
# These are direct download URLs from Unsplash (free to use with attribution)
ROOM_IMAGES = {
    'single': [
        'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1200&q=80',  # Modern single room
        'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=1200&q=80',  # Cozy single bed
        'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=1200&q=80',  # Classic hotel room
        'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=1200&q=80',  # Minimalist room
        'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&q=80',  # Business room
        'https://images.unsplash.com/photo-1618221195710-dd6b41faaea8?w=1200&q=80',  # Elegant single
        'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=1200&q=80',  # Modern decor
        'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=1200&q=80',  # Comfortable single
    ],
    'double': [
        'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1200&q=80',  # Luxury double
        'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=1200&q=80',  # Modern double
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=80',  # Elegant double
        'https://images.unsplash.com/photo-1618221195710-dd6b41faaea8?w=1200&q=80',  # Classic double
        'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1200&q=80',  # Contemporary
        'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=1200&q=80',  # Comfortable
        'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=1200&q=80',  # Spacious double
        'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80',  # Premium double
    ],
    'family': [
        'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80',  # Family suite
        'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=1200&q=80',  # Large family room
        'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=1200&q=80',  # Spacious suite
        'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=1200&q=80',  # Multi-bed room
        'https://images.unsplash.com/photo-1618221195710-dd6b41faaea8?w=1200&q=80',  # Family comfort
        'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1200&q=80',  # Large suite
    ],
    'couple': [
        'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1200&q=80',  # Romantic room
        'https://images.unsplash.com/photo-1618221195710-dd6b41faaea8?w=1200&q=80',  # Honeymoon suite
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=80',  # Intimate room
        'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=1200&q=80',  # Luxury romantic
        'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80',  # Elegant couple
        'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1200&q=80',  # Cozy romantic
    ],
    'vip': [
        'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80',  # Presidential suite
        'https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=1200&q=80',  # Executive suite
        'https://images.unsplash.com/photo-1618221195710-dd6b41faaea8?w=1200&q=80',  # Penthouse
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1200&q=80',  # Luxury villa
        'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1200&q=80',  # Premium suite
        'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1200&q=80',  # Grand suite
        'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=1200&q=80',  # VIP room
        'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=1200&q=80',  # Elite suite
    ]
}

def download_image(url, filepath, room_type, index):
    """Download an image from URL and save it to filepath"""
    try:
        print(f"Downloading {room_type} image {index}...")

        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✓ Saved: {filepath}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download {url}: {e}")
        return False

def main():
    """Download all room images"""

    # Get the static/images directory
    script_dir = Path(__file__).parent
    images_dir = script_dir / 'static' / 'images'

    # If script is in root directory, adjust path
    if not images_dir.exists():
        images_dir = Path(__file__).parent / 'Blissful_Abodes' / 'static' / 'images'

    # If still not found, use current directory
    if not images_dir.exists():
        images_dir = Path('static/images')

    # Create directory if it doesn't exist
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading Hotel Room Images")
    print(f"Destination: {images_dir.absolute()}")
    print(f"{'='*60}\n")

    total_downloaded = 0
    total_failed = 0

    # Download images for each room type
    for room_type, urls in ROOM_IMAGES.items():
        print(f"\n📥 Downloading {room_type.upper()} room images...")

        for index, url in enumerate(urls, 1):
            # Determine file extension
            ext = 'jpeg' if index <= 5 else 'jpg'

            # Create filename based on existing pattern
            if room_type == 'single':
                filename = f'1bed{index}.{ext}'
            elif room_type == 'double':
                filename = f'2bed{index}.{ext}'
            elif room_type == 'family':
                filename = f'family{index}.{ext}'
            elif room_type == 'couple':
                filename = f'couple{index}.{ext}'
            elif room_type == 'vip':
                filename = f'vip{index}.{ext}'

            filepath = images_dir / filename

            # Skip if file already exists
            if filepath.exists():
                print(f"⊘ Skipped: {filename} (already exists)")
                continue

            # Download the image
            success = download_image(url, filepath, room_type, index)

            if success:
                total_downloaded += 1
            else:
                total_failed += 1

            # Be nice to the server - wait between downloads
            time.sleep(1)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Download Complete!")
    print(f"✓ Successfully downloaded: {total_downloaded} images")
    if total_failed > 0:
        print(f"✗ Failed downloads: {total_failed} images")
    print(f"📁 Location: {images_dir.absolute()}")
    print(f"{'='*60}\n")

    print("\nNote: These images are from Unsplash and are free to use.")
    print("Consider adding attribution in your application footer:")
    print("'Photos by Unsplash (https://unsplash.com)'")

if __name__ == '__main__':
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("\n❌ Error: 'requests' library is not installed.")
        print("Please install it by running:")
        print("   pip install requests")
        print("\nOr if you're using the virtual environment:")
        print("   .venv\\Scripts\\activate")
        print("   pip install requests")
        exit(1)

    main()
