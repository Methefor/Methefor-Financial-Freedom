import { DollarSign, TrendingDown, TrendingUp, Wallet } from 'lucide-react';

export const PortfolioSection = ({ portfolio }) => {
  if (!portfolio) return null;

  return (
    <div className="space-y-8">
      {/* Portfolio Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard 
          label="Toplam Bakiye" 
          value={`$${portfolio.total_equity?.toLocaleString()}`} 
          icon={<Wallet className="text-gold" />} 
        />
        <StatCard 
          label="Nakit (USD)" 
          value={`$${portfolio.cash?.toLocaleString()}`} 
          icon={<DollarSign className="text-blue-400" />} 
        />
        <StatCard 
          label="Varlık Değeri" 
          value={`$${(portfolio.total_equity - portfolio.cash)?.toLocaleString()}`} 
          icon={<TrendingUp className="text-green-400" />} 
        />
      </div>

      {/* Holdings Table */}
      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-bold">Varlıklarım</h2>
        </div>
        <table className="w-full text-left">
          <thead className="bg-white/[0.02] text-white/40 text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4 font-semibold">Sembol</th>
              <th className="px-6 py-4 font-semibold">Miktar</th>
              <th className="px-6 py-4 font-semibold">Maliyet</th>
              <th className="px-6 py-4 font-semibold">Fiyat</th>
              <th className="px-6 py-4 font-semibold">Kar/Zarar</th>
              <th className="px-6 py-4 font-semibold">Değer</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {portfolio.holdings?.map((item, i) => (
              <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-6 py-4 font-bold">{item.symbol}</td>
                <td className="px-6 py-4 text-sm">{item.quantity?.toFixed(4)}</td>
                <td className="px-6 py-4 text-sm text-white/60">${item.avg_price?.toFixed(2)}</td>
                <td className="px-6 py-4 text-sm font-semibold">${item.price?.toFixed(2)}</td>
                <td className={`px-6 py-4 text-sm font-bold flex items-center gap-1 ${item.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {item.pnl >= 0 ? <TrendingUp size={14}/> : <TrendingDown size={14}/>}
                  {item.pnl?.toFixed(2)}%
                </td>
                <td className="px-6 py-4 text-sm font-bold">${item.value?.toLocaleString()}</td>
              </tr>
            ))}
            {(!portfolio.holdings || portfolio.holdings.length === 0) && (
              <tr>
                <td colSpan="6" className="px-6 py-20 text-center text-white/20 italic">
                  Henüz bir varlık bulunmuyor. Kağıt işlemler (Paper Trading) başladığında burada görünecektir.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon }) => (
  <div className="p-6 bg-white/5 border border-white/10 rounded-2xl flex items-center gap-6">
    <div className="w-14 h-14 bg-white/5 rounded-xl flex items-center justify-center text-2xl">
      {icon}
    </div>
    <div>
      <span className="text-sm text-white/40 font-medium">{label}</span>
      <h3 className="text-2xl font-bold tracking-tight">{value}</h3>
    </div>
  </div>
);
