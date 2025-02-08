import unittest
import os
import re
from PIL import Image
from fpdf import FPDF

# Função simulada para testar a ordenação das imagens
def ordenar_imagens(pasta_imagens):
    arquivos = sorted(
        [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.jpg', '.webp', '.png'))],
        key=lambda x: int(re.search(r'\d+', x).group())  # Ordena numericamente pelo número extraído do nome
    )
    return arquivos

# Função para compilar as imagens em PDF
def gerar_pdf(pasta_imagens, caminho_pdf):
    arquivos_ordenados = ordenar_imagens(pasta_imagens)
    pdf = FPDF()
    
    for arquivo in arquivos_ordenados:
        caminho_imagem = os.path.join(pasta_imagens, arquivo)
        
        # Adiciona uma página para cada imagem
        pdf.add_page()
        pdf.image(caminho_imagem, x=10, y=10, w=180)
    
    pdf.output(caminho_pdf)

class TestGeracaoPdf(unittest.TestCase):

    def setUp(self):
        # Criar pasta temporária para armazenar as imagens durante o teste
        self.pasta_imagens = "test_images"
        os.makedirs(self.pasta_imagens, exist_ok=True)
        
        # Adicionar algumas imagens de teste com nomes numéricos
        self.imagens_teste = [
            ("image10.jpg", 10),
            ("image2.jpg", 2),
            ("image1.jpg", 1),
            ("image9.jpg", 9),
            ("image3.jpg", 3)
        ]
        
        # Criando imagens de teste na pasta
        for nome_imagem, _ in self.imagens_teste:
            img = Image.new('RGB', (100, 100), color = (255, 0, 0))
            img.save(os.path.join(self.pasta_imagens, nome_imagem))

    def tearDown(self):
        # Limpar a pasta de imagens após o teste
        for arquivo in os.listdir(self.pasta_imagens):
            os.remove(os.path.join(self.pasta_imagens, arquivo))
        os.rmdir(self.pasta_imagens)

        # Excluir o PDF gerado (se existir)
        if os.path.exists("output.pdf"):
            os.remove("output.pdf")

    def test_gerar_pdf_em_ordem_certa(self):
        # Caminho para o PDF de saída
        caminho_pdf = "output.pdf"
        
        # Gera o PDF
        gerar_pdf(self.pasta_imagens, caminho_pdf)
        
        # Verifica se o arquivo PDF foi criado
        self.assertTrue(os.path.exists(caminho_pdf), "PDF não foi gerado")
        
        # Verificação da ordem das imagens
        arquivos_ordenados = ordenar_imagens(self.pasta_imagens)
        
        # Verifica se a ordem dos arquivos no diretório está correta
        self.assertEqual(arquivos_ordenados, ['image1.jpg', 'image2.jpg', 'image3.jpg', 'image9.jpg', 'image10.jpg'])

if __name__ == "__main__":
    unittest.main()
