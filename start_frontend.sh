#!/bin/bash

# Webconnex AI Text-to-SQL Frontend Launcher
# ============================================

echo "=================================================="
echo "🔷 WEBCONNEX AI TEXT-TO-SQL FRONTEND"
echo "=================================================="
echo "Powered by Amazon Nova Pro"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Streamlit
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit plotly pandas
fi

# Set AWS credentials
export AWS_PROFILE=654293192108-okta-admin-user
export AWS_REGION=us-west-2

echo "✅ Environment configured"
echo "  • AWS Profile: $AWS_PROFILE"
echo "  • AWS Region: $AWS_REGION"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend API is not running!"
    echo "   Start it first with: python backend/main.py"
    echo ""
fi

echo "🚀 Starting Webconnex AI Frontend..."
echo "=================================================="
echo ""
echo "📍 Access the application at:"
echo "   • Local: http://localhost:8501"
echo "   • Network: http://$(hostname):8501"
echo ""
echo "⚡ Press Ctrl+C to stop"
echo "=================================================="
echo ""

# Launch Streamlit (using fixed v2 version)
streamlit run frontend_streamlit_v2.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.primaryColor="#0047AB" \
    --theme.backgroundColor="#FFFFFF" \
    --theme.secondaryBackgroundColor="#F5F7FA" \
    --theme.textColor="#1A1A2E"