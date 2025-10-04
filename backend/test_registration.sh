#!/bin/bash

API_URL="https://economic-dashboard-production.up.railway.app"

echo "Testing user registration..."
curl -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_'$(date +%s)'@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }' | python3 -m json.tool

echo -e "\n\nDone. Check Railway logs for the error traceback."
