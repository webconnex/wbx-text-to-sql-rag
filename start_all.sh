#!/bin/bash

# Webconnex AI Text-to-SQL - Complete System Launcher
# ====================================================

clear

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🔷 WEBCONNEX AI TEXT-TO-SQL SYSTEM 🔷             ║"
echo "║           Powered by Amazon Nova Pro                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Function to check if port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    lsof -ti:$1 | xargs kill -9 2>/dev/null || true
}

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📋 Loading environment from .env file..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo "⚠️  .env file not found. Using default values."
fi

# Set AWS credentials from environment or use defaults
export AWS_PROFILE=${AWS_PROFILE:-your-okta-profile-name}
export AWS_REGION=${AWS_REGION:-us-west-2}
export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-your-aws-account-id}

echo "📋 System Configuration:"
echo "  • AWS Profile: $AWS_PROFILE"
echo "  • AWS Region: $AWS_REGION"
echo "  • Account ID: $AWS_ACCOUNT_ID"
echo "  • Model: Amazon Nova Pro (us.amazon.nova-pro-v1:0)"
echo ""

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "  ✅ AWS credentials valid"
else
    echo "  ⚠️  AWS credentials expired!"
    echo "  Run: gimme-aws-creds --profile $AWS_PROFILE"
    echo ""
fi

# Check and clean ports
echo "🔍 Checking ports..."
if check_port 8000; then
    echo "  ⚠️  Port 8000 in use, cleaning..."
    kill_port 8000
    sleep 2
fi

if check_port 8501; then
    echo "  ⚠️  Port 8501 in use, cleaning..."
    kill_port 8501
    sleep 2
fi

echo "  ✅ Ports available"
echo ""

# Start backend API
echo "🚀 Starting Backend API Server..."

# Start backend in background (from current directory)
nohup python3 -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    > backend.log 2>&1 &

BACKEND_PID=$!
echo "  • Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "  • Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✅ Backend API running on http://localhost:8000"
        break
    fi
    sleep 1
done

# Install frontend dependencies if needed
echo ""
echo "📦 Checking frontend dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "  • Installing Streamlit..."
    pip install streamlit plotly pandas > /dev/null 2>&1
fi
echo "  ✅ Dependencies installed"

# Start frontend
echo ""
echo "🚀 Starting Webconnex AI Frontend..."

# Start frontend in background (using fixed v2 version)
nohup streamlit run frontend_streamlit_v2.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.primaryColor="#0047AB" \
    > frontend.log 2>&1 &

FRONTEND_PID=$!
echo "  • Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "  • Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "  ✅ Frontend running on http://localhost:8501"
        break
    fi
    sleep 1
done

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║               ✅ SYSTEM SUCCESSFULLY STARTED              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Access Points:"
echo "  • Frontend UI: http://localhost:8501"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "📊 System Status:"
echo "  • Backend PID: $BACKEND_PID"
echo "  • Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "  • Backend: tail -f backend.log"
echo "  • Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "  • kill $BACKEND_PID $FRONTEND_PID"
echo "  • Or press Ctrl+C"
echo ""
echo "=================================================="

# Open browser
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    sleep 2
    open http://localhost:8501
fi

# Keep script running and handle shutdown
trap "echo ''; echo '🛑 Shutting down services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Services stopped'; exit" INT TERM

echo "Press Ctrl+C to stop all services"
echo ""

# Keep running and show logs
tail -f frontend.log backend.log 2>/dev/null