"""
WordPress Publicator - Aplicación principal
Una herramienta de escritorio para publicar posts en WordPress
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
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
        self.root.geometry("1800x1000")  # Increased window size for more space
        self.root.resizable(True, True)
        self.root.minsize(1400, 800)  # Set minimum size
        
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
        """Crea todos los widgets de la interfaz con diseño optimizado para escritura"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid para expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Content area gets most space
        
        # Título compacto
        title_label = ttk.Label(main_frame, text="WordPress Publicator", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Sección de conexión compacta
        connection_frame = ttk.LabelFrame(main_frame, text="Conexión WordPress", padding="10")
        connection_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.create_connection_section_compact(connection_frame)
        
        # Sección de imágenes compacta
        images_frame = ttk.LabelFrame(main_frame, text="Configuración de Imágenes", padding="10")
        images_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.create_images_section_compact(images_frame)
        
        # Área principal de contenido (maximizada)
        self.create_content_section(main_frame, 3)
        
        # Estado de la aplicación (compacto)
        env_loaded = all([os.getenv('WORDPRESS_URL'), os.getenv('WORDPRESS_USERNAME'), os.getenv('WORDPRESS_PASSWORD')])
        initial_status = "Datos cargados desde .env - Verificando conexión..." if env_loaded else "Listo para conectar"
        self.status_var = tk.StringVar(value=initial_status)
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('TkDefaultFont', 8))
        status_label.grid(row=4, column=0, pady=(5, 0))
    
    def create_connection_section_compact(self, parent):
        """Crea la sección de conexión a WordPress en formato compacto"""
        # Configurar grid
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
        
        # Primera fila: URL y Usuario
        ttk.Label(parent, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.url_var = tk.StringVar(value=os.getenv('WORDPRESS_URL', ''))
        url_entry = ttk.Entry(parent, textvariable=self.url_var, width=30)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=2)
        
        ttk.Label(parent, text="Usuario:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.username_var = tk.StringVar(value=os.getenv('WORDPRESS_USERNAME', ''))
        username_entry = ttk.Entry(parent, textvariable=self.username_var, width=25)
        username_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2)
        
        # Segunda fila: Contraseña, Botón y Estado
        ttk.Label(parent, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.password_var = tk.StringVar(value=os.getenv('WORDPRESS_PASSWORD', ''))
        password_entry = ttk.Entry(parent, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=2)
        
        # Frame para botón y estado
        button_status_frame = ttk.Frame(parent)
        button_status_frame.grid(row=1, column=2, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        self.verify_btn = ttk.Button(button_status_frame, text="Verificar", command=self.verify_connection)
        self.verify_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.connection_status_var = tk.StringVar(value="No conectado")
        self.connection_status_label = ttk.Label(button_status_frame, textvariable=self.connection_status_var)
        self.connection_status_label.pack(side=tk.LEFT)
    
    def create_images_section_compact(self, parent):
        """Crea la sección de configuración de imágenes en formato compacto"""
        # Configurar grid
        parent.columnconfigure(1, weight=1)
        
        # Checkbox principal
        self.enable_images_var = tk.BooleanVar(value=False)
        enable_images_cb = ttk.Checkbutton(parent, text="Agregar imágenes al contenido", 
                                         variable=self.enable_images_var,
                                         command=self._on_images_toggle)
        enable_images_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Frame para configuraciones (en una sola fila)
        config_frame = ttk.Frame(parent)
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Palabras por imagen
        ttk.Label(config_frame, text="Palabras por imagen:").pack(side=tk.LEFT, padx=(0, 5))
        self.words_per_image_var = tk.StringVar(value="200")
        self.words_spinbox = ttk.Spinbox(config_frame, from_=50, to=1000, increment=50, 
                                      textvariable=self.words_per_image_var, width=8, state='disabled')
        self.words_spinbox.pack(side=tk.LEFT, padx=(0, 20))
        
        # Fuente de imágenes
        ttk.Label(config_frame, text="Fuente:").pack(side=tk.LEFT, padx=(0, 5))
        self.image_source_var = tk.StringVar(value="Unsplash")
        self.image_source_combo = ttk.Combobox(config_frame, textvariable=self.image_source_var,
                                            values=["Unsplash", "Shutterstock", "Placeholder"], 
                                            state='disabled', width=12)
        self.image_source_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Upload to media library
        self.upload_to_media_var = tk.BooleanVar(value=True)
        self.upload_media_cb = ttk.Checkbutton(config_frame, text="Subir a Media Library", 
                                            variable=self.upload_to_media_var, state='disabled')
        self.upload_media_cb.pack(side=tk.LEFT)
    
    def create_content_section(self, parent, start_row):
        """Crea la sección principal de contenido maximizada"""
        # Frame principal para contenido
        content_main_frame = ttk.Frame(parent)
        content_main_frame.grid(row=start_row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_main_frame.columnconfigure(0, weight=1)
        content_main_frame.rowconfigure(1, weight=1)  # Content area expands
        
        # Frame superior para título y permalink (compacto)
        header_frame = ttk.Frame(content_main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(3, weight=1)
        
        # Título del post
        ttk.Label(header_frame, text="Título:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.post_title_var = tk.StringVar()
        title_entry = ttk.Entry(header_frame, textvariable=self.post_title_var, font=('TkDefaultFont', 11))
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # Permalink
        ttk.Label(header_frame, text="Permalink:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        permalink_frame = ttk.Frame(header_frame)
        permalink_frame.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        self.permalink_var = tk.StringVar()
        permalink_entry = ttk.Entry(permalink_frame, textvariable=self.permalink_var)
        permalink_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        generate_btn = ttk.Button(permalink_frame, text="Gen", command=self._generate_permalink_from_title, width=4)
        generate_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Vincular cambios en el título
        self.post_title_var.trace_add('write', self._on_title_change)
        
        # Área de contenido MAXIMIZADA
        content_frame = ttk.Frame(content_main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Textarea principal con mayor altura
        self.content_text = scrolledtext.ScrolledText(content_frame, width=100, height=30, 
                                                    wrap=tk.WORD, font=('Consolas', 11))
        self.content_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Panel lateral para botones y mensajes
        side_panel = ttk.Frame(content_main_frame)
        side_panel.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E), padx=(10, 0))
        
        # Botones de acción
        button_frame = ttk.LabelFrame(side_panel, text="Acciones", padding="10")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.publish_btn = ttk.Button(button_frame, text="Publicar Post", command=self.publish_post, state='disabled')
        self.publish_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.draft_btn = ttk.Button(button_frame, text="Guardar Borrador", command=self.save_draft, state='disabled')
        self.draft_btn.pack(fill=tk.X, pady=(0, 5))
        
        clear_btn = ttk.Button(button_frame, text="Limpiar", command=self.clear_post_fields)
        clear_btn.pack(fill=tk.X)
        
        # Área de mensajes
        message_frame = ttk.LabelFrame(side_panel, text="Mensajes", padding="10")
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        self.message_text = scrolledtext.ScrolledText(message_frame, width=35, height=15, 
                                                    wrap=tk.WORD, state='disabled', font=('TkDefaultFont', 9))
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para mensajes
        self.message_text.tag_configure("success", foreground="green")
        self.message_text.tag_configure("error", foreground="red")
        self.message_text.tag_configure("info", foreground="blue")
        self.message_text.tag_configure("warning", foreground="orange")
        
        # Mensaje de bienvenida
        self.root.after(100, lambda: self.show_message("WordPress Publicator iniciado. Los mensajes aparecerán aquí.", "info"))
    

    

    
    def show_message(self, message, message_type="info"):
        """Muestra un mensaje en el área de mensajes dedicada"""
        self.message_text.config(state='normal')
        
        # Agregar timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Insertar mensaje con formato
        self.message_text.insert(tk.END, f"[{timestamp}] {message}\n", message_type)
        
        # Auto-scroll al final
        self.message_text.see(tk.END)
        
        # Deshabilitar edición
        self.message_text.config(state='disabled')
        
        # Limitar número de líneas (mantener solo las últimas 50)
        lines = self.message_text.get(1.0, tk.END).split('\n')
        if len(lines) > 50:
            self.message_text.config(state='normal')
            self.message_text.delete(1.0, f"{len(lines)-50}.0")
            self.message_text.config(state='disabled')
    
    def verify_connection(self):
        """Verifica la conexión con WordPress en un hilo separado"""
        if not all([self.url_var.get(), self.username_var.get(), self.password_var.get()]):
            self.show_message("Por favor, completa todos los campos de conexión.", "error")
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
            self.show_message(f"✓ Conexión exitosa: {message}", "success")
        else:
            self.connection_verified = False
            self.connection_status_var.set("✗ Error")
            self.connection_status_label.config(style='Error.TLabel')
            self.publish_btn.config(state='disabled')
            self.draft_btn.config(state='disabled')
            self.status_var.set("Error de conexión")
            self.show_message(f"✗ Error de conexión: {message}", "error")
    
    def publish_post(self):
        """Publica el post en WordPress"""
        self._create_post('publish')
    
    def save_draft(self):
        """Guarda el post como borrador"""
        self._create_post('draft')
    
    def _create_post(self, status):
        """Crea un post con el estado especificado"""
        if not self.connection_verified:
            self.show_message("Primero debes verificar la conexión con WordPress.", "error")
            return
        
        title = self.post_title_var.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        permalink = self.permalink_var.get().strip()
        
        if not title:
            self.show_message("El título del post es obligatorio.", "error")
            return
        
        if not content:
            self.show_message("El contenido del post es obligatorio.", "error")
            return
        
        # Validar permalink si se proporciona
        if permalink:
            # Validación básica del permalink
            import re
            if not re.match(r'^[a-z0-9-]+$', permalink):
                self.show_message("El permalink solo puede contener letras minúsculas, números y guiones.", "error")
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
            # Always sanitize content for WordPress compatibility using HTMLCleaner
            from html_cleaner import HTMLCleaner
            html_cleaner = HTMLCleaner()
            
            # First, sanitize the HTML content
            self.root.after(0, lambda: self.status_var.set("Sanitizing HTML content..."))
            processed_content = html_cleaner.clean_html(content)
            
            if self.enable_images_var.get():
                self.root.after(0, lambda: self.status_var.set("Processing images..."))
                
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
                        processed_content, words_per_image
                    )
                    
                    if used_images:
                        self.root.after(0, lambda: self.status_var.set(f"Added {len(used_images)} images. Creating post..."))
                    else:
                        self.root.after(0, lambda: self.status_var.set("Content processed. Creating post..."))
                        
                except Exception as img_error:
                    print(f"Image processing error: {str(img_error)}")
                    self.root.after(0, lambda: self.status_var.set("Image processing failed. Creating post with sanitized content..."))
                    # Continue with sanitized content even if image processing fails
            else:
                # Images disabled - content is already sanitized
                self.root.after(0, lambda: self.status_var.set("Content sanitized. Creating post..."))
            
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
            self.show_message(f"✓ Post {action} exitosamente: {message}", "success")
            
            # Limpiar campos después de publicar exitosamente
            if status == 'publish':
                self.clear_post_fields()
        else:
            self.status_var.set("Error al crear el post")
            self.show_message(f"✗ Error al crear el post: {message}", "error")
    
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
        # Check if .env file exists
        env_file_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_file_path):
            self.status_var.set("No .env file found. Please configure WordPress credentials manually.")
            return
        
        # Check if all WordPress credentials are loaded from .env
        if all([self.url_var.get(), self.username_var.get(), self.password_var.get()]):
            self.status_var.set("WordPress credentials loaded from .env - Starting auto-verification...")
            # Wait a moment for the UI to load completely, then auto-verify
            self.root.after(1000, self._auto_verify_connection)
        else:
            self.status_var.set(".env file found but WordPress credentials are incomplete. Please check your .env file.")
    
    def _auto_verify_connection(self):
        """Performs automatic verification with error handling"""
        try:
            self.verify_connection()
        except Exception as e:
            self.status_var.set(f"Auto-verification failed: {str(e)}")
            print(f"Auto-verification error: {str(e)}")
    
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
            self.show_message(f"Permalink generado: {permalink}", "info")
        else:
            self.show_message("Primero ingresa un título para generar el permalink.", "warning")
    
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