"""
Document processing tool for reading PDF and text files.
"""

from langchain.tools import tool
import json
import os
from typing import Optional


@tool
def read_pdf(file_path: str) -> str:
    """
    Extract text content from PDF documents.
    
    This tool reads PDF files and extracts all text content. Useful for
    analyzing research papers, reports, documentation, and other PDF materials.
    
    Args:
        file_path (str): Path to the PDF file (relative or absolute)
    
    Returns:
        str: Extracted text content from the PDF
    
    Examples:
        >>> read_pdf("./data/research_paper.pdf")
        >>> read_pdf("C:/Documents/report.pdf")
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({
                "status": "error",
                "message": f"File not found: {file_path}",
                "file_path": file_path
            })
        
        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            return json.dumps({
                "status": "error",
                "message": "File must be a PDF (.pdf extension)",
                "file_path": file_path
            })
        
        # Try to import pypdf
        try:
            from pypdf import PdfReader
        except ImportError:
            return json.dumps({
                "status": "error",
                "message": "pypdf library not installed. Run: pip install pypdf",
                "file_path": file_path
            })
        
        # Read PDF
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        
        # Extract text from all pages
        text_content = []
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                text_content.append(f"--- Page {page_num} ---\n{text}")
        
        full_text = "\n\n".join(text_content)
        
        return json.dumps({
            "status": "success",
            "file_path": file_path,
            "num_pages": num_pages,
            "content_length": len(full_text),
            "content": full_text[:10000]  # Limit to first 10k chars
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to read PDF: {str(e)}",
            "file_path": file_path
        })


@tool
def read_text_file(file_path: str) -> str:
    """
    Read content from a text file.
    
    Args:
        file_path (str): Path to the text file
    
    Returns:
        str: File content
    
    Example:
        >>> read_text_file("./data/notes.txt")
    """
    try:
        if not os.path.exists(file_path):
            return json.dumps({
                "status": "error",
                "message": f"File not found: {file_path}"
            })
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return json.dumps({
            "status": "success",
            "file_path": file_path,
            "content_length": len(content),
            "content": content
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to read file: {str(e)}"
        })


@tool
def list_directory(directory_path: str = "./data") -> str:
    """
    List files in a directory.
    
    Args:
        directory_path (str): Path to directory (default: ./data)
    
    Returns:
        str: List of files and directories
    
    Example:
        >>> list_directory("./data")
    """
    try:
        if not os.path.exists(directory_path):
            return json.dumps({
                "status": "error",
                "message": f"Directory not found: {directory_path}"
            })
        
        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None
            })
        
        return json.dumps({
            "status": "success",
            "directory": directory_path,
            "count": len(items),
            "items": items
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to list directory: {str(e)}"
        })
