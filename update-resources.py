#!/usr/bin/env python3
"""
Jellyfin Elsewhere - Resource Update Script

This script fetches the latest regions and providers data from TMDB API
and updates the resource files used by the userscript.

Usage:
    python update-resources.py

Requirements:
    - requests
    - TMDB API key from environment variable TMDB_API_KEY
"""

import requests
import os
import sys
from datetime import datetime

def get_api_key():
    """Get TMDB API key from environment variable"""
    api_key = os.environ.get('TMDB_API_KEY')
    if not api_key:
        print("❌ Error: TMDB_API_KEY environment variable not found!")
        print("Please set the TMDB_API_KEY environment variable with your TMDB API key")
        sys.exit(1)
    return api_key

def fetch_tmdb_data(api_key, endpoint):
    """Fetch data from TMDB API"""
    headers = {'Content-Type': 'application/json'}
    url = f'https://api.themoviedb.org/3/{endpoint}?api_key={api_key}'

    try:
        print(f"🔄 Fetching data from: {endpoint}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return None

def update_regions(api_key, res_dir):
    """Update regions.txt with latest data from TMDB"""
    print("🌍 Updating regions...")

    data = fetch_tmdb_data(api_key, 'watch/providers/regions')
    if not data or 'results' not in data:
        print("❌ Failed to fetch regions data")
        return False

    regions_file = os.path.join(res_dir, 'regions.txt')

    try:
        with open(regions_file, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"# Regions data updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write("# Format: ISO_CODE<TAB>ENGLISH_NAME\n")

            # Sort regions by ISO code for consistency
            sorted_regions = sorted(data['results'], key=lambda x: x['iso_3166_1'])

            for region in sorted_regions:
                f.write(f"{region['iso_3166_1']}\t{region['english_name']}\n")

        print(f"✅ Updated {len(data['results'])} regions in {regions_file}")
        return True

    except Exception as e:
        print(f"❌ Error writing regions file: {e}")
        return False

def update_providers(api_key, res_dir):
    """Update providers.txt with latest data from TMDB"""
    print("📺 Updating providers...")

    # Fetch providers for both movies and TV shows
    movie_data = fetch_tmdb_data(api_key, 'watch/providers/movie')
    tv_data = fetch_tmdb_data(api_key, 'watch/providers/tv')

    if not movie_data or not tv_data:
        print("❌ Failed to fetch providers data")
        return False

    # Combine and deduplicate providers
    all_providers = set()

    if 'results' in movie_data:
        for provider in movie_data['results']:
            all_providers.add(provider['provider_name'])

    if 'results' in tv_data:
        for provider in tv_data['results']:
            all_providers.add(provider['provider_name'])

    providers_file = os.path.join(res_dir, 'providers.txt')

    try:
        with open(providers_file, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"# Providers data updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write("# Format: One provider name per line\n")

            # Sort providers alphabetically for consistency
            for provider in sorted(all_providers):
                f.write(f"{provider}\n")

        print(f"✅ Updated {len(all_providers)} providers in {providers_file}")
        return True

    except Exception as e:
        print(f"❌ Error writing providers file: {e}")
        return False

def create_res_directory():
    """Create res directory if it doesn't exist"""
    script_directory = os.path.dirname(os.path.abspath(__file__))
    res_dir = os.path.join(script_directory, 'resources')

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
        print(f"📁 Created directory: {res_dir}")

    return res_dir

def main():
    """Main function"""
    print("🎬 Jellyfin Elsewhere - Resource Update Script")
    print("=" * 50)

    # Get API key from environment
    api_key = get_api_key()

    # Create res directory
    res_dir = create_res_directory()

    # Update resources
    regions_success = update_regions(api_key, res_dir)
    providers_success = update_providers(api_key, res_dir)

    # Summary
    print("\n" + "=" * 50)
    if regions_success and providers_success:
        print("✅ All resources updated successfully!")
        print(f"📁 Files updated in: {res_dir}")
        print("🔄 Resources are ready for use by the userscript")
    else:
        print("❌ Some resources failed to update")
        sys.exit(1)

if __name__ == "__main__":
    main()