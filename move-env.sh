#!/bin/bash

# Move .env file to Next.js project directory
if [ -f ".env" ]; then
  echo "Moving .env file to buterin-cards-website directory..."
  mv .env buterin-cards-website/
  echo ".env file moved successfully!"
  echo "Please restart your development server for the changes to take effect."
else
  echo "No .env file found in the current directory."
  echo "Please create a .env file with your API keys and place it in the buterin-cards-website directory."
fi
