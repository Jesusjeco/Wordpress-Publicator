"""HTML Cleaner for WordPress Content

This module provides functionality to sanitize HTML content by removing
all styling attributes, data attributes, classes, and IDs while preserving
essential HTML structure and content for WordPress compatibility.
"""

import re
from bs4 import BeautifulSoup, NavigableString
from typing import List, Set


class HTMLCleaner:
    """HTML content sanitizer for WordPress publishing"""
    
    def __init__(self):
        # Define allowed HTML tags
        self.allowed_tags: Set[str] = {
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr',
            'strong', 'b', 'em', 'i', 'u',
            'ul', 'ol', 'li',
            'a', 'img',
            'blockquote', 'pre', 'code',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'div', 'span'
        }
        
        # Define allowed attributes for specific tags
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'blockquote': ['cite']
        }
        
        # Attributes to completely remove
        self.forbidden_attributes: Set[str] = {
            'style', 'class', 'id', 'onclick', 'onload', 'onerror',
            'onmouseover', 'onmouseout', 'onfocus', 'onblur'
        }
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML content by removing unwanted attributes and tags
        
        Args:
            html_content (str): Raw HTML content to clean
            
        Returns:
            str: Cleaned HTML content suitable for WordPress
        """
        if not html_content or not html_content.strip():
            return ""
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Clean all elements
            self._clean_element(soup)
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Remove any remaining data attributes using regex as fallback
            cleaned_html = self._remove_data_attributes_regex(cleaned_html)
            
            # Clean up extra whitespace
            cleaned_html = self._normalize_whitespace(cleaned_html)
            
            return cleaned_html.strip()
            
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            # Fallback: return text content only if parsing fails
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
    
    def _clean_element(self, element):
        """Recursively clean an element and its children"""
        if hasattr(element, 'name') and element.name:
            # Remove forbidden tags completely
            if element.name not in self.allowed_tags:
                # Replace with its contents safely
                try:
                    element.unwrap()
                except ValueError:
                    # If unwrap fails, just remove the element
                    element.extract()
                return
            
            # Clean attributes
            self._clean_attributes(element)
        
        # Recursively clean children
        if hasattr(element, 'children'):
            for child in list(element.children):
                if not isinstance(child, NavigableString):
                    self._clean_element(child)
    
    def _clean_attributes(self, element):
        """Remove unwanted attributes from an element"""
        if not hasattr(element, 'attrs'):
            return
        
        # Get allowed attributes for this tag
        allowed_for_tag = self.allowed_attributes.get(element.name, [])
        
        # Remove all attributes that are not allowed
        attrs_to_remove = []
        for attr_name in element.attrs:
            # Remove if it's a forbidden attribute
            if attr_name in self.forbidden_attributes:
                attrs_to_remove.append(attr_name)
            # Remove if it's a data attribute
            elif attr_name.startswith('data-'):
                attrs_to_remove.append(attr_name)
            # Remove if it's not in the allowed list for this tag
            elif attr_name not in allowed_for_tag:
                attrs_to_remove.append(attr_name)
        
        # Remove the attributes
        for attr in attrs_to_remove:
            del element.attrs[attr]
    
    def _remove_data_attributes_regex(self, html: str) -> str:
        """Remove any remaining data attributes using regex"""
        # Remove data-* attributes
        html = re.sub(r'\s+data-[\w-]+=["\'][^"\'>]*["\']', '', html)
        
        # Remove style attributes
        html = re.sub(r'\s+style=["\'][^"\'>]*["\']', '', html)
        
        # Remove class attributes
        html = re.sub(r'\s+class=["\'][^"\'>]*["\']', '', html)
        
        # Remove id attributes
        html = re.sub(r'\s+id=["\'][^"\'>]*["\']', '', html)
        
        return html
    
    def _normalize_whitespace(self, html: str) -> str:
        """Normalize whitespace in HTML"""
        # Remove extra spaces between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove extra spaces within tags
        html = re.sub(r'\s+', ' ', html)
        
        # Clean up empty attributes
        html = re.sub(r'\s+>', '>', html)
        
        return html
    
    def clean_text_content(self, html_content: str) -> str:
        """Extract and return only text content without any HTML tags
        
        Args:
            html_content (str): HTML content to extract text from
            
        Returns:
            str: Plain text content
        """
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Error extracting text: {e}")
            return html_content
    
    def preview_cleaning(self, html_content: str) -> dict:
        """Preview what will be cleaned from the HTML
        
        Args:
            html_content (str): HTML content to analyze
            
        Returns:
            dict: Analysis of what will be removed
        """
        analysis = {
            'original_length': len(html_content),
            'style_attributes': 0,
            'data_attributes': 0,
            'class_attributes': 0,
            'id_attributes': 0,
            'forbidden_tags': [],
            'cleaned_length': 0
        }
        
        # Count attributes that will be removed
        analysis['style_attributes'] = len(re.findall(r'style=["\'][^"\'>]*["\']', html_content))
        analysis['data_attributes'] = len(re.findall(r'data-[\w-]+=["\'][^"\'>]*["\']', html_content))
        analysis['class_attributes'] = len(re.findall(r'class=["\'][^"\'>]*["\']', html_content))
        analysis['id_attributes'] = len(re.findall(r'id=["\'][^"\'>]*["\']', html_content))
        
        # Find forbidden tags
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup.find_all():
            if element.name not in self.allowed_tags:
                if element.name not in analysis['forbidden_tags']:
                    analysis['forbidden_tags'].append(element.name)
        
        # Get cleaned length
        cleaned = self.clean_html(html_content)
        analysis['cleaned_length'] = len(cleaned)
        analysis['reduction_percentage'] = round(
            ((analysis['original_length'] - analysis['cleaned_length']) / analysis['original_length']) * 100, 2
        ) if analysis['original_length'] > 0 else 0
        
        return analysis


def clean_html_content(html_content: str) -> str:
    """Convenience function to clean HTML content
    
    Args:
        html_content (str): HTML content to clean
        
    Returns:
        str: Cleaned HTML content
    """
    cleaner = HTMLCleaner()
    return cleaner.clean_html(html_content)


def demo_cleaning():
    """Demonstrate the HTML cleaning functionality"""
    sample_html = '''
    <h1 style="font-weight: 400; color: #333;" data-attribute="main-title" class="header-main">The Importance of Sleep for Overall Health and Well-being</h1>
    
    <p style="margin: 15px 0;" data-content="intro">Quality sleep is one of the most fundamental pillars of good health, yet it's often the first thing we sacrifice in our busy lives. Getting adequate, restorative sleep affects virtually every aspect of our physical and mental well-being, from immune function to cognitive performance and emotional regulation.</p>
    
    <h2 style="font-weight: 300; font-size: 24px;" data-section="cycles" id="sleep-cycles">Understanding Sleep Cycles and Quality</h2>
    
    <p data-paragraph="1" style="line-height: 1.6;">Sleep occurs in cycles, with each cycle lasting approximately 90 minutes and consisting of different stages including light sleep, deep sleep, and REM (Rapid Eye Movement) sleep. Each stage serves specific functions in physical recovery, memory consolidation, and brain detoxification.</p>
    
    <ul style="padding-left: 20px;" data-list="quality-signs" class="bullet-list">
    <li data-item="1" style="margin-bottom: 5px;">Falling asleep within 15-20 minutes of lying down</li>
    <li data-item="2" class="list-item">Sleeping through the night with minimal interruptions</li>
    <li style="color: #666;" data-point="3">Waking up feeling refreshed and alert</li>
    </ul>
    '''
    
    cleaner = HTMLCleaner()
    
    print("=== HTML CLEANER DEMO ===")
    print("\nOriginal HTML:")
    print(sample_html)
    
    print("\n=== CLEANING ANALYSIS ===")
    analysis = cleaner.preview_cleaning(sample_html)
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    print("\n=== CLEANED HTML ===")
    cleaned = cleaner.clean_html(sample_html)
    print(cleaned)
    
    print("\n=== TEXT ONLY ===")
    text_only = cleaner.clean_text_content(sample_html)
    print(text_only)


if __name__ == "__main__":
    demo_cleaning()