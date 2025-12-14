"""
Gerador de PDF
Cria PDFs profissionais a partir do layout
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, pt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
from typing import Dict, Any, List


class PDFGenerator:
    """Gera PDFs profissionais"""
    
    def __init__(self):
        self.output_folder = 'outputs'
        os.makedirs(self.output_folder, exist_ok=True)
    
    def generate(self, layout: Dict[str, Any], config: Dict[str, Any], title: str) -> str:
        """
        Gera PDF a partir do layout
        """
        # Criar nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{title.replace(' ', '_')}_{timestamp}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        
        # Criar documento
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=config.get('margin_right', 1.5) * mm,
            leftMargin=config.get('margin_left', 1.5) * mm,
            topMargin=config.get('margin_top', 2.0) * mm,
            bottomMargin=config.get('margin_bottom', 2.0) * mm
        )
        
        # Criar estilos
        styles = self._create_styles(config)
        
        # Construir conteúdo
        story = []
        
        # Adicionar páginas
        for page in layout.get('pages', []):
            story.extend(self._build_page(page, styles, config))
            story.append(PageBreak())
        
        # Adicionar sumário
        toc = layout.get('table_of_contents', [])
        if toc:
            story.append(PageBreak())
            story.append(Paragraph("Sumário", styles['Heading1']))
            story.append(Spacer(1, 0.3 * mm))
            
            for entry in toc:
                indent = entry.get('indent', 0) * 20
                style_name = 'TOCEntry1' if entry.get('indent', 0) == 0 else 'TOCEntry2'
                story.append(Paragraph(entry.get('title', ''), styles[style_name]))
        
        # Adicionar índice
        index = layout.get('index', [])
        if index:
            story.append(PageBreak())
            story.append(Paragraph("Índice Remissivo", styles['Heading1']))
            story.append(Spacer(1, 0.3 * mm))
            
            for entry in index:
                story.append(Paragraph(entry.get('term', ''), styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        
        return filepath
    
    def _create_styles(self, config: Dict[str, Any]) -> Dict:
        """Cria estilos de parágrafo"""
        styles = getSampleStyleSheet()
        
        # Cores
        primary_color = self._hex_to_rgb(config.get('primary_color', '#1a1a1a'))
        accent_color = self._hex_to_rgb(config.get('accent_color', '#8b7355'))
        
        # Estilo de corpo de texto
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=config.get('font_size', 12),
            leading=config.get('font_size', 12) * config.get('line_height', 1.5),
            textColor=colors.HexColor(config.get('primary_color', '#1a1a1a')),
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Estilo de título
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=28,
            textColor=colors.HexColor(config.get('accent_color', '#8b7355')),
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Estilo de subtítulo
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Heading2'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=18,
            textColor=colors.HexColor(config.get('primary_color', '#1a1a1a')),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Estilo de capítulo
        styles.add(ParagraphStyle(
            name='Chapter',
            parent=styles['Heading1'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=20,
            textColor=colors.HexColor(config.get('accent_color', '#8b7355')),
            spaceAfter=12,
            spaceBefore=12,
            keepWithNext=True
        ))
        
        # Estilo de seção
        styles.add(ParagraphStyle(
            name='Section',
            parent=styles['Heading2'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=14,
            textColor=colors.HexColor(config.get('primary_color', '#1a1a1a')),
            spaceAfter=6,
            spaceBefore=6,
            keepWithNext=True
        ))
        
        # Estilo de entrada de sumário
        styles.add(ParagraphStyle(
            name='TOCEntry1',
            parent=styles['Normal'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=11,
            textColor=colors.HexColor(config.get('primary_color', '#1a1a1a')),
            leftIndent=0,
            spaceAfter=3
        ))
        
        styles.add(ParagraphStyle(
            name='TOCEntry2',
            parent=styles['Normal'],
            fontName=config.get('font_family', 'Georgia'),
            fontSize=10,
            textColor=colors.HexColor(config.get('primary_color', '#1a1a1a')),
            leftIndent=20,
            spaceAfter=2
        ))
        
        return styles
    
    def _build_page(self, page: Dict[str, Any], styles: Dict, config: Dict) -> List:
        """Constrói conteúdo de uma página"""
        story = []
        
        page_type = page.get('type', 'content')
        
        if page_type == 'cover':
            story.extend(self._build_cover_page(page, styles))
        elif page_type == 'title_page':
            story.extend(self._build_title_page(page, styles))
        elif page_type == 'toc':
            story.extend(self._build_toc_page(page, styles))
        else:
            story.extend(self._build_content_page(page, styles))
        
        return story
    
    def _build_cover_page(self, page: Dict, styles: Dict) -> List:
        """Constrói página de capa"""
        story = []
        
        # Adicionar espaço
        story.append(Spacer(1, 40 * mm))
        
        for item in page.get('content', []):
            if item.get('type') == 'title':
                story.append(Paragraph(item.get('text', ''), styles['Title']))
            elif item.get('type') == 'subtitle':
                story.append(Paragraph(item.get('text', ''), styles['Subtitle']))
        
        return story
    
    def _build_title_page(self, page: Dict, styles: Dict) -> List:
        """Constrói folha de rosto"""
        story = []
        
        story.append(Spacer(1, 30 * mm))
        
        for item in page.get('content', []):
            story.append(Paragraph(item.get('text', ''), styles['Normal']))
            story.append(Spacer(1, 10 * mm))
        
        return story
    
    def _build_toc_page(self, page: Dict, styles: Dict) -> List:
        """Constrói página de sumário"""
        story = []
        
        for item in page.get('content', []):
            if item.get('type') == 'heading':
                story.append(Paragraph(item.get('text', ''), styles['Heading1']))
                story.append(Spacer(1, 6 * mm))
            elif item.get('type') == 'toc_entry':
                story.append(Paragraph(item.get('text', ''), styles['Normal']))
        
        return story
    
    def _build_content_page(self, page: Dict, styles: Dict) -> List:
        """Constrói página de conteúdo"""
        story = []
        
        for item in page.get('content', []):
            item_type = item.get('type', 'text')
            
            if item_type == 'text':
                story.append(Paragraph(item.get('text', ''), styles['BodyText']))
            elif item_type == 'heading':
                story.append(Paragraph(item.get('text', ''), styles['Chapter']))
            elif item_type == 'subheading':
                story.append(Paragraph(item.get('text', ''), styles['Section']))
        
        return story
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Converte cor hexadecimal para RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))