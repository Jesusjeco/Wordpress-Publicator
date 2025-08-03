"""
WordPress Publicator - Aplicación principal
Una herramienta de escritorio para publicar posts en WordPress
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from dotenv import load_dotenv
from wordpress_api import WordPressAPI
from image_api import create_image_processor

# Cargar variables de entorno
load_dotenv()


class WordPressPublicator:
    """Aplicación principal para publicar en WordPress"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress Publicator")
        self.root.geometry("1500x800")
        self.root.resizable(True, True)
        
        # Variables para almacenar la conexión
        self.wp_api = None
        self.connection_verified = False
        
        # Variables para API de imágenes
        self.shutterstock_consumer_key = os.getenv('SHUTTERSTOCK_CONSUMER_KEY', '')
        self.shutterstock_secret_key = os.getenv('SHUTTERSTOCK_SECRET_KEY', '')
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        
        # Configurar el estilo
        self.setup_styles()
        
        # Crear la interfaz
        self.create_widgets()
        
        # Centrar la ventana
        self.center_window()
        
        # Auto-verificar conexión si hay datos del .env
        self.auto_verify_if_env_loaded()
    
    def setup_styles(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="WordPress Publicator", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sección de conexión
        self.create_connection_section(main_frame, 1)
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        # Sección de publicación
        self.create_post_section(main_frame, 7)
        
        # Estado de la aplicación
        env_loaded = all([os.getenv('WORDPRESS_URL'), os.getenv('WORDPRESS_USERNAME'), os.getenv('WORDPRESS_PASSWORD')])
        initial_status = "Datos cargados desde .env - Verificando conexión..." if env_loaded else "Listo para conectar"
        self.status_var = tk.StringVar(value=initial_status)
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=15, column=0, columnspan=2, pady=(20, 0))
    
    def create_connection_section(self, parent, start_row):
        """Crea la sección de conexión a WordPress"""
        # Título de sección
        conn_title = ttk.Label(parent, text="Configuración de WordPress", style='Section.TLabel')
        conn_title.grid(row=start_row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # URL de WordPress
        ttk.Label(parent, text="URL de WordPress:").grid(row=start_row+1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=os.getenv('WORDPRESS_URL', ''))
        url_entry = ttk.Entry(parent, textvariable=self.url_var, width=50)
        url_entry.grid(row=start_row+1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Usuario
        ttk.Label(parent, text="Usuario:").grid(row=start_row+2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=os.getenv('WORDPRESS_USERNAME', ''))
        username_entry = ttk.Entry(parent, textvariable=self.username_var, width=50)
        username_entry.grid(row=start_row+2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Contraseña
        ttk.Label(parent, text="Contraseña:").grid(row=start_row+3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=os.getenv('WORDPRESS_PASSWORD', ''))
        password_entry = ttk.Entry(parent, textvariable=self.password_var, show="*", width=50)
        password_entry.grid(row=start_row+3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botón de verificación
        self.verify_btn = ttk.Button(parent, text="Verificar Conexión", command=self.verify_connection)
        self.verify_btn.grid(row=start_row+4, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Estado de conexión
        self.connection_status_var = tk.StringVar(value="No conectado")
        self.connection_status_label = ttk.Label(parent, textvariable=self.connection_status_var)
        self.connection_status_label.grid(row=start_row+4, column=1, sticky=tk.E, pady=10)
    
    def create_post_section(self, parent, start_row):
        """Crea la sección de publicación de posts"""
        # Título de sección
        post_title = ttk.Label(parent, text="Crear Nuevo Post", style='Section.TLabel')
        post_title.grid(row=start_row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Título del post
        ttk.Label(parent, text="Título del Post:").grid(row=start_row+1, column=0, sticky=tk.W, pady=5)
        self.post_title_var = tk.StringVar()
        title_entry = ttk.Entry(parent, textvariable=self.post_title_var, width=50)
        title_entry.grid(row=start_row+1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Vincular cambios en el título para auto-generar permalink
        self.post_title_var.trace_add('write', self._on_title_change)
        
        # Permalink personalizado
        ttk.Label(parent, text="Permalink (opcional):").grid(row=start_row+2, column=0, sticky=tk.W, pady=5)
        
        # Frame para permalink y botón
        permalink_frame = ttk.Frame(parent)
        permalink_frame.grid(row=start_row+2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.permalink_var = tk.StringVar()
        permalink_entry = ttk.Entry(permalink_frame, textvariable=self.permalink_var, width=40)
        permalink_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botón para generar permalink
        generate_btn = ttk.Button(permalink_frame, text="Generar", command=self._generate_permalink_from_title)
        generate_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Etiqueta de ayuda para permalink
        permalink_help = ttk.Label(parent, text="Se genera automáticamente del título. Ej: mi-post-personalizado", 
                                 font=('TkDefaultFont', 8), foreground='gray')
        permalink_help.grid(row=start_row+3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Sección de configuración de imágenes
        # Separador visual
        separator = ttk.Separator(parent, orient='horizontal')
        separator.grid(row=start_row+4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Título de sección de imágenes
        images_title = ttk.Label(parent, text="Image Settings", font=('TkDefaultFont', 9, 'bold'))
        images_title.grid(row=start_row+5, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Checkbox para habilitar/deshabilitar imágenes
        self.enable_images_var = tk.BooleanVar(value=False)
        enable_images_cb = ttk.Checkbutton(parent, text="Add images to post content", 
                                         variable=self.enable_images_var,
                                         command=self._on_images_toggle)
        enable_images_cb.grid(row=start_row+6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Frame para configuraciones de imagen (inicialmente deshabilitado)
        self.images_config_frame = ttk.Frame(parent)
        self.images_config_frame.grid(row=start_row+7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Número de palabras por imagen
        ttk.Label(self.images_config_frame, text="Words per image:").grid(row=0, column=0, sticky=tk.W, padx=(20, 10))
        self.words_per_image_var = tk.StringVar(value="200")
        words_spinbox = ttk.Spinbox(self.images_config_frame, from_=50, to=1000, increment=50, 
                                  textvariable=self.words_per_image_var, width=10, state='disabled')
        words_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Fuente de imágenes
        ttk.Label(self.images_config_frame, text="Image source:").grid(row=1, column=0, sticky=tk.W, padx=(20, 10))
        self.image_source_var = tk.StringVar(value="Unsplash")
        image_source_combo = ttk.Combobox(self.images_config_frame, textvariable=self.image_source_var,
                                        values=["Unsplash", "Shutterstock", "Placeholder"], state='disabled', width=15)
        image_source_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Checkbox para subir imágenes a WordPress Media Library
        self.upload_to_media_var = tk.BooleanVar(value=True)
        upload_media_cb = ttk.Checkbutton(self.images_config_frame, text="Upload images to WordPress Media Library", 
                                        variable=self.upload_to_media_var, state='disabled')
        upload_media_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=(20, 0), pady=5)
        
        # Etiqueta de ayuda para media upload
        media_help = ttk.Label(self.images_config_frame, 
                             text="When enabled, images are uploaded to your WordPress Media Library for better management", 
                             font=('TkDefaultFont', 8), foreground='gray')
        media_help.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        # Guardar referencias para habilitar/deshabilitar
        self.words_spinbox = words_spinbox
        self.image_source_combo = image_source_combo
        self.upload_media_cb = upload_media_cb
        
        # Contenido del post
        ttk.Label(parent, text="Contenido:").grid(row=start_row+8, column=0, sticky=(tk.W, tk.N), pady=5)
        self.content_text = scrolledtext.ScrolledText(parent, width=60, height=15, wrap=tk.WORD)
        self.content_text.grid(row=start_row+8, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        # Configurar expansión del contenido
        parent.rowconfigure(start_row+8, weight=1)
        
        # Frame para botones
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=start_row+9, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Botones de acción
        self.publish_btn = ttk.Button(button_frame, text="Publicar Post", command=self.publish_post, state='disabled')
        self.publish_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.draft_btn = ttk.Button(button_frame, text="Guardar como Borrador", command=self.save_draft, state='disabled')
        self.draft_btn.pack(side=tk.LEFT)
        
        # Botón para limpiar
        clear_btn = ttk.Button(button_frame, text="Limpiar Campos", command=self.clear_post_fields)
        clear_btn.pack(side=tk.RIGHT)
    
    def verify_connection(self):
        """Verifica la conexión con WordPress en un hilo separado"""
        if not all([self.url_var.get(), self.username_var.get(), self.password_var.get()]):
            messagebox.showerror("Error", "Por favor, completa todos los campos de conexión.")
            return
        
        # Deshabilitar botón durante la verificación
        self.verify_btn.config(state='disabled', text="Verificando...")
        self.connection_status_var.set("Verificando...")
        
        # Ejecutar verificación en hilo separado
        thread = threading.Thread(target=self._verify_connection_thread)
        thread.daemon = True
        thread.start()
    
    def _verify_connection_thread(self):
        """Hilo para verificar la conexión"""
        try:
            self.wp_api = WordPressAPI(
                self.url_var.get(),
                self.username_var.get(),
                self.password_var.get()
            )
            
            success, message = self.wp_api.test_connection()
            
            # Actualizar UI en el hilo principal
            self.root.after(0, self._update_connection_result, success, message)
            
        except Exception as e:
            self.root.after(0, self._update_connection_result, False, f"Error: {str(e)}")
    
    def _update_connection_result(self, success, message):
        """Actualiza la UI con el resultado de la verificación"""
        self.verify_btn.config(state='normal', text="Verificar Conexión")
        
        if success:
            self.connection_verified = True
            self.connection_status_var.set("✓ Conectado")
            self.connection_status_label.config(style='Success.TLabel')
            self.publish_btn.config(state='normal')
            self.draft_btn.config(state='normal')
            self.status_var.set("Conexión verificada. Listo para publicar.")
            messagebox.showinfo("Éxito", message)
        else:
            self.connection_verified = False
            self.connection_status_var.set("✗ Error")
            self.connection_status_label.config(style='Error.TLabel')
            self.publish_btn.config(state='disabled')
            self.draft_btn.config(state='disabled')
            self.status_var.set("Error de conexión")
            messagebox.showerror("Error de Conexión", message)
    
    def publish_post(self):
        """Publica el post en WordPress"""
        self._create_post('publish')
    
    def save_draft(self):
        """Guarda el post como borrador"""
        self._create_post('draft')
    
    def _create_post(self, status):
        """Crea un post con el estado especificado"""
        if not self.connection_verified:
            messagebox.showerror("Error", "Primero debes verificar la conexión con WordPress.")
            return
        
        title = self.post_title_var.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        permalink = self.permalink_var.get().strip()
        
        if not title:
            messagebox.showerror("Error", "El título del post es obligatorio.")
            return
        
        if not content:
            messagebox.showerror("Error", "El contenido del post es obligatorio.")
            return
        
        # Validar permalink si se proporciona
        if permalink:
            # Validación básica del permalink
            import re
            if not re.match(r'^[a-z0-9-]+$', permalink):
                messagebox.showerror("Error", "El permalink solo puede contener letras minúsculas, números y guiones.")
                return
        
        # Deshabilitar botones durante la publicación
        self.publish_btn.config(state='disabled')
        self.draft_btn.config(state='disabled')
        
        action = "Publicando" if status == 'publish' else "Guardando borrador"
        self.status_var.set(f"{action}...")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._create_post_thread, args=(title, content, status, permalink))
        thread.daemon = True
        thread.start()
    
    def _create_post_thread(self, title, content, status, permalink=None):
        """Hilo para crear el post"""
        try:
            # Always sanitize content for WordPress compatibility
            processed_content = content
            
            if self.enable_images_var.get():
                self.root.after(0, lambda: self.status_var.set("Processing images and sanitizing content..."))
                
                # Create image processor based on selected source
                try:
                    selected_source = self.image_source_var.get()
                    # Only pass WordPress API if media upload is enabled
                    wp_api_for_upload = self.wp_api if self.upload_to_media_var.get() else None
                    
                    image_processor = create_image_processor(
                        image_source=selected_source,
                        unsplash_key=self.unsplash_access_key,
                        shutterstock_consumer_key=self.shutterstock_consumer_key,
                        shutterstock_secret_key=self.shutterstock_secret_key,
                        wordpress_api=wp_api_for_upload  # Pass WordPress API only if media upload enabled
                    )
                    
                    words_per_image = int(self.words_per_image_var.get())
                    processed_content, used_images = image_processor.insert_images_in_content(
                        content, words_per_image
                    )
                    
                    if used_images:
                        self.root.after(0, lambda: self.status_var.set(f"Added {len(used_images)} images. Creating post..."))
                    else:
                        self.root.after(0, lambda: self.status_var.set("Content sanitized. Creating post..."))
                        
                except Exception as img_error:
                    print(f"Image processing error: {str(img_error)}")
                    self.root.after(0, lambda: self.status_var.set("Image processing failed. Sanitizing content..."))
                    # Fallback to content-only sanitization if image processing fails
                    try:
                        from image_api import ImageProcessor
                        image_processor = ImageProcessor()
                        processed_content = image_processor.sanitize_content_only(content)
                    except Exception as sanitize_error:
                        print(f"Content sanitization error: {str(sanitize_error)}")
                        processed_content = content
            else:
                # Images disabled - only sanitize content
                self.root.after(0, lambda: self.status_var.set("Sanitizing content..."))
                try:
                    from image_api import ImageProcessor
                    image_processor = ImageProcessor()
                    processed_content = image_processor.sanitize_content_only(content)
                    self.root.after(0, lambda: self.status_var.set("Content sanitized. Creating post..."))
                except Exception as sanitize_error:
                    print(f"Content sanitization error: {str(sanitize_error)}")
                    self.root.after(0, lambda: self.status_var.set("Sanitization failed. Creating post with original content..."))
                    processed_content = content
            
            # Create the post with processed content
            success, message, post_data = self.wp_api.create_post(title, processed_content, status, permalink)
            self.root.after(0, self._update_post_result, success, message, status)
        except Exception as e:
            self.root.after(0, self._update_post_result, False, f"Error: {str(e)}", status)
    
    def _update_post_result(self, success, message, status):
        """Actualiza la UI con el resultado de la publicación"""
        self.publish_btn.config(state='normal')
        self.draft_btn.config(state='normal')
        
        if success:
            action = "publicado" if status == 'publish' else "guardado como borrador"
            self.status_var.set(f"Post {action} exitosamente")
            messagebox.showinfo("Éxito", message)
            
            # Limpiar campos después de publicar exitosamente
            if status == 'publish':
                self.clear_post_fields()
        else:
            self.status_var.set("Error al crear el post")
            messagebox.showerror("Error", message)
    
    def clear_post_fields(self):
        """Limpia los campos del post"""
        self.post_title_var.set("")
        self.permalink_var.set("")
        self.content_text.delete(1.0, tk.END)
        # Reset image settings
        self.enable_images_var.set(False)
        self.words_per_image_var.set("200")
        self.image_source_var.set("Unsplash")
        self._on_images_toggle()  # Disable image controls
        self.status_var.set("Campos limpiados")
    
    def auto_verify_if_env_loaded(self):
        """Auto-verifica la conexión si los datos están cargados desde .env"""
        if all([self.url_var.get(), self.username_var.get(), self.password_var.get()]):
            # Esperar un momento para que la UI se cargue completamente
            self.root.after(1000, self.verify_connection)
    
    def _on_title_change(self, *args):
        """Callback cuando cambia el título - auto-genera permalink si está vacío"""
        # Solo auto-generar si el campo permalink está vacío
        if not self.permalink_var.get().strip():
            title = self.post_title_var.get()
            if title:
                auto_permalink = self._generate_permalink(title)
                self.permalink_var.set(auto_permalink)
    
    def _generate_permalink(self, title):
        """Genera un permalink válido a partir del título"""
        import re
        import unicodedata
        
        # Convertir a minúsculas
        permalink = title.lower()
        
        # Normalizar caracteres unicode (quitar acentos)
        permalink = unicodedata.normalize('NFD', permalink)
        permalink = ''.join(c for c in permalink if unicodedata.category(c) != 'Mn')
        
        # Reemplazar espacios y caracteres especiales con guiones
        permalink = re.sub(r'[^a-z0-9]+', '-', permalink)
        
        # Quitar guiones al inicio y final
        permalink = permalink.strip('-')
        
        # Limitar longitud
        if len(permalink) > 50:
            permalink = permalink[:50].rstrip('-')
        
        return permalink
    
    def _generate_permalink_from_title(self):
        """Genera permalink manualmente desde el botón"""
        title = self.post_title_var.get().strip()
        if title:
            permalink = self._generate_permalink(title)
            self.permalink_var.set(permalink)
        else:
            messagebox.showwarning("Advertencia", "Primero ingresa un título para generar el permalink.")
    
    def _on_images_toggle(self):
        """Callback cuando se habilita/deshabilita la funcionalidad de imágenes"""
        enabled = self.enable_images_var.get()
        state = 'normal' if enabled else 'disabled'
        
        # Habilitar/deshabilitar controles de imagen
        self.words_spinbox.config(state=state)
        self.image_source_combo.config(state=state)
        self.upload_media_cb.config(state=state)


def main():
    """Función principal"""
    root = tk.Tk()
    app = WordPressPublicator(root)
    
    # Configurar el cierre de la aplicación
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")


if __name__ == "__main__":
    main()