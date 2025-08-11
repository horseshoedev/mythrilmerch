#!/bin/bash

# SSL Certificate Setup Script for MythrilMerch API
# This script helps set up SSL certificates for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
CERT_DIR="/etc/ssl/certs"
KEY_DIR="/etc/ssl/private"
LOG_DIR="/var/log/mythrilmerch"
RUN_DIR="/var/run/mythrilmerch"

echo -e "${GREEN}🔒 MythrilMerch SSL Certificate Setup${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p "$CERT_DIR"
mkdir -p "$KEY_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$RUN_DIR"

# Set proper permissions
chmod 755 "$CERT_DIR"
chmod 700 "$KEY_DIR"
chmod 755 "$LOG_DIR"
chmod 755 "$RUN_DIR"

# Function to generate self-signed certificate
generate_self_signed() {
    echo -e "${YELLOW}🔐 Generating self-signed certificate...${NC}"
    
    # Generate private key
    openssl genrsa -out "$KEY_DIR/mythrilmerch.key" 2048
    chmod 600 "$KEY_DIR/mythrilmerch.key"
    
    # Generate certificate signing request
    openssl req -new -key "$KEY_DIR/mythrilmerch.key" -out /tmp/mythrilmerch.csr -subj "/C=US/ST=State/L=City/O=MythrilMerch/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in /tmp/mythrilmerch.csr -signkey "$KEY_DIR/mythrilmerch.key" -out "$CERT_DIR/mythrilmerch.crt"
    
    # Clean up CSR
    rm /tmp/mythrilmerch.csr
    
    echo -e "${GREEN}✅ Self-signed certificate generated${NC}"
}

# Function to use Let's Encrypt
setup_lets_encrypt() {
    echo -e "${YELLOW}🌐 Setting up Let's Encrypt certificate...${NC}"
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}📦 Installing certbot...${NC}"
        if command -v apt-get &> /dev/null; then
            apt-get update
            apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            yum install -y certbot
        else
            echo -e "${RED}❌ Could not install certbot. Please install it manually.${NC}"
            exit 1
        fi
    fi
    
    # Generate certificate
    certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
    
    # Create symlinks
    ln -sf "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/mythrilmerch.crt"
    ln -sf "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$KEY_DIR/mythrilmerch.key"
    
    # Set proper permissions
    chmod 644 "$CERT_DIR/mythrilmerch.crt"
    chmod 600 "$KEY_DIR/mythrilmerch.key"
    
    echo -e "${GREEN}✅ Let's Encrypt certificate installed${NC}"
    
    # Create renewal script
    cat > /etc/cron.daily/renew-mythrilmerch-cert << EOF
#!/bin/bash
certbot renew --quiet
systemctl reload mythrilmerch-api
EOF
    chmod +x /etc/cron.daily/renew-mythrilmerch-cert
    
    echo -e "${GREEN}✅ Certificate renewal script created${NC}"
}

# Function to use existing certificate
use_existing_cert() {
    echo -e "${YELLOW}📄 Using existing certificate...${NC}"
    
    read -p "Enter path to your certificate file: " CERT_PATH
    read -p "Enter path to your private key file: " KEY_PATH
    
    if [[ ! -f "$CERT_PATH" ]]; then
        echo -e "${RED}❌ Certificate file not found: $CERT_PATH${NC}"
        exit 1
    fi
    
    if [[ ! -f "$KEY_PATH" ]]; then
        echo -e "${RED}❌ Private key file not found: $KEY_PATH${NC}"
        exit 1
    fi
    
    # Copy files
    cp "$CERT_PATH" "$CERT_DIR/mythrilmerch.crt"
    cp "$KEY_PATH" "$KEY_DIR/mythrilmerch.key"
    
    # Set proper permissions
    chmod 644 "$CERT_DIR/mythrilmerch.crt"
    chmod 600 "$KEY_DIR/mythrilmerch.key"
    
    echo -e "${GREEN}✅ Existing certificate installed${NC}"
}

# Main menu
echo "Choose SSL certificate option:"
echo "1) Generate self-signed certificate (for testing)"
echo "2) Use Let's Encrypt (recommended for production)"
echo "3) Use existing certificate"
echo "4) Skip SSL setup"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        generate_self_signed
        ;;
    2)
        setup_lets_encrypt
        ;;
    3)
        use_existing_cert
        ;;
    4)
        echo -e "${YELLOW}⚠️  Skipping SSL setup${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

# Create mythrilmerch user if it doesn't exist
if ! id "mythrilmerch" &>/dev/null; then
    echo -e "${YELLOW}👤 Creating mythrilmerch user...${NC}"
    useradd -r -s /bin/false -d /opt/mythrilmerch-backend mythrilmerch
    usermod -a -G mythrilmerch mythrilmerch
fi

# Set ownership
chown -R mythrilmerch:mythrilmerch "$LOG_DIR"
chown -R mythrilmerch:mythrilmerch "$RUN_DIR"

echo -e "${GREEN}🎉 SSL setup completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Copy the systemd service file to /etc/systemd/system/"
echo "2. Update the environment variables in the service file"
echo "3. Enable and start the service:"
echo "   sudo systemctl enable mythrilmerch-api"
echo "   sudo systemctl start mythrilmerch-api"
echo ""
echo -e "${YELLOW}🔍 To check the service status:${NC}"
echo "   sudo systemctl status mythrilmerch-api"
echo ""
echo -e "${YELLOW}📝 To view logs:${NC}"
echo "   sudo journalctl -u mythrilmerch-api -f" 