import axios from 'axios';
import { AlertCircle, Bell, CheckCircle2, Palette, Save, Settings as SettingsIcon, Sliders } from 'lucide-react';
import { useEffect, useState } from 'react';
import { AppSettings } from '../types';
import { popIn } from '../utils/animations';

interface SettingsSectionProps {
  initialSettings: Partial<AppSettings>;
}

export const SettingsSection = ({ initialSettings }: SettingsSectionProps) => {
  const defaultSettings: AppSettings = {
    analysis: { rsi_overbought: 70, rsi_oversold: 30, min_confidence: 70 },
    ui: { theme: 'dark', compact_mode: false },
    notifications: { telegram_enabled: true, browser_push_enabled: false }
  };
  
  const [settings, setSettings] = useState<AppSettings>({ ...defaultSettings, ...initialSettings as AppSettings });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    popIn('.settings-card');
  }, []);

  useEffect(() => {
    if (initialSettings && Object.keys(initialSettings).length > 0) {
      setSettings(prev => ({ ...prev, ...initialSettings as AppSettings }));
    }
  }, [initialSettings]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.post('/api/settings', settings);
      setMessage('Ayarlar başarıyla buluta kaydedildi!');
      setTimeout(() => setMessage(''), 4000);
    } catch (error) {
      setMessage('Hata: Ayarlar kaydedilemedi.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-6xl space-y-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-10">
        <div>
          <h2 className="text-3xl font-black tracking-tight flex items-center gap-4">
            <SettingsIcon className="text-gold" size={32} /> Sistem Yapılandırması
          </h2>
          <p className="text-white/40 font-medium mt-1">Algoritma eşikleri ve görsel arayüz tercihlerini yönet.</p>
        </div>
        <button 
          onClick={handleSave}
          disabled={loading}
          className="flex items-center gap-3 px-8 py-4 bg-gold text-dark-bg font-black rounded-[24px] hover:shadow-[0_20px_40px_rgba(255,215,0,0.3)] hover:-translate-y-1 active:translate-y-0 transition-all disabled:opacity-50 shadow-xl"
        >
          <Save size={20} />
          {loading ? 'Senkronize Ediliyor...' : 'Değişiklikleri Yayınla'}
        </button>
      </div>

      {message && (
        <div className={`p-6 rounded-[24px] flex items-center gap-4 border animate-in slide-in-from-top-4 duration-500 ${
          message.includes('Hata') 
          ? 'bg-red-500/10 text-red-400 border-red-500/20' 
          : 'bg-green-500/10 text-green-400 border-green-500/20'
        }`}>
          {message.includes('Hata') ? <AlertCircle size={24} /> : <CheckCircle2 size={24} />}
          <span className="font-bold tracking-tight">{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Analysis Settings */}
        <SettingsCard title="Analiz Motoru" icon={<Sliders size={20}/>} className="settings-card">
          <div className="space-y-8">
            <RangeInput 
              label="RSI Aşırı Alım" 
              min={50} max={90} 
              value={settings.analysis.rsi_overbought} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, rsi_overbought: val}})}
            />
            <RangeInput 
              label="RSI Aşırı Satım" 
              min={10} max={50} 
              value={settings.analysis.rsi_oversold} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, rsi_oversold: val}})}
            />
            <RangeInput 
              label="Min. Güven Skoru" 
              min={1} max={100} 
              value={settings.analysis.min_confidence} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, min_confidence: val}})}
            />
          </div>
        </SettingsCard>

        {/* UI Settings */}
        <SettingsCard title="Görsel Arayüz" icon={<Palette size={20}/>} className="settings-card">
          <div className="space-y-6">
             <div className="space-y-2">
               <label className="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">Renk Paleti</label>
               <select 
                value={settings.ui.theme}
                onChange={e => setSettings({...settings, ui: {...settings.ui, theme: e.target.value as any}})}
                className="w-full bg-[#0a0e27] border border-white/10 rounded-2xl px-5 py-4 focus:outline-none focus:border-gold/50 text-white font-bold transition-all appearance-none cursor-pointer"
               >
                 <option value="dark">Methefor Gold (Koyu)</option>
                 <option value="light">Methefor Silver (Açık)</option>
                 <option value="cyber">Cyberpunk Matrix</option>
               </select>
             </div>
             <div className="pt-4 border-t border-white/5">
              <ToggleInput 
                label="Kompakt Kenar Çubuğu" 
                checked={settings.ui.compact_mode}
                onChange={val => setSettings({...settings, ui: {...settings.ui, compact_mode: val}})}
              />
             </div>
          </div>
        </SettingsCard>

        {/* Notification Settings */}
        <SettingsCard title="Bildirim Kanalları" icon={<Bell size={20}/>} className="settings-card">
          <div className="space-y-6">
            <ToggleInput 
               label="Telegram Entegrasyonu" 
               checked={settings.notifications.telegram_enabled}
               onChange={val => setSettings({...settings, notifications: {...settings.notifications, telegram_enabled: val}})}
             />
             <div className="h-px bg-white/5" />
             <ToggleInput 
               label="Anlık Tarayıcı Bildirimi" 
               checked={settings.notifications.browser_push_enabled}
               onChange={val => setSettings({...settings, notifications: {...settings.notifications, browser_push_enabled: val}})}
             />
          </div>
        </SettingsCard>
      </div>

      <div className="p-10 bg-white/5 border border-white/5 rounded-[40px] flex items-center gap-8 group">
         <div className="w-16 h-16 bg-gold/10 rounded-[24px] flex items-center justify-center text-gold border border-gold/20 group-hover:scale-110 transition-transform">
            <AlertCircle size={32} />
         </div>
         <div className="flex-1">
            <h4 className="font-black text-xl mb-1">Sistem Güncellemeleri</h4>
            <p className="text-white/40 text-sm font-medium">Ayarlarınız bulut sunucularımızla senkronize edilir ve tüm cihazlarınızda (Masaüstü/Dizüstü) otomatik olarak uygulanır.</p>
         </div>
      </div>
    </div>
  );
};

