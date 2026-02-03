#!/bin/bash

# ============================================================================
# Blissful Abodes - EC2 Setup Script
# ============================================================================
# This script automates the setup of the Blissful Abodes application on EC2
# Run this script after connecting to your EC2 instance
# ============================================================================

echo "============================================================================"
echo "Blissful Abodes - EC2 Setup Script"
echo "============================================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info message
print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Step 1: Update System
print_info "Step 1: Updating system packages..."
sudo yum update -y
if [ $? -eq 0 ]; then
    print_success "System updated successfully"
else
    print_error "Failed to update system"
    exit 1
fi
echo ""

# Step 2: Install Python 3 and pip
print_info "Step 2: Installing Python 3 and pip..."
sudo yum install python3 python3-pip -y
if [ $? -eq 0 ]; then
    print_success "Python 3 installed successfully"
    python3 --version
    pip3 --version
else
    print_error "Failed to install Python 3"
    exit 1
fi
echo ""

# Step 3: Install Git (optional)
print_info "Step 3: Installing Git..."
sudo yum install git -y
if [ $? -eq 0 ]; then
    print_success "Git installed successfully"
else
    print_error "Failed to install Git"
fi
echo ""

# Step 4: Create application directory
print_info "Step 4: Creating application directory..."
APP_DIR="$HOME/blissful_abodes"
mkdir -p "$APP_DIR"
cd "$APP_DIR"
print_success "Application directory created at: $APP_DIR"
echo ""

# Step 5: Create directory structure
print_info "Step 5: Creating directory structure..."
mkdir -p static/uploads
mkdir -p templates
mkdir -p logs
print_success "Directory structure created"
echo ""

# Step 6: Install Python dependencies
print_info "Step 6: Installing Python dependencies..."
pip3 install --user flask boto3 werkzeug gunicorn
if [ $? -eq 0 ]; then
    print_success "Python dependencies installed successfully"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi
echo ""

# Step 7: Create requirements.txt
print_info "Step 7: Creating requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==3.0.0
boto3==1.34.0
Werkzeug==3.0.1
botocore==1.34.0
gunicorn==21.2.0
EOF
print_success "requirements.txt created"
echo ""

# Step 8: Display AWS Configuration Information
echo "============================================================================"
print_info "AWS Configuration Required"
echo "============================================================================"
echo ""
echo "Before running the application, ensure you have:"
echo "1. ✓ Attached IAM role to this EC2 instance with:"
echo "   - AmazonDynamoDBFullAccess"
echo "   - AmazonSNSFullAccess"
echo ""
echo "2. ✓ Created DynamoDB tables:"
echo "   - Users (Key: username)"
echo "   - AdminUsers (Key: username)"
echo "   - Projects (Key: id)"
echo "   - Enrollments (Key: username)"
echo ""
echo "3. ✓ Created SNS Topic and noted the ARN"
echo ""
echo "4. ✓ Updated app_aws.py with:"
echo "   - Correct SNS_TOPIC_ARN"
echo "   - Correct REGION"
echo "   - Strong SECRET_KEY"
echo ""

# Step 9: Test AWS connectivity
print_info "Step 9: Testing AWS connectivity..."
python3 << 'PYEOF'
import sys
try:
    import boto3

    # Test DynamoDB connection
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    tables = list(dynamodb.tables.all())
    print("✓ Connected to DynamoDB successfully")
    print(f"  Found {len(tables)} tables")

    # Test SNS connection
    sns = boto3.client('sns', region_name='us-east-1')
    topics = sns.list_topics()
    print("✓ Connected to SNS successfully")
    print(f"  Found {len(topics.get('Topics', []))} topics")

    # Get caller identity
    sts = boto3.client('sts', region_name='us-east-1')
    identity = sts.get_caller_identity()
    print(f"✓ AWS Account ID: {identity['Account']}")

except Exception as e:
    print(f"✗ AWS connectivity test failed: {e}")
    print("\nPlease ensure:")
    print("1. IAM role is attached to this EC2 instance")
    print("2. IAM role has DynamoDB and SNS permissions")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    print_success "AWS connectivity test passed"
else
    print_error "AWS connectivity test failed"
    echo ""
    echo "Please fix AWS configuration before proceeding."
    exit 1
fi
echo ""

# Step 10: Create systemd service file
print_info "Step 10: Creating systemd service file..."
cat > blissful_abodes.service << EOF
[Unit]
Description=Blissful Abodes Flask Application
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 app_aws:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Service file created: blissful_abodes.service"
echo ""
echo "To install the service, run:"
echo "  sudo cp blissful_abodes.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable blissful_abodes"
echo "  sudo systemctl start blissful_abodes"
echo ""

# Step 11: Create helper scripts
print_info "Step 11: Creating helper scripts..."

# Create start script
cat > start_app.sh << 'EOF'
#!/bin/bash
cd ~/blissful_abodes
nohup python3 app_aws.py > logs/app.log 2>&1 &
echo "Application started. PID: $!"
echo "View logs: tail -f logs/app.log"
EOF
chmod +x start_app.sh
print_success "Created start_app.sh"

# Create stop script
cat > stop_app.sh << 'EOF'
#!/bin/bash
pkill -f app_aws.py
echo "Application stopped"
EOF
chmod +x stop_app.sh
print_success "Created stop_app.sh"

# Create status script
cat > status_app.sh << 'EOF'
#!/bin/bash
if pgrep -f app_aws.py > /dev/null; then
    echo "✓ Application is RUNNING"
    ps aux | grep app_aws.py | grep -v grep
else
    echo "✗ Application is NOT running"
fi
EOF
chmod +x status_app.sh
print_success "Created status_app.sh"

# Create logs script
cat > view_logs.sh << 'EOF'
#!/bin/bash
tail -f logs/app.log
EOF
chmod +x view_logs.sh
print_success "Created view_logs.sh"

echo ""

# Step 12: Display completion message
echo "============================================================================"
echo "Setup Complete!"
echo "============================================================================"
echo ""
print_success "EC2 instance is now configured for Blissful Abodes deployment"
echo ""
echo "Next Steps:"
echo "------------"
echo "1. Upload your application files:"
echo "   - app_aws.py"
echo "   - All HTML templates to templates/"
echo "   - All static files to static/"
echo ""
echo "2. Create DynamoDB tables (if not already created):"
echo "   python3 create_dynamodb_tables.py --create"
echo ""
echo "3. Update app_aws.py with your SNS Topic ARN and SECRET_KEY"
echo ""
echo "4. Test the application:"
echo "   ./start_app.sh"
echo ""
echo "5. Access your application at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "6. For production deployment with systemd:"
echo "   sudo cp blissful_abodes.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable blissful_abodes"
echo "   sudo systemctl start blissful_abodes"
echo ""
echo "Useful Commands:"
echo "----------------"
echo "  ./start_app.sh    - Start the application"
echo "  ./stop_app.sh     - Stop the application"
echo "  ./status_app.sh   - Check application status"
echo "  ./view_logs.sh    - View application logs"
echo ""
echo "Application Directory: $APP_DIR"
echo ""
echo "============================================================================"

exit 0
