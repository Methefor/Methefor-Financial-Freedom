"""
METHEFOR FİNANSAL ÖZGÜRLÜK - OTOMATİK ZAMANLAYICI
Bu script, methefor_engine.py'yi belirli aralıklarla çalıştırır.
"""

import schedule
import time
import subprocess
import sys
import logging
from datetime import datetime

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Logging kurulumu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - SCOUT - %(message)s',
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_job():
    """Motoru çalıştır"""
    print("\n" + "="*50)
    logger.info("🕒 ZAMANLANMIŞ GÖREV BAŞLATILIYOR...")
    print("="*50)
    
    start_time = datetime.now()
    
    try:
        # Python interpreter path'ini kullanarak çalıştır
        # Bu, aynı environment'ı kullanmasını garanti eder
        result = subprocess.run(
            [sys.executable, "methefor_engine.py"],
            capture_output=False, # Çıktıyı canlı görmek için False yapabiliriz veya loglamak için True
            text=True,
            check=False # Hata durumunda scriptin durmaması için
        )
        
        duration = datetime.now() - start_time
        
        if result.returncode == 0:
            logger.info(f"✅ Görev başarıyla tamamlandı. Süre: {duration}")
        else:
            logger.error(f"❌ Görev hatalı tamamlandı. Return Code: {result.returncode}")
            
    except Exception as e:
        logger.error(f"❌ Kritik Hata: {e}")

def main():
    logger.info("🚀 METHEFOR SCHEDULER BAŞLATILDI")
    logger.info("⏱️  Periyot: Her 15 dakikada bir")
    
    # İsterseniz burayı değiştirebilirsiniz (örn: schedule.every(1).hours)
    schedule.every(15).minutes.do(run_job)
    
    # İlk çalışmayı hemen yap
    logger.info("🔄 İlk çalışma başlatılıyor...")
    run_job()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            logger.error(f"Scheduler Loop Hatası: {e}")
            time.sleep(60) # Hata olursa 1 dk bekle devam et

if __name__ == "__main__":
    main()
