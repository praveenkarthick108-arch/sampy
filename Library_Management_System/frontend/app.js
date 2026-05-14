/* =============================================================================
   Library Management System — React App
   Framework : React 18 (CDN UMD) + Babel Standalone (no Node.js / npm)
   Styling   : Tailwind CSS (CDN)
   HTTP      : Axios (CDN)
   Charts    : Recharts (CDN)
   Routing   : Hash-based (no react-router-dom needed)
   ========================================================================= */

/* global React, ReactDOM, axios, Recharts */

// Guard: surface missing CDN globals early with a clear message
if (typeof React === 'undefined')    throw new Error('React CDN did not load');
if (typeof ReactDOM === 'undefined') throw new Error('ReactDOM CDN did not load');
if (typeof axios === 'undefined')    throw new Error('Axios CDN did not load');
if (typeof Recharts === 'undefined') throw new Error('Recharts CDN did not load — check that prop-types is loaded before Recharts');

const {
  useState, useEffect, useCallback, useRef, createContext, useContext
} = React;

const {
  BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie,
  Cell, Legend, ResponsiveContainer
} = Recharts;


// ─────────────────────────────────────────────────────────────────────────────
// API LAYER
// ─────────────────────────────────────────────────────────────────────────────

const http = axios.create({ baseURL: '' });
http.interceptors.response.use(
  r => r,
  e => Promise.reject(new Error(e.response?.data?.detail || e.message || 'Request failed'))
);

const api = {
  getDashboard:        ()        => http.get('/dashboard'),
  getBooks:            ()        => http.get('/books/'),
  createBook:          d         => http.post('/books/', d),
  updateBook:          (id, d)   => http.put(`/books/${id}`, d),
  deleteBook:          id        => http.delete(`/books/${id}`),
  getCategories:       ()        => http.get('/books/categories'),
  getBorrowers:        ()        => http.get('/borrowers/'),
  createBorrower:      d         => http.post('/borrowers/', d),
  updateBorrower:      (id, d)   => http.put(`/borrowers/${id}`, d),
  deleteBorrower:      id        => http.delete(`/borrowers/${id}`),
  getBorrowerHistory:  id        => http.get(`/borrowers/${id}/transactions`),
  getTransactions:     ()        => http.get('/transactions'),
  borrowBook:          d         => http.post('/borrow', d),
  returnBook:          d         => http.post('/return', d),
  searchBooks:         (q, cat)  => http.get('/search', { params: { q, category: cat } }),
};


// ─────────────────────────────────────────────────────────────────────────────
// HASH ROUTER
// ─────────────────────────────────────────────────────────────────────────────

function useHash() {
  const [hash, setHash] = useState(window.location.hash || '#/');
  useEffect(() => {
    const h = () => setHash(window.location.hash || '#/');
    window.addEventListener('hashchange', h);
    return () => window.removeEventListener('hashchange', h);
  }, []);
  const go = useCallback(to => { window.location.hash = to; }, []);
  return [hash, go];
}


// ─────────────────────────────────────────────────────────────────────────────
// TOAST SYSTEM
// ─────────────────────────────────────────────────────────────────────────────

const ToastCtx = createContext(null);

