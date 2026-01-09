"""
Hash Service - Serviço para hashing seguro de senhas
"""
from werkzeug.security import generate_password_hash, check_password_hash


class HashService:
    """
    Serviço responsável por hashing e verificação de senhas.
    
    Responsabilidades:
    - Hash de senhas com salt
    - Verificação de senhas
    - Uso de algoritmos seguros (pbkdf2:sha256)
    """
    
    def __init__(self, method: str = 'pbkdf2:sha256', salt_length: int = 16):
        """
        Args:
            method: Método de hashing (pbkdf2:sha256, scrypt, etc)
            salt_length: Tamanho do salt em bytes
        """
        self.method = method
        self.salt_length = salt_length
    
    def hash_password(self, password: str) -> str:
        """
        Gera hash de uma senha.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
            
        Raises:
            ValueError: Se senha for vazia
        """
        if not password or not password.strip():
            raise ValueError("Senha não pode ser vazia")
        
        return generate_password_hash(
            password,
            method=self.method,
            salt_length=self.salt_length
        )
    
    def verificar_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            
        Returns:
            True se senha está correta
        """
        if not password or not password_hash:
            return False
        
        return check_password_hash(password_hash, password)
    
    def validar_forca_senha(self, password: str) -> tuple:
        """
        Valida força da senha.
        
        Args:
            password: Senha a validar
            
        Returns:
            Tupla (é_válida, mensagem_erro)
        """
        if not password:
            return False, "Senha não pode ser vazia"
        
        if len(password) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        if len(password) > 128:
            return False, "Senha muito longa (máximo 128 caracteres)"
        
        return True, ""