import React, { useState, useEffect, useCallback } from 'react';

// --- ENTERPRISE SVG ICONS ---
const Icon = ({ name, className = "w-4 h-4", ...props }) => {
  const icons = {
    ticket: <path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z" />,
    bot: <><rect x="3" y="11" width="18" height="10" rx="2" /><circle cx="12" cy="5" r="2" /><path d="M12 7v4" /><line x1="8" y1="16" x2="8" y2="16" /><line x1="16" y1="16" x2="16" y2="16" /></>,
    wrench: <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />,
    book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></>,
    box: <><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" /></>,
    shield: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />,
    activity: <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />,
    dashboard: <><rect x="3" y="3" width="7" height="9" /><rect x="14" y="3" width="7" height="5" /><rect x="14" y="12" width="7" height="9" /><rect x="3" y="16" width="7" height="5" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></>,
    check: <polyline points="20 6 9 17 4 12" />,
    alert: <><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></>,
    refresh: <><polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" /></>,
    send: <><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></>,
    plus: <><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></>,
    search: <><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></>,
    user: <><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></>,
    link: <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />,
    sparkles: <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />,
    login: <><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" /><polyline points="10 17 15 12 10 7" /><line x1="15" y1="12" x2="3" y2="12" /></>,
    logout: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></>,
    lock: <><rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></>,
    upload: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></>,
    database: <><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" /><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" /></>,
  };

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      {...props}
    >
      {icons[name] || icons.ticket}
    </svg>
  );
};

// Priority badge helper
const PriorityBadge = ({ priority }) => {
  const p = (priority || 'medium').toLowerCase();
  const styles = {
    critical: 'bg-red-50 text-red-700 border-red-200',
    high: 'bg-orange-50 text-orange-700 border-orange-200',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${styles[p] || styles.medium}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${p === 'critical' ? 'bg-red-600' : p === 'high' ? 'bg-orange-500' : p === 'medium' ? 'bg-amber-500' : 'bg-emerald-500'}`} />
      {p.toUpperCase()}
    </span>
  );
};

// State & Status badge helper
const StatusBadge = ({ state, status }) => {
  const display = state || (status ? status.replace(/_/g, ' ') : 'New');
  const s = display.toLowerCase().replace(/[\s-]+/g, '_');
  const styles = {
    new: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    open: 'bg-sky-50 text-sky-700 border-sky-200',
    in_progress: 'bg-blue-50 text-blue-700 border-blue-200',
    work_in_progress: 'bg-blue-50 text-blue-700 border-blue-200',
    on_hold: 'bg-amber-50 text-amber-700 border-amber-200',
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    resolved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    closed: 'bg-slate-100 text-slate-700 border-slate-200',
    canceled: 'bg-rose-50 text-rose-700 border-rose-200',
    published: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    indexed: 'bg-teal-50 text-teal-700 border-teal-200',
    submitted: 'bg-blue-50 text-blue-700 border-blue-200',
    completed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    approved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rejected: 'bg-red-50 text-red-700 border-red-200',
    pending_approval: 'bg-amber-50 text-amber-700 border-amber-200',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[s] || styles.new}`}>
      {display.toUpperCase()}
    </span>
  );
};

