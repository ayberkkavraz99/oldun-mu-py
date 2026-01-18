"""
Veritabanı bağlantısı ve session yönetimi
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

# Database bağlantı durumu
db_connected = False
engine = None
AsyncSessionLocal = None

# Base model
Base = declarative_base()


def init_engine():
    """Engine'i başlat"""
    global engine, AsyncSessionLocal, db_connected
    try:
        # Async engine oluştur
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
        )
        
        # Async session factory
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        return True
    except Exception as e:
        print(f"⚠️ Veritabanı engine oluşturulamadı: {e}")
        return False


# Engine'i başlat
init_engine()


async def get_db() -> AsyncSession:
    """
    Dependency injection için veritabanı session'ı
    Her request için yeni session oluşturur ve sonra kapatır
    """
    if AsyncSessionLocal is None:
        raise Exception("Veritabanı bağlantısı yapılandırılmamış")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Veritabanı tablolarını oluştur"""
    global db_connected
    
    if engine is None:
        print("⚠️ Veritabanı engine'i mevcut değil. DB işlemleri devre dışı.")
        return False
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_connected = True
        print("✅ Veritabanı tabloları oluşturuldu")
        return True
    except Exception as e:
        db_connected = False
        print(f"⚠️ Veritabanı bağlantısı başarısız: {e}")
        print("📝 Uygulama veritabanı olmadan çalışmaya devam edecek (sınırlı özellikler)")
        return False


def is_db_connected() -> bool:
    """Veritabanı bağlantı durumunu kontrol et"""
    return db_connected
