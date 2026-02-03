"""
Simple placeholder image creator for room listings
Run this script to generate a default placeholder image
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a simple gradient placeholder image
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='#667eea')
    draw = ImageDraw.Draw(image)
    
    # Add gradient effect by drawing rectangles
    for i in range(height):
        ratio = i / height
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (74 - 126) * ratio)
        b = int(234 + (186 - 234) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add text
    text = "🏨 Room Image"
    try:
        # Try to use a larger font if available
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save image
    output_path = os.path.join(os.path.dirname(__file__), 'default-room.jpg')
    image.save(output_path, 'JPEG')
    print(f"✓ Placeholder image created: {output_path}")
    
except ImportError:
    print("PIL not installed. Using SVG fallback instead.")
    print("The app will serve SVG placeholders via the /placeholder-room-image route.")