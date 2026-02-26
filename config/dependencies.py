"""
Dependency Injection Container
"""
from src.infrastructure.repositories import (
    FileSystemMangaRepository,
    FileSystemCapituloRepository,
    SQLiteUserRepository,
    SQLiteURLRepository,
    UserDataRepository
)
from src.infrastructure.persistence import DownloadJobRepository
from src.infrastructure.auth.jwt_service import JwtService
from src.infrastructure.services import (
    ImageDownloadService,
    PDFGeneratorService,
    ThumbnailService,
    HashService
)
from src.application.use_cases import (
    BaixarCapituloUseCase,
)
from config.settings import Config


class DependencyContainer:
    """Container de dependências"""
    
    def __init__(self, config: Config):
        self.config = config
        self._init_services()
        self._init_repositories()
        self._init_use_cases()
    
    def _init_services(self):
        """Inicializa services"""
        self.image_download_service = ImageDownloadService()
        self.pdf_generator_service = PDFGeneratorService()
        self.thumbnail_service = ThumbnailService()
        self.hash_service = HashService()
        self.jwt_service = JwtService()
    
    def _init_repositories(self):
        """Inicializa repositories"""
        db_path = str(self.config.DATABASE_PATH)
        self.manga_repository = FileSystemMangaRepository(self.config.BASE_COMICS)
        self.capitulo_repository = FileSystemCapituloRepository(self.config.BASE_COMICS)
        self.user_repository = SQLiteUserRepository(db_path)
        self.url_repository = SQLiteURLRepository(db_path)
        self.user_data_repository = UserDataRepository(db_path)
        self.download_job_repository = DownloadJobRepository(db_path)
    
    def _init_use_cases(self):
        """Inicializa use cases"""
        # Nota: O use case precisará ser atualizado para aceitar o user_id no método executar
        self.baixar_capitulo_use_case = BaixarCapituloUseCase(
            manga_repo=self.manga_repository,
            capitulo_repo=self.capitulo_repository,
            image_service=self.image_download_service,
            pdf_service=self.pdf_generator_service,
            thumbnail_service=self.thumbnail_service,
            base_dir=self.config.BASE_COMICS
        )
