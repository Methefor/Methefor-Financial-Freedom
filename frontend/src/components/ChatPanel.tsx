import axios from 'axios';
import { Bot, MessageSquare, Send, Sparkles, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { popIn } from '../utils/animations';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

export const ChatPanel = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Merhaba! Ben Methefor Asistanı. Finansal veriler ve sistem durumu hakkında sana nasıl yardımcı olabilirim?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (isOpen && chatWindowRef.current) {
      popIn(chatWindowRef.current);
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('/api/chat', { message: input });
      setMessages(prev => [...prev, { role: 'ai', content: res.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: '❌ Üzgünüm, bir bağlantı hatası oluştu.' }]);
    }
    setLoading(false);
  };

  return (
    <>
      {/* Mini Toggle Button */}
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="fixed bottom-10 right-10 w-20 h-20 bg-gold text-dark-bg rounded-[24px] shadow-[0_20px_50px_rgba(255,215,0,0.3)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-50 group hover:rotate-6"
        >
          <div className="relative">
             <MessageSquare size={32} className="group-hover:hidden" />
             <Sparkles size={32} className="hidden group-hover:block animate-pulse" />
             <div className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 border-4 border-gold rounded-full" />
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div 
          ref={chatWindowRef}
          className="fixed bottom-10 right-10 w-[450px] h-[700px] bg-[#0a0e27]/95 backdrop-blur-2xl border border-white/10 rounded-[40px] shadow-[0_40px_100px_rgba(0,0,0,0.6)] flex flex-col z-[110] overflow-hidden"
        >
          {/* Header */}
          <div className="p-8 bg-gradient-to-r from-gold to-yellow-500 text-dark-bg flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-dark-bg/10 rounded-2xl flex items-center justify-center border border-dark-bg/10">
                <Bot size={24} />
              </div>
              <div>
                <span className="font-black text-xl italic tracking-tighter">METHEFOR AI</span>
                <div className="flex items-center gap-2 text-[10px] font-bold opacity-60 uppercase tracking-widest">
                   <div className="w-2 h-2 bg-dark-bg rounded-full animate-pulse" />
                   Çevrimiçi
                </div>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)} 
              className="w-10 h-10 border border-dark-bg/10 rounded-xl flex items-center justify-center hover:bg-dark-bg/10 transition-all"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-thin">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-5 rounded-[24px] text-sm leading-relaxed shadow-sm transform transition-all hover:scale-[1.02] ${
                  msg.role === 'user' 
                  ? 'bg-gold text-dark-bg font-bold rounded-tr-none' 
                  : 'bg-white/5 border border-white/5 text-white/90 rounded-tl-none'
                }`}>
                   {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/5 p-5 rounded-[24px] rounded-tl-none">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gold/40 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gold/60 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-gold/40 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-8 border-t border-white/5 bg-white/[0.02]">
            <div className="relative group">
              <input 
                type="text" 
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Piyasa hakkında bir şey sor..."
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-5 pl-6 pr-16 focus:outline-none focus:border-gold/50 focus:bg-white/10 transition-all font-medium text-sm"
              />
              <button 
                onClick={handleSend}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-gold text-dark-bg rounded-xl hover:scale-105 active:scale-95 flex items-center justify-center shadow-lg transition-all"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
