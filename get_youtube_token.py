#!/usr/bin/env python3
"""
Helper script to get YouTube OAuth refresh token.
Run this once to get credentials for Lambda.
"""

import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_refresh_token(client_secrets_file):
    """Get OAuth refresh token by running local authentication flow."""
    
    print("\n" + "="*60)
    print("YouTube OAuth Authentication")
    print("="*60)
    print(f"\nUsing credentials from: {client_secrets_file}")
    print("\nThis will open your browser for authentication...")
    print("Please sign in and grant permissions.\n")
    
    # Create the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        SCOPES
    )
    
    # Run local server for OAuth callback
    credentials = flow.run_local_server(port=0)
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Authentication completed!")
    print("="*60)
    print("\nSAVE THESE CREDENTIALS TO YOUR LAMBDA ENVIRONMENT:\n")
    print(f"YOUTUBE_CLIENT_ID={credentials.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={credentials.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print("\n" + "="*60)
    print("\nNext steps:")
    print("1. Copy the three lines above")
    print("2. Add them to your Lambda environment variables")
    print("3. Test your full pipeline!")
    print("="*60 + "\n")
    
    return credentials

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 get_youtube_token.py <client_secrets.json>")
        print("\nExample:")
        print("  python3 get_youtube_token.py client_secret_*.json")
        sys.exit(1)
    
    client_secrets_file = sys.argv[1]
    get_refresh_token(client_secrets_file)

