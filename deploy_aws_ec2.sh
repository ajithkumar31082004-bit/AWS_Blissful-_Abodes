#!/bin/bash

# Blissful Abodes - AWS EC2 Deployment Script
# Run this script on your EC2 instance

set -e  # Exit on error

echo "=========================================="
echo "Blissful Abodes - AWS EC2 Deployment"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo yum update -y
sudo yum install -y python3 python3-pip git

# Clone or download application
echo "📥 Downloading application..."
cd /home/ec2-user
if [ ! -d "blissful-abodes" ]; then
    git clone https://github.com/your-repo/blissful-abodes.git
    cd blissful-abodes
else
    cd blissful-abodes
    git pull
fi

# Install dependencies
echo "📚 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create .env file
echo "⚙️ Setting up environment..."
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(ec2-metadata --document | grep -o '"accountId" : "[^"]*' | cut -d'"' -f4)
EOF

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/blissful-abodes.service > /dev/null << 'EOF'
[Unit]
Description=Blissful Abodes Hotel Booking System
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/home/ec2-user/blissful-abodes
Environment="FLASK_ENV=production"
ExecStart=/usr/local/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 app_aws:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start service
echo "🚀 Starting application..."
sudo systemctl daemon-reload
sudo systemctl enable blissful-abodes
sudo systemctl start blissful-abodes

# Verify deployment
echo "✅ Deployment completed!"
echo "📊 Service status:"
sudo systemctl status blissful-abodes

echo ""
echo "Application running at: http://$(hostname -I | awk '{print $1}'):5000"
echo "Health check: http://$(hostname -I | awk '{print $1}'):5000/health"
