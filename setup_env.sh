#!/bin/bash

# 🚀 Environment Setup Script for Internship Hub
# This script creates all necessary environment files

echo "🔧 Setting up environment variables for Internship Hub..."

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Create backend .env file
echo "📝 Creating backend .env file..."
cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./internships.db

# API Configuration
API_URL=http://localhost:8000

# Security
SECRET_KEY=$SECRET_KEY

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Create frontend .env.local file
echo "📝 Creating frontend .env.local file..."
cat > frontend/.env.local << EOF
# API Configuration
VITE_API_URL=http://localhost:8000
EOF

echo "✅ Environment files created successfully!"
echo ""
echo "📋 Created files:"
echo "   - backend/.env"
echo "   - frontend/.env.local"
echo ""
echo "🔑 Generated secret key: $SECRET_KEY"
echo ""
echo "🚀 Next steps:"
echo "   1. Start the backend: cd backend && python3 -m uvicorn app.main:app --reload"
echo "   2. Start the frontend: cd frontend && npm run dev"
echo "   3. Visit http://localhost:3000"
echo ""
echo "⚠️  Remember to add .env files to .gitignore (already done)"

