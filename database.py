from sqlalchemy import create_engine
import config
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, SMALLINT, BIGINT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


def get_connection():
    return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            config.DBUSERNAME, config.DBPASSWORD, config.DBHOST, config.DBPORT, config.DBNAME
        )
    )
    
def db_connect():
    engine = get_connection()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db

def get_proc():
    engine = get_connection()
    proc_connection = engine.raw_connection()
    return proc_connection

class MangaAnimeNews(Base):
    __tablename__ = "tx_news"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    idx = Column(String(36))
    name = Column(String(255))
    slug = Column(String(255))
    thumb = Column(String(255))
    description = Column(LONGTEXT)
    content = Column(LONGTEXT)
    original = Column(String(255))
    author = Column(String(255))
    featured = Column(SMALLINT, default=0)
    type = Column(SMALLINT, default=1)
    ordinal = Column(SMALLINT, default=0)
    status = Column(SMALLINT, default=1)
    news_category_id = Column(Integer)
    meta_tag_id = Column(BIGINT)
    manga_ids = Column(LONGTEXT)
    anime_ids = Column(LONGTEXT)
    total_comment = Column(Integer)
    total_view = Column(Integer)
    total_like = Column(Integer)
    published_by = Column(Integer)
    created_by = Column(Integer, default=1)
    updated_by = Column(Integer, default=1)
    deleted_by = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime)
    list_img = Column(String(255))
    img_per = Column(BIGINT)