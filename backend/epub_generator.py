"""
Gerador de ePub
Cria ePub 3.0 compatível com Amazon KDP
"""

from ebooklib import epub
from datetime import datetime
import os
from typing import Dict, Any


class EPubGenerator:
    """Gera ePub 3.0 profissional"""
    
    def __init__(self):
        self.output_folder = 'outputs'
        os.makedirs(self.output_folder, exist_ok=True)
    
    def generate(self, manuscript: Dict[str, Any], config: Dict[str, Any], 
                 title: str, author: str) -> str:
        """
        Gera ePub a partir do manuscrito
        """
        # Criar nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{title.replace(' ', '_')}_{timestamp}.epub"
        filepath = os.path.join(self.output_folder, filename)
        
        # Criar livro
        book = epub.EpubBook()
        
        # Adicionar metadados
        book.set_identifier(f'booklayout_{timestamp}')
        book.set_title(title)
        book.set_language('pt')
        book.add_author(author)
        
        # Adicionar CSS
        css = self._create_css(config)
        c1 = epub.EpubItem()
        c1.file_name = 'style/style.css'
        c1.media_type = 'text/css'
        c1.content = css
        book.add_item(c1)
        
        # Adicionar capítulos
        chapters = []
        structure = manuscript.get('structure', {})
        content = manuscript.get('content', '')
        
        # Capa
        cover_chapter = self._create_cover_chapter(title, author, config)
        book.add_item(cover_chapter)
        chapters.append(cover_chapter)
        
        # Sumário
        toc_chapter = self._create_toc_chapter(structure, config)
        book.add_item(toc_chapter)
        chapters.append(toc_chapter)
        
        # Conteúdo principal
        paragraphs = structure.get('paragraphs', [])
        current_chapter = None
        chapter_content = []
        
        for para in paragraphs:
            para_text = para.get('text', '')
            
            # Se há mudança de capítulo
            if para.get('chapter') and para.get('chapter') != current_chapter:
                # Salvar capítulo anterior
                if chapter_content:
                    chapter = self._create_content_chapter(
                        current_chapter or 'Introdução',
                        chapter_content,
                        config
                    )
                    book.add_item(chapter)
                    chapters.append(chapter)
                
                current_chapter = para.get('chapter')
                chapter_content = []
            
            chapter_content.append(para_text)
        
        # Adicionar último capítulo
        if chapter_content:
            chapter = self._create_content_chapter(
                current_chapter or 'Conclusão',
                chapter_content,
                config
            )
            book.add_item(chapter)
            chapters.append(chapter)
        
        # Definir tabela de conteúdos
        book.toc = tuple(chapters)
        
        # Adicionar navegação
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Definir ordem de leitura
        book.spine = ['nav'] + chapters
        
        # Escrever arquivo
        epub.write_epub(filepath, book, {})
        
        return filepath
    
    def _create_css(self, config: Dict[str, Any]) -> str:
        """Cria CSS para o ePub"""
        primary_color = config.get('primary_color', '#1a1a1a')
        accent_color = config.get('accent_color', '#8b7355')
        font_family = config.get('font_family', 'Georgia')
        font_size = config.get('font_size', 12)
        line_height = config.get('line_height', 1.5)
        
        css = f"""
/* BookLayout ePub Styles */

body {{
    font-family: {font_family}, serif;
    font-size: {font_size}pt;
    line-height: {line_height};
    color: {primary_color};
    margin: 0;
    padding: 1em;
}}

h1 {{
    font-size: 1.8em;
    color: {accent_color};
    margin-top: 1em;
    margin-bottom: 0.5em;
    page-break-before: always;
}}

h2 {{
    font-size: 1.4em;
    color: {primary_color};
    margin-top: 0.8em;
    margin-bottom: 0.4em;
}}

h3 {{
    font-size: 1.2em;
    color: {primary_color};
    margin-top: 0.6em;
    margin-bottom: 0.3em;
}}

p {{
    text-align: justify;
    margin-bottom: 0.5em;
    text-indent: 1.5em;
}}

p.first {{
    text-indent: 0;
}}

blockquote {{
    margin-left: 1.5em;
    margin-right: 1.5em;
    font-style: italic;
    color: {primary_color};
    border-left: 3px solid {accent_color};
    padding-left: 1em;
}}

.cover {{
    text-align: center;
    page-break-after: always;
}}

.cover-title {{
    font-size: 2.5em;
    color: {accent_color};
    margin-top: 2em;
    margin-bottom: 1em;
}}

.cover-author {{
    font-size: 1.2em;
    color: {primary_color};
    margin-top: 3em;
}}

.toc {{
    page-break-after: always;
}}

.toc-title {{
    font-size: 1.8em;
    color: {accent_color};
    margin-bottom: 1em;
}}

.toc-entry {{
    margin-bottom: 0.3em;
}}

.toc-entry-1 {{
    margin-left: 0;
    font-weight: bold;
}}

.toc-entry-2 {{
    margin-left: 1.5em;
}}

img {{
    max-width: 100%;
    height: auto;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}

th, td {{
    border: 1px solid {primary_color};
    padding: 0.5em;
    text-align: left;
}}

th {{
    background-color: {accent_color};
    color: white;
}}
"""
        return css
    
    def _create_cover_chapter(self, title: str, author: str, config: Dict) -> epub.EpubHtml:
        """Cria capítulo de capa"""
        c1 = epub.EpubHtml('cover', 'cover.xhtml', 'cover')
        c1.content = f"""
        <div class="cover">
            <h1 class="cover-title">{title}</h1>
            <p class="cover-author">por {author}</p>
        </div>
        """
        return c1
    
    def _create_toc_chapter(self, structure: Dict, config: Dict) -> epub.EpubHtml:
        """Cria capítulo de sumário"""
        c1 = epub.EpubHtml('toc_content', 'toc.xhtml', 'toc')
        
        toc_html = '<div class="toc"><h1 class="toc-title">Sumário</h1>'
        
        for chapter in structure.get('chapters', []):
            toc_html += f'<p class="toc-entry toc-entry-1">{chapter.get("title", "")}</p>'
            
            for section in chapter.get('sections', []):
                toc_html += f'<p class="toc-entry toc-entry-2">{section.get("title", "")}</p>'
        
        toc_html += '</div>'
        c1.content = toc_html
        return c1
    
    def _create_content_chapter(self, title: str, paragraphs: list, config: Dict) -> epub.EpubHtml:
        """Cria capítulo de conteúdo"""
        chapter_id = title.replace(' ', '_').lower()
        c1 = epub.EpubHtml(chapter_id, f'{chapter_id}.xhtml', 'chapter')
        
        content = f'<h1>{title}</h1>'
        
        for i, para in enumerate(paragraphs):
            first_class = ' class="first"' if i == 0 else ''
            content += f'<p{first_class}>{para}</p>'
        
        c1.content = content
        return c1