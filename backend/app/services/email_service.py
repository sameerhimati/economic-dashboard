"""
Email newsletter parsing service for Bisnow real estate newsletters.

Handles IMAP email fetching, HTML parsing, and content extraction for real estate
newsletters with comprehensive error handling and retry logic.
"""
import logging
import imaplib
import email
from email.message import Message
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any, Tuple
import re
import asyncio
from functools import partial

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.models.newsletter import Newsletter

# Configure logging
logger = logging.getLogger(__name__)


# Bisnow newsletter category mappings
BISNOW_CATEGORIES = {
    "Houston Morning Brief": ["Houston Morning Brief", "Houston AM Brief"],
    "Austin Morning Brief": ["Austin", "San Antonio", "Austin/San Antonio"],
    "National Deal Brief": ["National Deal Brief", "National Deals"],
    "Capital Markets": ["Capital Markets", "Finance", "Capital Markets Brief"],
    "Multifamily": ["Multifamily", "Multifamily Brief"],
    "Retail": ["Retail", "Retail Brief"],
    "Investment": ["Investment", "Investment Brief"],
    "Student Housing": ["Student Housing", "Student Housing Brief"],
    "Texas Tea": ["Texas Tea", "The Texas Tea"],
    "What Tenants Want": ["What Tenants Want", "Tenants"],
}

# Regex patterns for extracting real estate metrics
METRIC_PATTERNS = {
    "cap_rate": [
        re.compile(r'(\d+\.?\d*)\s*%?\s*cap\s*rate', re.IGNORECASE),
        re.compile(r'cap\s*rate\s*of\s*(\d+\.?\d*)\s*%?', re.IGNORECASE),
        re.compile(r'(\d+\.?\d*)\s*%\s*cap', re.IGNORECASE),
    ],
    "deal_value": [
        re.compile(r'\$(\d+(?:\.\d+)?)\s*(?:million|M)\b', re.IGNORECASE),
        re.compile(r'\$(\d+(?:\.\d+)?)\s*(?:billion|B)\b', re.IGNORECASE),
        re.compile(r'\$(\d{1,3}(?:,\d{3})+)\b'),
    ],
    "square_footage": [
        re.compile(r'([\d,]+)\s*(?:square[\s-]?feet|sq\.?\s*ft\.?|SF)\b', re.IGNORECASE),
        re.compile(r'([\d,]+)[\s-]?SF\b'),
    ],
    "price_per_sf": [
        re.compile(r'\$(\d+(?:,\d+)?)\s*(?:per|/)\s*(?:square[\s-]?foot|sq\.?\s*ft\.?|SF)\b', re.IGNORECASE),
        re.compile(r'\$(\d+(?:,\d+)?)/SF\b'),
    ],
    "occupancy": [
        re.compile(r'(\d+(?:\.\d+)?)\s*%\s*(?:occupied|occupancy)', re.IGNORECASE),
        re.compile(r'occupancy\s*(?:rate\s*)?of\s*(\d+(?:\.\d+)?)\s*%', re.IGNORECASE),
    ],
}


