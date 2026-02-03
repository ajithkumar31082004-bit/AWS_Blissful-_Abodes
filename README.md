# Blissful Abodes - Real Estate Project Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Flask-based web application for managing real estate projects, featuring user authentication, admin dashboard, project enrollment system, and email notifications. Designed for deployment on AWS Cloud using EC2, DynamoDB, and SNS.

---

## 🌟 Features

### User Features
- ✅ User registration and authentication
- ✅ Browse available real estate projects
- ✅ Enroll in projects of interest
- ✅ Personal dashboard showing enrolled projects
- ✅ Email notifications for important events

### Admin Features
- ✅ Separate admin authentication system
- ✅ Create and manage real estate projects
- ✅ Upload project images and documents
- ✅ View all users and enrollments
- ✅ Admin dashboard with statistics

### Technical Features
- ✅ AWS DynamoDB for scalable NoSQL database
- ✅ AWS SNS for email notifications
- ✅ IAM role-based authentication (no hardcoded credentials)
- ✅ Responsive web design
- ✅ Session-based authentication
- ✅ File upload support
- ✅ Production-ready with systemd

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Internet Users                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │   Security Group    │
            │   (Firewall)        │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │   EC2 Instance      │
            │   Flask App         │
            │   Port: 5000        │
            └─────────┬───────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
    ┌──────────────┐    ┌─────────────┐
    │  DynamoDB    │    │  SNS Topic  │
    │  (4 Tables)  │    │  (Email)    │
    └──────────────┘    └─────────────┘
```

---

## 🚀 Quick Start - AWS Deployment

### Prerequisites
- AWS Account
- SSH client (Terminal/PuTTY)
- Basic command line knowledge

### Deployment Steps

**1. Start with the documentation:**
```bash
# Read this first!
START_HERE_AWS.md
```

**2. Follow the deployment guide:**
- **New to AWS?** → Read `AWS_DEPLOYMENT_GUIDE.md` (45-60 minutes)
- **Experienced?** → Read `QUICK_START.md` (20-30 minutes)

**3. Create AWS resources:**
- IAM Role with DynamoDB + SNS permissions
- 4 DynamoDB tables (Users, AdminUsers, Projects, Enrollments)
- SNS topic with email subscription
- EC2 instance (t2.micro)

**4. Deploy application:**
```bash
# Connect to EC2
ssh -i "your-key.pem" ec2-user@YOUR-EC2-IP

# Run automated setup
bash setup_on_ec2.sh

