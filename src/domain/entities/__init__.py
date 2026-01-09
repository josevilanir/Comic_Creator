"""
Domain Entities - Entidades do domínio do sistema
"""
from .manga import Manga
from .capitulo import Capitulo
from .user import User
from .url_salva import URLSalva

__all__ = ['Manga', 'Capitulo', 'User', 'URLSalva']