class EmailServiceError(Exception):
    """Custom exception for email service errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class EmailService:
    """
    Production-ready email service for fetching and parsing newsletters.

    Features:
    - IMAP connection with retry logic
    - HTML email parsing with BeautifulSoup
    - Content extraction for Bisnow newsletters
    - Metric extraction (cap rates, deal values, etc.)
    - Duplicate prevention via database checks
    - Comprehensive error handling and logging
    """

    def __init__(
        self,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None,
        imap_server: Optional[str] = None,
        imap_port: Optional[int] = None
    ):
        """
        Initialize email service with configuration.

        Args:
            email_address: Email address for IMAP connection (falls back to env var)
            email_password: Email password for IMAP (falls back to env var)
            imap_server: IMAP server address (falls back to env var)
            imap_port: IMAP port (falls back to env var)

        If user-specific credentials are provided, they take precedence over
        environment variables. This enables user-specific email fetching.
        """
        # Use provided credentials or fall back to environment variables
        self.email_address = email_address or settings.EMAIL_ADDRESS
        self.email_password = email_password or settings.EMAIL_APP_PASSWORD
        self.imap_server = imap_server or settings.IMAP_SERVER
        self.imap_port = imap_port or settings.IMAP_PORT
        self.connection: Optional[imaplib.IMAP4_SSL] = None

        # Validate required configuration
        if not self.email_address:
            logger.warning("EMAIL_ADDRESS not configured (no user credentials or env vars)")
        if not self.email_password:
            logger.warning("EMAIL_APP_PASSWORD not configured (no user credentials or env vars)")
        if not self.imap_server:
            logger.warning("IMAP_SERVER not configured")
        if not self.imap_port:
            logger.warning("IMAP_PORT not configured")

    def _connect_with_retry(self, max_retries: int = 3) -> imaplib.IMAP4_SSL:
        """
        Connect to IMAP server with exponential backoff retry logic.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            imaplib.IMAP4_SSL: Connected IMAP client

        Raises:
            EmailServiceError: If connection fails after all retries
        """
        # Validate configuration before attempting connection
        if not self.email_address or not self.email_password:
            raise EmailServiceError(
                "Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_APP_PASSWORD environment variables."
            )
        if not self.imap_server:
            raise EmailServiceError(
                "IMAP server not configured. Please set IMAP_SERVER environment variable."
            )
        if not self.imap_port:
            raise EmailServiceError(
                "IMAP port not configured. Please set IMAP_PORT environment variable."
            )

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to IMAP server {self.imap_server}:{self.imap_port} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Create IMAP connection
                connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

                # Login
                connection.login(self.email_address, self.email_password)

                logger.info("Successfully connected to IMAP server")
                return connection

            except imaplib.IMAP4.error as e:
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    logger.warning(
                        f"IMAP connection failed: {str(e)}. "
                        f"Retrying in {sleep_time}s..."
                    )
                    import time
                    time.sleep(sleep_time)
                else:
                    logger.error(f"IMAP connection failed after {max_retries} attempts")
                    raise EmailServiceError(
                        f"Failed to connect to IMAP server: {str(e)}",
                        original_error=e
                    )
            except Exception as e:
                logger.error(f"Unexpected error connecting to IMAP: {str(e)}", exc_info=True)
                raise EmailServiceError(
                    f"Unexpected error connecting to IMAP: {str(e)}",
                    original_error=e
                )

        raise EmailServiceError("Maximum retries exceeded")

    def connect(self) -> None:
        """
        Establish IMAP connection.

        Raises:
            EmailServiceError: If connection fails
        """
        if self.connection is None:
            self.connection = self._connect_with_retry()

    def disconnect(self) -> None:
        """Close IMAP connection gracefully."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.warning(f"Error disconnecting from IMAP: {str(e)}")
            finally:
                self.connection = None

    def _identify_category(self, subject: str) -> str:
        """
        Identify newsletter category from subject line.

        Args:
            subject: Email subject line

        Returns:
            str: Newsletter category or "Unknown"
        """
        subject_lower = subject.lower()

        for category, keywords in BISNOW_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in subject_lower:
                    return category

        # If no match, try to extract location from subject
        if "morning brief" in subject_lower:
            # Extract potential location before "Morning Brief"
            match = re.search(r'(\w+)\s+Morning\s+Brief', subject, re.IGNORECASE)
            if match:
                return f"{match.group(1)} Morning Brief"

        return "Unknown"

    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content.

        Args:
            html_content: HTML string

        Returns:
            str: Extracted plain text
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "head", "title", "meta"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            return text

        except Exception as e:
            logger.error(f"Error extracting text from HTML: {str(e)}")
            return ""

    def _extract_headlines(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract headlines from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List[str]: List of headlines
        """
        headlines = []

        # Look for h1, h2, h3 tags
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            text = tag.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short text
                headlines.append(text)

        # Look for bold text that might be headlines
        for tag in soup.find_all(['b', 'strong']):
            text = tag.get_text(strip=True)
            # Only include if it's relatively short (likely a headline, not a paragraph)
            if text and 10 < len(text) < 200 and text not in headlines:
                headlines.append(text)

        # Limit to first 20 headlines to avoid noise
        return headlines[:20]

    def _extract_metrics(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract real estate metrics from text using regex patterns.

        Args:
            text: Text content to extract from

        Returns:
            List[Dict]: List of extracted metrics with type, value, and context
        """
        metrics = []

        for metric_type, patterns in METRIC_PATTERNS.items():
            for pattern in patterns:
                matches = pattern.finditer(text)

                for match in matches:
                    # Extract value
                    value = match.group(1) if match.groups() else match.group(0)

                    # Get context (surrounding text)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()

                    # Format value based on type
                    formatted_value = value
                    if metric_type == "cap_rate":
                        formatted_value = f"{value}%"
                    elif metric_type == "deal_value":
                        if "billion" in match.group(0).lower() or "B" in match.group(0):
                            formatted_value = f"${value}B"
                        else:
                            formatted_value = f"${value}M"
                    elif metric_type == "square_footage":
                        formatted_value = f"{value} SF"
                    elif metric_type == "price_per_sf":
                        formatted_value = f"${value}/SF"
                    elif metric_type == "occupancy":
                        formatted_value = f"{value}%"

                    metrics.append({
                        "type": metric_type,
                        "value": formatted_value,
                        "context": context
                    })

        # Remove duplicates based on type and value
        seen = set()
        unique_metrics = []
        for metric in metrics:
            key = (metric["type"], metric["value"])
            if key not in seen:
                seen.add(key)
                unique_metrics.append(metric)

        return unique_metrics

    def _extract_locations(self, text: str) -> List[str]:
        """
        Extract location mentions from text.

        Args:
            text: Text content

        Returns:
            List[str]: List of locations
        """
        locations = []

        # Common real estate location patterns
        location_patterns = [
            re.compile(r'\b(Downtown|Uptown|Midtown)\s+(\w+)', re.IGNORECASE),
            re.compile(r'\b(Houston|Austin|Dallas|San Antonio|Fort Worth)\b', re.IGNORECASE),
            re.compile(r'\b(Domain|Galleria|Energy Corridor|Medical Center)\b', re.IGNORECASE),
            re.compile(r'\b([A-Z][a-z]+\s+(?:District|Area|Center|Park|Plaza))\b'),
        ]

        for pattern in location_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                location = match.group(0).strip()
                if location and location not in locations:
                    locations.append(location)

        # Limit to first 15 locations
        return locations[:15]

    def _extract_companies(self, text: str) -> List[str]:
        """
        Extract company mentions from text.

        Args:
            text: Text content

        Returns:
            List[str]: List of companies
        """
        companies = []

        # Common real estate company patterns
        company_patterns = [
            re.compile(r'\b(CBRE|JLL|Cushman & Wakefield|Marcus & Millichap)\b'),
            re.compile(r'\b(Hines|Trammell Crow|Lincoln Property|Greystar)\b'),
            re.compile(r'\b(Brookfield|Blackstone|KKR|Starwood)\b'),
            re.compile(r'\b([A-Z][a-z]+\s+(?:Realty|Properties|Development|Capital|Partners|Group))\b'),
        ]

        for pattern in company_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                company = match.group(0).strip()
                if company and company not in companies:
                    companies.append(company)

        # Limit to first 15 companies
        return companies[:15]

    def _parse_email_content(self, html_content: str, text_content: str) -> Dict[str, Any]:
        """
        Parse email content and extract key points.

        Args:
            html_content: HTML content of email
            text_content: Plain text content

        Returns:
            Dict: Extracted key points
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract headlines
        headlines = self._extract_headlines(soup)

        # Use plain text for metric/entity extraction
        content_for_extraction = text_content if text_content else self._extract_text_from_html(html_content)

        # Extract metrics
        metrics = self._extract_metrics(content_for_extraction)

        # Extract locations
        locations = self._extract_locations(content_for_extraction)

        # Extract companies
        companies = self._extract_companies(content_for_extraction)

        return {
            "headlines": headlines,
            "metrics": metrics,
            "locations": locations,
            "companies": companies
        }

    def _get_email_body(self, msg: Message) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract HTML and text body from email message.

        Args:
            msg: Email message object

        Returns:
            Tuple[Optional[str], Optional[str]]: (html_content, text_content)
        """
        html_content = None
        text_content = None

        try:
            # Handle multipart messages
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()

                    if content_type == "text/html":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_content = payload.decode('utf-8', errors='ignore')
                        except Exception as e:
                            logger.warning(f"Error decoding HTML part: {str(e)}")

                    elif content_type == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                text_content = payload.decode('utf-8', errors='ignore')
                        except Exception as e:
                            logger.warning(f"Error decoding text part: {str(e)}")

            # Handle single-part messages
            else:
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True)

                if payload:
                    decoded = payload.decode('utf-8', errors='ignore')

                    if content_type == "text/html":
                        html_content = decoded
                    elif content_type == "text/plain":
                        text_content = decoded

        except Exception as e:
            logger.error(f"Error extracting email body: {str(e)}", exc_info=True)

        return html_content, text_content

    def fetch_emails(
        self,
        days: int = 7,
        sender_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails from IMAP server.

        Args:
            days: Number of days to look back
            sender_filter: List of sender domains to filter (e.g., ['@bisnow.com'])

        Returns:
            List[Dict]: List of parsed email data

        Raises:
            EmailServiceError: If email fetch fails
        """
        if sender_filter is None:
            sender_filter = [
                '@bisnow.com',
                '@mail.bisnow.com',
                '@publications.bisnow.com',
                '@info.bisnow.com'
            ]

        try:
            # Ensure connection
            if self.connection is None:
                self.connect()

            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")

            # Build search query
            search_criteria = f'(SINCE {since_date})'

            parsed_emails = []

            # Search in multiple folders (INBOX and Gmail All Mail to get Promotions/Social/etc)
            folders_to_search = ['INBOX', '[Gmail]/All Mail']

            for folder in folders_to_search:
                try:
                    # Select folder
                    status, _ = self.connection.select(folder, readonly=True)
                    if status != 'OK':
                        logger.warning(f"Could not access folder: {folder}")
                        continue

                    logger.info(f"Searching {folder} for emails: {search_criteria}")

                    # Search emails
                    status, messages = self.connection.search(None, search_criteria)

                    if status != 'OK':
                        logger.warning(f"Email search failed in {folder} with status: {status}")
                        continue

                    email_ids = messages[0].split()
                    logger.info(f"Found {len(email_ids)} emails in {folder}")

                    # Process each email in this folder
                    for email_id in email_ids:
                        try:
                            # Fetch email
                            status, msg_data = self.connection.fetch(email_id, '(RFC822)')

                            if status != 'OK':
                                logger.warning(f"Failed to fetch email {email_id}")
                                continue

                            # Parse email
                            raw_email = msg_data[0][1]
                            msg = email.message_from_bytes(raw_email)

                            # Get sender
                            sender = msg.get('From', '')

                            # Filter by sender
                            if sender_filter:
                                if not any(domain in sender for domain in sender_filter):
                                    continue

                            # Get subject
                            subject = msg.get('Subject', '')

                            # Get date
                            date_str = msg.get('Date', '')
                            try:
                                from email.utils import parsedate_to_datetime
                                received_date = parsedate_to_datetime(date_str)
                            except Exception:
                                received_date = datetime.now(timezone.utc)

                            # Get email body
                            html_content, text_content = self._get_email_body(msg)

                            # Skip if no content
                            if not html_content and not text_content:
                                logger.warning(f"No content found in email: {subject}")
                                continue

                            # Extract plain text if not available
                            if not text_content and html_content:
                                text_content = self._extract_text_from_html(html_content)

                            # Identify category
                            category = self._identify_category(subject)

                            # Parse content and extract key points
                            key_points = self._parse_email_content(
                                html_content or "",
                                text_content or ""
                            )

                            parsed_email = {
                                "source": sender,
                                "category": category,
                                "subject": subject,
                                "content_html": html_content,
                                "content_text": text_content,
                                "key_points": key_points,
                                "received_date": received_date,
                            }

                            parsed_emails.append(parsed_email)

                            logger.info(
                                f"Parsed email: {subject[:50]}... "
                                f"(category: {category}, metrics: {len(key_points.get('metrics', []))})"
                            )

                        except Exception as e:
                            logger.error(f"Error processing email {email_id}: {str(e)}", exc_info=True)
                            continue

                    # Break after All Mail to avoid processing same emails twice
                    if folder == '[Gmail]/All Mail':
                        break

                except Exception as e:
                    logger.error(f"Error searching folder {folder}: {str(e)}")
                    continue

            return parsed_emails

        except EmailServiceError:
            raise
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
            raise EmailServiceError(
                f"Failed to fetch emails: {str(e)}",
                original_error=e
            )

    async def fetch_and_store_emails(
        self,
        db: AsyncSession,
        days: int = 7,
        sender_filter: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch emails and store them in the database.

        This is an async wrapper that runs the synchronous IMAP operations
        in a thread pool to avoid blocking.

        Args:
            db: Database session
            days: Number of days to look back
            sender_filter: List of sender domains to filter
            user_id: ID of user who owns these newsletters (required for user-specific fetching)

        Returns:
            Dict: Summary of fetch operation

        Raises:
            EmailServiceError: If user_id is not provided or email fetch fails
        """
        # Validate user_id is provided
        if user_id is None:
            raise EmailServiceError(
                "user_id is required for newsletter fetching. "
                "Newsletters must be associated with a specific user."
            )
        try:
            # Run synchronous fetch in thread pool
            logger.info(f"Fetching emails from IMAP for user {user_id} (last {days} days)")
            loop = asyncio.get_event_loop()
            fetch_func = partial(self.fetch_emails, days=days, sender_filter=sender_filter)

            try:
                emails = await loop.run_in_executor(None, fetch_func)
            except EmailServiceError as e:
                # Re-raise email service errors as-is
                logger.error(f"Email fetch failed: {e.message}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during email fetch: {str(e)}", exc_info=True)
                raise EmailServiceError(
                    f"Failed to fetch emails from IMAP: {str(e)}",
                    original_error=e
                )

            if not emails:
                logger.info("No emails found matching criteria")
                return {
                    "status": "success",
                    "fetched": 0,
                    "stored": 0,
                    "skipped": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

            logger.info(f"Fetched {len(emails)} emails, processing for storage")

            # Store emails in database
            stored_count = 0
            skipped_count = 0

            for email_data in emails:
                try:
                    # Check if email already exists for this user
                    result = await db.execute(
                        select(Newsletter).where(
                            and_(
                                Newsletter.user_id == user_id,
                                Newsletter.subject == email_data["subject"],
                                Newsletter.received_date == email_data["received_date"]
                            )
                        )
                    )
                    existing = result.scalar_one_or_none()

                    if existing:
                        logger.debug(f"Newsletter already exists for user {user_id}: {email_data['subject'][:50]}...")
                        skipped_count += 1
                        continue

                    # Create newsletter record with user_id
                    newsletter = Newsletter(
                        user_id=user_id,
                        source=email_data["source"],
                        category=email_data["category"],
                        subject=email_data["subject"],
                        content_html=email_data["content_html"],
                        content_text=email_data["content_text"],
                        key_points=email_data["key_points"],
                        received_date=email_data["received_date"],
                        parsed_date=datetime.now(timezone.utc)
                    )

                    db.add(newsletter)
                    stored_count += 1

                except Exception as e:
                    logger.error(
                        f"Error processing individual email: {email_data.get('subject', 'unknown')[:50]}, "
                        f"error: {str(e)}",
                        exc_info=True
                    )
                    # Continue processing other emails even if one fails
                    continue

            # Commit all newsletters
            try:
                await db.commit()
                logger.info(
                    f"Database commit successful: {stored_count} newsletters stored, "
                    f"{skipped_count} skipped (duplicates)"
                )
            except Exception as e:
                await db.rollback()
                logger.error(f"Database commit failed: {str(e)}", exc_info=True)
                raise EmailServiceError(
                    f"Failed to save newsletters to database: {str(e)}",
                    original_error=e
                )

            logger.info(
                f"Newsletter fetch complete for user {user_id}: {stored_count} stored, "
                f"{skipped_count} skipped (duplicates)"
            )

            return {
                "status": "success",
                "fetched": len(emails),
                "stored": stored_count,
                "skipped": skipped_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except EmailServiceError:
            # Re-raise EmailServiceError as-is
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error in fetch_and_store_emails: {str(e)}", exc_info=True)
            raise EmailServiceError(
                f"Failed to fetch and store emails: {str(e)}",
                original_error=e
            )
        finally:
            # Always disconnect
            self.disconnect()


def get_email_service() -> EmailService:
    """
    Dependency function to get email service instance.

    Returns:
        EmailService: Email service instance
    """
    return EmailService()
