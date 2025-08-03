"""
WordPress REST API Client
Maneja la comunicación con la API REST de WordPress
"""

import requests
import base64
from typing import Dict, Tuple, Optional
import json
import os
import re
import unicodedata
from urllib.parse import urlparse


class WordPressAPI:
    """Cliente para interactuar con la WordPress REST API"""
    
    def __init__(self, url: str, username: str, password: str):
        """
        Inicializa el cliente de WordPress API
        
        Args:
            url: URL del sitio WordPress (ej: https://misitio.com)
            username: Nombre de usuario de WordPress
            password: Contraseña de WordPress
        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.url}/wp-json/wp/v2"
        
        # Crear headers de autenticación
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json',
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Verifica la conexión con WordPress
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Intentar obtener información del usuario actual
            response = requests.get(
                f"{self.api_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"Conexión exitosa. Bienvenido, {user_data.get('name', 'Usuario')}"
            elif response.status_code == 401:
                return False, "Credenciales incorrectas. Verifica tu usuario y contraseña."
            elif response.status_code == 404:
                return False, "No se pudo encontrar la API de WordPress. Verifica la URL."
            else:
                return False, f"Error de conexión: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "No se pudo conectar al sitio. Verifica la URL y tu conexión a internet."
        except requests.exceptions.Timeout:
            return False, "Tiempo de espera agotado. El sitio no responde."
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def create_post(self, title: str, content: str, status: str = 'publish', slug: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Crea un nuevo post en WordPress
        
        Args:
            title: Título del post
            content: Contenido del post
            status: Estado del post ('publish', 'draft', 'private')
            slug: Slug personalizado para el permalink (opcional)
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos del post)
        """
        try:
            post_data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            # Agregar slug si se proporciona
            if slug and slug.strip():
                post_data['slug'] = slug.strip()
            
            response = requests.post(
                f"{self.api_url}/posts",
                headers=self.headers,
                data=json.dumps(post_data),
                timeout=30
            )
            
            if response.status_code == 201:
                post_info = response.json()
                post_url = post_info.get('link', '')
                return True, f"Post publicado exitosamente!\nURL: {post_url}", post_info
            elif response.status_code == 401:
                return False, "No tienes permisos para publicar posts.", None
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('message', 'Datos del post inválidos')
                return False, f"Error en los datos: {error_msg}", None
            else:
                return False, f"Error al publicar: {response.status_code}", None
                
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión al publicar el post.", None
        except requests.exceptions.Timeout:
            return False, "Tiempo de espera agotado al publicar.", None
        except Exception as e:
            return False, f"Error inesperado al publicar: {str(e)}", None
    
    def _generate_seo_filename(self, alt_text: str, image_url: str) -> str:
        """
        Generate SEO-friendly filename from alt text
        
        Args:
            alt_text: Alt text description of the image
            image_url: Original image URL to determine file extension
            
        Returns:
            str: SEO-friendly filename
        """
        if not alt_text or alt_text.strip() == "":
            # Fallback to URL-based filename
            parsed_url = urlparse(image_url)
            base_filename = os.path.basename(parsed_url.path)
            if base_filename and '.' in base_filename:
                return base_filename
            return f"image_{hash(image_url) % 10000}.jpg"
        
        # Clean and normalize the alt text
        filename = alt_text.strip().lower()
        
        # Remove or replace problematic characters
        filename = re.sub(r'[^\w\s-]', '', filename)  # Remove special chars except spaces and hyphens
        filename = re.sub(r'\s+', '-', filename)      # Replace spaces with hyphens
        filename = re.sub(r'-+', '-', filename)       # Replace multiple hyphens with single
        filename = filename.strip('-')                # Remove leading/trailing hyphens
        
        # Normalize unicode characters (remove accents)
        filename = unicodedata.normalize('NFD', filename)
        filename = ''.join(c for c in filename if unicodedata.category(c) != 'Mn')
        
        # Limit length to avoid filesystem issues
        if len(filename) > 50:
            filename = filename[:50].rstrip('-')
        
        # Ensure we have a valid filename
        if not filename:
            filename = f"image_{hash(alt_text) % 10000}"
        
        # Determine file extension from URL or content type
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path)
        
        if original_filename and '.' in original_filename:
            extension = os.path.splitext(original_filename)[1].lower()
            if extension in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                return f"{filename}{extension}"
        
        # Default to .jpg if no extension found
        return f"{filename}.jpg"

    def get_posts(self, per_page: int = 10) -> Tuple[bool, str, Optional[list]]:
        """
        Obtiene una lista de posts del sitio
        
        Args:
            per_page: Número de posts a obtener
            
        Returns:
            Tuple[bool, str, Optional[list]]: (éxito, mensaje, lista de posts)
        """
        try:
            response = requests.get(
                f"{self.api_url}/posts",
                headers=self.headers,
                params={'per_page': per_page},
                timeout=10
            )
            
            if response.status_code == 200:
                posts = response.json()
                return True, f"Se obtuvieron {len(posts)} posts", posts
            else:
                return False, f"Error al obtener posts: {response.status_code}", None
                
        except Exception as e:
            return False, f"Error al obtener posts: {str(e)}", None
    
    def upload_media(self, image_url: str, filename: str = None, alt_text: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Upload an image from URL to WordPress Media Library
        
        Args:
            image_url: URL of the image to upload
            filename: Custom filename (optional, will be generated from URL if not provided)
            alt_text: Alt text for the image (optional)
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, media_data)
        """
        try:
            # Download the image from the URL
            print(f"Downloading image from: {image_url}")
            image_response = requests.get(image_url, timeout=30)
            
            if image_response.status_code != 200:
                return False, f"Failed to download image: {image_response.status_code}", None
            
            # Generate SEO-friendly filename from alt text if not provided
            if not filename:
                filename = self._generate_seo_filename(alt_text, image_url)
                print(f"Generated SEO filename: {filename}")
            
            # Prepare headers for media upload
            media_headers = {
                'Authorization': self.headers['Authorization'],
                'Content-Disposition': f'attachment; filename="{filename}"',
            }
            
            # Set content type based on file extension
            if filename.lower().endswith('.png'):
                media_headers['Content-Type'] = 'image/png'
            elif filename.lower().endswith('.webp'):
                media_headers['Content-Type'] = 'image/webp'
            else:
                media_headers['Content-Type'] = 'image/jpeg'
            
            # Upload to WordPress Media Library
            print(f"Uploading image to WordPress Media Library: {filename}")
            upload_response = requests.post(
                f"{self.api_url}/media",
                headers=media_headers,
                data=image_response.content,
                timeout=60
            )
            
            if upload_response.status_code == 201:
                media_data = upload_response.json()
                
                # Update alt text if provided
                if alt_text:
                    media_id = media_data['id']
                    alt_update_data = {'alt_text': alt_text}
                    
                    requests.post(
                        f"{self.api_url}/media/{media_id}",
                        headers=self.headers,
                        data=json.dumps(alt_update_data),
                        timeout=10
                    )
                
                media_url = media_data.get('source_url', '')
                media_id = media_data.get('id', '')
                print(f"Image uploaded successfully! Media ID: {media_id}")
                
                return True, f"Image uploaded to Media Library (ID: {media_id})", media_data
            
            elif upload_response.status_code == 401:
                return False, "No tienes permisos para subir archivos al Media Library.", None
            elif upload_response.status_code == 413:
                return False, "El archivo es demasiado grande para subir.", None
            else:
                error_data = upload_response.json() if upload_response.content else {}
                error_msg = error_data.get('message', f'Error {upload_response.status_code}')
                return False, f"Error al subir imagen: {error_msg}", None
                
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión al subir la imagen.", None
        except requests.exceptions.Timeout:
            return False, "Tiempo de espera agotado al subir la imagen.", None
        except Exception as e:
            return False, f"Error inesperado al subir imagen: {str(e)}", None