interface SettingsCardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const SettingsCard = ({ title, icon, children, className }: SettingsCardProps) => (
  <div className={`p-8 bg-[#0a0e27]/40 backdrop-blur-xl border border-white/10 rounded-[40px] shadow-sm transform transition-all hover:bg-[#0a0e27]/60 ${className}`}>
    <div className="flex items-center gap-4 text-gold border-b border-white/5 pb-6 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center border border-gold/10">
        {icon}
      </div>
      <h3 className="font-black text-lg italic tracking-tighter uppercase">{title}</h3>
    </div>
    {children}
  </div>
);

interface RangeInputProps {
  label: string;
  min: number;
  max: number;
  value: number;
  onChange: (val: number) => void;
}

const RangeInput = ({ label, min, max, value, onChange }: RangeInputProps) => (
  <div className="space-y-4">
    <div className="flex justify-between items-end">
      <span className="text-[10px] font-black text-white/30 uppercase tracking-widest ml-1">{label}</span>
      <span className="text-xl font-black text-gold">{value}</span>
    </div>
    <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
       <div 
        className="absolute top-0 left-0 h-full bg-gradient-to-r from-gold to-yellow-500 shadow-[0_0_10px_rgba(255,215,0,0.5)]" 
        style={{ width: `${((value - min) / (max - min)) * 100}%` }}
       />
       <input 
        type="range" min={min} max={max} value={value || min} 
        onChange={e => onChange(parseInt(e.target.value))}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
      />
    </div>
  </div>
);

interface ToggleInputProps {
  label: string;
  checked: boolean;
  onChange: (val: boolean) => void;
}

const ToggleInput = ({ label, checked, onChange }: ToggleInputProps) => (
  <div className="flex justify-between items-center group cursor-pointer" onClick={() => onChange(!checked)}>
    <span className="text-sm font-bold text-white/60 group-hover:text-white transition-colors">{label}</span>
    <button 
      className={`w-14 h-8 rounded-full transition-all relative ${checked ? 'bg-gold shadow-[0_0_15px_rgba(255,215,0,0.3)]' : 'bg-white/5 border border-white/10'}`}
    >
      <div className={`absolute top-1 w-6 h-6 rounded-full shadow-lg transition-all ${checked ? 'left-7 bg-dark-bg' : 'left-1 bg-white/20'}`} />
    </button>
  </div>
);
