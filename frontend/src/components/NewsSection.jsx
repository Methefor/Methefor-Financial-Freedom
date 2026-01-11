import { ExternalLink, Newspaper } from 'lucide-react';

export const NewsSection = ({ news }) => (
  <div className="flex flex-col gap-4">
    <div className="flex items-center gap-2 mb-4">
      <Newspaper size={24} className="text-gold" />
      <h2 className="text-2xl font-bold">Son Haberler</h2>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {news.map((item, i) => (
        <NewsCard key={i} item={item} />
      ))}
    </div>
  </div>
);

const NewsCard = ({ item }) => (
  <div className="p-5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/[0.08] transition-all flex flex-col justify-between gap-4 group">
    <div>
      <div className="flex justify-between items-start mb-3">
        <span className="text-[10px] uppercase font-bold text-white/30 tracking-widest">{item.source}</span>
        <SentimentBadge sentiment={item.sentiment} />
      </div>
      <h3 className="font-semibold text-white/90 leading-snug group-hover:text-gold transition-colors underline-offset-4 decoration-gold/50 cursor-pointer">
        {item.title}
      </h3>
    </div>
    
    <div className="flex justify-between items-center mt-auto">
      <span className="text-[10px] text-white/40">{new Date(item.published).toLocaleString()}</span>
      <a 
        href={item.link} 
        target="_blank" 
        rel="noreferrer"
        className="text-gold hover:scale-110 transition-transform"
      >
        <ExternalLink size={16} />
      </a>
    </div>
  </div>
);

const SentimentBadge = ({ sentiment }) => {
  const colors = {
    positive: 'bg-green-500/20 text-green-400 border-green-500/50 shadow-[0_0_10px_rgba(34,197,94,0.2)]',
    negative: 'bg-red-500/20 text-red-400 border-red-500/50 shadow-[0_0_10px_rgba(239,68,68,0.2)]',
    neutral: 'bg-white/10 text-white/50 border-white/20'
  };
  return (
    <span className={`px-3 py-1 rounded-full text-[9px] font-bold border uppercase tracking-wider ${colors[sentiment?.label] || colors.neutral}`}>
      {sentiment?.label || 'Neutral'}
    </span>
  );
};
