import {
    Bot,
    Newspaper,
    RefreshCcw,
    Search,
    Settings as SettingsIcon,
    TrendingUp,
    Wallet,
    Zap
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { NewsSection } from './components/NewsSection';
import { PortfolioSection } from './components/PortfolioSection';
import { SettingsSection } from './components/SettingsSection';
import { TradingViewChart } from './components/TradingViewChart';
import { useSocket } from './hooks/useSocket';

const App = () => {
  const { signals, news, portfolio, settings, status, requestUpdate } = useSocket();
  const [activeTab, setActiveTab] = useState('signals');
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Tema ve Kompakt Mod yönetimi
  const themeClass = settings.ui?.theme || 'dark';
  const isCompact = settings.ui?.compact_mode;

  // Sinyalleri arama terimine göre filtrele
  const filteredSignals = useMemo(() => {
    if (!searchTerm) return signals;
    const term = searchTerm.toLowerCase();
    return signals.filter(s => 
      s.symbol.toLowerCase().includes(term) ||
      s.decision.toLowerCase().includes(term) ||
      s.ai_explanation?.toLowerCase().includes(term) ||
      s.reasons?.some(r => r.toLowerCase().includes(term))
    );
  }, [signals, searchTerm]);

  return (
    <div className={`min-h-screen text-white flex overflow-hidden transition-colors duration-500 ${
      themeClass === 'light' ? 'bg-[#f0f2f5] text-slate-900' : 
      themeClass === 'cyber' ? 'bg-[#050505] text-[#00ffcc] font-mono' :
      'bg-[#0a0e27] text-white'
    }`}>
      {/* Sidebar */}
      <aside className={`w-64 border-r p-6 flex flex-col gap-8 shrink-0 transition-all ${
        themeClass === 'light' ? 'bg-white border-slate-200' : 
        themeClass === 'cyber' ? 'bg-black border-[#00ffcc]/30' :
        'bg-[#0a0e27]/80 border-white/10'
      } ${isCompact ? 'w-20' : 'w-64'}`}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gold rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(255,215,0,0.3)]">
            <Zap className="text-black fill-black" size={24} />
          </div>
          <span className="text-xl font-black tracking-tighter">METHEFOR</span>
        </div>

        <nav className="flex flex-col gap-2">
          <NavItem 
            icon={<TrendingUp size={20}/>} 
            label={isCompact ? '' : "Sinyaller"} 
            active={activeTab === 'signals'} 
            onClick={() => setActiveTab('signals')} 
            theme={themeClass}
          />
          <NavItem 
            icon={<Newspaper size={20}/>} 
            label={isCompact ? '' : "Haberler"} 
            active={activeTab === 'news'} 
            onClick={() => setActiveTab('news')} 
            theme={themeClass}
          />
          <NavItem 
            icon={<Wallet size={20}/>} 
            label={isCompact ? '' : "Portföy"} 
            active={activeTab === 'portfolio'} 
            onClick={() => setActiveTab('portfolio')} 
            theme={themeClass}
          />
          <NavItem 
            icon={<SettingsIcon size={20}/>} 
            label={isCompact ? '' : "Ayarlar"} 
            active={activeTab === 'settings'} 
            onClick={() => setActiveTab('settings')} 
            theme={themeClass}
          />
        </nav>
      </aside>

      {/* Main Content */}
       <main className="flex-1 overflow-y-auto h-screen scroll-smooth">
        <div className="p-8 pb-32">
          <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
            <div>
              <h1 className="text-4xl font-black mb-2 tracking-tight">Finansal Özgürlük</h1>
              <div className="flex items-center gap-2 text-white/40 text-sm font-medium">
                <div className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                {status === 'connected' ? 'Canlı Veri Akışı Bağlı' : 'Bağlantı Kesildi...'}
              </div>
            </div>
            
            <div className="flex items-center gap-4 w-full md:w-auto">
              <button 
                onClick={requestUpdate}
                className="p-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all hover:scale-105 active:scale-95 group"
                title="Verileri Yenile"
              >
                <RefreshCcw size={20} className={status !== 'connected' ? 'animate-spin opacity-50' : 'group-hover:rotate-180 transition-transform duration-500'} />
              </button>
              <div className="relative flex-1 md:flex-initial">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={18} />
                <input 
                  type="text" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Sembol Ara (MSTR, BTC...)" 
                  className="bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 w-full md:w-64 focus:outline-none focus:border-gold/50 transition-all"
                />
              </div>
            </div>
          </header>

          {/* Content Tabs */}
          <div className="animate-in fade-in slide-in-from-top-4 duration-500">
            {activeTab === 'signals' && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredSignals.map((sig, i) => (
                  <SignalCard key={`${sig.symbol}-${i}`} signal={sig} onClick={() => setSelectedSignal(sig)} />
                ))}
                {filteredSignals.length === 0 && (
                  <EmptyState label={searchTerm ? `"${searchTerm}" için sonuç bulunamadı.` : "Henüz sinyal bulunmuyor"} />
                )}
              </div>
            )}

            {activeTab === 'news' && <NewsSection news={news} />}
            
            {activeTab === 'portfolio' && <PortfolioSection portfolio={portfolio} />}
            
            {activeTab === 'settings' && <SettingsSection initialSettings={settings} />}
          </div>
        </div>
      </main>

      {/* Modals & Overlays */}
      {selectedSignal && (
        <SignalModal 
          signal={selectedSignal} 
          onClose={() => setSelectedSignal(null)} 
        />
      )}

      {/* Floating Chat */}
      <ChatPanel />
    </div>
  );
};

