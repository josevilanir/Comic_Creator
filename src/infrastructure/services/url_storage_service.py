"""
URL Storage Service - Serviço para persistir URLs salvas em JSON
"""
import json
import os
from typing import Dict


class URLStorageService:
    """
    Serviço responsável por persistir URLs salvas em arquivo JSON.
    
    Responsabilidades:
    - Carregar URLs de arquivo JSON
    - Salvar URLs em arquivo JSON
    - Garantir integridade do arquivo
    """
    
    def __init__(self, caminho_arquivo: str = 'urls_salvas.json'):
        """
        Args:
            caminho_arquivo: Caminho do arquivo JSON
        """
        self.caminho_arquivo = caminho_arquivo
    
    def carregar_urls(self) -> Dict[str, str]:
        """
        Carrega URLs do arquivo JSON.
        
        Returns:
            Dicionário {nome_manga: url_base}
            
        Note:
            Retorna dicionário vazio se arquivo não existir
        """
        if not os.path.exists(self.caminho_arquivo):
            return {}
        
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Arquivo corrompido, retorna vazio
            print(f"Aviso: Arquivo {self.caminho_arquivo} está corrompido. Iniciando vazio.")
            return {}
        except Exception as e:
            print(f"Erro ao carregar URLs: {e}")
            return {}
    
    def salvar_urls(self, urls: Dict[str, str]) -> bool:
        """
        Salva URLs no arquivo JSON.
        
        Args:
            urls: Dicionário de URLs a salvar
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Garante que diretório existe
            diretorio = os.path.dirname(self.caminho_arquivo)
            if diretorio and not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
            
            # Salva com indentação para facilitar leitura
            with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(urls, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar URLs: {e}")
            return False
    
    def adicionar_url(self, nome_manga: str, url_base: str) -> bool:
        """
        Adiciona ou atualiza uma URL.
        
        Args:
            nome_manga: Nome do mangá (chave)
            url_base: URL base
            
        Returns:
            True se salvou com sucesso
        """
        urls = self.carregar_urls()
        urls[nome_manga] = url_base
        return self.salvar_urls(urls)
    
    def remover_url(self, nome_manga: str) -> bool:
        """
        Remove uma URL.
        
        Args:
            nome_manga: Nome do mangá a remover
            
        Returns:
            True se removeu com sucesso
        """
        urls = self.carregar_urls()
        
        if nome_manga in urls:
            del urls[nome_manga]
            return self.salvar_urls(urls)
        
        return False
    
    def url_existe(self, nome_manga: str) -> bool:
        """
        Verifica se uma URL existe.
        
        Args:
            nome_manga: Nome do mangá
            
        Returns:
            True se existe
        """
        urls = self.carregar_urls()
        return nome_manga in urls
    
    def buscar_url(self, nome_manga: str) -> str:
        """
        Busca URL por nome do mangá.
        
        Args:
            nome_manga: Nome do mangá
            
        Returns:
            URL base ou None se não encontrar
        """
        urls = self.carregar_urls()
        return urls.get(nome_manga)
    
    def criar_backup(self, sufixo: str = '.backup') -> bool:
        """
        Cria backup do arquivo JSON.
        
        Args:
            sufixo: Sufixo do arquivo de backup
            
        Returns:
            True se criou backup com sucesso
        """
        if not os.path.exists(self.caminho_arquivo):
            return False
        
        try:
            import shutil
            caminho_backup = f"{self.caminho_arquivo}{sufixo}"
            shutil.copy2(self.caminho_arquivo, caminho_backup)
            return True
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return False