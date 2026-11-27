"""
Connection string validation and security module.
Provides basic sanitization for display purposes.
"""
import logging
from html import escape
from pymongo.uri_parser import parse_uri

logger = logging.getLogger(__name__)


def sanitize_for_display(connection_string):
    """
    Sanitize connection string for safe HTML display.
    Removes credentials and escapes HTML special characters.
    
    Args:
        connection_string (str): Connection string to sanitize
        
    Returns:
        str: Sanitized string safe for HTML display
    """
    try:
        parsed = parse_uri(connection_string)
        hosts = parsed['nodelist']
        hosts_str = ", ".join([f"{escape(str(host))}:{escape(str(port))}" for host, port in hosts])
        
        # Include database name if present (without credentials)
        database = parsed.get('database', '')
        if database:
            return f"{hosts_str} (database: {escape(database)})"
        return hosts_str
    except Exception as e:
        # Parser messages can echo parts of the URI, including the password.
        logger.error(
            "Error sanitizing connection string for display: %s", type(e).__name__
        )
        return "[Connection String Provided]"
