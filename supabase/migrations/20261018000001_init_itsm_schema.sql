-- ==============================================================================
-- ITSM HELPDESK PLATFORM SCHEMA MIGRATION
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PROFILES TABLE (linked to auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT DEFAULT 'General',
    role TEXT NOT NULL DEFAULT 'employee' CHECK (role IN ('employee', 'it_agent', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Index for profile lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

-- Automatic handle_new_user trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, role, department)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'role', 'employee'),
        COALESCE(NEW.raw_user_meta_data->>'department', 'IT')
    )
    ON CONFLICT (id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        email = EXCLUDED.email,
        updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Sequence for Ticket numbers
CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START WITH 1001;

-- 2. TICKETS TABLE
CREATE TABLE IF NOT EXISTS public.tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number TEXT UNIQUE NOT NULL DEFAULT ('INC-' || nextval('ticket_number_seq')::text),
    requester_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Hardware', 'Network', 'Software', 'Account and Access', 'Email', 'Security', 'General IT')),
    ticket_type TEXT NOT NULL DEFAULT 'incident' CHECK (ticket_type IN ('incident', 'service_request')),
    impact TEXT NOT NULL DEFAULT 'low' CHECK (impact IN ('low', 'medium', 'high', 'critical')),
    urgency TEXT NOT NULL DEFAULT 'low' CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    priority TEXT NOT NULL DEFAULT 'low' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'open', 'in_progress', 'pending', 'resolved', 'closed')),
    source TEXT NOT NULL DEFAULT 'portal',
    ai_summary TEXT,
    ai_confidence NUMERIC(5,2),
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    resolution TEXT,
    external_system TEXT DEFAULT NULL,
    external_record_id TEXT DEFAULT NULL,
    external_record_url TEXT DEFAULT NULL,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tickets_requester ON public.tickets(requester_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON public.tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON public.tickets(category);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON public.tickets(assigned_to);

-- 3. TICKET COMMENTS TABLE
CREATE TABLE IF NOT EXISTS public.ticket_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES public.tickets(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    comment TEXT NOT NULL,
    visibility TEXT NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'internal')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_id ON public.ticket_comments(ticket_id);

-- 4. CHAT SESSIONS TABLE
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON public.chat_sessions(user_id);

-- 5. CHAT MESSAGES TABLE
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);

-- 6. KNOWLEDGE DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS public.knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type TEXT,
    file_size BIGINT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'indexed', 'failed', 'archived')),
    chunk_count INT NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_status ON public.knowledge_documents(status);

-- 7. KNOWLEDGE ARTICLES TABLE
CREATE TABLE IF NOT EXISTS public.knowledge_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'General IT',
    source_ticket_id UUID REFERENCES public.tickets(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_review', 'published', 'rejected')),
    created_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    approved_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_knowledge_articles_status ON public.knowledge_articles(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_articles_category ON public.knowledge_articles(category);

-- 8. AUTOMATION RUNS TABLE
CREATE TABLE IF NOT EXISTS public.automation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES public.tickets(id) ON DELETE SET NULL,
    initiated_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    workflow_name TEXT NOT NULL,
    issue_category TEXT,
    input_summary TEXT,
    status TEXT NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'in_progress', 'completed', 'failed', 'requires_approval')),
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    result_summary TEXT,
    error_message TEXT,
    resolved BOOLEAN NOT NULL DEFAULT false,
    requires_approval BOOLEAN NOT NULL DEFAULT false,
    execution_mode TEXT NOT NULL DEFAULT 'simulated' CHECK (execution_mode IN ('real', 'simulated', 'guided')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_automation_runs_initiated_by ON public.automation_runs(initiated_by);
CREATE INDEX IF NOT EXISTS idx_automation_runs_status ON public.automation_runs(status);

-- Sequence for Software Requests
CREATE SEQUENCE IF NOT EXISTS software_request_seq START WITH 5001;

-- 9. SOFTWARE CATALOG TABLE
CREATE TABLE IF NOT EXISTS public.software_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    vendor TEXT,
    category TEXT DEFAULT 'Developer Tools',
    approval_required BOOLEAN NOT NULL DEFAULT true,
    enabled BOOLEAN NOT NULL DEFAULT true,
    provisioning_mode TEXT NOT NULL DEFAULT 'simulated' CHECK (provisioning_mode IN ('manual', 'simulated', 'integrated')),
    instructions TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 10. SOFTWARE REQUESTS TABLE
CREATE TABLE IF NOT EXISTS public.software_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_number TEXT UNIQUE NOT NULL DEFAULT ('SR-' || nextval('software_request_seq')::text),
    requester_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    software_id UUID NOT NULL REFERENCES public.software_catalog(id) ON DELETE RESTRICT,
    business_justification TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'pending_approval', 'approved', 'rejected', 'provisioning', 'completed', 'failed', 'cancelled')),
    approved_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    approval_comment TEXT,
    provisioning_status TEXT NOT NULL DEFAULT 'pending',
    execution_mode TEXT NOT NULL DEFAULT 'simulated' CHECK (execution_mode IN ('manual', 'simulated', 'integrated')),
    external_record_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_software_requests_requester ON public.software_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_software_requests_status ON public.software_requests(status);