function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const add = useCallback((msg, type = 'success') => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, msg, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3800);
  }, []);

  const toast = {
    success: m => add(m, 'success'),
    error:   m => add(m, 'error'),
  };

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div style={{ position:'fixed', top:16, right:16, zIndex:9999, display:'flex', flexDirection:'column', gap:8, maxWidth:360 }}>
        {toasts.map(t => (
          <div key={t.id} className={`toast-in px-4 py-3 rounded-xl shadow-xl text-white text-sm font-medium flex items-center gap-2 ${
            t.type === 'error' ? 'bg-red-500' : 'bg-emerald-500'
          }`}>
            <span>{t.type === 'error' ? '✗' : '✓'}</span>
            {t.msg}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
const useToast = () => useContext(ToastCtx);


// ─────────────────────────────────────────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────────────────────────────────────────

const fmtDate = dt =>
  dt ? new Date(dt).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' }) : '—';

const fmtDateTime = dt =>
  dt ? new Date(dt).toLocaleString('en-IN', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' }) : '—';

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}


// ─────────────────────────────────────────────────────────────────────────────
// ICON COMPONENTS (inline SVG — no icon library needed)
// ─────────────────────────────────────────────────────────────────────────────

const ICONS = {
  dashboard:   <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  book:        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>,
  users:       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  arrows:      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>,
  search:      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  library:     <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  plus:        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  edit:        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  trash:       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>,
  refresh:     <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.5"/></svg>,
  return:      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 14l-4-4 4-4"/><path d="M5 10h11a4 4 0 0 1 0 8h-1"/></svg>,
  x:           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  history:     <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="12 8 12 12 14 14"/><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"/></svg>,
  check:       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  alert:       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
};

function Ico({ n, size = 16, cls = '' }) {
  return (
    <span style={{ width: size, height: size, display: 'inline-flex', flexShrink: 0, alignItems: 'center' }} className={cls}>
      {ICONS[n]}
    </span>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// SHARED UI COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────

function Spinner({ size = 28 }) {
  return (
    <div className="flex items-center justify-center w-full py-16">
      <span className="spin" style={{ display:'inline-block', width:size, height:size, border:`3px solid #e0e7ff`, borderTopColor:`#4f46e5`, borderRadius:'50%' }} />
    </div>
  );
}

function EmptyState({ icon, text, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-gray-400">
      <Ico n={icon} size={44} />
      <p className="text-base">{text}</p>
      {action}
    </div>
  );
}

function Badge({ status }) {
  const map = {
    available: 'bg-emerald-100 text-emerald-700',
    borrowed:  'bg-amber-100  text-amber-700',
    returned:  'bg-gray-100   text-gray-500',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${map[status] || map.returned}`}>
      {status}
    </span>
  );
}

function Btn({ children, variant = 'primary', size = 'md', onClick, disabled, type = 'button', cls = '' }) {
  const v = {
    primary:   'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-indigo-400',
    danger:    'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    success:   'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500',
  }[variant];
  const s = size === 'sm' ? 'px-3 py-1.5 text-xs' : 'px-4 py-2 text-sm';
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center gap-1.5 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed ${v} ${s} ${cls}`}
    >
      {children}
    </button>
  );
}

function Input({ label, value, onChange, placeholder, type = 'text', error, required }) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className={`block w-full rounded-lg border px-3 py-2 text-sm placeholder-gray-400 shadow-sm focus:outline-none focus:ring-1 ${
          error ? 'border-red-400 focus:ring-red-400 focus:border-red-400' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
        } bg-white`}
      />
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}

function Select({ label, value, onChange, children, error, required }) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className={`block w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 bg-white ${
          error ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
        }`}
      >
        {children}
      </select>
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}

function Table({ head, children, empty }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            {head.map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {children}
        </tbody>
      </table>
      {empty}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// MODAL
// ─────────────────────────────────────────────────────────────────────────────

function Modal({ open, onClose, title, children, size = 'md' }) {
  useEffect(() => {
    const h = e => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, [onClose]);

  if (!open) return null;
  const w = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' }[size];

  return (
    <div style={{ position:'fixed', inset:0, zIndex:1000, display:'flex', alignItems:'center', justifyContent:'center', padding:16 }}>
      <div style={{ position:'absolute', inset:0, background:'rgba(0,0,0,0.5)' }} onClick={onClose} />
      <div className={`relative w-full ${w} bg-white rounded-2xl shadow-2xl flex flex-col`} style={{ maxHeight:'90vh' }}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors">
            <Ico n="x" size={18} />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 px-6 py-5">{children}</div>
      </div>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// SIDEBAR / LAYOUT
// ─────────────────────────────────────────────────────────────────────────────

const NAV = [
  { hash: '#/',            icon: 'dashboard', label: 'Dashboard'    },
  { hash: '#/books',       icon: 'book',      label: 'Books'        },
  { hash: '#/borrowers',   icon: 'users',     label: 'Borrowers'    },
  { hash: '#/transactions',icon: 'arrows',    label: 'Transactions' },
  { hash: '#/search',      icon: 'search',    label: 'Search'       },
];

function Sidebar({ currentHash, go }) {
  return (
    <aside className="flex-shrink-0 bg-indigo-900 flex flex-col" style={{ width: 220 }}>
      <div className="flex items-center gap-3 px-4 py-5 border-b border-indigo-700">
        <div className="p-2 bg-indigo-600 rounded-lg text-white"><Ico n="library" size={20} /></div>
        <div>
          <p className="text-white font-bold text-sm leading-tight">LibraryMS</p>
          <p className="text-indigo-300 text-xs">Management System</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4" style={{ display:'flex', flexDirection:'column', gap:4 }}>
        {NAV.map(({ hash, icon, label }) => {
          const active = currentHash === hash || (hash !== '#/' && currentHash.startsWith(hash));
          return (
            <a
              key={hash}
              href={hash}
              onClick={e => { e.preventDefault(); go(hash); }}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active ? 'bg-indigo-600 text-white' : 'text-indigo-200 hover:bg-indigo-800 hover:text-white'
              }`}
            >
              <Ico n={icon} size={16} />
              {label}
            </a>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-indigo-700">
        <p className="text-indigo-400 text-xs">Phase 1 · v1.0.0</p>
      </div>
    </aside>
  );
}

function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// PAGE: DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

function StatCard({ icon, label, value, color, onClick }) {
  const colors = {
    indigo:  { bg: 'bg-indigo-50',  text: 'text-indigo-600',  border: 'border-indigo-200' },
    emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200' },
    amber:   { bg: 'bg-amber-50',   text: 'text-amber-600',   border: 'border-amber-200'  },
    violet:  { bg: 'bg-violet-50',  text: 'text-violet-600',  border: 'border-violet-200' },
    sky:     { bg: 'bg-sky-50',     text: 'text-sky-600',     border: 'border-sky-200'    },
  }[color];

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl shadow-sm border p-5 flex items-center justify-between cursor-pointer hover:shadow-md transition-shadow ${colors.border}`}
    >
      <div>
        <p className={`text-xs font-semibold uppercase tracking-wide mb-1 ${colors.text}`}>{label}</p>
        <p className="text-3xl font-bold text-gray-900">{value ?? '—'}</p>
      </div>
      <div className={`p-3 rounded-xl ${colors.bg} ${colors.text}`}>
        <Ico n={icon} size={24} />
      </div>
    </div>
  );
}

function Dashboard({ go }) {
  const [stats, setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.getDashboard();
      setStats(data);
    } catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, []);

  if (loading) return <Spinner />;
  if (!stats) return null;

  const barData = [
    { name: 'Total',     value: stats.total_books },
    { name: 'Available', value: stats.available_books },
    { name: 'Borrowed',  value: stats.borrowed_books },
    { name: 'Borrowers', value: stats.total_borrowers },
  ];
  const pieData = [
    { name: 'Available', value: stats.available_books },
    { name: 'Borrowed',  value: stats.borrowed_books  },
  ];
  const PIE_COLORS = ['#10b981', '#f59e0b'];

  return (
    <div className="p-6">
      <PageHeader title="Dashboard" subtitle="Library at a glance">
        <Btn variant="secondary" size="sm" onClick={load}><Ico n="refresh" size={13} /> Refresh</Btn>
      </PageHeader>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
        <StatCard icon="book"    label="Total Books"   value={stats.total_books}       color="indigo"  onClick={() => go('#/books')} />
        <StatCard icon="check"   label="Available"     value={stats.available_books}   color="emerald" onClick={() => go('#/books')} />
        <StatCard icon="alert"   label="Borrowed"      value={stats.borrowed_books}    color="amber"   onClick={() => go('#/transactions')} />
        <StatCard icon="users"   label="Borrowers"     value={stats.total_borrowers}   color="violet"  onClick={() => go('#/borrowers')} />
        <StatCard icon="arrows"  label="Transactions"  value={stats.total_transactions} color="sky"    onClick={() => go('#/transactions')} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <p className="font-semibold text-gray-800 mb-4">Library Overview</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} barSize={44}>
              <XAxis dataKey="name" tick={{ fontSize:12 }} />
              <YAxis tick={{ fontSize:12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[6,6,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <p className="font-semibold text-gray-800 mb-4">Book Availability</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
              </Pie>
              <Tooltip />
              <Legend iconType="circle" iconSize={10} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent transactions */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <p className="font-semibold text-gray-800">Recent Transactions</p>
          <button onClick={() => go('#/transactions')} className="text-indigo-600 text-sm hover:underline">View all →</button>
        </div>
        {stats.recent_transactions.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No transactions yet.</p>
        ) : (
          <Table head={['#', 'Book', 'Borrower', 'Borrow Date', 'Return Date', 'Status']}>
            {stats.recent_transactions.map(t => (
              <tr key={t.transaction_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-xs text-gray-400">{t.transaction_id}</td>
                <td className="px-4 py-3 text-sm font-medium">{t.book?.title ?? `Book #${t.book_id}`}</td>
                <td className="px-4 py-3 text-sm">{t.borrower?.borrower_name ?? `#${t.borrower_id}`}</td>
                <td className="px-4 py-3 text-xs">{fmtDate(t.borrow_date)}</td>
                <td className="px-4 py-3 text-xs">{fmtDate(t.return_date)}</td>
                <td className="px-4 py-3"><Badge status={t.status} /></td>
              </tr>
            ))}
          </Table>
        )}
      </div>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// PAGE: BOOKS
// ─────────────────────────────────────────────────────────────────────────────

const BOOK_EMPTY = { title:'', author:'', category:'', isbn:'' };

function BookForm({ initial, onSave, onCancel, saving }) {
  const [f, setF] = useState(initial || BOOK_EMPTY);
  const [err, setErr] = useState({});

  const set = (k, v) => { setF(p => ({ ...p, [k]: v })); setErr(p => ({ ...p, [k]: '' })); };

  const validate = () => {
    const e = {};
    if (!f.title.trim())    e.title    = 'Title is required';
    if (!f.author.trim())   e.author   = 'Author is required';
    if (!f.category.trim()) e.category = 'Category is required';
    if (!f.isbn.trim())     e.isbn     = 'ISBN is required';
    setErr(e);
    return !Object.keys(e).length;
  };

  const submit = ev => { ev.preventDefault(); if (validate()) onSave(f); };

  return (
    <form onSubmit={submit} className="space-y-4">
      <Input label="Title"    value={f.title}    onChange={v => set('title', v)}    placeholder="e.g. Clean Code"           error={err.title}    required />
      <Input label="Author"   value={f.author}   onChange={v => set('author', v)}   placeholder="e.g. Robert C. Martin"    error={err.author}   required />
      <Input label="Category" value={f.category} onChange={v => set('category', v)} placeholder="e.g. Technology"          error={err.category} required />
      <Input label="ISBN"     value={f.isbn}     onChange={v => set('isbn', v)}     placeholder="e.g. 978-0-13-468599-1"   error={err.isbn}     required />
      <div className="flex justify-end gap-2 pt-2">
        <Btn variant="secondary" onClick={onCancel}>Cancel</Btn>
        <Btn type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save Book'}</Btn>
      </div>
    </form>
  );
}

function Books() {
  const [books,    setBooks]    = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [saving,   setSaving]   = useState(false);
  const [query,    setQuery]    = useState('');
  const [statusF,  setStatusF]  = useState('all');
  const [modal,    setModal]    = useState(null);   // null | { mode, book? }
  const [delTarget,setDelTarget] = useState(null);
  const toast = useToast();

  const load = useCallback(async () => {
    setLoading(true);
    try { const { data } = await api.getBooks(); setBooks(data); }
    catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, []);

  useEffect(() => {
    let r = books;
    if (query) {
      const q = query.toLowerCase();
      r = r.filter(b =>
        b.title.toLowerCase().includes(q) ||
        b.author.toLowerCase().includes(q) ||
        b.isbn.toLowerCase().includes(q) ||
        b.category.toLowerCase().includes(q)
      );
    }
    if (statusF !== 'all') r = r.filter(b => b.availability_status === statusF);
    setFiltered(r);
  }, [books, query, statusF]);

  const handleSave = async form => {
    setSaving(true);
    try {
      if (modal.mode === 'add') { await api.createBook(form); toast.success('Book added!'); }
      else { await api.updateBook(modal.book.book_id, form); toast.success('Book updated!'); }
      setModal(null); load();
    } catch (e) { toast.error(e.message); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    try { await api.deleteBook(delTarget.book_id); toast.success('Book deleted'); setDelTarget(null); load(); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="p-6">
      <PageHeader title="Books" subtitle={`${books.length} book${books.length !== 1 ? 's' : ''} in library`}>
        <Btn variant="secondary" size="sm" onClick={load}><Ico n="refresh" size={13} /></Btn>
        <Btn onClick={() => setModal({ mode:'add' })}><Ico n="plus" size={15} /> Add Book</Btn>
      </PageHeader>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <div className="relative flex-1">
          <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)', color:'#9ca3af' }}><Ico n="search" size={15} /></span>
          <input
            className="block w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
            placeholder="Search title, author, ISBN, category…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <Select value={statusF} onChange={setStatusF}>
          <option value="all">All Status</option>
          <option value="available">Available</option>
          <option value="borrowed">Borrowed</option>
        </Select>
      </div>

      {/* Table */}
      {loading ? <Spinner /> : filtered.length === 0 ? (
        <EmptyState icon="book" text="No books found"
          action={!query && statusF === 'all' && (
            <Btn onClick={() => setModal({ mode:'add' })}><Ico n="plus" size={15}/> Add First Book</Btn>
          )}
        />
      ) : (
        <Table head={['#','Title','Author','Category','ISBN','Status','Actions']}>
          {filtered.map((b, i) => (
            <tr key={b.book_id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-xs text-gray-400">{i + 1}</td>
              <td className="px-4 py-3 text-sm font-medium text-gray-900" style={{ maxWidth:200 }}>{b.title}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{b.author}</td>
              <td className="px-4 py-3">
                <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full text-xs font-medium">{b.category}</span>
              </td>
              <td className="px-4 py-3 text-xs font-mono text-gray-500">{b.isbn}</td>
              <td className="px-4 py-3"><Badge status={b.availability_status} /></td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-1">
                  <Btn variant="secondary" size="sm" onClick={() => setModal({ mode:'edit', book:b })}>
                    <Ico n="edit" size={13} />
                  </Btn>
                  <Btn variant="danger" size="sm" onClick={() => setDelTarget(b)} disabled={b.availability_status === 'borrowed'}>
                    <Ico n="trash" size={13} />
                  </Btn>
                </div>
              </td>
            </tr>
          ))}
        </Table>
      )}

      {/* Add / Edit */}
      <Modal open={!!modal} onClose={() => setModal(null)} title={modal?.mode === 'add' ? 'Add New Book' : 'Edit Book'}>
        <BookForm
          initial={modal?.book ? { title:modal.book.title, author:modal.book.author, category:modal.book.category, isbn:modal.book.isbn } : BOOK_EMPTY}
          onSave={handleSave} onCancel={() => setModal(null)} saving={saving}
        />
      </Modal>

      {/* Delete confirm */}
      <Modal open={!!delTarget} onClose={() => setDelTarget(null)} title="Delete Book" size="sm">
        <p className="text-gray-700 text-sm">Delete <strong>"{delTarget?.title}"</strong>? This cannot be undone.</p>
        <div className="flex justify-end gap-2 mt-5">
          <Btn variant="secondary" onClick={() => setDelTarget(null)}>Cancel</Btn>
          <Btn variant="danger" onClick={handleDelete}>Delete</Btn>
        </div>
      </Modal>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// PAGE: BORROWERS
// ─────────────────────────────────────────────────────────────────────────────

const BORROWER_EMPTY = { borrower_name:'', email:'', phone:'' };

function BorrowerForm({ initial, onSave, onCancel, saving }) {
  const [f, setF] = useState(initial || BORROWER_EMPTY);
  const [err, setErr] = useState({});

  const set = (k, v) => { setF(p => ({ ...p, [k]: v })); setErr(p => ({ ...p, [k]: '' })); };

  const validate = () => {
    const e = {};
    if (!f.borrower_name.trim()) e.borrower_name = 'Name is required';
    if (!f.email.trim())         e.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email)) e.email = 'Enter a valid email';
    if (!f.phone.trim())         e.phone = 'Phone is required';
    else if (!/^[0-9+\-\s()]{7,15}$/.test(f.phone)) e.phone = 'Enter a valid phone number';
    setErr(e);
    return !Object.keys(e).length;
  };

  const submit = ev => { ev.preventDefault(); if (validate()) onSave(f); };

  return (
    <form onSubmit={submit} className="space-y-4">
      <Input label="Full Name" value={f.borrower_name} onChange={v => set('borrower_name', v)} placeholder="e.g. Alice Smith"         error={err.borrower_name} required />
      <Input label="Email"     type="email" value={f.email} onChange={v => set('email', v)} placeholder="alice@example.com"          error={err.email}         required />
      <Input label="Phone"     value={f.phone} onChange={v => set('phone', v)} placeholder="+91 9876543210"                          error={err.phone}         required />
      <div className="flex justify-end gap-2 pt-2">
        <Btn variant="secondary" onClick={onCancel}>Cancel</Btn>
        <Btn type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save Borrower'}</Btn>
      </div>
    </form>
  );
}

function Borrowers() {
  const [borrowers, setBorrowers]   = useState([]);
  const [filtered,  setFiltered]    = useState([]);
  const [loading,   setLoading]     = useState(true);
  const [saving,    setSaving]      = useState(false);
  const [query,     setQuery]       = useState('');
  const [modal,     setModal]       = useState(null);
  const [delTarget, setDelTarget]   = useState(null);
  const [histModal, setHistModal]   = useState(null);
  const [history,   setHistory]     = useState([]);
  const [histLoad,  setHistLoad]    = useState(false);
  const toast = useToast();

  const load = useCallback(async () => {
    setLoading(true);
    try { const { data } = await api.getBorrowers(); setBorrowers(data); }
    catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (!query) return setFiltered(borrowers);
    const q = query.toLowerCase();
    setFiltered(borrowers.filter(b =>
      b.borrower_name.toLowerCase().includes(q) ||
      b.email.toLowerCase().includes(q) ||
      b.phone.includes(q)
    ));
  }, [borrowers, query]);

  const openHistory = async b => {
    setHistModal(b); setHistLoad(true); setHistory([]);
    try { const { data } = await api.getBorrowerHistory(b.borrower_id); setHistory(data); }
    catch (e) { toast.error(e.message); }
    finally { setHistLoad(false); }
  };

  const handleSave = async form => {
    setSaving(true);
    try {
      if (modal.mode === 'add') { await api.createBorrower(form); toast.success('Borrower added!'); }
      else { await api.updateBorrower(modal.borrower.borrower_id, form); toast.success('Borrower updated!'); }
      setModal(null); load();
    } catch (e) { toast.error(e.message); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    try { await api.deleteBorrower(delTarget.borrower_id); toast.success('Borrower deleted'); setDelTarget(null); load(); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="p-6">
      <PageHeader title="Borrowers" subtitle={`${borrowers.length} registered borrower${borrowers.length !== 1 ? 's' : ''}`}>
        <Btn variant="secondary" size="sm" onClick={load}><Ico n="refresh" size={13} /></Btn>
        <Btn onClick={() => setModal({ mode:'add' })}><Ico n="plus" size={15} /> Add Borrower</Btn>
      </PageHeader>

      <div className="relative max-w-sm mb-5">
        <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)', color:'#9ca3af' }}><Ico n="search" size={15} /></span>
        <input
          className="block w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
          placeholder="Search by name, email or phone…"
          value={query} onChange={e => setQuery(e.target.value)}
        />
      </div>

      {loading ? <Spinner /> : filtered.length === 0 ? (
        <EmptyState icon="users" text="No borrowers found"
          action={!query && <Btn onClick={() => setModal({ mode:'add' })}><Ico n="plus" size={15}/> Add First Borrower</Btn>}
        />
      ) : (
        <Table head={['#','Name','Email','Phone','Actions']}>
          {filtered.map((b, i) => (
            <tr key={b.borrower_id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-xs text-gray-400">{i + 1}</td>
              <td className="px-4 py-3 text-sm font-medium">{b.borrower_name}</td>
              <td className="px-4 py-3 text-sm text-indigo-600">
                <a href={`mailto:${b.email}`}>{b.email}</a>
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{b.phone}</td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-1">
                  <Btn variant="secondary" size="sm" onClick={() => openHistory(b)}><Ico n="history" size={13} /> History</Btn>
                  <Btn variant="secondary" size="sm" onClick={() => setModal({ mode:'edit', borrower:b })}><Ico n="edit" size={13} /></Btn>
                  <Btn variant="danger"    size="sm" onClick={() => setDelTarget(b)}><Ico n="trash" size={13} /></Btn>
                </div>
              </td>
            </tr>
          ))}
        </Table>
      )}

      {/* Add/Edit */}
      <Modal open={!!modal} onClose={() => setModal(null)} title={modal?.mode === 'add' ? 'Add Borrower' : 'Edit Borrower'}>
        <BorrowerForm
          initial={modal?.borrower ? { borrower_name:modal.borrower.borrower_name, email:modal.borrower.email, phone:modal.borrower.phone } : BORROWER_EMPTY}
          onSave={handleSave} onCancel={() => setModal(null)} saving={saving}
        />
      </Modal>

      {/* Delete */}
      <Modal open={!!delTarget} onClose={() => setDelTarget(null)} title="Delete Borrower" size="sm">
        <p className="text-gray-700 text-sm">Delete <strong>"{delTarget?.borrower_name}"</strong>? This cannot be undone.</p>
        <div className="flex justify-end gap-2 mt-5">
          <Btn variant="secondary" onClick={() => setDelTarget(null)}>Cancel</Btn>
          <Btn variant="danger" onClick={handleDelete}>Delete</Btn>
        </div>
      </Modal>

      {/* History */}
      <Modal open={!!histModal} onClose={() => setHistModal(null)} title={`Borrowing History — ${histModal?.borrower_name}`} size="lg">
        {histLoad ? <Spinner /> : history.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No borrowing history.</p>
        ) : (
          <Table head={['Book','Author','Borrow Date','Return Date','Status']}>
            {history.map(t => (
              <tr key={t.transaction_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{t.book?.title ?? `Book #${t.book_id}`}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{t.book?.author ?? '—'}</td>
                <td className="px-4 py-3 text-sm">{fmtDate(t.borrow_date)}</td>
                <td className="px-4 py-3 text-sm">{fmtDate(t.return_date)}</td>
                <td className="px-4 py-3"><Badge status={t.status} /></td>
              </tr>
            ))}
          </Table>
        )}
      </Modal>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// PAGE: TRANSACTIONS
// ─────────────────────────────────────────────────────────────────────────────

function BorrowForm({ books, borrowers, onSave, onCancel, saving }) {
  const [bookId,     setBookId]     = useState('');
  const [borrowerId, setBorrowerId] = useState('');
  const [err,        setErr]        = useState({});

  const available = books.filter(b => b.availability_status === 'available');

  const validate = () => {
    const e = {};
    if (!bookId)     e.book     = 'Please select a book';
    if (!borrowerId) e.borrower = 'Please select a borrower';
    setErr(e);
    return !Object.keys(e).length;
  };

  const submit = ev => {
    ev.preventDefault();
    if (validate()) onSave({ book_id: Number(bookId), borrower_id: Number(borrowerId) });
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <Select label="Book" value={bookId} onChange={v => { setBookId(v); setErr(p => ({ ...p, book:'' })); }} error={err.book} required>
        <option value="">— Select available book —</option>
        {available.map(b => <option key={b.book_id} value={b.book_id}>{b.title} — {b.author}</option>)}
      </Select>
      {available.length === 0 && <p className="text-amber-600 text-xs -mt-2">No books currently available.</p>}

      <Select label="Borrower" value={borrowerId} onChange={v => { setBorrowerId(v); setErr(p => ({ ...p, borrower:'' })); }} error={err.borrower} required>
        <option value="">— Select borrower —</option>
        {borrowers.map(b => <option key={b.borrower_id} value={b.borrower_id}>{b.borrower_name} ({b.email})</option>)}
      </Select>

      <div className="flex justify-end gap-2 pt-2">
        <Btn variant="secondary" onClick={onCancel}>Cancel</Btn>
        <Btn type="submit" disabled={saving || available.length === 0}>{saving ? 'Processing…' : 'Confirm Borrow'}</Btn>
      </div>
    </form>
  );
}

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [books,        setBooks]        = useState([]);
  const [borrowers,    setBorrowers]    = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [saving,       setSaving]       = useState(false);
  const [filter,       setFilter]       = useState('all');
  const [borrowModal,  setBorrowModal]  = useState(false);
  const [retTarget,    setRetTarget]    = useState(null);
  const toast = useToast();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [t, b, br] = await Promise.all([api.getTransactions(), api.getBooks(), api.getBorrowers()]);
      setTransactions(t.data); setBooks(b.data); setBorrowers(br.data);
    } catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, []);

  const filtered = filter === 'all' ? transactions : transactions.filter(t => t.status === filter);
  const activeCount = transactions.filter(t => t.status === 'borrowed').length;

  const handleBorrow = async form => {
    setSaving(true);
    try { await api.borrowBook(form); toast.success('Book borrowed successfully!'); setBorrowModal(false); load(); }
    catch (e) { toast.error(e.message); }
    finally { setSaving(false); }
  };

  const handleReturn = async () => {
    try { await api.returnBook({ transaction_id: retTarget.transaction_id }); toast.success('Book returned!'); setRetTarget(null); load(); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="p-6">
      <PageHeader title="Transactions" subtitle={`${transactions.length} total · ${activeCount} active borrow${activeCount !== 1 ? 's' : ''}`}>
        <Btn variant="secondary" size="sm" onClick={load}><Ico n="refresh" size={13} /></Btn>
        <Btn onClick={() => setBorrowModal(true)}><Ico n="plus" size={15} /> Borrow Book</Btn>
      </PageHeader>

      {/* Filter tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit mb-5">
        {['all','borrowed','returned'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
              filter === f ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}>
            {f}
          </button>
        ))}
      </div>

      {loading ? <Spinner /> : filtered.length === 0 ? (
        <EmptyState icon="arrows" text={`No ${filter !== 'all' ? filter : ''} transactions`} />
      ) : (
        <Table head={['#','Book','Borrower','Borrow Date','Return Date','Status','Action']}>
          {filtered.map(t => (
            <tr key={t.transaction_id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-xs text-gray-400">{t.transaction_id}</td>
              <td className="px-4 py-3">
                <p className="text-sm font-medium">{t.book?.title ?? `Book #${t.book_id}`}</p>
                <p className="text-xs text-gray-400">{t.book?.author}</p>
              </td>
              <td className="px-4 py-3">
                <p className="text-sm">{t.borrower?.borrower_name ?? `#${t.borrower_id}`}</p>
                <p className="text-xs text-gray-400">{t.borrower?.email}</p>
              </td>
              <td className="px-4 py-3 text-xs">{fmtDateTime(t.borrow_date)}</td>
              <td className="px-4 py-3 text-xs">{fmtDateTime(t.return_date)}</td>
              <td className="px-4 py-3"><Badge status={t.status} /></td>
              <td className="px-4 py-3">
                {t.status === 'borrowed' && (
                  <Btn variant="success" size="sm" onClick={() => setRetTarget(t)}>
                    <Ico n="return" size={13} /> Return
                  </Btn>
                )}
              </td>
            </tr>
          ))}
        </Table>
      )}

      {/* Borrow Modal */}
      <Modal open={borrowModal} onClose={() => setBorrowModal(false)} title="Borrow a Book">
        <BorrowForm books={books} borrowers={borrowers} onSave={handleBorrow} onCancel={() => setBorrowModal(false)} saving={saving} />
      </Modal>

      {/* Return Confirm */}
      <Modal open={!!retTarget} onClose={() => setRetTarget(null)} title="Return Book" size="sm">
        <p className="text-gray-700 text-sm">
          Confirm return of <strong>"{retTarget?.book?.title}"</strong> by <strong>{retTarget?.borrower?.borrower_name}</strong>?
        </p>
        <div className="flex justify-end gap-2 mt-5">
          <Btn variant="secondary" onClick={() => setRetTarget(null)}>Cancel</Btn>
          <Btn variant="success" onClick={handleReturn}>Confirm Return</Btn>
        </div>
      </Modal>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// PAGE: SEARCH
// ─────────────────────────────────────────────────────────────────────────────

function Search() {
  const [query,      setQuery]      = useState('');
  const [category,   setCategory]   = useState('');
  const [categories, setCategories] = useState([]);
  const [results,    setResults]    = useState([]);
  const [loading,    setLoading]    = useState(false);
  const [searched,   setSearched]   = useState(false);
  const toast = useToast();

  useEffect(() => {
    api.getCategories().then(({ data }) => setCategories(data)).catch(() => {});
  }, []);

  const doSearch = useCallback(
    debounce(async (q, cat) => {
      if (!q && !cat) { setResults([]); setSearched(false); return; }
      setLoading(true);
      try { const { data } = await api.searchBooks(q, cat); setResults(data); setSearched(true); }
      catch (e) { toast.error(e.message); }
      finally { setLoading(false); }
    }, 300),
    []
  );

  useEffect(() => { doSearch(query, category); }, [query, category]);

  const clear = () => { setQuery(''); setCategory(''); setResults([]); setSearched(false); };

  return (
    <div className="p-6">
      <PageHeader title="Search Books" subtitle="Search by title, author, ISBN or category" />

      {/* Search bar */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 max-w-2xl mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)', color:'#9ca3af' }}><Ico n="search" size={18} /></span>
            <input
              className="block w-full rounded-lg border border-gray-300 pl-10 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
              placeholder="Search by title, author or ISBN…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              autoFocus
            />
          </div>
          <Select value={category} onChange={setCategory}>
            <option value="">All Categories</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </Select>
          {(query || category) && <Btn variant="secondary" onClick={clear}>Clear</Btn>}
        </div>
      </div>

      {loading && <Spinner />}

      {!loading && searched && results.length === 0 && (
        <EmptyState icon="search" text="No books found matching your query" />
      )}

      {!loading && !searched && (
        <div className="flex flex-col items-center py-20 gap-3 text-gray-300">
          <Ico n="search" size={48} />
          <p className="text-gray-400 text-base">Start typing to search books</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Found <span className="font-semibold text-indigo-600">{results.length}</span> result{results.length !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {results.map(b => (
              <div key={b.book_id} className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-3 hover:shadow-md transition-shadow">
                <div className="w-full rounded-lg bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center" style={{ height:80 }}>
                  <Ico n="book" size={32} cls="text-indigo-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-sm leading-snug">{b.title}</h3>
                  <p className="text-gray-500 text-xs mt-0.5">{b.author}</p>
                </div>
                <div className="flex items-center justify-between">
                  <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full text-xs font-medium">{b.category}</span>
                  <Badge status={b.availability_status} />
                </div>
                <p className="text-xs font-mono text-gray-400 border-t border-gray-100 pt-2">ISBN: {b.isbn}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
// ROOT APP
// ─────────────────────────────────────────────────────────────────────────────

function App() {
  const [hash, go] = useHash();

  const page = () => {
    if (hash === '#/' || hash === '#')    return <Dashboard go={go} />;
    if (hash.startsWith('#/books'))       return <Books />;
    if (hash.startsWith('#/borrowers'))   return <Borrowers />;
    if (hash.startsWith('#/transactions'))return <Transactions />;
    if (hash.startsWith('#/search'))      return <Search />;
    return <Dashboard go={go} />;
  };

  return (
    <ToastProvider>
      <div style={{ display:'flex', height:'100vh', overflow:'hidden' }}>
        <Sidebar currentHash={hash} go={go} />
        <main style={{ flex:1, overflowY:'auto' }}>
          {page()}
        </main>
      </div>
    </ToastProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
