#!/bin/bash

# Generate self-signed SSL certificates for development
# DO NOT USE THESE IN PRODUCTION - Get proper certificates from a trusted CA

# Set variables
CERT_DIR="./nginx/ssl"
DOMAIN="localhost"
DAYS_VALID=365

echo "Generating self-signed SSL certificate for $DOMAIN (valid for $DAYS_VALID days)"

# Create directory if it doesn't exist
mkdir -p $CERT_DIR

# Generate private key
openssl genrsa -out $CERT_DIR/server.key 2048

# Generate CSR (Certificate Signing Request)
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr -subj "/CN=$DOMAIN/O=Inventory Management/C=US"

# Generate self-signed certificate
openssl x509 -req -days $DAYS_VALID -in $CERT_DIR/server.csr -signkey $CERT_DIR/server.key -out $CERT_DIR/server.crt

# Remove CSR as it's no longer needed
rm $CERT_DIR/server.csr

echo "Self-signed SSL certificate generated successfully!"
echo "Files created:"
echo "  - $CERT_DIR/server.key (private key)"
echo "  - $CERT_DIR/server.crt (certificate)"
echo ""
echo "NOTE: These are self-signed certificates and should only be used for development."
echo "      For production, obtain certificates from a trusted Certificate Authority."