# Upload files
scp -i "your-key.pem" -r ./* ec2-user@YOUR-EC2-IP:~/blissful_abodes/

# Configure and run
python3 app_aws.py
```

**5. Access your application:**
```
http://YOUR-EC2-PUBLIC-IP:5000
```

---

## 📁 Project Structure

```
Blissful_Abodes/
├── README.md                      ← You are here
├── START_HERE_AWS.md              ← Start deployment here!
├── AWS_DEPLOYMENT_GUIDE.md        ← Complete deployment guide
├── QUICK_START.md                 ← Fast deployment (30 min)
├── AWS_README.md                  ← Technical reference
├── AWS_COMMANDS_CHEATSHEET.md     ← Command reference
├── README_AWS_DEPLOYMENT.md       ← File overview
│
├── app_aws.py                     ← Main Flask application (AWS)
├── create_dynamodb_tables.py      ← DynamoDB setup script
├── test_aws_connectivity.py       ← AWS connectivity test
├── setup_on_ec2.sh                ← Automated EC2 setup
├── requirements.txt               ← Python dependencies
│
├── templates/                     ← HTML templates
│   ├── index.html                 ← Landing page
│   ├── login.html                 ← User login
│   ├── signup.html                ← User registration
│   ├── home.html                  ← User dashboard
│   ├── projects_list.html         ← Browse projects
│   ├── admin_login.html           ← Admin login
│   ├── admin_dashboard.html       ← Admin panel
│   └── admin_create_project.html  ← Create project form
│
└── static/                        ← Static files
    ├── css/                       ← Stylesheets
    ├── js/                        ← JavaScript files
    ├── images/                    ← Site images
    └── uploads/                   ← User-uploaded files
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask 3.0
- **Language:** Python 3.8+
- **WSGI Server:** Gunicorn (production)

### AWS Services
- **EC2:** Application hosting
- **DynamoDB:** NoSQL database
- **SNS:** Email notifications
- **IAM:** Access management

### Frontend
- **HTML5** with Jinja2 templates
- **CSS3** for styling
- **JavaScript** for interactivity
- **Bootstrap** (optional)

---

## 💾 Database Schema

### DynamoDB Tables

**1. Users Table**
- Primary Key: `username` (String)
- Attributes: `password`, `email`, `created_at`

**2. AdminUsers Table**
- Primary Key: `username` (String)
- Attributes: `password`, `email`, `created_at`

**3. Projects Table**
- Primary Key: `id` (String, UUID)
- Attributes: `title`, `problem_statement`, `solution_overview`, `image`, `document`, `created_at`

**4. Enrollments Table**
- Primary Key: `username` (String)
- Attributes: `project_ids` (List), `updated_at`

---

## 🔧 Configuration

### Required Configuration in `app_aws.py`:

```python
# Line 9: Strong secret key for sessions
app.secret_key = 'your-super-secret-key-here'  # CHANGE THIS!

# Line 11: AWS Region
REGION = 'us-east-1'  # Change if using different region

# Line 21: SNS Topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:ACCOUNT-ID:TOPIC-NAME'  # UPDATE!
```

**Generate a secure secret key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📦 Installation

### Local Development (Optional)

```bash
# Clone repository
git clone https://github.com/yourusername/blissful-abodes.git
cd Blissful_Abodes

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials (for local testing)
aws configure

# Create DynamoDB tables
python3 create_dynamodb_tables.py --create

# Run application
python3 app_aws.py
```

---

## 🧪 Testing

### Run Connectivity Tests
```bash
# Test AWS services connectivity
python3 test_aws_connectivity.py
```

### Manual Testing Checklist
- [ ] Access homepage
- [ ] Create user account
- [ ] Login as user
- [ ] Browse projects
- [ ] Enroll in project
- [ ] Check DynamoDB for data
- [ ] Verify email notification
- [ ] Create admin account
- [ ] Login as admin
- [ ] Create project
- [ ] Verify project appears

---

## 🚀 Deployment

### Production Deployment on AWS EC2

**Step 1: Setup AWS Services**
```bash
# Create IAM role with DynamoDB + SNS permissions
# Create DynamoDB tables
python3 create_dynamodb_tables.py --create

# Create SNS topic and subscribe email
aws sns create-topic --name BlissfulAbodes-Notifications
```

**Step 2: Launch EC2 Instance**
- Instance Type: t2.micro (free tier)
- AMI: Amazon Linux 2023 or Ubuntu 22.04
- Attach IAM role
- Configure Security Group (SSH, HTTP, port 5000)

**Step 3: Deploy Application**
```bash
# Connect to EC2
ssh -i "your-key.pem" ec2-user@YOUR-EC2-IP

# Run setup script
bash setup_on_ec2.sh

# Upload files
# Configure app_aws.py
# Run application
python3 app_aws.py
```

**Step 4: Production Setup (Systemd)**
```bash
sudo cp blissful_abodes.service /etc/systemd/system/
sudo systemctl enable blissful_abodes
sudo systemctl start blissful_abodes
```

### Detailed Instructions
See `AWS_DEPLOYMENT_GUIDE.md` for complete step-by-step instructions.

---

## 💰 Cost Estimate

### AWS Free Tier (First 12 Months)
- ✅ EC2 t2.micro: 750 hours/month (FREE)
- ✅ DynamoDB: 25 GB storage (FREE)
- ✅ SNS: 1,000 email notifications (FREE)

**Total: $0/month** 🎉

### After Free Tier
- EC2 t2.micro: ~$8-10/month
- DynamoDB On-Demand: ~$1-5/month
- SNS: ~$0.50/1000 emails

**Total: ~$10-20/month**

---

## 🔐 Security

### Implemented Security Features
- ✅ IAM role-based AWS authentication (no hardcoded credentials)
- ✅ Session-based user authentication
- ✅ Security groups as firewall
- ✅ Environment variable configuration
- ✅ Input validation and sanitization

### Recommended Enhancements
- [ ] Password hashing (bcrypt or werkzeug.security)
- [ ] HTTPS with SSL certificate
- [ ] Rate limiting
- [ ] CSRF protection
- [ ] Content Security Policy headers
- [ ] Regular security audits

---

## 📊 Monitoring

### Application Monitoring
```bash
# Check application status
systemctl status blissful_abodes

# View logs
tail -f ~/blissful_abodes/logs/app.log

# Monitor system resources
htop
```

### AWS CloudWatch
- EC2 metrics (CPU, memory, network)
- DynamoDB metrics (read/write capacity)
- SNS delivery status
- Custom application logs

---

## 🐛 Troubleshooting

### Common Issues

**Can't connect to EC2?**
```bash
# Fix permissions
chmod 400 your-key.pem

# Verify security group allows SSH
# Check instance is running
```

**DynamoDB access denied?**
```bash
# Verify IAM role attached
python3 test_aws_connectivity.py

# Check IAM permissions
```

**Application won't start?**
```bash
# Check dependencies
pip3 list | grep -E 'flask|boto3'

# View errors
python3 app_aws.py

# Check logs
tail -f logs/app.log
```

For detailed troubleshooting, see `AWS_DEPLOYMENT_GUIDE.md`

---

## 📚 Documentation

- **START_HERE_AWS.md** - Your starting point
- **AWS_DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **QUICK_START.md** - Fast deployment (30 minutes)
- **AWS_README.md** - Technical reference
- **AWS_COMMANDS_CHEATSHEET.md** - Command reference
- **README_AWS_DEPLOYMENT.md** - Files overview

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Your Name** - *Initial work*

---

## 🙏 Acknowledgments

- Flask documentation and community
- AWS documentation and tutorials
- Bootstrap for UI components
- All contributors and testers

---

## 📞 Support

### Getting Help
1. Read the documentation in this repository
2. Check the troubleshooting section
3. Review AWS service documentation
4. Open an issue on GitHub

### Useful Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [DynamoDB Guide](https://docs.aws.amazon.com/dynamodb/)

---

## 🎯 Roadmap

### Current Version: 1.0
- ✅ User authentication and management
- ✅ Admin dashboard
- ✅ Project management
- ✅ Email notifications
- ✅ AWS deployment

### Planned Features
- [ ] Password reset functionality
- [ ] User profile management
- [ ] Advanced search and filtering
- [ ] Project categories and tags
- [ ] User reviews and ratings
- [ ] Mobile app
- [ ] Multi-language support

---

## 📈 Performance

### Optimization Tips
- Use Gunicorn with multiple workers
- Add Nginx reverse proxy
- Enable DynamoDB auto-scaling
- Implement caching (Redis/ElastiCache)
- Use CloudFront CDN for static files
- Optimize images before upload

---

## 🔄 Backup and Recovery

### Automated Backups
```bash
# Enable DynamoDB point-in-time recovery
aws dynamodb update-continuous-backups \
    --table-name Users \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Create on-demand backup
aws dynamodb create-backup \
    --table-name Users \
    --backup-name Users-Backup-$(date +%Y%m%d)

# Create EC2 snapshot
# Via AWS Console: EC2 → Volumes → Create Snapshot
```

---

## 📱 Screenshots

_(Add screenshots of your application here)_

- Landing Page
- User Dashboard
- Admin Panel
- Project Listing
- Project Creation Form

---

## 🌐 Live Demo

_(Add link to live demo if available)_

```
http://your-demo-url.com
```

**Demo Credentials:**
- User: demo@example.com / password
- Admin: admin@example.com / password

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/blissful-abodes&type=Date)](https://star-history.com/#yourusername/blissful-abodes&Date)

---

## 📧 Contact

For questions or feedback:
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

---

**Made with ❤️ for Real Estate Management**

**Deployed on AWS Cloud ☁️**

**Built with Flask 🔥**

---

*Last Updated: 2024*