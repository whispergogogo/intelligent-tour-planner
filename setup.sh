#!/bin/bash

echo "🚀 Setting up Intelligent Tour Planner"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if API key is already set
if [ -n "$GOOGLE_MAPS_API_KEY" ]; then
    echo "✅ Google Maps API key is already set"
else
    echo "🔑 Setting up Google Maps API key..."
    echo ""
    echo "To use this application, you need a Google Maps API key."
    echo "Follow these steps:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project or select existing one"
    echo "3. Enable these APIs:"
    echo "   - Places API (Text Search)"
    echo "   - Distance Matrix API"
    echo "4. Create credentials (API Key)"
    echo "5. Restrict the API key to only these APIs"
    echo ""
    
    read -p "Enter your Google Maps API key: " api_key
    
    if [ -n "$api_key" ]; then
        echo "export GOOGLE_MAPS_API_KEY=\"$api_key\"" >> ~/.bashrc
        echo "export GOOGLE_MAPS_API_KEY=\"$api_key\"" >> ~/.zshrc
        export GOOGLE_MAPS_API_KEY="$api_key"
        echo "✅ API key saved to shell configuration files"
    else
        echo "❌ No API key provided. You'll need to set it manually."
        echo "Run: export GOOGLE_MAPS_API_KEY='your_api_key_here'"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo "To run the tour planner:"
echo "  python3 main.py"
echo ""
echo "For help, see README.md"
