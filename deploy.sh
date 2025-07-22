#!/bin/bash

# Rinda CallOps Deployment Script
# This script deploys Firebase configuration and sets up demo account

set -e

echo "🚀 Starting Rinda CallOps Deployment..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI is not installed. Please install it first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Login to Firebase (if not already logged in)
echo "🔐 Checking Firebase authentication..."
if ! firebase projects:list &> /dev/null; then
    echo "Please log in to Firebase:"
    firebase login
fi

# Set the Firebase project
echo "📋 Setting Firebase project..."
firebase use phone-agents-7076c

# Deploy Firestore rules and indexes
echo "🔥 Deploying Firestore rules and indexes..."
firebase deploy --only firestore

# Create demo account in Firebase
echo "👤 Setting up demo account in Firebase..."
python3 setup_demo_account.py

echo "✅ Deployment completed successfully!"
echo ""
echo "🎉 Your Rinda CallOps is ready!"
echo "📱 Frontend: http://localhost:3000"
echo "🖥️  Backend: http://localhost:8000"
echo "🔑 Demo credentials: demo/demo"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd server && uv run python app/main.py"
echo "2. Start the frontend: cd client && npm run dev"
echo "3. Visit http://localhost:3000"
echo "4. Login with demo/demo"
echo ""
echo "🧪 Ready to test real functionality:"
echo "• Create meetings and process transcripts"
echo "• Test AI agent capabilities"
echo "• Execute real Google API actions" 