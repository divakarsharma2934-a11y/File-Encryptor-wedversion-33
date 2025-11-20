import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_locker_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

import argparse

def setup_google_app(client_id=None, secret=None):
    # Ensure the default site exists
    site, created = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'File Locker'})
    if not created and site.domain == 'example.com':
        site.domain = '127.0.0.1:8000'
        site.name = 'File Locker'
        site.save()
        print("Updated default site to 127.0.0.1:8000")

    # Check if Google app exists
    try:
        app = SocialApp.objects.get(provider='google')
        print("Google app already exists.")
        if client_id and secret:
            app.client_id = client_id
            app.secret = secret
            app.save()
            print("Updated Google app with provided credentials.")
        
        if site not in app.sites.all():
            app.sites.add(site)
            print("Added site to existing Google app.")
            
    except SocialApp.DoesNotExist:
        print("Creating Google app...")
        if not client_id or not secret:
            print("WARNING: No credentials provided. Using DUMMY credentials.")
            client_id = client_id or 'DUMMY_CLIENT_ID'
            secret = secret or 'DUMMY_SECRET'
            
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret,
        )
        app.sites.add(site)
        print(f"Created Google app with client_id: {client_id}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup Google SocialApp')
    parser.add_argument('--client-id', help='Google Client ID')
    parser.add_argument('--secret', help='Google Client Secret')
    args = parser.parse_args()
    
    setup_google_app(args.client_id, args.secret)
