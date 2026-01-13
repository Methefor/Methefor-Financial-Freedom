import {
    Bell,
    ChevronRight,
    Globe,
    LineChart,
    Newspaper,
    Search,
    Settings as SettingsIcon,
    Wallet,
    Zap
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { NewsSection } from './components/NewsSection';
import { PortfolioSection } from './components/PortfolioSection';
import { SettingsSection } from './components/SettingsSection';
import { SignalCard } from './components/SignalCard';
import { SignalModal } from './components/SignalModal';
import { WatchlistSection } from './components/WatchlistSection';
import { useSocket } from './hooks/useSocket';
import { Portfolio, Signal } from './types';
import { fadeIn, slideIn } from './utils/animations';

const App = () => {
  const { signals, news, portfolio, settings, status } = useSocket();
  const [activeTab, setActiveTab] = useState('signals');
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  const themeClass = settings.ui?.theme || 'dark';
  const isCompact = settings.ui?.compact_mode;

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

  // Giriş animasyonları
  useEffect(() => {
    fadeIn('.main-content');
    slideIn('.sidebar-item');
  }, [activeTab]);

  return (
    <div className={`min-h-screen text-white flex overflow-hidden transition-colors duration-500 font-outfit ${
      themeClass === 'light' ? 'bg-[#f0f2f5] text-slate-900' : 
      themeClass === 'cyber' ? 'bg-[#050505] text-[#00ffcc] font-mono' :
      'bg-[#0a0e27] text-white'
    }`}>
      {/* Sidebar */}
      <aside className={`relative border-r transition-all duration-500 backdrop-blur-xl ${
        themeClass === 'light' ? 'bg-white/80 border-slate-200' : 
        themeClass === 'cyber' ? 'bg-black/90 border-[#00ffcc]/30' :
        'bg-[#0a0e27]/40 border-white/10'
      } ${isSidebarOpen ? (isCompact ? 'w-24' : 'w-72') : 'w-0 -ml-72'}`}>
        
        <div className="p-8 flex flex-col h-full gap-10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-tr from-gold to-yellow-500 rounded-2xl flex items-center justify-center shadow-[0_0_20px_rgba(255,215,0,0.3)]">
              <Zap className="text-dark-bg fill-current" size={24} />
            </div>
            {!isCompact && (
              <div className="flex flex-col">
                <span className="text-xl font-black tracking-tighter text-gold italic">METHEFOR</span>
                <span className="text-[10px] font-bold text-white/40 tracking-[0.2em] uppercase -mt-1">PRO v6.0</span>
              </div>
            )}
          </div>

          <nav className="flex flex-col gap-2">
            <SidebarItem 
              id="signals" 
              icon={<LineChart size={22} />} 
              label="Sinyaller" 
              active={activeTab === 'signals'} 
              onClick={setActiveTab} 
              isCompact={isCompact}
            />
            <SidebarItem 
              id="news" 
              icon={<Newspaper size={22} />} 
              label="Haber Akışı" 
              active={activeTab === 'news'} 
              onClick={setActiveTab} 
              isCompact={isCompact}
            />
            <SidebarItem 
              id="portfolio" 
              icon={<Wallet size={22} />} 
              label="Portföy" 
              active={activeTab === 'portfolio'} 
              onClick={setActiveTab} 
              isCompact={isCompact}
            />
            <SidebarItem 
              id="watchlist" 
              icon={<Globe size={22} />} 
              label="Radar" 
              active={activeTab === 'watchlist'} 
              onClick={setActiveTab} 
              isCompact={isCompact}
            />
            <div className="my-4 h-px bg-white/5 mx-2" />
            <SidebarItem 
              id="settings" 
              icon={<SettingsIcon size={22} />} 
              label="Ayarlar" 
              active={activeTab === 'settings'} 
              onClick={setActiveTab} 
              isCompact={isCompact}
            />
          </nav>

          <div className="mt-auto">
             {!isCompact && (
               <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-4">
                 <div className={`w-3 h-3 rounded-full animate-pulse ${status === 'connected' ? 'bg-green-500 shadow-[0_0_10px_#22c55e]' : 'bg-red-500'}`} />
                 <span className="text-xs font-bold text-white/60 uppercase tracking-widest">{status}</span>
               </div>
             )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
       <main className="flex-1 overflow-y-auto h-screen scroll-smooth bg-gradient-to-b from-transparent to-black/20">
        <div className="max-w-[1600px] mx-auto p-10 main-content">
          {/* Header Area */}
          <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
            <div>
              <h1 className="text-4xl font-black tracking-tight mb-2 capitalize">
                {activeTab === 'signals' && 'Canlı Sinyaller'}
                {activeTab === 'news' && 'Finansal Haberler'}
                {activeTab === 'portfolio' && 'Kişisel Portföy'}
                {activeTab === 'watchlist' && 'Radar & Takip'}
                {activeTab === 'settings' && 'Uygulama Ayarları'}
              </h1>
              <p className="text-white/40 font-medium">Hoşgeldin Methefor, bugün piyasalar hareketli.</p>
            </div>

            <div className="flex items-center gap-4 w-full md:w-auto">
              <div className="relative flex-1 md:w-80 group">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-gold transition-colors" size={20} />
                <input 
                  type="text" 
                  placeholder="Sembol veya anahtar kelime ara..."
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-14 pr-6 focus:outline-none focus:border-gold/50 focus:bg-white/[0.08] transition-all text-sm font-medium"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="relative">
                <button 
                  onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                  className={`p-4 bg-white/5 border border-white/10 rounded-2xl transition-all group ${isNotificationsOpen ? 'bg-gold text-dark-bg' : 'hover:bg-gold hover:text-dark-bg'}`}
                >
                  <Bell size={20} className="group-hover:scale-110 transition-transform" />
                  {signals.length > 0 && <span className="absolute top-3 right-3 w-2 h-2 bg-red-500 rounded-full border-2 border-[#0a0e27]" />}
                </button>

                {isNotificationsOpen && (
                  <div className="absolute right-0 mt-4 w-80 bg-[#0a0e27]/95 backdrop-blur-3xl border border-white/10 rounded-[32px] shadow-[0_20px_60px_rgba(0,0,0,0.5)] z-50 p-6 space-y-4 animate-in fade-in zoom-in-95 duration-200">
                    <div className="flex justify-between items-center mb-2">
                       <h4 className="text-xs font-black uppercase tracking-widest text-white/40">Son Sinyaller</h4>
                       <span className="text-[10px] font-bold text-gold px-2 py-1 bg-gold/10 rounded-lg">{signals.length} Yeni</span>
                    </div>
                    <div className="space-y-3">
                       {signals.slice(0, 5).map((sig, idx) => (
                         <div 
                          key={idx} 
                          onClick={() => { setSelectedSignal(sig); setIsNotificationsOpen(false); }}
                          className="p-4 bg-white/5 hover:bg-white/[0.08] rounded-2xl border border-white/5 cursor-pointer transition-all group"
                         >
                            <div className="flex justify-between items-center">
                               <span className="font-black text-sm">{sig.symbol}</span>
                               <span className={`text-[10px] font-black italic ${sig.decision.includes('BUY') ? 'text-green-400' : 'text-red-400'}`}>{sig.decision}</span>
                            </div>
                            <div className="text-[10px] text-white/30 font-bold mt-1">Güven: {sig.confidence.toFixed(1)}%</div>
                         </div>
                       ))}
                    </div>
                    <button 
                      onClick={() => { setActiveTab('signals'); setIsNotificationsOpen(false); }}
                      className="w-full py-3 bg-white/5 hover:bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest text-white/60 transition-all"
                    >
                      Tümünü Gör
                    </button>
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* Content Tabs */}
          <div className="min-h-[60vh]">
            {activeTab === 'signals' && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
                {filteredSignals.map((sig, i) => (
                  <SignalCard key={`${sig.symbol}-${i}`} signal={sig} onClick={() => setSelectedSignal(sig)} />
                ))}
              </div>
            )}

            {activeTab === 'news' && <NewsSection news={news} />}
            
            {activeTab === 'portfolio' && <PortfolioSection portfolio={portfolio as Portfolio} />}
            
            {activeTab === 'watchlist' && <WatchlistSection />}

            {activeTab === 'settings' && <SettingsSection initialSettings={settings} />}
          </div>
        </div>
      </main>

      {/* Modals */}
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

interface SidebarItemProps {
  id: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: (id: string) => void;
  isCompact?: boolean;
}

const SidebarItem = ({ id, icon, label, active, onClick, isCompact }: SidebarItemProps) => (
  <button 
    onClick={() => onClick(id)}
    className={`sidebar-item flex items-center gap-5 p-4 rounded-2xl transition-all relative group ${
      active 
        ? 'bg-gold text-dark-bg font-bold shadow-[0_10px_20px_rgba(255,215,0,0.2)]' 
        : 'text-white/40 hover:bg-white/5 hover:text-white'
    }`}
  >
    <div className={`${active ? 'scale-110' : 'group-hover:scale-110'} transition-transform`}>
      {icon}
    </div>
    {!isCompact && <span className="text-sm tracking-wide">{label}</span>}
    {active && !isCompact && (
      <ChevronRight size={16} className="ml-auto opacity-50" />
    )}
  </button>
);

export default App;
