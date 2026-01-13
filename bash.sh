#!/bin/bash

# Configuration
ACCESS_KEY="admin"
SECRET_KEY="minio_admin_password"
MINIO_URL="http://localhost:9000"

# Date au format RFC 1123 forcé en ANGLAIS (Indispensable pour S3)
DATE=$(LC_ALL=C date -u +'%a, %d %b %Y %H:%M:%S GMT')

# Signature simplifiée
STRING_TO_SIGN="GET\n\n\n${DATE}\n/"
SIGNATURE=$(printf "${STRING_TO_SIGN}" | openssl sha1 -hmac "${SECRET_KEY}" -binary | base64)

# Appel curl avec la date correcte
curl -v -H "Date: ${DATE}" \
     -H "Authorization: AWS ${ACCESS_KEY}:${SIGNATURE}" \
     ${MINIO_URL}/