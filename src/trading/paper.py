import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import PortfolioItem, TradeExecution

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/trading.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PaperTrader")

class PaperTrader:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.initial_balance = 10000.0 # Başlangıç Bakiyesi ($)
        self._ensure_cash_account()

    def _ensure_cash_account(self):
        """USD bakiyesini kontrol et, yoksa oluştur"""
        session = self.session_factory()
        try:
            cash = session.query(PortfolioItem).filter_by(symbol='USD').first()
            if not cash:
                cash = PortfolioItem(
                    symbol='USD',
                    quantity=self.initial_balance,
                    average_price=1.0,
                    current_price=1.0
                )
                session.add(cash)
                session.commit()
                logger.info(f"💰 Cüzdan oluşturuldu: ${self.initial_balance}")
        except Exception as e:
            logger.error(f"Cüzdan hatası: {e}")
        finally:
            session.close()

    def get_portfolio_status(self):
        """Mevcut portföy durumunu döndür"""
        session = self.session_factory()
        try:
            items = session.query(PortfolioItem).all()
            total_value = 0.0
            holdings = []
            
            cash_item = next((i for i in items if i.symbol == 'USD'), None)
            cash = cash_item.quantity if cash_item else 0.0
            
            for item in items:
                if item.symbol == 'USD': continue
                
                value = item.quantity * item.current_price
                total_value += value
                
                holdings.append({
                    'symbol': item.symbol,
                    'quantity': item.quantity,
                    'avg_price': item.average_price,
                    'current_price': item.current_price,
                    'value': value,
                    'pnl': (item.current_price - item.average_price) / item.average_price * 100 if item.average_price > 0 else 0
                })
                
            return {
                'total_equity': total_value + cash,
                'cash': cash,
                'holdings': holdings
            }
        finally:
            session.close()

    def execute_strategy(self, signals):
        """Sinyallere göre işlem yap"""
        status = self.get_portfolio_status()
        cash = status['cash']
        
        session = self.session_factory()
        try:
            for signal in signals:
                symbol = signal['symbol']
                price = signal.get('price', {}).get('current', 0)
                decision = signal['decision']
                confidence = signal['confidence']
                
                if price <= 0: continue

                # Mevcut pozisyonu bul
                position = session.query(PortfolioItem).filter_by(symbol=symbol).first()
                current_qty = position.quantity if position else 0

                # --- SATIŞ MANTIĞI ---
                if decision in ['SELL', 'STRONG SELL'] and current_qty > 0:
                    sell_qty = current_qty # Hepsini sat (basit strateji)
                    amount = sell_qty * price
                    
                    # Log Trade
                    trade = TradeExecution(
                        symbol=symbol,
                        action='SELL',
                        quantity=sell_qty,
                        price=price,
                        total_amount=amount,
                        pnl=amount - (sell_qty * position.average_price) # Kar/Zarar
                    )
                    session.add(trade)
                    
                    # Update Portfolio
                    session.delete(position)
                    
                    # Update Cash
                    cash_acc = session.query(PortfolioItem).filter_by(symbol='USD').first()
                    cash_acc.quantity += amount
                    
                    logger.info(f"🔴 SATIŞ: {symbol} - {sell_qty} adet @ ${price}")

                # --- ALIM MANTIĞI ---
                elif decision in ['BUY', 'STRONG BUY'] and confidence > 70:
                    # Bakiyenin %10'u ile al
                    trade_amount = status['total_equity'] * 0.10
                    if trade_amount > cash: trade_amount = cash # Nakit yetmiyorsa kalanı kullan
                    
                    if trade_amount > 100: # Minimum 100$lık işlem
                        qty = trade_amount / price
                        
                        # Log Trade
                        trade = TradeExecution(
                            symbol=symbol,
                            action='BUY',
                            quantity=qty,
                            price=price,
                            total_amount=trade_amount
                        )
                        session.add(trade)
                        
                        # Update Portfolio
                        if position:
                            # Ortalama maliyet hesabı
                            total_cost = (position.quantity * position.average_price) + trade_amount
                            position.quantity += qty
                            position.average_price = total_cost / position.quantity
                            position.current_price = price
                        else:
                            new_pos = PortfolioItem(
                                symbol=symbol, 
                                quantity=qty, 
                                average_price=price,
                                current_price=price
                            )
                            session.add(new_pos)
                        
                        # Update Cash
                        cash_acc = session.query(PortfolioItem).filter_by(symbol='USD').first()
                        cash_acc.quantity -= trade_amount
                        
                        logger.info(f"🟢 ALIM: {symbol} - {qty:.2f} adet @ ${price}")
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Trade hatası: {e}")
            session.rollback()
        finally:
            session.close()
