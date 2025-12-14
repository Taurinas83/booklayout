"""
Configurações da Aplicação BookLayout
"""

import os
from datetime import timedelta

# Configurações Gerais
DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
TESTING = os.getenv('TESTING', 'False') == 'True'

# Pastas
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
TEMP_FOLDER = os.getenv('TEMP_FOLDER', 'temp')

# Limites de Arquivo
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

# Configurações de Processamento
MAX_PAGES = int(os.getenv('MAX_PAGES', 1000))
CHARS_PER_LINE = int(os.getenv('CHARS_PER_LINE', 80))

# Configurações de PDF
PDF_QUALITY = os.getenv('PDF_QUALITY', 'high')  # low, medium, high
PDF_COMPRESSION = os.getenv('PDF_COMPRESSION', 'True') == 'True'

# Configurações de ePub
EPUB_VERSION = os.getenv('EPUB_VERSION', '3.0')
EPUB_COMPRESSION = os.getenv('EPUB_COMPRESSION', 'True') == 'True'

# Configurações de Sessão
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Configurações CORS
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'booklayout.log')

# Criar pastas se não existirem
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)