-- 11. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON public.audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.software_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.software_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Helper to check user role
CREATE OR REPLACE FUNCTION public.current_user_role()
RETURNS TEXT AS $$
    SELECT role FROM public.profiles WHERE id = auth.uid();
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Profiles: Anyone can view their own profile; IT staff/admin can view all profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id OR public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Users can update own non-sensitive profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id AND role = (SELECT role FROM public.profiles WHERE id = auth.uid()));

CREATE POLICY "Admins can update any profile" ON public.profiles
    FOR ALL USING (public.current_user_role() = 'admin');

-- Tickets: Employees view own tickets; IT staff and Admin view all tickets
CREATE POLICY "Employees can view own tickets" ON public.tickets
    FOR SELECT USING (auth.uid() = requester_id OR public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Authenticated users can create tickets" ON public.tickets
    FOR INSERT WITH CHECK (auth.uid() = requester_id);

CREATE POLICY "Staff can update tickets" ON public.tickets
    FOR UPDATE USING (public.current_user_role() IN ('it_agent', 'admin') OR auth.uid() = requester_id);

-- Ticket comments: Public visible to ticket requester and staff; Internal only visible to staff
CREATE POLICY "View ticket comments" ON public.ticket_comments
    FOR SELECT USING (
        (visibility = 'public' AND EXISTS (SELECT 1 FROM public.tickets WHERE id = ticket_id AND (requester_id = auth.uid() OR public.current_user_role() IN ('it_agent', 'admin'))))
        OR
        (visibility = 'internal' AND public.current_user_role() IN ('it_agent', 'admin'))
    );

CREATE POLICY "Insert ticket comments" ON public.ticket_comments
    FOR INSERT WITH CHECK (
        auth.uid() = author_id AND (
            visibility = 'public' OR public.current_user_role() IN ('it_agent', 'admin')
        )
    );

-- Chat sessions & messages: User isolated
CREATE POLICY "Manage own chat sessions" ON public.chat_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Manage own chat messages" ON public.chat_messages
    FOR ALL USING (EXISTS (SELECT 1 FROM public.chat_sessions WHERE id = session_id AND user_id = auth.uid()));

-- Knowledge documents: Only admins/agents manage, public/employees can't edit
CREATE POLICY "View knowledge documents" ON public.knowledge_documents
    FOR SELECT USING (public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Manage knowledge documents" ON public.knowledge_documents
    FOR ALL USING (public.current_user_role() IN ('it_agent', 'admin'));

-- Knowledge articles: Everyone can read published; Agents/Admins can see draft/review
CREATE POLICY "Read published articles" ON public.knowledge_articles
    FOR SELECT USING (status = 'published' OR public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Manage articles" ON public.knowledge_articles
    FOR ALL USING (public.current_user_role() IN ('it_agent', 'admin'));

-- Automation runs: Users see own runs; Staff see all
CREATE POLICY "View automation runs" ON public.automation_runs
    FOR SELECT USING (auth.uid() = initiated_by OR public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Insert automation runs" ON public.automation_runs
    FOR INSERT WITH CHECK (auth.uid() = initiated_by);

-- Software Catalog: Everyone can view enabled; Admins can manage
CREATE POLICY "View enabled software" ON public.software_catalog
    FOR SELECT USING (enabled = true OR public.current_user_role() = 'admin');

CREATE POLICY "Manage software catalog" ON public.software_catalog
    FOR ALL USING (public.current_user_role() = 'admin');

-- Software requests: Requesters view own; IT staff/admin manage
CREATE POLICY "View software requests" ON public.software_requests
    FOR SELECT USING (auth.uid() = requester_id OR public.current_user_role() IN ('it_agent', 'admin'));

CREATE POLICY "Insert software request" ON public.software_requests
    FOR INSERT WITH CHECK (auth.uid() = requester_id);

CREATE POLICY "Update software request" ON public.software_requests
    FOR UPDATE USING (public.current_user_role() IN ('it_agent', 'admin'));

-- Audit logs: Read-only for admins
CREATE POLICY "Admins can view audit logs" ON public.audit_logs
    FOR SELECT USING (public.current_user_role() = 'admin');

CREATE POLICY "System can insert audit logs" ON public.audit_logs
    FOR INSERT WITH CHECK (true);
