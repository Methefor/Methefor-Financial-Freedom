import { ExternalLink, Newspaper } from 'lucide-react';
import { useEffect } from 'react';
import { NewsItem } from '../types';
import { slideIn } from '../utils/animations';

export const NewsSection = ({ news }: { news: NewsItem[] }) => {
  useEffect(() => {
    slideIn('.news-card');
  }, [news]);

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center gap-4">
        <div className="p-3 bg-gold/10 rounded-xl border border-gold/20">
          <Newspaper size={20} className="text-gold" />
        </div>
        <h2 className="text-2xl font-black tracking-tight">Piyasa Gündemi</h2>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {news.map((item, i) => (
          <NewsCard key={i} item={item} />
        ))}
      </div>
    </div>
  );
};

const NewsCard = ({ item }: { item: NewsItem }) => (
  <div className="news-card group p-6 bg-[#0a0e27]/40 backdrop-blur-xl border border-white/5 rounded-3xl hover:bg-white/[0.05] transition-all flex flex-col justify-between gap-6 border-l-2 border-l-gold/30">
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-[10px] uppercase font-bold text-white/30 tracking-widest bg-white/5 px-3 py-1 rounded-full">{item.source}</span>
        <div className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${
          item.sentiment?.label === 'positive' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 
          item.sentiment?.label === 'negative' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
          'bg-white/5 text-white/40 border-white/10'
        }`}>
          {item.sentiment?.label || 'Neutral'}
        </div>
      </div>
      <h3 className="text-lg font-bold text-white/90 leading-tight group-hover:text-gold transition-colors">
        {item.title}
      </h3>
      <p className="text-sm text-white/40 line-clamp-2 leading-relaxed font-medium">{item.summary}</p>
    </div>
    
    <div className="flex justify-between items-center pt-4 border-t border-white/5">
      <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest">
        {new Date(item.published).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {new Date(item.published).toLocaleDateString()}
      </span>
      <a 
        href={item.link} 
        target="_blank" 
        rel="noreferrer"
        className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center text-gold hover:bg-gold hover:text-dark-bg transition-all"
      >
        <ExternalLink size={16} />
      </a>
    </div>
  </div>
);
