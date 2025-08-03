"""
Image API Integration Module
Handles image fetching from various sources like Shutterstock, Unsplash, and placeholder images
"""

import requests
import base64
import re
import random
from typing import List, Tuple, Optional, Set
from bs4 import BeautifulSoup


class ContentSanitizer:
    """Sanitizes HTML content by removing styles, classes, and data attributes"""
    
    def __init__(self):
        # Attributes to remove from all HTML elements
        self.attributes_to_remove = [
            'style', 'class', 'id', 'data-*', 'onclick', 'onload', 'onerror',
            'onmouseover', 'onmouseout', 'onfocus', 'onblur', 'onchange',
            'onsubmit', 'onreset', 'onselect', 'onkeydown', 'onkeypress',
            'onkeyup', 'width', 'height', 'align', 'valign', 'bgcolor',
            'background', 'border', 'cellpadding', 'cellspacing', 'face',
            'size', 'color'
        ]
        
        # Allowed HTML tags for WordPress content
        self.allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr',
            'strong', 'b', 'em', 'i', 'u', 'strike', 'del',
            'blockquote', 'cite', 'q',
            'ul', 'ol', 'li',
            'a', 'img',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'div', 'span',
            'code', 'pre'
        ]
        
        # Attributes to keep for specific tags
        self.allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title'],
            'blockquote': ['cite'],
            'q': ['cite']
        }
    
    def sanitize_content(self, html_content: str) -> str:
        """
        Sanitize HTML content by removing unwanted attributes and tags
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            str: Sanitized HTML content
        """
        if not html_content or not html_content.strip():
            return html_content
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted tags completely
            self._remove_unwanted_tags(soup)
            
            # Clean attributes from all remaining tags
            self._clean_attributes(soup)
            
            # Return cleaned HTML
            return str(soup)
            
        except Exception as e:
            print(f"Content sanitization error: {str(e)}")
            # Return original content if sanitization fails
            return html_content
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> None:
        """Remove tags that are not in the allowed list"""
        for tag in soup.find_all():
            if tag.name not in self.allowed_tags:
                # Replace tag with its content
                tag.unwrap()
    
    def _clean_attributes(self, soup: BeautifulSoup) -> None:
        """Remove unwanted attributes from all tags"""
        for tag in soup.find_all():
            if not tag.name:
                continue
                
            # Get allowed attributes for this tag
            allowed_attrs = self.allowed_attributes.get(tag.name, [])
            
            # Get all current attributes
            current_attrs = list(tag.attrs.keys())
            
            # Remove unwanted attributes
            for attr in current_attrs:
                should_remove = False
                
                # Check if attribute should be removed
                if attr not in allowed_attrs:
                    should_remove = True
                
                # Special handling for data-* attributes
                if attr.startswith('data-'):
                    should_remove = True
                
                # Remove the attribute
                if should_remove:
                    del tag[attr]
    
    def clean_text_content(self, content: str) -> str:
        """
        Clean content that might be mixed HTML and text
        
        Args:
            content (str): Content to clean
            
        Returns:
            str: Cleaned content
        """
        # First, sanitize any HTML
        sanitized = self.sanitize_content(content)
        
        # Remove extra whitespace and normalize line breaks
        sanitized = re.sub(r'\n\s*\n\s*\n+', '\n\n', sanitized)
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        
        return sanitized.strip()