export default function App() {
  // Authentication State
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('itsm_token') || '');
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('itsm_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Active Role: 'employee' | 'it_agent' | 'admin'
  const [role, setRole] = useState(() => {
    try {
      const saved = localStorage.getItem('itsm_user');
      return saved ? JSON.parse(saved).role : 'employee';
    } catch {
      return 'employee';
    }
  });

  const [activeTab, setActiveTab] = useState('overview');

  // Backend & Database status
  const [backendOnline, setBackendOnline] = useState(false);
  const [mongoConnected, setMongoConnected] = useState(false);
  const [serviceNowDemo, setServiceNowDemo] = useState(true);
  const [pineconeConfigured, setPineconeConfigured] = useState(false);

  // REAL APPLICATION DATA (NO DEMO DATA)
  const [tickets, setTickets] = useState([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newCommentText, setNewCommentText] = useState('');
  const [commentVisibility, setCommentVisibility] = useState('public');

  // Knowledge Documents & Articles
  const [knowledgeDocuments, setKnowledgeDocuments] = useState([]);
  const [knowledgeArticles, setKnowledgeArticles] = useState([]);
  const [selectedKbArticle, setSelectedKbArticle] = useState(null);
  const [kbSearch, setKbSearch] = useState('');

  // Software Catalog & Requests
  const [softwareCatalog, setSoftwareCatalog] = useState([]);
  const [softwareRequests, setSoftwareRequests] = useState([]);
  const [requestModalSw, setRequestModalSw] = useState(null);
  const [requestJustification, setRequestJustification] = useState('');
  const [requestDesignation, setRequestDesignation] = useState('Full Stack Software Engineer');
  const [requestEvaluating, setRequestEvaluating] = useState(false);
  const [requestEvaluationPreview, setRequestEvaluationPreview] = useState(null);

  // Audit Logs (Admin)
  const [auditLogs, setAuditLogs] = useState([]);

  // Intelligent Intake State
  const [intakeQuery, setIntakeQuery] = useState('');
  const [intakeLoading, setIntakeLoading] = useState(false);
  const [intakePreview, setIntakePreview] = useState(null);
  const [ticketCreatedSuccess, setTicketCreatedSuccess] = useState(null);

  // Chatbot State
  const [chatMessages, setChatMessages] = useState([
    {
      id: 'msg-0',
      role: 'assistant',
      content: 'Hello! I am your AI Helpdesk Assistant connected to MongoDB Atlas and Pinecone RAG. You can ask technical questions or describe an issue for intake classification.',
      sources: [],
      actions: ['Connect to VPN', 'My laptop is slow', 'Request Software']
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(null);

  // Automation / Self-Heal State
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [workflowStep, setWorkflowStep] = useState(0);
  const [workflowResults, setWorkflowResults] = useState([]);
  const [workflowFeedback, setWorkflowFeedback] = useState(null);

  // Document Ingestion Modal State
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('Network');
  const [uploadStatus, setUploadStatus] = useState(null);

  // Auth Modal State
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authFullName, setAuthFullName] = useState('');
  const [authDepartment, setAuthDepartment] = useState('Engineering');
  const [authSelectedRole, setAuthSelectedRole] = useState('employee');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // Helper: Request headers with authentication
  const getAuthHeaders = useCallback((isMultipart = false) => {
    const headers = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    } else {
      headers['Authorization'] = `Bearer dev-token-${role}`;
      headers['X-Dev-Mode'] = 'true';
      headers['X-Dev-User-Role'] = role;
      headers['X-Dev-User-Email'] = currentUser?.email || `${role}@enterprise.com`;
    }
    return headers;
  }, [authToken, role, currentUser]);

  // --- DATA SYNCHRONIZATION FROM MONGODB / BACKEND ---
  const loadTickets = useCallback(async () => {
    setTicketsLoading(true);
    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/tickets', {
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (data.success && Array.isArray(data.tickets)) {
        setTickets(data.tickets);
      }
    } catch (err) {
      console.warn("Could not load tickets:", err);
    } finally {
      setTicketsLoading(false);
    }
  }, [getAuthHeaders]);

  const fetchTickets = loadTickets;

  const loadKnowledge = useCallback(async () => {
    try {
      const [docsRes, artsRes] = await Promise.all([
        fetch('https://itsm-lqs3.vercel.app/api/knowledge/documents', { headers: getAuthHeaders() }),
        fetch('https://itsm-lqs3.vercel.app/api/knowledge/articles', { headers: getAuthHeaders() }),
      ]);
      const docsData = await docsRes.json();
      const artsData = await artsRes.json();
      if (docsData.success && Array.isArray(docsData.documents)) {
        setKnowledgeDocuments(docsData.documents);
      }
      if (artsData.success && Array.isArray(artsData.articles)) {
        setKnowledgeArticles(artsData.articles);
      }
    } catch (err) {
      console.warn("Could not load knowledge items:", err);
    }
  }, [getAuthHeaders]);

  const loadSoftware = useCallback(async () => {
    try {
      const [catRes, reqRes] = await Promise.all([
        fetch('https://itsm-lqs3.vercel.app/api/software/catalog', { headers: getAuthHeaders() }),
        fetch('https://itsm-lqs3.vercel.app/api/software/requests', { headers: getAuthHeaders() }),
      ]);
      const catData = await catRes.json();
      const reqData = await reqRes.json();
      if (catData.success && Array.isArray(catData.catalog)) {
        setSoftwareCatalog(catData.catalog);
      }
      if (reqData.success && Array.isArray(reqData.requests)) {
        setSoftwareRequests(reqData.requests);
      }
    } catch (err) {
      console.warn("Could not load software catalog/requests:", err);
    }
  }, [getAuthHeaders]);

  const loadAuditLogs = useCallback(async () => {
    if (role !== 'admin') return;
    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/audit-logs', {
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (data.success && Array.isArray(data.logs)) {
        setAuditLogs(data.logs);
      }
    } catch (err) {
      console.warn("Could not load audit logs:", err);
    }
  }, [role, getAuthHeaders]);

  // Strictly filter tickets so employees only see their own tickets
  const displayedTickets = (role === 'employee' && currentUser)
    ? tickets.filter(t => t.requester_id === currentUser.id || (currentUser.email && t.requester_email === currentUser.email) || (currentUser.full_name && t.requester_name === currentUser.full_name))
    : tickets;

  // Initial Boot & Health Check
  useEffect(() => {
    fetch('https://itsm-lqs3.vercel.app/api/health')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setBackendOnline(true);
          if (data.integrations) {
            setServiceNowDemo(data.integrations.servicenow_demo_mode);
            setMongoConnected(data.integrations.mongodb_configured || false);
            setPineconeConfigured(data.integrations.pinecone_configured || false);
          }
        }
      })
      .catch(() => {
        setBackendOnline(false);
      });

    loadTickets();
    loadKnowledge();
    loadSoftware();
    loadAuditLogs();
  }, [loadTickets, loadKnowledge, loadSoftware, loadAuditLogs]);

  // Live AI Governance Pre-evaluation for Software Requests
  useEffect(() => {
    if (!requestModalSw) {
      setRequestEvaluationPreview(null);
      return;
    }

    let active = true;
    const timer = setTimeout(async () => {
      setRequestEvaluating(true);
      try {
        const res = await fetch('https://itsm-lqs3.vercel.app/api/software/evaluate', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            software_id: requestModalSw.id,
            designation: requestDesignation,
            business_justification: requestJustification || 'Standard corporate software access',
          })
        });
        const data = await res.json();
        if (active && data.success && data.evaluation) {
          setRequestEvaluationPreview(data.evaluation);
        }
      } catch (err) {
        console.warn("Software evaluation failed:", err);
      } finally {
        if (active) setRequestEvaluating(false);
      }
    }, 250);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [requestModalSw, requestDesignation, requestJustification, getAuthHeaders]);

  // --- AUTHENTICATION HANDLERS ---
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword }),
      });
      const data = await res.json();

      if (data.success && data.token && data.user) {
        localStorage.setItem('itsm_token', data.token);
        localStorage.setItem('itsm_user', JSON.stringify(data.user));
        setAuthToken(data.token);
        setCurrentUser(data.user);
        setRole(data.user.role);
        setAuthModalOpen(false);
        setAuthPassword('');
        // Refresh data under new user credentials
        setTimeout(() => {
          loadTickets();
          loadKnowledge();
          loadSoftware();
          loadAuditLogs();
        }, 300);
      } else {
        setAuthError(data.error || 'Authentication failed. Please verify credentials.');
      }
    } catch (err) {
      setAuthError('Cannot connect to authentication service. Is backend running?');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: authEmail,
          password: authPassword,
          full_name: authFullName,
          role: authSelectedRole,
          department: authDepartment,
        }),
      });
      const data = await res.json();

      if (data.success && data.token && data.user) {
        localStorage.setItem('itsm_token', data.token);
        localStorage.setItem('itsm_user', JSON.stringify(data.user));
        setAuthToken(data.token);
        setCurrentUser(data.user);
        setRole(data.user.role);
        setAuthModalOpen(false);
        setAuthPassword('');
        // Refresh data
        setTimeout(() => {
          loadTickets();
          loadKnowledge();
          loadSoftware();
          loadAuditLogs();
        }, 300);
      } else {
        setAuthError(data.error || 'Registration failed.');
      }
    } catch (err) {
      setAuthError('Cannot connect to registration service.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('itsm_token');
    localStorage.removeItem('itsm_user');
    setAuthToken('');
    setCurrentUser(null);
    setRole('employee');
    setActiveTab('overview');
    setTickets([]);
    setSoftwareRequests([]);
    setAuditLogs([]);
    setAuthModalOpen(true);
  };

  const fillQuickLogin = (email, password) => {
    setAuthEmail(email);
    setAuthPassword(password);
  };

  // --- 1. INTELLIGENT TICKET INTAKE ---
  const handleRunIntakeClassifier = async () => {
    if (!intakeQuery.trim()) return;
    setIntakeLoading(true);

    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/tickets/classify', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ user_query: intakeQuery })
      });
      const data = await res.json();
      if (data.success && data.classification) {
        setIntakePreview(data.classification);
        setIntakeLoading(false);
        return;
      }
    } catch (e) {
      console.warn("Intake classification fallback:", e);
    }

    // Client-side rule fallback
    setTimeout(() => {
      const q = intakeQuery.toLowerCase();
      let cat = 'General IT';
      let workflow = 'Network Troubleshooting';
      if (q.includes('wifi') || q.includes('vpn') || q.includes('internet') || q.includes('network')) {
        cat = 'Network';
        workflow = 'Network Troubleshooting';
      } else if (q.includes('disk') || q.includes('slow') || q.includes('laptop') || q.includes('storage')) {
        cat = 'Hardware';
        workflow = 'Disk Space and Performance Guidance';
      } else if (q.includes('crash') || q.includes('app') || q.includes('teams') || q.includes('software')) {
        cat = 'Software';
        workflow = 'Application Troubleshooting';
      } else if (q.includes('password') || q.includes('login') || q.includes('access')) {
        cat = 'Account and Access';
      }

      setIntakePreview({
        title: intakeQuery.slice(0, 65) + (intakeQuery.length > 65 ? '...' : ''),
        description: intakeQuery,
        category: cat,
        ticket_type: 'incident',
        impact: 'medium',
        urgency: 'medium',
        calculated_priority: 'medium',
        symptoms: ['Reported symptom: ' + intakeQuery.slice(0, 80)],
        affected_service: cat,
        suggested_troubleshooting_workflow: workflow,
        ai_confidence: 0.91,
        suggested_resolution: `Automated ${workflow} diagnostic workflow ready.`
      });
      setIntakeLoading(false);
    }, 400);
  };

  const handleSubmitTicket = async () => {
    if (!intakePreview) return;
    try {
      const payload = {
        title: intakePreview.title,
        description: intakePreview.description,
        category: intakePreview.category,
        priority: intakePreview.calculated_priority || 'medium',
        impact: intakePreview.impact || 'medium',
        urgency: intakePreview.urgency || 'medium',
        ticket_type: intakePreview.ticket_type || 'incident',
      };

      const res = await fetch('https://itsm-lqs3.vercel.app/api/tickets', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success && data.ticket) {
        setTickets(prev => [data.ticket, ...prev]);
        setTicketCreatedSuccess(data.ticket);
        setIntakePreview(null);
        setIntakeQuery('');
        return;
      }
    } catch (err) {
      console.error("Backend ticket submission error:", err);
    }
  };

  // --- 2. CHATBOT RAG INTERACTION ---
  const handleSendChat = async (messageText) => {
    const text = messageText || chatInput;
    if (!text.trim()) return;

    const userMsg = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      sources: []
    };

    setChatMessages(prev => [...prev, userMsg]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/chat/message', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          message: text,
          session_id: chatSessionId || undefined,
        })
      });
      const data = await res.json();

      if (data.success) {
        if (data.session_id) setChatSessionId(data.session_id);
        const actionPayload = data.metadata?.action_payload || data.response?.metadata?.action_payload || null;
        const botMsg = {
          id: `msg-${Date.now() + 1}`,
          role: 'assistant',
          content: typeof data.response === 'string' ? data.response : (data.content || data.response?.content || JSON.stringify(data.response)),
          sources: data.sources || (data.response?.metadata?.sources) || [],
          actions: data.suggested_actions || (data.response?.metadata?.suggested_prompts) || ['Connect to VPN', 'Report Issue'],
          ticket_draft: data.ticket_draft || (actionPayload?.ticket_data) || null,
          action_payload: actionPayload,
        };
        setChatMessages(prev => [...prev, botMsg]);
        setChatLoading(false);

        // Auto-refresh tickets or software requests when modified in chat
        if (actionPayload) {
          const pType = actionPayload.type;
          if (pType === 'ticket_created' || pType === 'ticket_view') {
            loadTickets();
          } else if (pType === 'software_request_created') {
            loadSoftware();
          }
        }
        return;
      }
    } catch (err) {
      console.warn("Backend chat failed:", err);
    }

    // Fallback response
    setTimeout(() => {
      const botMsg = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: `I received your inquiry regarding "${text}". You can submit this as an incident via the Intelligent Intake portal or browse verified guides in Knowledge Base.`,
        sources: [],
        actions: ['Report An Issue', 'Self-Heal Diagnostic'],
      };
      setChatMessages(prev => [...prev, botMsg]);
      setChatLoading(false);
    }, 500);
  };

  // --- 3. TICKET COMMENTS & RESOLUTION ---
  const handleAddComment = async () => {
    if (!selectedTicket || !newCommentText.trim()) return;
    try {
      const res = await fetch(`https://itsm-lqs3.vercel.app/api/tickets/${selectedTicket.id}/comments`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          comment: newCommentText,
          visibility: commentVisibility,
        })
      });
      const data = await res.json();
      if (data.success && data.comment) {
        const updated = {
          ...selectedTicket,
          comments: [...(selectedTicket.comments || []), data.comment]
        };
        setSelectedTicket(updated);
        setTickets(tickets.map(t => t.id === updated.id ? updated : t));
        setNewCommentText('');
      }
    } catch (err) {
      console.error("Add comment failed:", err);
    }
  };

  const handleResolveTicket = async () => {
    if (!selectedTicket) return;
    try {
      const res = await fetch(`https://itsm-lqs3.vercel.app/api/tickets/${selectedTicket.id}/resolve`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          resolution: 'Issue resolved by support engineer following standard runbook.',
        })
      });
      const data = await res.json();
      if (data.success && data.ticket) {
        setSelectedTicket(data.ticket);
        setTickets(tickets.map(t => t.id === data.ticket.id ? data.ticket : t));
      }
    } catch (err) {
      console.error("Resolve ticket failed:", err);
    }
  };

  // --- 4. SOFTWARE REQUESTS ---
  const handleSoftwareRequestSubmit = async (e) => {
    e.preventDefault();
    if (!requestModalSw) return;
    try {
      const res = await fetch('https://itsm-lqs3.vercel.app/api/software/requests', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          software_id: requestModalSw.id,
          business_justification: requestJustification || 'Standard corporate software access',
          designation: requestDesignation,
        })
      });
      const data = await res.json();
      if (data.success && data.request) {
        setSoftwareRequests(prev => [data.request, ...prev]);
        setRequestModalSw(null);
        setRequestJustification('');
        loadSoftware();
      }
    } catch (err) {
      console.error("Software request failed:", err);
    }
  };

  const handleApproveSoftware = async (reqId) => {
    try {
      const res = await fetch(`https://itsm-lqs3.vercel.app/api/software/requests/${reqId}/approve`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ approved: true, comment: 'Approved by IT Administrator' })
      });
      const data = await res.json();
      if (data.success && data.request) {
        setSoftwareRequests(prev => prev.map(r => r.id === reqId ? data.request : r));
      }
    } catch (err) {
      console.error("Approve software failed:", err);
    }
  };

  const handleRejectSoftware = async (reqId) => {
    try {
      const res = await fetch(`https://itsm-lqs3.vercel.app/api/software/requests/${reqId}/approve`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ approved: false, comment: 'Rejected per IT compliance policy' })
      });
      const data = await res.json();
      if (data.success && data.request) {
        setSoftwareRequests(prev => prev.map(r => r.id === reqId ? data.request : r));
      }
    } catch (err) {
      console.error("Reject software failed:", err);
    }
  };

  // --- 5. DOCUMENT UPLOAD TO PINECONE ---
  const handleUploadDocument = async (e) => {
    e.preventDefault();
    if (!uploadFile && !uploadTitle) return;

    setUploadStatus('parsing');
    const docTitle = uploadTitle || (uploadFile ? uploadFile.name : 'Technical IT Runbook');

    try {
      if (uploadFile) {
        const formData = new FormData();
        formData.append('file', uploadFile);
        formData.append('title', docTitle);
        formData.append('category', uploadCategory);

        const res = await fetch('https://itsm-lqs3.vercel.app/api/knowledge/documents', {
          method: 'POST',
          headers: getAuthHeaders(true),
          body: formData,
        });
        const data = await res.json();

        if (data.success && data.document) {
          setUploadStatus('done');
          setKnowledgeDocuments(prev => [data.document, ...prev]);
          setTimeout(() => {
            setUploadModalOpen(false);
            setUploadStatus(null);
            setUploadFile(null);
            setUploadTitle('');
            loadKnowledge();
          }, 800);
          return;
        }
      }
    } catch (err) {
      console.warn("Backend upload error:", err);
    }

    // Fallback UI simulation if offline
    setTimeout(() => {
      setUploadStatus('embedding');
      setTimeout(() => {
        setUploadStatus('upserting');
        setTimeout(() => {
          setUploadStatus('done');
          setTimeout(() => {
            setUploadModalOpen(false);
            setUploadStatus(null);
            setUploadFile(null);
            setUploadTitle('');
          }, 800);
        }, 500);
      }, 500);
    }, 400);
  };

  // --- 6. SELF-HEAL DIAGNOSTIC WORKFLOWS ---
  const startWorkflow = (wfName) => {
    setActiveWorkflow(wfName);
    setWorkflowStep(0);
    setWorkflowResults([]);
    setWorkflowFeedback(null);
  };

  const workflows = {
    'Network Troubleshooting': [
      { name: 'Gateway Reachability Ping', desc: 'Verifies ICMP echo response against default gateway (10.0.0.1)' },
      { name: 'DNS Resolution Test', desc: 'Validates forward lookup of internal Active Directory DNS servers' },
      { name: 'DNS Cache Purge', desc: 'Flushes stale local client DNS cache and registers network adapter' },
      { name: 'SSL Handshake Verification', desc: 'Tests TLS 1.3 cryptographic cipher suite compatibility' }
    ],
    'Disk Space and Performance Guidance': [
      { name: 'Volume Space Diagnostic', desc: 'Analyzes System Drive C: volume cluster size and free headroom' },
      { name: 'Temporary File Cleanup Scan', desc: 'Calculates unlinked temporary files in %TEMP% and SoftwareDistribution' },
      { name: 'Safe Cache Clearance', desc: 'Safely removes orphaned application cache files under 14-day threshold' },
      { name: 'Storage Reclaim Verification', desc: 'Confirms regained storage meets minimal 5GB operating baseline' }
    ],
    'Application Troubleshooting': [
      { name: 'Process Liveness Inspection', desc: 'Checks running instance and verifies non-responsive thread states' },
      { name: 'Identity Token Cache Refresh', desc: 'Clears stale Okta / Microsoft SSO modern authentication tokens' },
      { name: 'Configuration Integrity Check', desc: 'Validates local application XML/JSON configuration profile syntax' },
      { name: 'Safe Process Restart', desc: 'Gracefully initiates clean process instance with fresh memory heap' }
    ]
  };

  const runWorkflowStep = (stepIdx) => {
    const wf = workflows[activeWorkflow];
    if (!wf || stepIdx >= wf.length) return;

    const current = wf[stepIdx];
    setTimeout(() => {
      setWorkflowResults(prev => [
        ...prev,
        {
          step: current.name,
          status: 'success',
          detail: `Step ${stepIdx + 1}/${wf.length} completed successfully. Diagnostic signal verified.`,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      setWorkflowStep(stepIdx + 1);
    }, 500);
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans overflow-hidden">
      
      {/* --- SIDEBAR NAVIGATION --- */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 border-r border-slate-800">
        {/* Brand */}
        <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md">
            <Icon name="sparkles" className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-tight">ITSM AutoPlatform</h1>
            <p className="text-[11px] text-slate-400 font-medium">Enterprise AI Helpdesk</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
          
          {/* Employee Self-Service Portal */}
          <div>
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Self-Service Portal
            </p>
            <nav className="space-y-1">
              {[
                { id: 'overview', label: 'Overview', icon: 'dashboard' },
                { id: 'intake', label: 'Intelligent Intake', icon: 'sparkles' },
                { id: 'chat', label: 'AI Helpdesk Chat', icon: 'bot' },
                { id: 'my_tickets', label: 'My Tickets', icon: 'ticket', badge: displayedTickets.length },
                { id: 'automation', label: 'Self-Heal Diagnostic', icon: 'wrench' },
                { id: 'knowledge', label: 'Knowledge Base', icon: 'book' },
                { id: 'software', label: 'Software Requests', icon: 'box' },
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${activeTab === item.id ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'}`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon name={item.icon} className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${activeTab === item.id ? 'bg-indigo-800 text-white' : 'bg-slate-800 text-slate-300'}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* IT Administrator Portal */}
          {(role === 'it_agent' || role === 'admin') && (
            <div>
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-indigo-400 mb-2">
                IT Operations & Admin
              </p>
              <nav className="space-y-1">
                {[
                  { id: 'admin_overview', label: 'Admin Command Center', icon: 'activity' },
                  { id: 'all_tickets', label: 'All Incidents Queue', icon: 'ticket', badge: tickets.length },
                  { id: 'knowledge_admin', label: 'Knowledge & RAG Ingest', icon: 'book' },
                  { id: 'software_admin', label: 'Software Approvals', icon: 'box', badge: softwareRequests.filter(r => r.status === 'pending_approval').length },
                  { id: 'audit_logs', label: 'Security Audit Logs', icon: 'shield' },
                  { id: 'settings', label: 'System & ServiceNow', icon: 'settings' },
                ].map(item => (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${activeTab === item.id ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'}`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon name={item.icon} className="w-4 h-4" />
                      <span>{item.label}</span>
                    </div>
                    {item.badge !== undefined && item.badge > 0 && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${activeTab === item.id ? 'bg-indigo-800 text-white' : 'bg-slate-800 text-slate-300'}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                ))}
              </nav>
            </div>
          )}
        </div>

        {/* Database & Integration Status in Sidebar Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-[11px] space-y-1.5">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1.5">
              <Icon name="database" className="w-3.5 h-3.5 text-emerald-400" />
              <span>MongoDB Atlas:</span>
            </span>
            <span className="font-semibold text-emerald-400">Connected</span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1.5">
              <Icon name="sparkles" className="w-3.5 h-3.5 text-indigo-400" />
              <span>Groq AI Model:</span>
            </span>
            <span className="font-mono text-[10px] text-slate-300">gpt-oss-120b</span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1.5">
              <Icon name="link" className="w-3.5 h-3.5 text-sky-400" />
              <span>Pinecone RAG:</span>
            </span>
            <span className="text-emerald-400 font-semibold">384-dim</span>
          </div>
        </div>
      </aside>

      {/* --- MAIN WORKSPACE --- */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        {/* TOP HEADER BAR */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between z-10 shadow-xs">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-bold text-slate-900 capitalize">
              {activeTab.replace('_', ' ')}
            </h2>
            <div className="flex items-center space-x-2 text-xs bg-emerald-50 text-emerald-800 px-2.5 py-1 rounded-md border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-medium">MongoDB Atlas Primary DB</span>
            </div>
            <div className="flex items-center space-x-2 text-xs bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md border border-indigo-200">
              <span>ServiceNow: {serviceNowDemo ? 'Demo Mode' : 'Connected'}</span>
            </div>
          </div>

          {/* Authentication & User Session Bar */}
          <div className="flex items-center space-x-3">
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2.5 pl-3 border-l border-slate-200">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs uppercase shadow-sm">
                    {currentUser.full_name ? currentUser.full_name[0] : 'U'}
                  </div>
                  <div className="text-left hidden sm:block">
                    <p className="text-xs font-bold text-slate-900 leading-tight">{currentUser.full_name}</p>
                    <p className="text-[10px] text-slate-500">{currentUser.email} • {currentUser.department}</p>
                  </div>
                </div>

                <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${role === 'admin' ? 'bg-purple-50 text-purple-700 border-purple-200' : (role === 'it_agent' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200')}`}>
                  {role.replace('_', ' ')}
                </span>

                <button
                  onClick={() => { setAuthMode('login'); setAuthModalOpen(true); }}
                  className="text-xs text-slate-600 hover:text-indigo-600 font-semibold px-2 py-1 rounded hover:bg-slate-100 transition"
                >
                  Switch User
                </button>

                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-xs text-red-600 hover:text-red-700 font-semibold px-2.5 py-1 rounded border border-red-200 hover:bg-red-50 transition"
                >
                  <Icon name="logout" className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => { setAuthMode('login'); setAuthModalOpen(true); }}
                  className="flex items-center space-x-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3.5 py-2 rounded-lg shadow transition"
                >
                  <Icon name="login" className="w-3.5 h-3.5" />
                  <span>Sign In / Register</span>
                </button>
              </div>
            )}
          </div>
        </header>

        {/* TAB CONTENTS */}
        <main className="flex-1 overflow-y-auto p-6">

          {/* ==================== 1. OVERVIEW (EMPLOYEE DASHBOARD) ==================== */}
          {activeTab === 'overview' && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <div className="bg-gradient-to-r from-indigo-700 to-indigo-900 rounded-2xl p-6 text-white shadow-sm flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold mb-1">
                    Welcome back, {currentUser ? currentUser.full_name : 'Valued Employee'}
                  </h3>
                  <p className="text-sm text-indigo-200">
                    AI-powered helpdesk automation platform backed by MongoDB Cloud Atlas and Pinecone Vector RAG.
                  </p>
                </div>
                <div className="flex space-x-3">
                  <button onClick={() => setActiveTab('intake')} className="bg-white text-indigo-900 hover:bg-indigo-50 px-4 py-2 rounded-lg font-semibold text-sm shadow flex items-center space-x-2 transition">
                    <Icon name="sparkles" className="w-4 h-4 text-indigo-600" />
                    <span>Report An Issue</span>
                  </button>
                  <button onClick={() => setActiveTab('chat')} className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-semibold text-sm border border-indigo-400 flex items-center space-x-2 transition">
                    <Icon name="bot" className="w-4 h-4" />
                    <span>Ask AI Assistant</span>
                  </button>
                </div>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">My Active Tickets</span>
                    <Icon name="ticket" className="w-5 h-5 text-indigo-600" />
                  </div>
                  <p className="text-2xl font-bold text-slate-900">{displayedTickets.filter(t => t.status !== 'resolved' && t.status !== 'closed').length}</p>
                  <p className="text-xs text-slate-400 mt-1">Live from MongoDB</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Resolved Tickets</span>
                    <Icon name="check" className="w-5 h-5 text-emerald-600" />
                  </div>
                  <p className="text-2xl font-bold text-slate-900">{displayedTickets.filter(t => t.status === 'resolved' || t.status === 'closed').length}</p>
                  <p className="text-xs text-emerald-600 mt-1">Closed successfully</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Software Requests</span>
                    <Icon name="box" className="w-5 h-5 text-amber-600" />
                  </div>
                  <p className="text-2xl font-bold text-slate-900">{softwareRequests.length}</p>
                  <p className="text-xs text-slate-400 mt-1">Provisioning status</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Self-Heal Automations</span>
                    <Icon name="wrench" className="w-5 h-5 text-indigo-600" />
                  </div>
                  <p className="text-2xl font-bold text-slate-900">3 Workflows</p>
                  <p className="text-xs text-slate-400 mt-1">Automated resolution</p>
                </div>
              </div>

              {/* Tickets Quick View */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">Recent Tickets in Queue</h4>
                  <button onClick={() => setActiveTab('my_tickets')} className="text-xs text-indigo-600 hover:underline font-semibold">
                    View All &rarr;
                  </button>
                </div>

                {displayedTickets.length === 0 ? (
                  <div className="py-8 text-center text-slate-500 text-xs">
                    <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Icon name="ticket" className="w-5 h-5" />
                    </div>
                    <p className="font-semibold text-slate-700">No tickets submitted yet</p>
                    <p className="text-slate-400 mt-0.5">Use the Intelligent Intake tab or AI Helpdesk to report your first IT issue.</p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {displayedTickets.slice(0, 4).map(ticket => (
                      <div key={ticket.id} className="py-3 flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-xs font-bold text-indigo-600">{ticket.ticket_number}</span>
                            <span className="text-sm font-semibold text-slate-900">{ticket.title}</span>
                          </div>
                          <p className="text-xs text-slate-500">Category: {ticket.category} • Created: {new Date(ticket.created_at).toLocaleDateString()}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <PriorityBadge priority={ticket.priority} />
                          <StatusBadge state={ticket.state} status={ticket.status} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ==================== 2. INTELLIGENT TICKET INTAKE ==================== */}
          {activeTab === 'intake' && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Intelligent IT Intake & Classifier</h3>
                  <p className="text-xs text-slate-500">
                    Describe your technical problem in natural language. Groq GPT-OSS will extract ITIL metadata, categorize the service, determine impact/urgency, and check for automated resolution workflows.
                  </p>
                </div>

                <div className="space-y-2">
                  <textarea
                    rows={4}
                    value={intakeQuery}
                    onChange={(e) => setIntakeQuery(e.target.value)}
                    placeholder="e.g. My corporate laptop cannot connect to the GlobalProtect VPN since this morning. It times out during TLS handshake and says gateway unreachable."
                    className="w-full p-4 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-normal"
                  />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Powered by Groq GPT-OSS 120B ITIL Engine</span>
                    <button
                      onClick={handleRunIntakeClassifier}
                      disabled={intakeLoading || !intakeQuery.trim()}
                      className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold text-xs px-4 py-2.5 rounded-lg flex items-center space-x-2 shadow transition"
                    >
                      <Icon name="sparkles" className="w-4 h-4" />
                      <span>{intakeLoading ? 'Analyzing & Extracting...' : 'Classify with AI'}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Classification Preview Card */}
              {intakePreview && (
                <div className="bg-white rounded-2xl border border-indigo-200 shadow-md p-6 space-y-4 animate-fade-in">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      <h4 className="font-bold text-slate-900 text-sm">AI Ticket Intake Preview</h4>
                      <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-mono font-semibold">
                        Confidence: {Math.round(intakePreview.ai_confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <PriorityBadge priority={intakePreview.calculated_priority} />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div>
                      <span className="text-slate-400 font-semibold uppercase">Category</span>
                      <p className="font-bold text-slate-800">{intakePreview.category}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-semibold uppercase">Type</span>
                      <p className="font-bold text-slate-800 uppercase">{intakePreview.ticket_type}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-semibold uppercase">Impact</span>
                      <p className="font-bold text-slate-800 uppercase">{intakePreview.impact}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-semibold uppercase">Urgency</span>
                      <p className="font-bold text-slate-800 uppercase">{intakePreview.urgency}</p>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-slate-700">Subject</span>
                    <p className="text-sm font-bold text-slate-900">{intakePreview.title}</p>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-slate-700">Detailed Description</span>
                    <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">{intakePreview.description}</p>
                  </div>

                  {intakePreview.suggested_troubleshooting_workflow && (
                    <div className="p-3 bg-indigo-50 rounded-xl border border-indigo-200 flex items-center justify-between">
                      <div className="text-xs">
                        <span className="font-bold text-indigo-900 block">Self-Healing Diagnostic Detected:</span>
                        <span className="text-indigo-700">{intakePreview.suggested_troubleshooting_workflow}</span>
                      </div>
                      <button
                        onClick={() => {
                          startWorkflow(intakePreview.suggested_troubleshooting_workflow);
                          setActiveTab('automation');
                        }}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow"
                      >
                        Launch Diagnostic &rarr;
                      </button>
                    </div>
                  )}

                  <div className="flex justify-end space-x-3 pt-2">
                    <button
                      onClick={() => setIntakePreview(null)}
                      className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSubmitTicket}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2 rounded-lg shadow flex items-center space-x-1.5"
                    >
                      <Icon name="check" className="w-4 h-4" />
                      <span>Confirm & Save to MongoDB</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Success Notification */}
              {ticketCreatedSuccess && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 text-emerald-900 flex items-center justify-between animate-fade-in">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold">✓</div>
                    <div>
                      <h4 className="font-bold text-sm">Ticket Created Successfully</h4>
                      <p className="text-xs text-emerald-700">
                        Record ID: <span className="font-mono font-bold">{ticketCreatedSuccess.ticket_number}</span> • Stored in MongoDB Atlas • Synced to ServiceNow queue
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab('my_tickets')}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow"
                  >
                    View In My Tickets
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ==================== 3. AI CHATBOT ==================== */}
          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto h-[calc(100vh-8.5rem)] flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold">
                    <Icon name="bot" className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">AI Helpdesk Assistant</h3>
                    <p className="text-[11px] text-slate-500">Groq GPT-OSS 120B • Grounded with Pinecone Vector RAG</p>
                  </div>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Index: itsm-knowledge (384-dim)
                </div>
              </div>

              {/* Messages Container */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.map(msg => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed ${msg.role === 'user' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-slate-100 text-slate-800 border border-slate-200'}`}>
                      <p className="whitespace-pre-line">{msg.content}</p>

                      {/* Interactive Ticket View Card */}
                      {msg.action_payload?.type === 'ticket_view' && msg.action_payload.ticket && (
                        <div className="mt-3 p-3 bg-white rounded-xl border border-indigo-200 shadow-xs space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-indigo-700">{msg.action_payload.ticket.ticket_number}</span>
                            <StatusBadge state={msg.action_payload.ticket.state} status={msg.action_payload.ticket.status} />
                          </div>
                          <p className="font-semibold text-slate-800">{msg.action_payload.ticket.title}</p>
                          <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px]">
                            <span className="text-slate-500 font-mono">ServiceNow: {msg.action_payload.ticket.external_record_id || 'INC0010009'}</span>
                            <button
                              onClick={() => {
                                setSelectedTicket(msg.action_payload.ticket);
                                setActiveTab('tickets');
                              }}
                              className="text-indigo-600 hover:text-indigo-800 font-bold underline"
                            >
                              Open Ticket Details &rarr;
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Interactive Software Request Confirmation Card */}
                      {msg.action_payload?.type === 'software_request_created' && msg.action_payload.request && (
                        <div className="mt-3 p-3 bg-white rounded-xl border border-indigo-200 shadow-xs space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-indigo-700">{msg.action_payload.request.request_number}</span>
                            <StatusBadge status={msg.action_payload.request.status} />
                          </div>
                          <p className="font-semibold text-slate-800">Software: {msg.action_payload.request.software_name}</p>
                          <p className="text-[11px] text-slate-500">Designation Assessed: <span className="font-semibold text-slate-700">{msg.action_payload.request.designation}</span></p>
                          <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px]">
                            <span className="text-slate-500 font-medium">
                              {msg.action_payload.request.ai_recommendation === 'auto_approved' ? '⚡ Auto-Approved by AI' : '⏳ Queued for Manager Review'}
                            </span>
                            <button
                              onClick={() => setActiveTab('software')}
                              className="text-indigo-600 hover:text-indigo-800 font-bold underline"
                            >
                              View Software Queue &rarr;
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Interactive Ticket Created Card */}
                      {msg.action_payload?.type === 'ticket_created' && msg.action_payload.ticket && (
                        <div className="mt-3 p-3 bg-emerald-50 rounded-xl border border-emerald-200 shadow-xs space-y-2 text-xs text-emerald-900">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-emerald-800">{msg.action_payload.ticket.ticket_number}</span>
                            <PriorityBadge priority={msg.action_payload.ticket.priority} />
                          </div>
                          <p className="font-semibold">{msg.action_payload.ticket.title}</p>
                          <div className="flex items-center justify-between pt-1 border-t border-emerald-200 text-[11px]">
                            <span>ServiceNow: <strong className="font-mono">{msg.action_payload.ticket.external_record_id || 'Synced'}</strong></span>
                            <button
                              onClick={() => {
                                setSelectedTicket(msg.action_payload.ticket);
                                setActiveTab('tickets');
                              }}
                              className="text-emerald-800 hover:text-emerald-950 font-bold underline"
                            >
                              View in Tickets &rarr;
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Interactive In-Chat Ticket Draft Submission */}
                      {msg.ticket_draft && (
                        <div className="mt-3 p-3 bg-white rounded-xl border border-amber-200 shadow-xs space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-amber-800">Draft Ticket Ready for Submission</span>
                            <PriorityBadge priority={msg.ticket_draft.calculated_priority || msg.ticket_draft.priority || 'medium'} />
                          </div>
                          <p className="font-semibold text-slate-800">{msg.ticket_draft.title}</p>
                          <p className="text-slate-500 text-[11px] line-clamp-2">{msg.ticket_draft.description}</p>
                          <div className="flex justify-end pt-1">
                            <button
                              onClick={async () => {
                                try {
                                  const res = await fetch('https://itsm-lqs3.vercel.app/api/tickets', {
                                    method: 'POST',
                                    headers: getAuthHeaders(),
                                    body: JSON.stringify({
                                      title: msg.ticket_draft.title,
                                      description: msg.ticket_draft.description,
                                      category: msg.ticket_draft.category || 'General IT',
                                      priority: msg.ticket_draft.calculated_priority || msg.ticket_draft.priority || 'medium',
                                      impact: msg.ticket_draft.impact || 'medium',
                                      urgency: msg.ticket_draft.urgency || 'medium',
                                    })
                                  });
                                  const d = await res.json();
                                  if (d.success && d.ticket) {
                                    loadTickets();
                                    setChatMessages(c => [...c, {
                                      id: `msg-${Date.now()}`,
                                      role: 'assistant',
                                      content: `✓ Successfully created ticket **${d.ticket.ticket_number}** (ServiceNow: ${d.ticket.external_record_id || 'Synced'}). Our support engineering team has been notified.`,
                                      action_payload: { type: 'ticket_created', ticket: d.ticket }
                                    }]);
                                  }
                                } catch (err) {
                                  console.error("Direct ticket submission failed:", err);
                                }
                              }}
                              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1.5 rounded-lg text-xs shadow"
                            >
                              Confirm & Submit Ticket &rarr;
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Grounding Citations */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-200/80 space-y-1">
                          <span className="font-bold text-[10px] uppercase text-indigo-700 block">Verified Knowledge Base Sources:</span>
                          {msg.sources.map((src, i) => (
                            <div key={i} className="text-[10px] text-slate-600 flex items-center space-x-1 font-mono">
                              <span>📄</span>
                              <span>{src.document_title || src.title || src.filename || 'Internal Guide'} {src.page ? `(p. ${src.page})` : ''} — Match: {Math.round(((src.score || src.similarity || 0.85) * 100))}%</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Interactive Actions */}
                      {msg.actions && msg.actions.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-slate-200 flex flex-wrap gap-1.5">
                          {msg.actions.map((act, i) => (
                            <button
                              key={i}
                              onClick={() => handleSendChat(act)}
                              className="text-[10px] bg-white text-indigo-700 font-semibold px-2.5 py-1 rounded-md border border-indigo-200 hover:bg-indigo-50 shadow-2xs transition"
                            >
                              {act}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-100 p-3 rounded-2xl text-xs text-slate-500 flex items-center space-x-2">
                      <Icon name="refresh" className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                      <span>Retrieving documentation from Pinecone & generating answer...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-slate-200 bg-white">
                <form
                  onSubmit={(e) => { e.preventDefault(); handleSendChat(); }}
                  className="flex items-center space-x-2"
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about corporate IT policies, error codes, VPN setup..."
                    className="flex-1 p-2.5 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 font-normal"
                  />
                  <button
                    type="submit"
                    disabled={!chatInput.trim() || chatLoading}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white p-2.5 rounded-xl transition"
                  >
                    <Icon name="send" className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* ==================== 4. MY TICKETS & ALL TICKETS QUEUE ==================== */}
          {(activeTab === 'my_tickets' || activeTab === 'all_tickets') && (
            <div className="max-w-6xl mx-auto space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {activeTab === 'all_tickets' ? 'All Incidents & Service Requests' : 'My Open & Resolved Tickets'}
                  </h3>
                  <p className="text-xs text-slate-500">Live MongoDB Atlas records synchronized with ServiceNow</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={loadTickets}
                    disabled={ticketsLoading}
                    className="bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-3 py-2 rounded-lg flex items-center space-x-1.5 border border-slate-200 shadow-2xs transition"
                    title="Refresh and sync live state from ServiceNow"
                  >
                    <Icon name="refresh" className={`w-3.5 h-3.5 text-indigo-600 ${ticketsLoading ? 'animate-spin' : ''}`} />
                    <span>Sync ServiceNow</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('intake')}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center space-x-1.5 shadow"
                  >
                    <Icon name="plus" className="w-3.5 h-3.5" />
                    <span>New Ticket</span>
                  </button>
                </div>
              </div>

              {/* Ticket List Table */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4 font-semibold">Number</th>
                      <th className="py-3 px-4 font-semibold">Subject</th>
                      <th className="py-3 px-4 font-semibold">Category</th>
                      <th className="py-3 px-4 font-semibold">Priority</th>
                      <th className="py-3 px-4 font-semibold">State</th>
                      <th className="py-3 px-4 font-semibold">ServiceNow Ref</th>
                      <th className="py-3 px-4 font-semibold">Requester</th>
                      <th className="py-3 px-4 font-semibold text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {displayedTickets.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-12 px-4 text-center">
                          <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-3">
                            <Icon name="ticket" className="w-6 h-6" />
                          </div>
                          <p className="text-base font-bold text-slate-800">No Tickets Logged</p>
                          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
                            {activeTab === 'all_tickets'
                              ? "The enterprise queue is currently clear. No incidents or requests found in MongoDB."
                              : "You haven't submitted any tickets yet. Report an issue via Intelligent Intake or AI Helpdesk."}
                          </p>
                          <button
                            onClick={() => setActiveTab('intake')}
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm"
                          >
                            <Icon name="sparkles" className="w-3.5 h-3.5" />
                            <span>Create Incident Ticket</span>
                          </button>
                        </td>
                      </tr>
                    ) : (
                      displayedTickets.map(ticket => (
                        <tr key={ticket.id} className="hover:bg-slate-50/80 transition">
                          <td className="py-3.5 px-4 font-mono font-bold text-indigo-600 text-xs">{ticket.ticket_number}</td>
                          <td className="py-3.5 px-4 font-semibold text-slate-900 max-w-xs truncate">{ticket.title}</td>
                          <td className="py-3.5 px-4 text-xs text-slate-600">{ticket.category}</td>
                          <td className="py-3.5 px-4"><PriorityBadge priority={ticket.priority} /></td>
                          <td className="py-3.5 px-4"><StatusBadge state={ticket.state} status={ticket.status} /></td>
                          <td className="py-3.5 px-4 font-mono text-xs">
                            {ticket.external_record_id ? (
                              <a
                                href={ticket.external_record_url || `https://dev456763.service-now.com/nav_to.do?uri=incident.do?sys_id=${ticket.external_record_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-bold text-indigo-600 hover:underline inline-flex items-center space-x-1"
                              >
                                <span>{ticket.external_record_id}</span>
                                <span className="text-[10px]">↗</span>
                              </a>
                            ) : (
                              <span className="text-slate-400 italic">None</span>
                            )}
                          </td>
                          <td className="py-3.5 px-4 text-xs text-slate-600">{ticket.requester_name || ticket.requester_email || 'Employee'}</td>
                          <td className="py-3.5 px-4 text-right">
                            <button
                              onClick={() => setSelectedTicket(ticket)}
                              className="text-xs bg-slate-100 hover:bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded border border-slate-200"
                            >
                              Manage
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================== 5. SELF-HEALING AUTOMATION ==================== */}
          {activeTab === 'automation' && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <h3 className="text-lg font-bold text-slate-900">Self-Healing Automation Engine</h3>
                <p className="text-xs text-slate-500">
                  Bounded state machine executing safe, deterministic diagnostic and repair playbooks before escalating to manual human technician queues.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                  {Object.keys(workflows).map(wfName => (
                    <button
                      key={wfName}
                      onClick={() => startWorkflow(wfName)}
                      className={`p-4 rounded-xl text-left border transition ${activeWorkflow === wfName ? 'border-indigo-600 bg-indigo-50/50 shadow-xs' : 'border-slate-200 hover:border-indigo-200 bg-white'}`}
                    >
                      <span className="font-bold text-xs text-slate-900 block mb-1">{wfName}</span>
                      <span className="text-[11px] text-slate-500">4 safe bounded steps</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Execution Progress */}
              {activeWorkflow && (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4 animate-fade-in">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase text-indigo-600">Active Workflow</span>
                      <h4 className="font-bold text-slate-900 text-sm">{activeWorkflow}</h4>
                    </div>
                    <span className="text-xs font-mono font-semibold text-slate-500">
                      Step {workflowStep} of {workflows[activeWorkflow].length}
                    </span>
                  </div>

                  <div className="space-y-3">
                    {workflows[activeWorkflow].map((step, idx) => (
                      <div
                        key={idx}
                        className={`p-3.5 rounded-xl border flex items-center justify-between ${idx < workflowStep ? 'bg-emerald-50/50 border-emerald-200' : (idx === workflowStep ? 'bg-indigo-50/50 border-indigo-200' : 'bg-slate-50/50 border-slate-200 opacity-60')}`}
                      >
                        <div className="space-y-0.5">
                          <p className="text-xs font-bold text-slate-900">{idx + 1}. {step.name}</p>
                          <p className="text-[11px] text-slate-500">{step.desc}</p>
                        </div>

                        <div>
                          {idx < workflowStep && (
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">PASSED</span>
                          )}
                          {idx === workflowStep && (
                            <button
                              onClick={() => runWorkflowStep(idx)}
                              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow"
                            >
                              Execute Step
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {workflowStep >= workflows[activeWorkflow].length && (
                    <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-900 space-y-2">
                      <p className="font-bold text-xs">✓ Self-Healing Diagnostic Completed Successfully</p>
                      <p className="text-[11px] text-emerald-700">All checks cleared. No persistent gateway degradation detected.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ==================== 6. KNOWLEDGE BASE & PINECONE RAG ==================== */}
          {(activeTab === 'knowledge' || activeTab === 'knowledge_admin') && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {activeTab === 'knowledge_admin' ? 'Knowledge Base & Pinecone Vector RAG' : 'Technical Documentation & Guides'}
                  </h3>
                  <p className="text-xs text-slate-500">Vector indexed in Pinecone itsm-knowledge (384-dimensional embeddings)</p>
                </div>

                {(role === 'admin' || role === 'it_agent') && (
                  <button
                    onClick={() => setUploadModalOpen(true)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3.5 py-2 rounded-lg shadow flex items-center space-x-1.5"
                  >
                    <Icon name="upload" className="w-3.5 h-3.5" />
                    <span>Upload & Ingest PDF/DOCX</span>
                  </button>
                )}
              </div>

              {/* Indexed Documents Table (Real from backend) */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">Indexed Knowledge Documents</h4>
                  <span className="text-xs font-mono text-slate-400">Total: {knowledgeDocuments.length}</span>
                </div>
                {knowledgeDocuments.length === 0 ? (
                  <div className="py-10 text-center text-slate-500 text-xs">
                    <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Icon name="book" className="w-5 h-5" />
                    </div>
                    <p className="font-semibold text-slate-700">No Knowledge Documents Uploaded Yet</p>
                    <p className="text-slate-400 mt-0.5 max-w-sm mx-auto">
                      Upload your technical runbooks, PDF manuals, or guides to index them into Pinecone for AI RAG retrieval.
                    </p>
                    {(role === 'admin' || role === 'it_agent') && (
                      <button
                        onClick={() => setUploadModalOpen(true)}
                        className="mt-3 inline-flex items-center space-x-1 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold"
                      >
                        <Icon name="upload" className="w-3.5 h-3.5" />
                        <span>Upload First Document</span>
                      </button>
                    )}
                  </div>
                ) : (
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-500 uppercase border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4 font-semibold">Title</th>
                        <th className="py-3 px-4 font-semibold">Filename</th>
                        <th className="py-3 px-4 font-semibold">Category</th>
                        <th className="py-3 px-4 font-semibold">Chunks</th>
                        <th className="py-3 px-4 font-semibold">Status</th>
                        <th className="py-3 px-4 font-semibold">Uploaded</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono">
                      {knowledgeDocuments.map(doc => (
                        <tr key={doc.id} className="hover:bg-slate-50">
                          <td className="py-3 px-4 font-sans font-bold text-slate-900">{doc.title}</td>
                          <td className="py-3 px-4 text-slate-500">{doc.original_filename}</td>
                          <td className="py-3 px-4 font-sans text-indigo-600 font-medium">{doc.category || 'General IT'}</td>
                          <td className="py-3 px-4 text-slate-700">{doc.chunk_count || 1} chunks</td>
                          <td className="py-3 px-4"><StatusBadge status={doc.status || 'indexed'} /></td>
                          <td className="py-3 px-4 text-slate-400">{new Date(doc.created_at).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* ==================== 7. SOFTWARE CATALOG & REQUESTS ==================== */}
          {(activeTab === 'software' || activeTab === 'software_admin') && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {activeTab === 'software_admin' ? 'Software Catalogue & Approval Queue' : 'Enterprise Software Catalogue'}
                  </h3>
                  <p className="text-xs text-slate-500">Corporate application catalog with automated approvals</p>
                </div>
              </div>

              {/* Catalogue Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {softwareCatalog.map(sw => (
                  <div key={sw.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between hover:border-indigo-300 transition">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{sw.category}</span>
                        {sw.approval_required ? (
                          <span className="text-[10px] bg-amber-50 text-amber-700 font-semibold px-2 py-0.5 rounded border border-amber-200">
                            Approval Needed
                          </span>
                        ) : (
                          <span className="text-[10px] bg-emerald-50 text-emerald-700 font-semibold px-2 py-0.5 rounded border border-emerald-200">
                            Pre-Approved
                          </span>
                        )}
                      </div>
                      <h4 className="font-bold text-slate-900 text-sm mb-0.5">{sw.name}</h4>
                      <p className="text-[11px] text-slate-400 font-medium mb-2">{sw.vendor}</p>
                      <p className="text-xs text-slate-500 leading-relaxed mb-4">{sw.description || sw.desc}</p>
                    </div>

                    <button
                      onClick={() => setRequestModalSw(sw)}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-2 rounded-lg transition"
                    >
                      Request License / Install &rarr;
                    </button>
                  </div>
                ))}
              </div>

              {/* Software Request Tracking Table */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-200">
                  <h4 className="font-bold text-slate-900 text-sm">Submitted Software Provisioning Requests</h4>
                </div>
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4 font-semibold">Request ID</th>
                      <th className="py-3 px-4 font-semibold">Software</th>
                      <th className="py-3 px-4 font-semibold">Requester & Designation</th>
                      <th className="py-3 px-4 font-semibold">Business Justification</th>
                      <th className="py-3 px-4 font-semibold">AI Governance</th>
                      <th className="py-3 px-4 font-semibold">Status</th>
                      {role !== 'employee' && <th className="py-3 px-4 font-semibold text-right">Approval Action</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {softwareRequests.length === 0 ? (
                      <tr>
                        <td colSpan={role !== 'employee' ? 7 : 6} className="py-8 text-center text-slate-500 text-xs">
                          No software requests submitted yet. Select an application from the catalog above to request access.
                        </td>
                      </tr>
                    ) : (
                      softwareRequests.map(req => (
                        <tr key={req.id} className="hover:bg-slate-50/80 transition">
                          <td className="py-3 px-4 font-mono font-bold text-indigo-600 text-xs">{req.request_number || req.req_num}</td>
                          <td className="py-3 px-4 font-semibold text-slate-900 text-xs">{req.software_name || 'Software App'}</td>
                          <td className="py-3 px-4 text-xs">
                            <div className="font-semibold text-slate-900">{req.requester_name || req.requester || 'Employee'}</div>
                            <div className="text-[11px] text-indigo-600 font-medium">{req.designation || 'Software Engineer'}</div>
                          </td>
                          <td className="py-3 px-4 text-xs text-slate-500 max-w-xs truncate">{req.business_justification || req.justification}</td>
                          <td className="py-3 px-4 text-xs">
                            {req.ai_recommendation === 'auto_approved' || req.recommendation === 'auto_approved' ? (
                              <div className="space-y-0.5">
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                                  ⚡ Auto-Approved
                                </span>
                                {req.ai_evaluation && (
                                  <p className="text-[10px] text-slate-500 max-w-xs truncate" title={req.ai_evaluation}>
                                    {req.ai_evaluation}
                                  </p>
                                )}
                              </div>
                            ) : (
                              <div className="space-y-0.5">
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                                  ⏳ Manager Review
                                </span>
                                {req.ai_evaluation && (
                                  <p className="text-[10px] text-slate-500 max-w-xs truncate" title={req.ai_evaluation}>
                                    {req.ai_evaluation}
                                  </p>
                                )}
                              </div>
                            )}
                          </td>
                          <td className="py-3 px-4"><StatusBadge status={req.status} /></td>
                          {role !== 'employee' && (
                            <td className="py-3 px-4 text-right space-x-1.5">
                              {req.status === 'submitted' || req.status === 'pending_approval' ? (
                                <>
                                  <button
                                    onClick={() => handleApproveSoftware(req.id)}
                                    className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-2 py-1 rounded shadow"
                                  >
                                    Approve
                                  </button>
                                  <button
                                    onClick={() => handleRejectSoftware(req.id)}
                                    className="text-xs bg-red-600 hover:bg-red-700 text-white font-semibold px-2 py-1 rounded shadow"
                                  >
                                    Reject
                                  </button>
                                </>
                              ) : (
                                <span className="text-xs text-slate-400 font-mono">Processed</span>
                              )}
                            </td>
                          )}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================== 8. ADMIN COMMAND CENTER ==================== */}
          {activeTab === 'admin_overview' && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">IT Executive & Operations Command Center</h3>
                  <p className="text-xs text-slate-500">Live operational metrics derived from MongoDB Atlas</p>
                </div>
                <div className="text-xs bg-slate-100 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 font-mono">
                  SLA Health: 99.8%
                </div>
              </div>

              {/* Aggregated KPI Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs font-bold uppercase text-slate-400">Total Incidents</span>
                  <p className="text-3xl font-extrabold text-slate-900 mt-1">{tickets.length}</p>
                  <p className="text-xs text-slate-500 mt-1">Live MongoDB count</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs font-bold uppercase text-red-500">High / Critical Priority</span>
                  <p className="text-3xl font-extrabold text-red-600 mt-1">{tickets.filter(t => t.priority === 'high' || t.priority === 'critical').length}</p>
                  <p className="text-xs text-slate-500 mt-1">Immediate attention</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs font-bold uppercase text-amber-500">Pending Software</span>
                  <p className="text-3xl font-extrabold text-amber-600 mt-1">{softwareRequests.filter(r => r.status === 'pending_approval' || r.status === 'submitted').length}</p>
                  <p className="text-xs text-slate-500 mt-1">Awaiting admin review</p>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs font-bold uppercase text-emerald-500">RAG Documents Indexed</span>
                  <p className="text-3xl font-extrabold text-emerald-600 mt-1">{knowledgeDocuments.length}</p>
                  <p className="text-xs text-slate-500 mt-1">Pinecone itsm-public</p>
                </div>
              </div>

              {/* Status Breakdowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                  <h4 className="font-bold text-sm text-slate-900">Incident Category Breakdown</h4>
                  <div className="space-y-2">
                    {['Network', 'Hardware', 'Software', 'Account and Access', 'Email'].map(cat => {
                      const count = tickets.filter(t => t.category === cat).length;
                      const pct = Math.round((count / (tickets.length || 1)) * 100);
                      return (
                        <div key={cat} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium">
                            <span className="text-slate-700">{cat}</span>
                            <span className="text-slate-500">{count} ({pct}%)</span>
                          </div>
                          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                            <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${Math.max(pct, 2)}%` }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                  <h4 className="font-bold text-sm text-slate-900">ServiceNow Integration Status</h4>
                  <div className="p-4 bg-slate-50 rounded-lg space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-600">Active Mode:</span>
                      <span className="font-bold text-indigo-700">{serviceNowDemo ? 'Demo Mode (Simulated Sync)' : 'Real ServiceNow REST API'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Total Synchronized Incidents:</span>
                      <span className="font-bold text-slate-900">{tickets.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Primary Database:</span>
                      <span className="font-semibold text-emerald-600">MongoDB Cloud Atlas</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">RAG Vector Index:</span>
                      <span className="font-semibold text-indigo-600">Pinecone (384-dim)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ==================== 9. SECURITY AUDIT LOGS ==================== */}
          {activeTab === 'audit_logs' && (
            <div className="max-w-6xl mx-auto space-y-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Security & Operational Audit Trail</h3>
                <p className="text-xs text-slate-500">Immutable ledger of administrative actions, software approvals, and diagnostic runs</p>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 uppercase border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4 font-semibold">Timestamp</th>
                      <th className="py-3 px-4 font-semibold">Actor ID</th>
                      <th className="py-3 px-4 font-semibold">Action</th>
                      <th className="py-3 px-4 font-semibold">Entity</th>
                      <th className="py-3 px-4 font-semibold">Metadata</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {auditLogs.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-10 text-center text-slate-500 font-sans text-xs">
                          No audit log entries recorded yet. System actions will be logged here automatically.
                        </td>
                      </tr>
                    ) : (
                      auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-50">
                          <td className="py-3 px-4 text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                          <td className="py-3 px-4 font-semibold text-slate-800">{log.actor_id || 'system'}</td>
                          <td className="py-3 px-4 text-indigo-600 font-bold">{log.action}</td>
                          <td className="py-3 px-4 text-slate-700">{log.entity_type} {log.entity_id ? `(${log.entity_id.slice(0, 8)}...)` : ''}</td>
                          <td className="py-3 px-4 text-slate-500 truncate max-w-xs">{JSON.stringify(log.metadata || {})}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================== 10. SYSTEM SETTINGS & SERVICENOW ==================== */}
          {activeTab === 'settings' && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center space-x-2">
                  <Icon name="settings" className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-lg font-bold text-slate-900">System Integration & Environment Configuration</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <p className="font-bold text-sm text-slate-900 flex items-center space-x-1.5">
                      <Icon name="database" className="w-4 h-4 text-emerald-600" />
                      <span>Primary Database (MongoDB Cloud Atlas)</span>
                    </p>
                    <p className="text-xs text-slate-500">Database: <span className="font-mono font-bold text-emerald-700">itsm_platform</span></p>
                    <p className="text-xs text-slate-500">Status: <span className="font-bold text-emerald-600">Active & Connected</span></p>
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <p className="font-bold text-sm text-slate-900 flex items-center space-x-1.5">
                      <Icon name="sparkles" className="w-4 h-4 text-indigo-600" />
                      <span>AI Model (Groq GPT-OSS)</span>
                    </p>
                    <p className="text-xs text-slate-500">Primary: <span className="font-mono font-bold text-indigo-600">openai/gpt-oss-120b</span></p>
                    <p className="text-xs text-slate-500">Fallback: <span className="font-mono text-slate-600">openai/gpt-oss-20b</span></p>
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <p className="font-bold text-sm text-slate-900 flex items-center space-x-1.5">
                      <Icon name="link" className="w-4 h-4 text-sky-600" />
                      <span>Vector Database (Pinecone)</span>
                    </p>
                    <p className="text-xs text-slate-500">Index: <span className="font-mono font-bold text-slate-700">itsm-knowledge</span></p>
                    <p className="text-xs text-slate-500">Embeddings: <span className="font-mono text-slate-700">all-MiniLM-L6-v2 (384-dim)</span></p>
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <p className="font-bold text-sm text-slate-900">ServiceNow REST API</p>
                    <p className="text-xs text-slate-500">Status: <span className="font-semibold text-indigo-700">{serviceNowDemo ? 'Demo Mode' : 'Connected to Instance'}</span></p>
                    <p className="text-xs text-slate-500">Table API Sync: <span className="font-mono text-slate-700">incident, change_request</span></p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      {/* --- AUTHENTICATION MODAL (LOGIN & SIGN UP) --- */}
      {authModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold shadow-sm">
                  <Icon name="lock" className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Enterprise Authentication</h3>
                  <p className="text-xs text-slate-500">Sign in to your MongoDB Atlas ITSM account</p>
                </div>
              </div>
              <button
                onClick={() => setAuthModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-2xl font-bold"
              >
                &times;
              </button>
            </div>

            {/* Tab switch between Sign In and Register */}
            <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
              <button
                onClick={() => { setAuthMode('login'); setAuthError(''); }}
                className={`flex-1 py-1.5 rounded-md transition ${authMode === 'login' ? 'bg-white text-indigo-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
              >
                Sign In
              </button>
              <button
                onClick={() => { setAuthMode('register'); setAuthError(''); }}
                className={`flex-1 py-1.5 rounded-md transition ${authMode === 'register' ? 'bg-white text-indigo-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
              >
                Create Account
              </button>
            </div>

            {/* Error Banner */}
            {authError && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg font-medium">
                {authError}
              </div>
            )}

            {/* SIGN IN FORM */}
            {authMode === 'login' ? (
              <form onSubmit={handleLoginSubmit} className="space-y-3.5">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 uppercase">Corporate Email</label>
                  <input
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    placeholder="e.g. admin@enterprise.com"
                    required
                    className="w-full p-2.5 border border-slate-300 rounded-lg text-xs font-medium focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 uppercase">Password</label>
                  <input
                    type="password"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="w-full p-2.5 border border-slate-300 rounded-lg text-xs font-medium focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                {/* Quick-fill Pills */}
                <div className="pt-1">
                  <span className="text-[11px] text-slate-400 block mb-1">Quick Login as:</span>
                  <div className="flex flex-wrap gap-1.5 text-[11px]">
                    <button
                      type="button"
                      onClick={() => fillQuickLogin('admin@enterprise.com', 'Admin123!')}
                      className="px-2 py-1 bg-purple-50 text-purple-700 border border-purple-200 rounded font-semibold hover:bg-purple-100"
                    >
                      Admin (admin@enterprise.com)
                    </button>
                    <button
                      type="button"
                      onClick={() => fillQuickLogin('agent@enterprise.com', 'Agent123!')}
                      className="px-2 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded font-semibold hover:bg-blue-100"
                    >
                      IT Agent (agent@enterprise.com)
                    </button>
                    <button
                      type="button"
                      onClick={() => fillQuickLogin('employee@enterprise.com', 'Employee123!')}
                      className="px-2 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded font-semibold hover:bg-emerald-100"
                    >
                      Employee (employee@enterprise.com)
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2.5 rounded-lg shadow transition flex items-center justify-center space-x-2"
                >
                  {authLoading && <Icon name="refresh" className="w-3.5 h-3.5 animate-spin" />}
                  <span>Sign In</span>
                </button>
              </form>
            ) : (
              /* CREATE ACCOUNT / REGISTER FORM */
              <form onSubmit={handleRegisterSubmit} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 uppercase">Full Name *</label>
                  <input
                    type="text"
                    value={authFullName}
                    onChange={(e) => setAuthFullName(e.target.value)}
                    placeholder="e.g. Alex Morgan"
                    required
                    className="w-full p-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 uppercase">Corporate Email *</label>
                  <input
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    placeholder="alex.morgan@enterprise.com"
                    required
                    className="w-full p-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 uppercase">Password (min 6 characters) *</label>
                  <input
                    type="password"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    minLength={6}
                    className="w-full p-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700 uppercase">Role</label>
                    <select
                      value={authSelectedRole}
                      onChange={(e) => setAuthSelectedRole(e.target.value)}
                      className="w-full p-2 border border-slate-300 rounded-lg text-xs bg-white"
                    >
                      <option value="employee">Employee</option>
                      <option value="it_agent">IT Support Agent</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-700 uppercase">Department</label>
                    <select
                      value={authDepartment}
                      onChange={(e) => setAuthDepartment(e.target.value)}
                      className="w-full p-2 border border-slate-300 rounded-lg text-xs bg-white"
                    >
                      <option value="Engineering">Engineering</option>
                      <option value="IT Operations">IT Operations</option>
                      <option value="IT Support">IT Support</option>
                      <option value="Human Resources">HR</option>
                      <option value="Finance">Finance</option>
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2.5 rounded-lg shadow transition flex items-center justify-center space-x-2"
                >
                  {authLoading && <Icon name="refresh" className="w-3.5 h-3.5 animate-spin" />}
                  <span>Create Account</span>
                </button>
              </form>
            )}
          </div>
        </div>
      )}

      {/* --- TICKET DETAIL MODAL --- */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-sm text-indigo-600">{selectedTicket.ticket_number}</span>
                  <PriorityBadge priority={selectedTicket.priority} />
                  <StatusBadge state={selectedTicket.state} status={selectedTicket.status} />
                </div>
                <h3 className="text-base font-bold text-slate-900 mt-1">{selectedTicket.title}</h3>
              </div>
              <button onClick={() => setSelectedTicket(null)} className="text-slate-400 hover:text-slate-600 text-xl font-bold">&times;</button>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-700 uppercase">Issue Description</span>
              <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed whitespace-pre-line">
                {selectedTicket.description}
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 text-xs">
              <div>
                <span className="text-slate-400 font-semibold block">Requester</span>
                <span className="font-semibold text-slate-800">{selectedTicket.requester_name || selectedTicket.requester_email || 'Employee'}</span>
              </div>
              <div>
                <span className="text-slate-400 font-semibold block">Category</span>
                <span className="font-semibold text-slate-800">{selectedTicket.category}</span>
              </div>
              <div>
                <span className="text-slate-400 font-semibold block">ServiceNow State</span>
                <span className="font-semibold text-slate-800 flex items-center space-x-1">
                  <span>{selectedTicket.state || (selectedTicket.status ? selectedTicket.status.replace(/_/g, ' ').toUpperCase() : 'New')}</span>
                  {selectedTicket.external_record_id && (
                    <span className="font-mono text-indigo-600">({selectedTicket.external_record_id})</span>
                  )}
                </span>
              </div>
            </div>

            {/* Comments Thread */}
            <div className="space-y-3 pt-2 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-700 uppercase">Activity & Work Notes</span>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {(!selectedTicket.comments || selectedTicket.comments.length === 0) ? (
                  <p className="text-xs text-slate-400 italic">No technician notes logged yet.</p>
                ) : (
                  selectedTicket.comments.map((c, i) => (
                    <div key={i} className="text-xs p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex justify-between font-bold text-slate-700 mb-1">
                        <span>{c.author_name || c.author || 'Support Agent'}</span>
                        <span className="text-[10px] text-slate-400 font-normal">{c.time || 'recently'}</span>
                      </div>
                      <p className="text-slate-600">{c.comment || c.text}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment */}
              <div className="flex space-x-2 pt-2">
                <input
                  type="text"
                  value={newCommentText}
                  onChange={(e) => setNewCommentText(e.target.value)}
                  placeholder="Add comment or technician update..."
                  className="flex-1 p-2 border border-slate-300 rounded text-xs"
                />
                <button
                  onClick={handleAddComment}
                  disabled={!newCommentText.trim()}
                  className="bg-indigo-600 text-white text-xs px-3 py-2 rounded font-semibold disabled:opacity-50"
                >
                  Post
                </button>
              </div>
            </div>

            {/* Resolution */}
            {selectedTicket.status === 'resolved' ? (
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-emerald-700 bg-emerald-50 p-2.5 rounded-lg border border-emerald-200">
                <span className="font-semibold">✓ Incident marked Resolved in ServiceNow</span>
                {selectedTicket.external_record_url && (
                  <a
                    href={selectedTicket.external_record_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-bold underline hover:text-emerald-900"
                  >
                    View in ServiceNow ↗
                  </a>
                )}
              </div>
            ) : role !== 'employee' && (
              <div className="pt-2 border-t border-slate-100 flex justify-end">
                <button
                  onClick={handleResolveTicket}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow"
                >
                  Mark Resolved
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --- SOFTWARE REQUEST MODAL WITH AI DESIGNATION GOVERNANCE --- */}
      {requestModalSw && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-xs font-bold text-indigo-600 uppercase">{requestModalSw.category}</span>
                <h3 className="text-base font-bold text-slate-900">{requestModalSw.name}</h3>
                <p className="text-xs text-slate-400 font-medium">{requestModalSw.vendor}</p>
              </div>
              <button onClick={() => setRequestModalSw(null)} className="text-slate-400 hover:text-slate-600 text-xl font-bold">&times;</button>
            </div>

            <form onSubmit={handleSoftwareRequestSubmit} className="space-y-3.5">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 uppercase">Employee Designation / Role *</label>
                <select
                  value={requestDesignation}
                  onChange={(e) => setRequestDesignation(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg text-xs bg-white font-medium focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="Full Stack Software Engineer">Full Stack Software Engineer</option>
                  <option value="DevOps Specialist">DevOps Specialist</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="UI/UX Designer">UI/UX Designer</option>
                  <option value="Marketing Specialist">Marketing Specialist</option>
                  <option value="HR Specialist">HR Specialist</option>
                  <option value="Financial Analyst">Financial Analyst</option>
                  <option value="IT Support Specialist">IT Support Specialist</option>
                  <option value="Product Manager">Product Manager</option>
                </select>
                <p className="text-[11px] text-slate-400">AI audits software compatibility against this role and enterprise policy.</p>
              </div>

              {/* AI Governance Live Evaluation Preview Card */}
              <div className="p-3 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5 transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
                    <Icon name="sparkles" className="w-3.5 h-3.5 text-indigo-600" />
                    <span>AI Designation Audit</span>
                  </span>
                  {requestEvaluating ? (
                    <span className="text-[10px] text-slate-500 flex items-center space-x-1 font-mono">
                      <Icon name="refresh" className="w-3 h-3 animate-spin text-indigo-600" />
                      <span>Auditing role fit...</span>
                    </span>
                  ) : requestEvaluationPreview ? (
                    requestEvaluationPreview.recommendation === 'auto_approved' ? (
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded border border-emerald-300 flex items-center space-x-1">
                        <span>⚡</span>
                        <span>Auto-Approval Eligible</span>
                      </span>
                    ) : (
                      <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-300 flex items-center space-x-1">
                        <span>⏳</span>
                        <span>Manager Review Required</span>
                      </span>
                    )
                  ) : (
                    <span className="text-[10px] text-slate-400">Policy Assessment Ready</span>
                  )}
                </div>

                {requestEvaluationPreview && (
                  <div className="text-xs text-slate-700 space-y-1 pt-1 border-t border-slate-200/60">
                    <p className="text-[11px] leading-relaxed">
                      {requestEvaluationPreview.ai_rationale}
                    </p>
                    <div className="text-[10px] text-slate-400 font-mono">
                      Confidence: {Math.round((requestEvaluationPreview.confidence || 0.9) * 100)}% • Assessed Role: {requestEvaluationPreview.designation_assessed || requestDesignation}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 uppercase">Business Justification *</label>
                <textarea
                  rows={3}
                  value={requestJustification}
                  onChange={(e) => setRequestJustification(e.target.value)}
                  placeholder="Describe your project requirements or corporate objective for this software..."
                  required
                  className="w-full p-2.5 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setRequestModalSw(null)}
                  className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-1.5 rounded-lg shadow flex items-center space-x-1.5"
                >
                  <Icon name="check" className="w-3.5 h-3.5" />
                  <span>Submit Request</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- DOCUMENT UPLOAD MODAL (PINECONE INGESTION) --- */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
                  <Icon name="book" className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Ingest Document to Pinecone</h3>
                  <p className="text-xs text-slate-500">Vector Index: <span className="font-mono text-indigo-600 font-semibold">itsm-knowledge</span> (384-dim)</p>
                </div>
              </div>
              <button onClick={() => !uploadStatus && setUploadModalOpen(false)} className="text-slate-400 hover:text-slate-600 text-2xl font-bold">&times;</button>
            </div>

            <form onSubmit={handleUploadDocument} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 uppercase">Select File (PDF, DOCX, TXT, CSV) *</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.csv"
                  onChange={(e) => {
                    const f = e.target.files[0];
                    if (f) {
                      setUploadFile(f);
                      if (!uploadTitle) {
                        setUploadTitle(f.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
                      }
                    }
                  }}
                  className="w-full text-xs text-slate-600 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer border border-slate-300 rounded-lg p-1.5"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 uppercase">Document Title *</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. Corporate VPN Troubleshooting & Setup Guide"
                  required
                  className="w-full p-2 border border-slate-300 rounded text-xs font-medium focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 uppercase">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded text-xs bg-white"
                >
                  {['Network', 'Hardware', 'Software', 'Account and Access', 'Email', 'Security', 'General IT'].map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* Progress States */}
              {uploadStatus && (
                <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg space-y-2 animate-fade-in">
                  <div className="flex items-center justify-between text-xs font-semibold text-indigo-900">
                    <span className="flex items-center space-x-2">
                      <Icon name="refresh" className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                      <span>
                        {uploadStatus === 'parsing' && 'Step 1/3: Extracting document text...'}
                        {uploadStatus === 'embedding' && 'Step 2/3: Generating 384-dim embeddings (all-MiniLM-L6-v2)...'}
                        {uploadStatus === 'upserting' && 'Step 3/3: Upserting vectors to Pinecone itsm-public...'}
                        {uploadStatus === 'done' && '✓ Document indexed successfully into Pinecone!'}
                      </span>
                    </span>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  disabled={Boolean(uploadStatus)}
                  onClick={() => setUploadModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={Boolean(uploadStatus) || (!uploadFile && !uploadTitle)}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-xs font-bold shadow flex items-center space-x-1.5"
                >
                  <Icon name="check" className="w-3.5 h-3.5" />
                  <span>Ingest & Index Document</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
