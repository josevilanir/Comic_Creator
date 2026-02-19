"""
Dependency Injection Container
"""
from src.domain.repositories import (
    IMangaRepository,
    ICapituloRepository,
    IUserRepository,
    IURLSalvaRepository
)
from src.infrastructure.repositories import (
    FileSystemMangaRepository,
    FileSystemCapituloRepository,
    SQLiteUserRepository,
    JSONURLRepository
)
from src.infrastructure.services import (
    ImageDownloadService,
    PDFGeneratorService,
    ThumbnailService,
    HashService,
    URLStorageService
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
        self.url_storage_service = URLStorageService(self.config.URLS_JSON)
        self.image_download_service = ImageDownloadService()
        self.pdf_generator_service = PDFGeneratorService()
        self.thumbnail_service = ThumbnailService()
        self.hash_service = HashService()
    
    def _init_repositories(self):
        """Inicializa repositories"""
        self.manga_repository = FileSystemMangaRepository(self.config.BASE_COMICS)
        self.capitulo_repository = FileSystemCapituloRepository(self.config.BASE_COMICS)
        self.user_repository = SQLiteUserRepository(self.config.DATABASE_PATH)
        self.url_repository = JSONURLRepository(self.url_storage_service)
    
    def _init_use_cases(self):
        """Inicializa use cases"""
        self.baixar_capitulo_use_case = BaixarCapituloUseCase(
            manga_repo=self.manga_repository,
            capitulo_repo=self.capitulo_repository,
            image_service=self.image_download_service,
            pdf_service=self.pdf_generator_service,
            thumbnail_service=self.thumbnail_service,
            base_dir=self.config.BASE_COMICS
        )