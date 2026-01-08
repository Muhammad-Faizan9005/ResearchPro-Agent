"""Tools package initialization."""

from .search import web_search, web_search_simple
from .calculator import calculate, percentage_change, compound_growth_rate
from .scraper import scrape_webpage, extract_links
from .document import read_pdf, read_text_file, list_directory
from .storage import store_finding, retrieve_finding, list_all_findings, clear_storage
from .verification import verify_fact, check_source_credibility, citation_formatter

__all__ = [
    # Search tools
    "web_search",
    "web_search_simple",
    # Calculator tools
    "calculate",
    "percentage_change",
    "compound_growth_rate",
    # Scraper tools
    "scrape_webpage",
    "extract_links",
    # Document tools
    "read_pdf",
    "read_text_file",
    "list_directory",
    # Storage tools
    "store_finding",
    "retrieve_finding",
    "list_all_findings",
    "clear_storage",
    # Verification tools
    "verify_fact",
    "check_source_credibility",
    "citation_formatter",
]
