"""
Motor de Layout
Distribui conteúdo textual nas páginas conforme configurações
"""

from typing import Dict, List, Any
import math


class LayoutEngine:
    """Gera layout de páginas com distribuição automática de conteúdo"""
    
    def __init__(self):
        # Configurações padrão
        self.default_config = {
            'page_width': 210,  # mm (A4)
            'page_height': 297,  # mm (A4)
            'margin_top': 2.0,
            'margin_bottom': 2.0,
            'margin_left': 1.5,
            'margin_right': 1.5,
            'font_family': 'Georgia',
            'font_size': 12,
            'line_height': 1.5,
            'primary_color': '#1a1a1a',
            'accent_color': '#8b7355',
            'background_color': '#ffffff'
        }
    
    def generate_layout(self, manuscript: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera layout completo do livro
        """
        # Mesclar configurações
        final_config = {**self.default_config, **config}
        
        # Calcular área útil da página
        usable_width = final_config['page_width'] - final_config['margin_left'] - final_config['margin_right']
        usable_height = final_config['page_height'] - final_config['margin_top'] - final_config['margin_bottom']
        
        # Extrair conteúdo
        content = manuscript.get('content', '')
        structure = manuscript.get('structure', {})
        
        # Distribuir conteúdo em páginas
        pages = self._distribute_content(
            content,
            structure,
            manuscript.get('metadata', {}),  # Passar metadados
            usable_width,
            usable_height,
            final_config
        )
        
        # Gerar sumário
        table_of_contents = self._generate_toc(structure)
        
        # Gerar índice remissivo
        index = self._generate_index(structure)
        
        return {
            'pages': pages,
            'table_of_contents': table_of_contents,
            'index': index,
            'config': final_config,
            'total_pages': len(pages),
            'metadata': {
                'word_count': manuscript.get('word_count', 0),
                'char_count': manuscript.get('char_count', 0)
            }
        }
    
    def _distribute_content(self, content: str, structure: Dict, metadata: Dict, width: float, 
                           height: float, config: Dict) -> List[Dict[str, Any]]:
        """
        Distribui conteúdo em páginas
        """
        pages = []
        
        # Adicionar capa
        pages.append(self._create_cover_page(config, metadata))
        
        # Adicionar folha de rosto
        pages.append(self._create_title_page(config, metadata))
        
        # Adicionar sumário
        toc_pages = self._create_toc_pages(structure, config)
        pages.extend(toc_pages)
        
        # Distribuir conteúdo principal
        chapters = structure.get('chapters', [])
        
        # Calcular linhas por página
        lines_per_page = self._calculate_lines_per_page(height, config['font_size'], config['line_height'])
        
        current_page = None
        current_lines = 0
        
        for chapter in chapters:
            # Nova página para cada capítulo
            if current_page is not None:
                pages.append(current_page)
            
            current_page = self._create_page(config, len(pages) + 1)
            current_lines = 0
            
            # Título do Capítulo (Big Number Style handled in frontend, just pass data)
            current_page['content'].append({
                'type': 'chapter_title',
                'text': chapter['title'],
                'font_size': config['font_size'] * 2.5,
                'font_family': config['font_family'],
                'color': config['primary_color']
            })
            current_lines += 5 # Espaço do título
            
            # Processar blocos de conteúdo
            for block in chapter.get('content_blocks', []):
                
                # Quebra de página se necessário
                if current_lines >= lines_per_page:
                    if current_page is not None:
                        pages.append(current_page)
                    current_page = self._create_page(config, len(pages) + 1)
                    current_lines = 0

                if block['type'] == 'paragraph':
                    # Processamento normal de parágrafo
                    lines = self._wrap_text(block['text'], width, config['font_size'])
                    for line in lines:
                        if current_lines >= lines_per_page:
                            pages.append(current_page)
                            current_page = self._create_page(config, len(pages) + 1)
                            current_lines = 0
                        
                        current_page['content'].append({
                            'type': 'text',
                            'text': line,
                            'font_size': config['font_size'],
                            'font_family': config['font_family'],
                            'color': config['primary_color']
                        })
                        current_lines += 1
                        
                elif block['type'] == 'tool':
                    # Bloco de Ferramenta (não quebra em linhas, passa o bloco inteiro)
                    # Frontend desenha a caixa
                    # Estimar tamanho: 2 linhas título + 1 linha por item
                    tool_height = 2 + len(block['content'])
                    
                    if current_lines + tool_height > lines_per_page:
                         pages.append(current_page)
                         current_page = self._create_page(config, len(pages) + 1)
                         current_lines = 0
                    
                    current_page['content'].append({
                        'type': 'tool_block',
                        'data': block, # Passa estrutura completa da ferramenta
                        'font_family': config['font_family'],
                        'color': config['primary_color']
                    })
                    current_lines += tool_height

        
        # Adicionar última página
        if current_page is not None:
            pages.append(current_page)
        
        return pages
    
    def _create_cover_page(self, config: Dict, metadata: Dict) -> Dict[str, Any]:
        """Cria página de capa"""
        title = metadata.get('title', 'Seu Livro')
        # Se título for muito longo, pode quebrar? O frontend cuida em grande parte, mas aqui definimos o texto.
        
        return {
            'page_number': 1,
            'type': 'cover',
            'content': [
                {
                    'type': 'title',
                    'text': title,
                    'font_size': 48,
                    'font_family': config['font_family'],
                    'color': config['accent_color'],
                    'alignment': 'center'
                },
                {
                    'type': 'subtitle',
                    'text': 'Diagramado Automaticamente',
                    'font_size': 24,
                    'font_family': config['font_family'],
                    'color': config['primary_color'],
                    'alignment': 'center'
                }
            ],
            'background_color': config['background_color']
        }
    
    def _create_title_page(self, config: Dict, metadata: Dict) -> Dict[str, Any]:
        """Cria folha de rosto"""
        title = metadata.get('title', 'Seu Livro')
        author = metadata.get('author', 'Autor Desconhecido')

        return {
            'page_number': 2,
            'type': 'title_page',
            'content': [
                {
                    'type': 'text',
                    'text': title,
                    'font_size': 32,
                    'font_family': config['font_family'],
                    'color': config['primary_color'],
                    'alignment': 'center'
                },
                {
                    'type': 'text',
                    'text': author,
                    'font_size': 16,
                    'font_family': config['font_family'],
                    'color': config['primary_color'],
                    'alignment': 'center'
                }
            ],
            'background_color': config['background_color']
        }
    
    def _create_toc_pages(self, structure: Dict, config: Dict) -> List[Dict[str, Any]]:
        """Cria páginas de sumário"""
        pages = []
        
        page = {
            'page_number': 3,
            'type': 'toc',
            'content': [
                {
                    'type': 'heading',
                    'text': 'Sumário',
                    'font_size': 24,
                    'font_family': config['font_family'],
                    'color': config['accent_color']
                }
            ],
            'background_color': config['background_color']
        }
        
        # Adicionar capítulos ao sumário
        for chapter in structure.get('chapters', []):
            page['content'].append({
                'type': 'toc_entry',
                'text': chapter.get('title', ''),
                'font_size': 12,
                'font_family': config['font_family'],
                'color': config['primary_color'],
                'indent': 0
            })
            
            # Adicionar seções
            for section in chapter.get('sections', []):
                page['content'].append({
                    'type': 'toc_entry',
                    'text': section.get('title', ''),
                    'font_size': 11,
                    'font_family': config['font_family'],
                    'color': config['primary_color'],
                    'indent': 1
                })
        
        pages.append(page)
        return pages
    
    def _create_page(self, config: Dict, page_number: int) -> Dict[str, Any]:
        """Cria página vazia"""
        return {
            'page_number': page_number,
            'type': 'content',
            'content': [],
            'background_color': config['background_color'],
            'header': f'Página {page_number}',
            'footer': f'{page_number}'
        }
    
    def _calculate_lines_per_page(self, height: float, font_size: float, line_height: float) -> int:
        """Calcula quantas linhas cabem em uma página"""
        # Converter mm para pontos (1mm ≈ 2.834645669 pontos)
        height_points = height * 2.834645669
        line_height_points = font_size * line_height
        
        return int(height_points / line_height_points)
    
    def _wrap_text(self, text: str, width: float, font_size: float) -> List[str]:
        """
        Quebra texto em linhas conforme largura disponível (estimativa conservadora)
        width: mm
        font_size: pt
        """
        # Converter largura para pontos (1mm = 2.83pt)
        # Proteção contra valores inválidos
        safe_width = max(width, 10) # Mínimo 10mm de largura
        safe_font_size = max(font_size, 6) # Mínimo 6pt
        
        width_points = safe_width * 2.83465
        
        # Estimar largura média do caractere (0.6 * font_size é conservador para fontes serifadas)
        avg_char_width = safe_font_size * 0.6
        
        # Proteção contra divisão por zero (redundante com max acima, mas boa prática)
        if avg_char_width <= 0: avg_char_width = 7.2 # Equivalente a 12pt
        
        chars_per_line = int(width_points / avg_char_width)
        
        # Garante mínimo de segurança
        if chars_per_line < 20: chars_per_line = 20
        
        lines = []
        words = text.split()
        current_line = []
        
        for word in words:
            # Verifica se adicionar a palavra excede o limite (com espaço)
            line_len = sum(len(w) for w in current_line) + len(current_line) + len(word)
            
            if line_len > chars_per_line:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                
                # Se a palavra sozinha for maior que a linha (caso raro), quebra ela
                if len(word) > chars_per_line:
                    # Aqui apenas aceitamos, o CSS vai lidar ou cortará. 
                    # Complexidade de hifenização backend é alta.
                    pass
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _generate_toc(self, structure: Dict) -> List[Dict[str, Any]]:
        """Gera tabela de conteúdos"""
        toc = []
        
        for chapter in structure.get('chapters', []):
            toc.append({
                'level': 1,
                'title': chapter.get('title', ''),
                'page': None  # Será preenchido durante geração de PDF
            })
            
            for section in chapter.get('sections', []):
                toc.append({
                    'level': 2,
                    'title': section.get('title', ''),
                    'page': None
                })
        
        return toc
    
    def _generate_index(self, structure: Dict) -> List[Dict[str, Any]]:
        """Gera índice remissivo"""
        index = []
        
        # Coletar palavras-chave das citações
        for citation in structure.get('citations', []):
            index.append({
                'term': citation.get('text', ''),
                'type': 'citation',
                'page': None
            })
        
        return index