const NavItem = ({ icon, label, active, onClick, theme }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 w-full ${
      active 
        ? (theme === 'cyber' ? 'bg-[#00ffcc] text-black shadow-[0_0_20px_#00ffcc]' : 'bg-gold text-black font-bold') 
        : (theme === 'light' ? 'text-slate-500 hover:bg-slate-100' : 'text-white/50 hover:bg-white/5')
    }`}
  >
    {icon}
    {label && <span className="text-sm tracking-wide">{label}</span>}
  </button>
);

const SignalModal = ({ signal, onClose }) => (
  <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-300">
    <div className="bg-dark-bg border border-white/10 w-full max-w-5xl rounded-[32px] overflow-hidden shadow-[0_20px_80px_rgba(0,0,0,0.6)] animate-in zoom-in-95 duration-300">
      <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gold/10 border border-gold/20 rounded-xl flex items-center justify-center text-gold font-black text-xl">
            {signal.symbol[0]}
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tight">{signal.symbol}</h2>
            <p className="text-white/30 text-xs font-mono">{new Date(signal.timestamp).toLocaleString()}</p>
          </div>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-all text-white/20 hover:text-white">
          <Zap size={24} className="rotate-45" />
        </button>
      </div>

      <div className="p-8 space-y-8 overflow-y-auto max-h-[80vh] scrollbar-thin">
        {/* TradingView Chart */}
        <TradingViewChart symbol={signal.symbol} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-8">
            <div className="p-6 bg-white/5 rounded-3xl border border-white/5 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gold/5 blur-3xl -mr-10 -mt-10" />
              <span className="text-[10px] text-white/30 block mb-3 uppercase tracking-[0.2em] font-bold">ANALİZ KARARI</span>
              <div className="flex items-center gap-4">
                <Badge decision={signal.decision} size="lg" />
                <div className="h-8 w-px bg-white/10" />
                <div>
                   <span className="text-[10px] text-white/30 block mb-0.5 uppercase tracking-tighter">SKOR</span>
                   <span className="text-2xl font-black text-gold">{(signal.combined_score || 0).toFixed(1)}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm font-black mb-4 flex items-center gap-2 text-gold tracking-widest uppercase">
                <Bot size={18} /> ASİSTAN ANALİZİ
              </h3>
              <div className="p-6 bg-gold/5 border border-gold/10 rounded-3xl text-base text-white/80 leading-relaxed font-medium">
                {signal.ai_explanation || 'Bu piyasa koşulları için detaylı AI analizi oluşturuluyor. Lütfen biraz sonra tekrar kontrol edin.'}
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="p-6 bg-white/5 rounded-3xl border border-white/5">
              <span className="text-[10px] text-white/30 block mb-4 uppercase tracking-[0.2em] font-bold">GÜVEN SEVİYESİ</span>
              <div className="flex items-center gap-4">
                <div className="flex-1 bg-white/10 h-2 rounded-full overflow-hidden">
                  <div className="bg-gold h-full shadow-[0_0_15px_rgba(255,215,0,0.5)] transition-all duration-1000" style={{ width: `${signal.confidence || 0}%` }} />
                </div>
                <span className="text-gold font-black text-xl tabular-nums">{(signal.confidence || 0).toFixed(0)}%</span>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-black mb-4 tracking-widest uppercase">TEKNİK KANITLAR</h3>
              <ul className="grid grid-cols-1 gap-3">
                {signal.reasons?.map((reason, i) => (
                  <li key={i} className="text-sm text-white/60 bg-white/[0.02] p-4 rounded-2xl border border-white/5 flex gap-4 items-center group hover:bg-white/5 transition-colors">
                    <div className="w-2 h-2 bg-gold rounded-full group-hover:scale-150 transition-transform" />
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const SignalCard = ({ signal, onClick }) => {
  const sentimentScore = signal.sentiment?.score || 0;
  const sentimentColor = sentimentScore > 0 ? 'text-green-400' : sentimentScore < 0 ? 'text-red-400' : 'text-white/40';

  return (
    <div 
      onClick={onClick}
      className="p-6 bg-white/5 border border-white/10 rounded-3xl hover:border-gold/30 hover:bg-white/[0.07] transition-all duration-500 group cursor-pointer relative overflow-hidden flex flex-col h-full shadow-lg"
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-gold/5 blur-3xl rounded-full -mr-10 -mt-10 group-hover:bg-gold/10 transition-colors" />
      
      <div className="flex justify-between items-start mb-6 shrink-0 z-10">
        <div>
          <h3 className="text-2xl font-black mb-1 group-hover:text-gold transition-colors tracking-tight">{signal.symbol}</h3>
          <span className="text-[10px] text-white/30 uppercase tracking-[0.15em] font-mono">{new Date(signal.timestamp).toLocaleTimeString()}</span>
        </div>
        <Badge decision={signal.decision} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8 flex-1 z-10">
        <div className="p-4 bg-white/[0.03] rounded-2xl border border-white/5 flex flex-col justify-center group-hover:bg-white/[0.05] transition-colors">
          <span className="text-[9px] uppercase tracking-widest text-white/30 mb-1 font-bold">Skor</span>
          <span className="text-2xl font-black text-gold tracking-tighter">{(signal.combined_score || 0).toFixed(1)}</span>
        </div>
        <div className="p-4 bg-white/[0.03] rounded-2xl border border-white/5 flex flex-col justify-center group-hover:bg-white/[0.05] transition-colors">
          <span className="text-[9px] uppercase tracking-widest text-white/30 mb-1 font-bold">Duyarlılık</span>
          <span className={`text-2xl font-black tracking-tighter ${sentimentColor}`}>
            {(sentimentScore || 0).toFixed(2)}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-white/5 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 bg-white/10 h-1 rounded-full overflow-hidden">
            <div className="bg-gold h-full" style={{ width: `${signal.confidence || 0}%` }} />
          </div>
          <span className="text-[10px] font-black text-white/50 tracking-tighter">{(signal.confidence || 0).toFixed(0)}% GÜVEN</span>
        </div>
        <span className="text-[11px] font-black text-gold group-hover:translate-x-2 transition-transform duration-500 flex items-center gap-1">
          DETAYLAR <Zap size={10} className="fill-gold" />
        </span>
      </div>
    </div>
  );
};

const Badge = ({ decision, size = 'sm' }) => {
  const styles = {
    'STRONG BUY': 'bg-green-500/20 text-green-400 border-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.3)]',
    'BUY': 'bg-green-500/10 text-green-500 border-green-500/30',
    'HOLD': 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30',
    'SELL': 'bg-red-500/10 text-red-500 border-red-500/30',
    'STRONG SELL': 'bg-red-500/20 text-red-400 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]',
  };
  
  const sizeClass = size === 'lg' ? 'px-6 py-2 text-xs' : 'px-3 py-1 text-[10px]';
  
  return (
    <span className={`${sizeClass} rounded-full font-black border uppercase tracking-[0.1em] text-center inline-block ${styles[decision] || styles['HOLD']}`}>
      {decision}
    </span>
  );
};

const EmptyState = ({ label }) => (
  <div className="col-span-full py-32 text-center bg-white/5 rounded-[40px] border border-dashed border-white/10 text-white/40 flex flex-col items-center justify-center gap-4">
    <Zap size={64} className="opacity-10 animate-pulse" />
    <p className="text-xl font-medium tracking-tight px-10">{label}</p>
    <button onClick={() => window.location.reload()} className="text-gold text-sm font-bold hover:underline">Safayı Yenile</button>
  </div>
);

export default App;
