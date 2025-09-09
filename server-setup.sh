#!/bin/bash

# LibProxy Server Setup Script for 80.251.40.216
# Run this script on the production server

echo "🖥️  Setting up LibProxy on production server..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "✅ Docker is already installed"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose is already installed"
fi

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/libproxy
sudo chown $USER:$USER /opt/libproxy

# Set up firewall (UFW)
echo "🔒 Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (important!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 5001/tcp  # Backend API
sudo ufw allow 8404/tcp  # HAProxy Stats

# Allow PostgreSQL and Redis (only from localhost for security)
sudo ufw allow from 127.0.0.1 to any port 5432
sudo ufw allow from 127.0.0.1 to any port 6379

# Reload firewall
sudo ufw reload
sudo ufw status

# Create log directories
echo "📋 Creating log directories..."
sudo mkdir -p /var/log/libproxy
sudo chown $USER:$USER /var/log/libproxy

# Set up log rotation
echo "🔄 Setting up log rotation..."
sudo tee /etc/logrotate.d/libproxy > /dev/null <<EOF
/var/log/libproxy/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
}
EOF

# Install fail2ban for security
echo "🛡️  Installing fail2ban..."
sudo apt install -y fail2ban

# Configure fail2ban for SSH
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Set up automatic updates
echo "🔄 Setting up automatic security updates..."
sudo apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades

# Create backup directory
echo "💾 Creating backup directory..."
sudo mkdir -p /opt/libproxy-backups
sudo chown $USER:$USER /opt/libproxy-backups

# Create backup script
cat > /opt/libproxy-backups/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/libproxy-backups"
DB_BACKUP="$BACKUP_DIR/libproxy_db_$DATE.sql"

# Backup database
docker-compose -f /opt/libproxy/docker-compose.prod.yml exec -T db pg_dump -U libproxy_user libproxy > "$DB_BACKUP"

# Compress backup
gzip "$DB_BACKUP"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

echo "Backup completed: ${DB_BACKUP}.gz"
EOF

chmod +x /opt/libproxy-backups/backup.sh

# Set up daily backup cron job
echo "⏰ Setting up daily backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/libproxy-backups/backup.sh >> /var/log/libproxy/backup.log 2>&1") | crontab -

# Install monitoring tools
echo "📊 Installing monitoring tools..."
sudo apt install -y htop iotop nethogs

# Create systemd service for LibProxy (optional)
sudo tee /etc/systemd/system/libproxy.service > /dev/null <<EOF
[Unit]
Description=LibProxy Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/libproxy
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo ""
echo "✅ Server setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Copy your LibProxy application files to /opt/libproxy/"
echo "2. Update env.production with secure passwords"
echo "3. Run the deployment script: ./deploy.sh"
echo "4. Test the application"
echo "5. Set up SSL certificates (recommended)"
echo ""
echo "🔒 Security recommendations:"
echo "1. Change default SSH port"
echo "2. Set up SSH key authentication"
echo "3. Disable password authentication"
echo "4. Set up SSL/TLS certificates"
echo "5. Configure regular security updates"
echo "6. Monitor logs regularly"
echo ""
echo "📊 Monitoring:"
echo "   System: htop, iotop, nethogs"
echo "   Logs: tail -f /var/log/libproxy/*.log"
echo "   Docker: docker-compose -f docker-compose.prod.yml logs -f"
echo ""
