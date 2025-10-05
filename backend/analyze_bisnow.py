import asyncio
from app.services.email_service import EmailService
from app.core.database import async_session_maker
from app.core.encryption import decrypt_email_password
from sqlalchemy import select
from app.models.user import User

async def analyze_emails():
    async with async_session_maker() as db:
        # Get your user
        result = await db.execute(select(User).where(User.email == "samhimre@gmail.com"))
        user = result.scalar_one_or_none()
        
        if not user or not user.email_app_password:
            print("User not found or no email configured")
            return
        
        # Decrypt password
        password = decrypt_email_password(user.email_app_password)
        
        # Create email service
        service = EmailService(
            email_address=user.email_address,
            email_password=password,
            imap_server=user.imap_server,
            imap_port=user.imap_port
        )
        
        # Fetch emails
        print("Fetching emails...")
        emails = await service.fetch_emails(days=7)
        
        print(f"\nFound {len(emails)} Bisnow emails\n")
        
        # Analyze first 3
        for i, email_data in enumerate(emails[:3], 1):
            print(f"\n{'='*80}")
            print(f"EMAIL {i}: {email_data['subject']}")
            print(f"{'='*80}")
            print(f"From: {email_data['source']}")
            print(f"Category: {email_data['category']}")
            print(f"\nKey Points Found:")
            print(f"  Headlines: {len(email_data['key_points'].get('headlines', []))}")
            print(f"  Metrics: {len(email_data['key_points'].get('metrics', []))}")
            print(f"  Locations: {len(email_data['key_points'].get('locations', []))}")
            print(f"  Companies: {len(email_data['key_points'].get('companies', []))}")
            
            if email_data['key_points'].get('headlines'):
                print(f"\nFirst 5 Headlines:")
                for h in email_data['key_points']['headlines'][:5]:
                    print(f"  - {h}")
            
            if email_data['key_points'].get('metrics'):
                print(f"\nMetrics Found:")
                for m in email_data['key_points']['metrics'][:3]:
                    print(f"  - {m['type']}: {m['value']} ({m['context'][:50]}...)")
            
            # Show raw HTML structure
            if email_data.get('content_html'):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(email_data['content_html'], 'html.parser')
                
                print(f"\nHTML Structure:")
                print(f"  Total links: {len(soup.find_all('a'))}")
                print(f"  Total paragraphs: {len(soup.find_all('p'))}")
                print(f"  Total divs: {len(soup.find_all('div'))}")
                print(f"  Total tables: {len(soup.find_all('table'))}")
                
                # Sample first few links
                links = soup.find_all('a', href=True)[:3]
                if links:
                    print(f"\nSample Links:")
                    for link in links:
                        print(f"  - {link.get_text(strip=True)[:60]} -> {link['href'][:50]}")

if __name__ == "__main__":
    asyncio.run(analyze_emails())
