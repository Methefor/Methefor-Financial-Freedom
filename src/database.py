
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import json
import os
from pathlib import Path

Base = declarative_base()

class NewsItem(Base):
    """Haber verisi modeli"""
    __tablename__ = 'news_items'

    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    title = Column(String(500))
    summary = Column(Text)
    link = Column(String(500), unique=True)
    published_date = Column(DateTime)
    category = Column(String(50))
    related_symbols = Column(String(200))  # JSON string or comma-separated
    sentiment_score = Column(Float, default=0.0)
    sentiment_label = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class TechnicalResult(Base):
    """Teknik analiz sonucu modeli"""
    __tablename__ = 'technical_results'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    price = Column(Float)
    rsi = Column(Float)
    macd_signal = Column(String(20)) # bullish/bearish
    trend = Column(String(20))       # bullish/bearish/neutral
    overall_score = Column(Float)
    
    # Detaylı JSON verisi (metrics)
    details = Column(JSON) 
    
    timestamp = Column(DateTime, default=datetime.utcnow)

class Signal(Base):
    """Al/Sat Sinyali modeli"""
    __tablename__ = 'signals'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), index=True)
    decision = Column(String(20))    # BUY, SELL, HOLD, STRONG BUY/SELL
    combined_score = Column(Float)
    confidence = Column(Float)
    
    news_sentiment_score = Column(Float)
    technical_score = Column(Float)
    
    reasons = Column(JSON)           # Neden bu karar verildi?
    ai_explanation = Column(Text, nullable=True) # YZ Açıklaması
    is_sent_to_telegram = Column(Integer, default=0) # Boolean 0/1
    
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db(db_path: str = "methefor.db"):
    """Veritabanını başlat"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Yeni bir session oluştur"""
    Session = sessionmaker(bind=engine)
    return Session()
