"""
WordPress REST API Client
Maneja la comunicación con la API REST de WordPress
"""

import requests
import base64
from typing import Dict, Tuple, Optional
import json


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