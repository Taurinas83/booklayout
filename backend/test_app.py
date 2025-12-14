"""
Testes para BookLayout
"""

import unittest
import json
import os
from app import app
from manuscript_processor import ManuscriptProcessor
from layout_engine import LayoutEngine


class BookLayoutTestCase(unittest.TestCase):
    """Testes da aplicação BookLayout"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.processor = ManuscriptProcessor()
        self.layout_engine = LayoutEngine()
    
    def test_health_endpoint(self):
        """Testa endpoint de health check"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    def test_templates_endpoint(self):
        """Testa endpoint de templates"""
        response = self.client.get('/api/templates')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('templates', data)
        self.assertGreater(len(data['templates']), 0)
    
    def test_manuscript_processor_txt(self):
        """Testa processamento de arquivo TXT"""
        # Criar arquivo de teste
        test_file = 'test_manuscript.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("CAPÍTULO 1: Teste\n\nEste é um parágrafo de teste.")
        
        try:
            result = self.processor.process(test_file)
            
            self.assertIn('content', result)
            self.assertIn('structure', result)
            self.assertIn('word_count', result)
            self.assertGreater(result['word_count'], 0)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_structure_analysis(self):
        """Testa análise de estrutura"""
        content = """CAPÍTULO 1: Introdução
        
Este é o primeiro parágrafo.

SEÇÃO 1.1: Subsection

Este é outro parágrafo com uma "citação" importante.
"""
        
        structure = self.processor._analyze_structure(content)
        
        self.assertGreater(len(structure['chapters']), 0)
        self.assertGreater(len(structure['sections']), 0)
        self.assertGreater(len(structure['paragraphs']), 0)
        self.assertGreater(len(structure['citations']), 0)
    
    def test_layout_generation(self):
        """Testa geração de layout"""
        manuscript = {
            'content': 'Teste de conteúdo',
            'structure': {
                'chapters': [{'title': 'Capítulo 1', 'sections': []}],
                'sections': [],
                'paragraphs': [{'text': 'Parágrafo de teste', 'chapter': 'Capítulo 1'}],
                'citations': [],
                'images': []
            },
            'word_count': 3,
            'char_count': 18
        }
        
        config = {
            'font_family': 'Georgia',
            'font_size': 12,
            'line_height': 1.5
        }
        
        layout = self.layout_engine.generate_layout(manuscript, config)
        
        self.assertIn('pages', layout)
        self.assertIn('table_of_contents', layout)
        self.assertIn('index', layout)
        self.assertGreater(len(layout['pages']), 0)
    
    def test_text_wrapping(self):
        """Testa quebra de texto"""
        text = "Este é um texto longo que deve ser quebrado em múltiplas linhas"
        lines = self.layout_engine._wrap_text(text, 100, 12)
        
        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(len(line), 100)
    
    def test_lines_per_page_calculation(self):
        """Testa cálculo de linhas por página"""
        lines = self.layout_engine._calculate_lines_per_page(297, 12, 1.5)
        
        self.assertGreater(lines, 0)
        self.assertLess(lines, 100)  # Sanidade check
    
    def test_invalid_file_upload(self):
        """Testa upload de arquivo inválido"""
        response = self.client.post('/api/upload')
        self.assertEqual(response.status_code, 400)
    
    def test_preview_without_manuscript(self):
        """Testa preview sem manuscrito"""
        response = self.client.post(
            '/api/preview',
            data=json.dumps({'config': {}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_config_merging(self):
        """Testa mesclagem de configurações"""
        default_config = self.layout_engine.default_config
        custom_config = {'font_size': 14}
        
        merged = {**default_config, **custom_config}
        
        self.assertEqual(merged['font_size'], 14)
        self.assertEqual(merged['font_family'], default_config['font_family'])


class PerformanceTestCase(unittest.TestCase):
    """Testes de performance"""
    
    def setUp(self):
        self.processor = ManuscriptProcessor()
        self.layout_engine = LayoutEngine()
    
    def test_large_manuscript_processing(self):
        """Testa processamento de manuscrito grande"""
        # Criar manuscrito de teste com ~10000 palavras
        content = "Parágrafo de teste. " * 500
        
        structure = self.processor._analyze_structure(content)
        
        self.assertGreater(len(structure['paragraphs']), 0)


class IntegrationTestCase(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_full_workflow(self):
        """Testa fluxo completo: upload -> preview -> export"""
        # 1. Criar arquivo de teste
        test_file = 'test_workflow.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("CAPÍTULO 1: Teste\n\nConteúdo do teste.")
        
        try:
            # 2. Upload
            with open(test_file, 'rb') as f:
                response = self.client.post(
                    '/api/upload',
                    data={'file': f}
                )
            
            self.assertEqual(response.status_code, 200)
            upload_data = json.loads(response.data)
            self.assertTrue(upload_data['success'])
            
            # 3. Preview
            preview_response = self.client.post(
                '/api/preview',
                data=json.dumps({
                    'manuscript': upload_data['manuscript'],
                    'config': {}
                }),
                content_type='application/json'
            )
            
            self.assertEqual(preview_response.status_code, 200)
            preview_data = json.loads(preview_response.data)
            self.assertTrue(preview_data['success'])
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    unittest.main()