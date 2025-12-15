"""
BookLayout - Aplicativo de Diagramação Automática de Livros
Backend Flask com processamento de manuscritos e geração de PDFs/ePub
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import traceback

# Importar módulos de processamento
from manuscript_processor import ManuscriptProcessor
from layout_engine import LayoutEngine
from pdf_generator import PDFGenerator
from epub_generator import EPubGenerator

# Configuração da aplicação
# Configuração da aplicação
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def serve_frontend():
    return send_file(os.path.join(app.static_folder, 'index.html'))

# Configuração de Logs
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações de Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logger.info(f"Diretório base: {BASE_DIR}")
logger.info(f"Pasta de uploads: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Inicializar processadores
try:
    manuscript_processor = ManuscriptProcessor()
    layout_engine = LayoutEngine()
    pdf_generator = PDFGenerator()
    epub_generator = EPubGenerator()
    logger.info("Processadores inicializados com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar processadores: {e}")
    # Não vamos travar o app aqui, para permitir debug
    pass

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    # Now you're handling non-HTTP exceptions only
    logger.error(f"Erro não tratado: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc(),
        "type": type(e).__name__
    }), 500

from werkzeug.exceptions import HTTPException

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Rota para verificar estado do servidor"""
    return jsonify({
        "status": "online",
        "cwd": os.getcwd(),
        "files_in_upload": os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else "Folder Missing",
        "write_test": test_write_permission()
    })

def test_write_permission():
    try:
        test_file = os.path.join(UPLOAD_FOLDER, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return "OK"
    except Exception as e:
        return f"Fail: {str(e)}"


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/upload-text', methods=['POST'])
def upload_text():
    """
    Endpoint para processar texto direto (Copy & Paste)
    """
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'Nenhum texto enviado'}), 400
            
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Texto vazio'}), 400

        # Gerar um ID temporário
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + "direct_input.txt"
        
        logger.info(f"Processando entrada de texto direto: {len(text)} chars")
        
        # Processar texto
        manuscript_data = manuscript_processor.process_text(text, filename)
        
        return jsonify({
            'success': True,
            'file_id': filename,
            'manuscript': manuscript_data,
            'message': 'Texto processado com sucesso'
        }), 200

    except Exception as e:
        logger.error(f"Erro no processamento de texto: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "type": type(e).__name__
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_manuscript():
    """
    Endpoint para upload de manuscrito
    Aceita: txt, pdf, docx
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Arquivo vazio'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processar manuscrito
        logger.info(f"Iniciando processamento do arquivo: {filename}")
        manuscript_data = manuscript_processor.process(filepath)
        logger.info(f"Manuscrito processado com sucesso: {filename}")
        
        return jsonify({
            'success': True,
            'file_id': filename,
            'manuscript': manuscript_data,
            'message': 'Manuscrito processado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """
    Gera preview do layout com as configurações fornecidas
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'manuscript' not in data or 'config' not in data:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        manuscript = data['manuscript']
        config = data['config']
        
        # Gerar layout
        layout = layout_engine.generate_layout(manuscript, config)
        
        return jsonify({
            'success': True,
            'layout': layout,
            'message': 'Preview gerado com sucesso'
        }), 200
        
    except Exception as e:
        print(f"Erro no preview: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Gera PDF do livro com as configurações fornecidas
    """
    try:
        data = request.json
        
        if not data or 'manuscript' not in data or 'config' not in data:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        manuscript = data['manuscript']
        config = data['config']
        book_title = data.get('title', 'Livro')
        
        # Gerar layout
        layout = layout_engine.generate_layout(manuscript, config)
        
        # Gerar PDF
        pdf_path = pdf_generator.generate(layout, config, book_title)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{book_title}.pdf'
        )
        
    except Exception as e:
        print(f"Erro na geração de PDF: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-epub', methods=['POST'])
def generate_epub():
    """
    Gera ePub do livro com as configurações fornecidas
    """
    try:
        data = request.json
        
        if not data or 'manuscript' not in data or 'config' not in data:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        manuscript = data['manuscript']
        config = data['config']
        book_title = data.get('title', 'Livro')
        book_author = data.get('author', 'Autor')
        
        # Gerar ePub
        epub_path = epub_generator.generate(manuscript, config, book_title, book_author)
        
        return send_file(
            epub_path,
            mimetype='application/epub+zip',
            as_attachment=True,
            download_name=f'{book_title}.epub'
        )
        
    except Exception as e:
        print(f"Erro na geração de ePub: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """
    Retorna lista de templates de design disponíveis
    """
    templates = {
        'templates': [
            {
                'id': 'classic',
                'name': 'Clássico Premium',
                'description': 'Design elegante e tradicional',
                'config': {
                    'font_family': 'Georgia',
                    'font_size': 12,
                    'line_height': 1.5,
                    'margin_top': 2.0,
                    'margin_bottom': 2.0,
                    'margin_left': 1.5,
                    'margin_right': 1.5,
                    'primary_color': '#1a1a1a',
                    'accent_color': '#8b7355',
                    'background_color': '#ffffff'
                }
            },
            {
                'id': 'modern',
                'name': 'Moderno Limpo',
                'description': 'Design contemporâneo e minimalista',
                'config': {
                    'font_family': 'Segoe UI',
                    'font_size': 11,
                    'line_height': 1.6,
                    'margin_top': 1.5,
                    'margin_bottom': 1.5,
                    'margin_left': 1.25,
                    'margin_right': 1.25,
                    'primary_color': '#2c3e50',
                    'accent_color': '#3498db',
                    'background_color': '#ffffff'
                }
            },
            {
                'id': 'academic',
                'name': 'Acadêmico',
                'description': 'Design formal para publicações acadêmicas',
                'config': {
                    'font_family': 'Times New Roman',
                    'font_size': 12,
                    'line_height': 2.0,
                    'margin_top': 2.5,
                    'margin_bottom': 2.5,
                    'margin_left': 1.5,
                    'margin_right': 1.5,
                    'primary_color': '#000000',
                    'accent_color': '#333333',
                    'background_color': '#ffffff'
                }
            },
            {
                'id': 'contemporary',
                'name': 'Contemporâneo',
                'description': 'Design moderno com toque criativo',
                'config': {
                    'font_family': 'Calibri',
                    'font_size': 11.5,
                    'line_height': 1.55,
                    'margin_top': 1.75,
                    'margin_bottom': 1.75,
                    'margin_left': 1.5,
                    'margin_right': 1.5,
                    'primary_color': '#34495e',
                    'accent_color': '#e74c3c',
                    'background_color': '#fafafa'
                }
            }
        ]
    }
    return jsonify(templates), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    # Usar porta do ambiente (Render) ou 5000 (local)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)