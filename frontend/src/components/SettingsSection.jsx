import axios from 'axios';
import { AlertCircle, Bell, Palette, Save, Settings as SettingsIcon, Sliders } from 'lucide-react';
import { useEffect, useState } from 'react';

export const SettingsSection = ({ initialSettings }) => {
  const defaultSettings = {
    analysis: { rsi_overbought: 70, rsi_oversold: 30, min_confidence: 70 },
    ui: { theme: 'dark', compact_mode: false },
    notifications: { telegram_enabled: true, browser_push_enabled: false }
  };
  
  const [settings, setSettings] = useState({ ...defaultSettings, ...initialSettings });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Update if initialSettings loads later
  useEffect(() => {
    if (initialSettings && Object.keys(initialSettings).length > 0) {
      setSettings(prev => ({ ...prev, ...initialSettings }));
    }
  }, [initialSettings]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.post('/api/settings', settings);
      setMessage('Ayarlar başarıyla kaydedildi!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Hata oluştu!');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl space-y-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-3">
          <SettingsIcon className="text-gold" /> Gelişmiş Özelleştirme
        </h2>
        <button 
          onClick={handleSave}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-gold text-dark-bg font-bold rounded-xl hover:shadow-[0_0_20px_rgba(255,215,0,0.4)] transition-all disabled:opacity-50"
        >
          <Save size={20} />
          {loading ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-xl flex items-center gap-3 ${message.includes('Hata') ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
          <AlertCircle size={20} />
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Analysis Settings */}
        <SettingsCard title="Analiz Eşikleri" icon={<Sliders size={20}/>}>
          <div className="space-y-4">
            <RangeInput 
              label="RSI Aşırı Alım (Overbought)" 
              min={50} max={90} 
              value={settings.analysis?.rsi_overbought} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, rsi_overbought: val}})}
            />
            <RangeInput 
              label="RSI Aşırı Satım (Oversold)" 
              min={10} max={50} 
              value={settings.analysis?.rsi_oversold} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, rsi_oversold: val}})}
            />
            <RangeInput 
              label="Minimum Güven Skoru (%)" 
              min={1} max={100} 
              value={settings.analysis?.min_confidence} 
              onChange={val => setSettings({...settings, analysis: {...settings.analysis, min_confidence: val}})}
            />
          </div>
        </SettingsCard>

        {/* UI Settings */}
        <SettingsCard title="Görünüm ve Tema" icon={<Palette size={20}/>}>
          <div className="space-y-4">
             <div className="flex justify-between items-center">
               <span className="text-white/60">Tema</span>
               <select 
                value={settings.ui?.theme}
                onChange={e => setSettings({...settings, ui: {...settings.ui, theme: e.target.value}})}
                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
               >
                 <option value="dark">Koyu (Gold Edition)</option>
                 <option value="light">Aydınlık (Silver)</option>
                 <option value="cyber">Cyberpunk</option>
               </select>
             </div>
             <ToggleInput 
               label="Kompakt Görünüm" 
               checked={settings.ui?.compact_mode}
               onChange={val => setSettings({...settings, ui: {...settings.ui, compact_mode: val}})}
             />
          </div>
        </SettingsCard>

        {/* Notification Settings */}
        <SettingsCard title="Bildirim Kanalları" icon={<Bell size={20}/>}>
          <div className="space-y-4">
            <ToggleInput 
               label="Telegram Bildirimleri" 
               checked={settings.notifications?.telegram_enabled}
               onChange={val => setSettings({...settings, notifications: {...settings.notifications, telegram_enabled: val}})}
             />
             <ToggleInput 
               label="Tarayıcı Bildirimleri" 
               checked={settings.notifications?.browser_push_enabled}
               onChange={val => setSettings({...settings, notifications: {...settings.notifications, browser_push_enabled: val}})}
             />
          </div>
        </SettingsCard>
      </div>
    </div>
  );
};

const SettingsCard = ({ title, icon, children }) => (
  <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
    <div className="flex items-center gap-3 text-gold/80 border-b border-white/5 pb-4 mb-2">
      {icon}
      <h3 className="font-bold text-lg">{title}</h3>
    </div>
    {children}
  </div>
);

const RangeInput = ({ label, min, max, value, onChange }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-sm">
      <span className="text-white/60">{label}</span>
      <span className="text-gold font-bold">{value}</span>
    </div>
    <input 
      type="range" min={min} max={max} value={value || min} 
      onChange={e => onChange(parseInt(e.target.value))}
      className="w-full accent-gold bg-white/10 rounded-lg h-2"
    />
  </div>
);

const ToggleInput = ({ label, checked, onChange }) => (
  <div className="flex justify-between items-center">
    <span className="text-white/60">{label}</span>
    <button 
      onClick={() => onChange(!checked)}
      className={`w-12 h-6 rounded-full transition-colors relative ${checked ? 'bg-gold' : 'bg-white/10'}`}
    >
      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${checked ? 'left-7' : 'left-1'}`} />
    </button>
  </div>
);
