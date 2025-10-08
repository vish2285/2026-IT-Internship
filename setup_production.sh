#!/bin/bash

# 🚀 Production Setup Script for Internship Hub
# This script sets up production environment variables

echo "🔧 Setting up production environment variables..."

# Generate a new production secret key
PRODUCTION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "📝 Production environment variables ready:"
echo ""
echo "🔑 Database URL:"
echo "postgresql://neondb_owner:npg_l7zw0VaudiRo@ep-dark-truth-adri72k9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
echo ""
echo "🔑 GitHub Token:"
echo "YOUR_GITHUB_TOKEN_HERE"
echo ""
echo "🔑 Production Secret Key:"
echo "$PRODUCTION_SECRET"
echo ""
echo "🚀 Next steps for deployment:"
echo ""
echo "1. Deploy Backend to Railway:"
echo "   railway variables set DATABASE_URL='postgresql://neondb_owner:npg_l7zw0VaudiRo@ep-dark-truth-adri72k9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'"
echo "   railway variables set SECRET_KEY='$PRODUCTION_SECRET'"
echo "   railway variables set ENVIRONMENT=production"
echo "   railway variables set DEBUG=false"
echo ""
echo "2. Deploy Frontend to Vercel:"
echo "   Set VITE_API_URL=https://your-backend.railway.app"
echo ""
echo "3. Configure GitHub Actions:"
echo "   Add repository secrets:"
echo "   - API_URL=https://your-backend.railway.app"
echo "   - GITHUB_TOKEN=YOUR_GITHUB_TOKEN_HERE"
echo ""
echo "✅ Environment setup complete!"