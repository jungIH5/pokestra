import logging
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String(64), primary_key=True)
    status = Column(String(20), nullable=False)
    score_url = Column(Text)
    audio_url = Column(Text)
    image_type = Column(String(20))
    music_params = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def _get_engine():
    global _engine
    if _engine is None:
        url = os.getenv("MYSQL_URL")
        if not url:
            return None
        try:
            _engine = create_engine(url, pool_pre_ping=True)
        except Exception as e:
            logger.warning("MySQL 엔진 생성 실패: %s", e)
            return None
    return _engine


def _get_session():
    global _SessionLocal
    engine = _get_engine()
    if engine is None:
        return None
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine)
    return _SessionLocal()


def init_db() -> None:
    engine = _get_engine()
    if engine is None:
        logger.info("MYSQL_URL 미설정 — DB 초기화 건너뜀")
        return
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.warning("DB 테이블 생성 실패: %s", e)


def upsert_job(job_id: str, status: str, **kwargs) -> None:
    session = _get_session()
    if session is None:
        return
    try:
        job = session.get(Job, job_id)
        if job is None:
            job = Job(job_id=job_id, status=status, **kwargs)
            session.add(job)
        else:
            job.status = status
            job.updated_at = datetime.utcnow()
            for k, v in kwargs.items():
                setattr(job, k, v)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.warning("DB 저장 실패 (job_id=%s): %s", job_id, e)
    finally:
        session.close()
