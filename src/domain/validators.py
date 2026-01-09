"""
Validadores para regras de negócio do domínio
"""
import re
from typing import List, Tuple
from urllib.parse import urlparse, ParseResult


class ValidadorCapitulo:
    """
    Valida se imagens baixadas são realmente páginas de capítulo.
    
    Regra de negócio: Evitar download de imagens aleatórias do site
    """
    
    # Padrões que indicam que é uma página de capítulo
    PADROES_VALIDOS = [
        r'^\d+[_-]?image',  # 1_image, 2-image
        r'^\d{1,4}$',  # 1, 01, 001, 1234
        r'(page|p|img|scan|pagina|capitulo|chapter|ch)[\W_]*\d+',  # page-1, img_01
        r'wp-content/uploads/wp-manga/data/manga_',  # Padrão comum em sites WordPress
    ]
    
    # Extensões válidas
    EXTENSOES_VALIDAS = {'.jpg', '.jpeg', '.png', '.webp'}
    
    @classmethod
    def validar_nome_imagem(cls, nome_arquivo: str) -> bool:
        """
        Valida se o nome do arquivo parece ser uma página de capítulo.
        
        Args:
            nome_arquivo: Nome do arquivo de imagem
            
        Returns:
            True se parece ser uma página válida
        """
        nome_lower = nome_arquivo.lower()
        nome_sem_ext = nome_lower.rsplit('.', 1)[0]
        
        # Verifica extensão
        tem_extensao_valida = any(nome_lower.endswith(ext) for ext in cls.EXTENSOES_VALIDAS)
        if not tem_extensao_valida:
            return False
        
        # Verifica padrões
        for padrao in cls.PADROES_VALIDOS:
            if re.search(padrao, nome_sem_ext, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def validar_url_imagem(cls, url: str) -> bool:
        """
        Valida se a URL parece conter uma imagem de capítulo.
        
        Args:
            url: URL da imagem
            
        Returns:
            True se parece ser uma página válida
        """
        url_lower = url.lower()
        
        # Padrões específicos de sites de mangá
        if 'wp-manga/data/manga_' in url_lower and '_image.jpeg' in url_lower:
            return True
        
        if 'wp-manga' in url_lower and ('/data/' in url_lower or '/content/' in url_lower):
            return True
        
        # Valida pelo nome do arquivo na URL
        try:
            nome_arquivo = url.split('/')[-1].split('?')[0]
            return cls.validar_nome_imagem(nome_arquivo)
        except Exception:
            return False
    
    @classmethod
    def validar_quantidade_minima(cls, quantidade: int, minimo: int = 5) -> Tuple[bool, str]:
        """
        Valida se a quantidade de imagens baixadas é aceitável.
        
        Args:
            quantidade: Número de imagens baixadas
            minimo: Quantidade mínima esperada
            
        Returns:
            Tuple com (é_valido, mensagem_erro)
        """
        if quantidade == 0:
            return False, "Nenhuma imagem foi baixada"
        
        if quantidade < minimo:
            return False, f"Poucas imagens baixadas ({quantidade}). Esperado pelo menos {minimo}"
        
        return True, ""


class ValidadorURL:
    """Valida URLs de mangá"""
    
    PADROES_CAPITULO = ['capitulo-', 'chap-', 'chapter-', '/capitulo/', '/chap/']
    
    @classmethod
    def validar_url_base(cls, url: str) -> Tuple[bool, str]:
        """
        Valida se a URL base é válida para download de mangá.
        
        Args:
            url: URL base
            
        Returns:
            Tuple com (é_valido, mensagem_erro)
        """
        if not url or not url.strip():
            return False, "URL não pode ser vazia"
        
        # Valida formato de URL
        try:
            resultado: ParseResult = urlparse(url)
            if not all([resultado.scheme, resultado.netloc]):
                return False, "URL mal formatada"
        except Exception:
            return False, "URL inválida"
        
        # Verifica se contém padrão de capítulo
        url_lower = url.lower()
        tem_padrao = any(padrao in url_lower for padrao in cls.PADROES_CAPITULO)
        
        if not tem_padrao:
            return False, "URL não contém padrão de capítulo reconhecido"
        
        return True, ""
    
    @classmethod
    def extrair_padrao_capitulo(cls, url: str) -> str:
        """
        Extrai o padrão de capítulo da URL.
        
        Args:
            url: URL base
            
        Returns:
            Padrão identificado (capitulo-, chap-, etc)
        """
        url_lower = url.lower()
        
        for padrao in cls.PADROES_CAPITULO:
            if padrao in url_lower:
                return padrao.strip('/')
        
        return "capitulo-"  # Padrão default


class ValidadorManga:
    """Valida regras relacionadas a mangás"""
    
    @classmethod
    def validar_nome(cls, nome: str) -> Tuple[bool, str]:
        """
        Valida nome do mangá.
        
        Args:
            nome: Nome do mangá
            
        Returns:
            Tuple com (é_valido, mensagem_erro)
        """
        if not nome or not nome.strip():
            return False, "Nome do mangá não pode ser vazio"
        
        nome_limpo = nome.strip()
        
        if len(nome_limpo) < 2:
            return False, "Nome do mangá muito curto"
        
        if len(nome_limpo) > 200:
            return False, "Nome do mangá muito longo"
        
        # Caracteres não permitidos em nomes de arquivo
        caracteres_invalidos = '<>:"/\\|?*'
        if any(c in nome_limpo for c in caracteres_invalidos):
            return False, f"Nome contém caracteres inválidos: {caracteres_invalidos}"
        
        return True, ""