class ShutterstockAPI:
    """Handles Shutterstock API integration for image search and download"""
    
    def __init__(self, consumer_key: str, secret_key: str):
        self.consumer_key = consumer_key
        self.secret_key = secret_key
        self.base_url = "https://api.shutterstock.com/v2"
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with Shutterstock API using OAuth"""
        try:
            # Use basic auth with consumer key and secret
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.consumer_key,
                'client_secret': self.secret_key
            }
            
            response = requests.post(
                'https://api.shutterstock.com/v2/oauth/access_token',
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def search_images(self, query: str, per_page: int = 10) -> List[dict]:
        """Search for images based on query"""
        if not self.access_token:
            if not self.authenticate():
                return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': query,
                'per_page': min(per_page, 20),  # Limit to avoid quota issues
                'sort': 'popular',
                'orientation': 'horizontal',
                'category': 'business',
                'image_type': 'photo'
            }
            
            response = requests.get(
                f"{self.base_url}/images/search",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])
                
                # Transform to consistent format with proper descriptions
                formatted_results = []
                for image in results:
                    # Extract description from Shutterstock response
                    description = (
                        image.get('description', '') or 
                        image.get('alt', '') or 
                        ', '.join(image.get('keywords', [])[:3]) or  # Use first 3 keywords
                        query
                    )
                    
                    formatted_results.append({
                        'id': image['id'],
                        'description': description,
                        'keywords': image.get('keywords', []),
                        'assets': image.get('assets', {}),
                        'original_data': image  # Keep original for reference
                    })
                
                return formatted_results
            else:
                print(f"Search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_image_download_url(self, image_id: str, size: str = 'medium') -> Optional[str]:
        """Get download URL for a specific image"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # For free accounts, we'll use the preview URL
            # For paid accounts, you would use the licensing endpoint
            response = requests.get(
                f"{self.base_url}/images/{image_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Return preview URL for free accounts
                assets = data.get('assets', {})
                preview = assets.get('preview', {})
                return preview.get('url')
            else:
                print(f"Image details failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Image download error: {str(e)}")
            return None


class UnsplashAPI:
    """Handles Unsplash API integration for high-quality, watermark-free images"""
    
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"
        
    def authenticate(self) -> bool:
        """Test authentication with Unsplash API"""
        if not self.access_key:
            return False
            
        try:
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/photos/random",
                headers=headers,
                params={'count': 1},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Unsplash authentication error: {str(e)}")
            return False
    
    def search_images(self, query: str, per_page: int = 10) -> List[dict]:
        """Search for images on Unsplash"""
        try:
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            params = {
                'query': query,
                'per_page': min(per_page, 10),  # Unsplash allows up to 30
                'orientation': 'landscape',
                'order_by': 'relevant'
            }
            
            response = requests.get(
                f"{self.base_url}/search/photos",
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Transform to consistent format
                formatted_results = []
                for photo in results:
                    formatted_results.append({
                        'id': photo['id'],
                        'description': photo.get('alt_description') or photo.get('description') or query,
                        'urls': photo['urls'],
                        'user': photo['user'],
                        'assets': {
                            'preview': {
                                'url': photo['urls']['regular']  # High quality, no watermark
                            }
                        }
                    })
                
                return formatted_results
            else:
                print(f"Unsplash search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Unsplash search error: {str(e)}")
            return []
    
    def get_image_download_url(self, image_id: str, size: str = 'regular') -> Optional[str]:
        """Get download URL for a specific Unsplash image"""
        try:
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            response = requests.get(
                f"{self.base_url}/photos/{image_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                urls = data.get('urls', {})
                
                # Choose size (regular is good quality ~1080px width)
                size_map = {
                    'small': 'small',
                    'medium': 'regular', 
                    'large': 'full'
                }
                
                selected_size = size_map.get(size, 'regular')
                return urls.get(selected_size, urls.get('regular'))
            else:
                print(f"Unsplash image details failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Unsplash image download error: {str(e)}")
            return None


class ImageProcessor:
    """Processes content and integrates images"""
    
    def __init__(self, image_api, wordpress_api=None):
        """
        Initialize ImageProcessor
        
        Args:
            image_api: Instance of an image API (UnsplashAPI, ShutterstockAPI, or PlaceholderImageAPI)
            wordpress_api: Optional WordPress API instance for uploading images to Media Library
        """
        self.image_api = image_api
        self.wordpress_api = wordpress_api
        self.content_sanitizer = ContentSanitizer()
        self.used_image_ids: Set[str] = set()  # Track used image IDs to prevent duplicates
    
    def extract_keywords_from_content(self, content: str, max_keywords: int = 3) -> List[str]:
        """Extract relevant keywords from content for image search"""
        # Remove HTML tags if any
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Split into words and filter
        words = re.findall(r'\b[a-zA-Z]{4,}\b', clean_content.lower())
        
        # Common stop words to exclude
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
            'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
            'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
            'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your',
            'about', 'after', 'again', 'before', 'being', 'below', 'between',
            'both', 'during', 'each', 'further', 'having', 'into', 'more',
            'most', 'other', 'should', 'through', 'under', 'until', 'while',
            'above', 'against', 'because', 'doing', 'down', 'once', 'only',
            'same', 'there', 'these', 'those', 'where', 'which', 'would'
        }
        
        # Filter out stop words and get unique words
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency and get most common
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    def select_unique_image(self, images: List[dict]) -> Optional[dict]:
        """Select a random image that hasn't been used yet"""
        if not images:
            return None
        
        # Filter out already used images
        available_images = [img for img in images if img['id'] not in self.used_image_ids]
        
        # If all images have been used, reset the tracking and use any image
        if not available_images:
            print("All images from this search have been used, resetting tracking...")
            self.used_image_ids.clear()
            available_images = images
        
        # Select a random image from available ones
        selected_image = random.choice(available_images)
        self.used_image_ids.add(selected_image['id'])
        
        return selected_image
    
    def reset_used_images(self):
        """Reset the tracking of used images for a new post"""
        self.used_image_ids.clear()
        print("Reset used images tracking for new post")
    
    def split_content_by_words(self, content: str, words_per_section: int) -> List[str]:
        """Split content into sections based on word count, respecting paragraph boundaries"""
        # Split content into paragraphs first
        paragraphs = re.split(r'(\n\s*\n|</p>\s*<p>|</p>|<p>)', content)
        
        sections = []
        current_section = ""
        current_word_count = 0
        
        for paragraph in paragraphs:
            # Skip empty paragraphs or HTML tags
            if not paragraph.strip() or paragraph.strip() in ['</p>', '<p>'] or re.match(r'</p>\s*<p>', paragraph.strip()):
                current_section += paragraph
                continue
            
            # Count words in this paragraph
            paragraph_words = len(re.findall(r'\b\w+\b', paragraph))
            
            # If adding this paragraph would exceed the word limit
            if current_word_count > 0 and current_word_count + paragraph_words > words_per_section:
                # Finish current section and start a new one
                sections.append(current_section.strip())
                current_section = paragraph
                current_word_count = paragraph_words
            else:
                # Add paragraph to current section
                current_section += paragraph
                current_word_count += paragraph_words
        
        # Add the last section if it has content
        if current_section.strip():
            sections.append(current_section.strip())
        
        return sections
    
    def insert_images_in_content(self, content: str, words_per_image: int) -> Tuple[str, List[str]]:
        """Insert images into content based on word count and return modified content with image URLs"""
        if not content.strip():
            return content, []
        
        # Reset used images tracking for this new post
        self.reset_used_images()
        
        # First, sanitize the input content to remove unwanted attributes
        print("Sanitizing input content...")
        sanitized_content = self.content_sanitizer.sanitize_content(content)
        
        # Extract keywords for image search from sanitized content
        keywords = self.extract_keywords_from_content(sanitized_content, max_keywords=6)  # Get more keywords
        if not keywords:
            keywords = ['business', 'technology', 'professional', 'modern', 'creative', 'innovation']  # More fallback keywords
        
        # Shuffle keywords for randomness
        random.shuffle(keywords)
        print(f"Using keywords for images: {keywords}")
        
        # Split content into sections respecting paragraph boundaries
        sections = self.split_content_by_words(sanitized_content, words_per_image)
        
        if len(sections) <= 1:
            # Still sanitize even if no images are added
            return self.content_sanitizer.clean_text_content(sanitized_content), []
        
        modified_content = ""
        used_images = []
        
        for i, section in enumerate(sections):
            # Add the section content
            modified_content += section
            
            # Add image after each section except the last one
            if i < len(sections) - 1:
                # Use different keywords for variety
                keyword = keywords[i % len(keywords)]
                
                # Search for more images to increase variety
                images = self.image_api.search_images(keyword, per_page=10)
                
                if images:
                    # Select a random, unique image
                    image = self.select_unique_image(images)
                    
                    if image:
                        image_url = self.image_api.get_image_download_url(image['id'])
                        
                        if image_url:
                            alt_text = image.get('description', keyword)
                            final_image_url = image_url
                            
                            # Try to upload to WordPress Media Library if available
                            if self.wordpress_api:
                                print(f"Uploading image to WordPress Media Library...")
                                success, message, media_data = self.wordpress_api.upload_media(
                                    image_url, 
                                    alt_text=alt_text
                                )
                                
                                if success and media_data:
                                    # Use the WordPress media URL instead
                                    final_image_url = media_data.get('source_url', image_url)
                                    media_id = media_data.get('id', '')
                                    print(f"✓ Image uploaded to Media Library (ID: {media_id})")
                                else:
                                    print(f"⚠ Media upload failed: {message}, using original URL")
                            
                            # Ensure proper spacing and paragraph structure
                            if not modified_content.endswith('\n'):
                                modified_content += '\n'
                            
                            # Add image as a proper paragraph without inline styles
                            image_html = f'\n<p><img src="{final_image_url}" alt="{alt_text}"></p>\n'
                            modified_content += image_html
                            used_images.append(final_image_url)
                            
                            if self.wordpress_api:
                                print(f"Added image from Media Library for keyword '{keyword}' (ID: {image['id']})")
                            else:
                                print(f"Added unique image for keyword '{keyword}' (ID: {image['id']})")
        
        # Final sanitization to ensure clean output
        final_content = self.content_sanitizer.clean_text_content(modified_content)
        
        return final_content, used_images
    
    def sanitize_content_only(self, content: str) -> str:
        """
        Sanitize content without adding images
        
        Args:
            content (str): HTML content to sanitize
            
        Returns:
            str: Sanitized HTML content
        """
        if not content.strip():
            return content
            
        print("Sanitizing content (no images)...")
        return self.content_sanitizer.clean_text_content(content)


class PlaceholderImageAPI:
    """Fallback image API that provides placeholder images"""
    
    def __init__(self):
        self.base_url = "https://picsum.photos"
        
    def authenticate(self) -> bool:
        """No authentication needed for placeholder images"""
        return True
    
    def search_images(self, query: str, per_page: int = 10) -> List[dict]:
        """Return placeholder image data with descriptive alt text"""
        images = []
        # Generate more unique random seeds
        base_seed = hash(query) % 10000
        
        # Create more descriptive alt text variations
        alt_variations = [
            f"Professional {query} image",
            f"High-quality {query} photo",
            f"Modern {query} illustration",
            f"Creative {query} design",
            f"Business {query} concept",
            f"Abstract {query} background",
            f"Minimalist {query} artwork",
            f"Contemporary {query} visual"
        ]
        
        for i in range(min(per_page, 10)):  # Allow up to 10 placeholder images
            random_seed = base_seed + i * 137 + random.randint(1, 1000)  # More randomness
            alt_text = alt_variations[i % len(alt_variations)]
            
            images.append({
                'id': f'placeholder_{random_seed}_{i}',
                'description': alt_text,
                'assets': {
                    'preview': {
                        'url': f"{self.base_url}/800/400?random={random_seed}"
                    }
                }
            })
        return images
    
    def get_image_download_url(self, image_id: str, size: str = 'medium') -> Optional[str]:
        """Return placeholder image URL"""
        # Extract random seed from image_id
        try:
            seed = image_id.split('_')[-1]
            return f"{self.base_url}/800/400?random={seed}"
        except:
            return f"{self.base_url}/800/400"


def create_image_processor(image_source: str, unsplash_key: str = None, 
                          shutterstock_consumer_key: str = None, shutterstock_secret_key: str = None,
                          wordpress_api=None) -> ImageProcessor:
    """Factory function to create ImageProcessor with specified image source"""
    
    if image_source == "Unsplash":
        if unsplash_key:
            unsplash_api = UnsplashAPI(unsplash_key)
            if unsplash_api.authenticate():
                print("Using Unsplash API for images")
                return ImageProcessor(unsplash_api, wordpress_api)
            else:
                print("Unsplash authentication failed, falling back to placeholder images")
        else:
            print("Unsplash key not provided, falling back to placeholder images")
    
    elif image_source == "Shutterstock":
        if shutterstock_consumer_key and shutterstock_secret_key:
            shutterstock_api = ShutterstockAPI(shutterstock_consumer_key, shutterstock_secret_key)
            if shutterstock_api.authenticate():
                print("Using Shutterstock API for images")
                return ImageProcessor(shutterstock_api, wordpress_api)
            else:
                print("Shutterstock authentication failed, falling back to placeholder images")
        else:
            print("Shutterstock credentials not provided, falling back to placeholder images")
    
    elif image_source == "Placeholder":
        print("Using placeholder images")
        placeholder_api = PlaceholderImageAPI()
        return ImageProcessor(placeholder_api, wordpress_api)
    
    # Default fallback to placeholder images
    print("Using placeholder images as fallback")
    placeholder_api = PlaceholderImageAPI()
    return ImageProcessor(placeholder_api, wordpress_api)