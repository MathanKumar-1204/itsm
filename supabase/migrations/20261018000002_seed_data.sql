-- ==============================================================================
-- ITSM HELPDESK PLATFORM SEED DATA
-- All sample records are clearly identifiable
-- ==============================================================================

-- 1. SEED SOFTWARE CATALOG
INSERT INTO public.software_catalog (id, name, description, vendor, category, approval_required, enabled, provisioning_mode, instructions)
VALUES 
    (
        '11111111-1111-1111-1111-111111111101',
        'Visual Studio Code',
        'Standard corporate IDE for software engineering, scripting, and web development.',
        'Microsoft',
        'Developer Tools',
        false, -- Pre-approved standard tool
        true,
        'simulated',
        'Automated silent installation via enterprise package manager winget install Microsoft.VisualStudioCode'
    ),
    (
        '11111111-1111-1111-1111-111111111102',
        'Python 3.12 Developer Suite',
        'Official Python runtime environment with pip, virtualenv, and standard developer tools.',
        'Python Software Foundation',
        'Developer Tools',
        false, -- Pre-approved
        true,
        'simulated',
        'Deploys standard Python 3.12 runtime configured with company trusted PyPI mirror.'
    ),
    (
        '11111111-1111-1111-1111-111111111103',
        'Microsoft Teams Enterprise',
        'Primary collaboration, voice, video conferencing, and internal communication client.',
        'Microsoft',
        'Collaboration',
        false,
        true,
        'integrated',
        'Provisioned via Microsoft 365 licensing portal and Intune endpoint deployment.'
    ),
    (
        '11111111-1111-1111-1111-111111111104',
        'Docker Desktop Enterprise',
        'Containerization software for local development and microservice testing. Requires paid corporate license.',
        'Docker Inc.',
        'Developer Tools',
        true, -- Requires Manager/IT approval
        true,
        'simulated',
        'Assigned via Docker Business admin console after departmental billing approval.'
    ),
    (
        '11111111-1111-1111-1111-111111111105',
        'Postman Enterprise',
        'API platform for building, designing, and testing RESTful and GraphQL APIs.',
        'Postman',
        'Developer Tools',
        true,
        true,
        'simulated',
        'Requires IT security review for API workspace sharing permissions.'
    ),
    (
        '11111111-1111-1111-1111-111111111106',
        'Internal ERP & Finance Access',
        'Privileged access to enterprise resource planning portal and accounting records.',
        'Enterprise Internal',
        'Security & Access',
        true,
        true,
        'manual',
        'Manual provisioning ticket dispatched to Identity & Access Management team.'
    )
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    vendor = EXCLUDED.vendor,
    category = EXCLUDED.category,
    approval_required = EXCLUDED.approval_required,
    enabled = EXCLUDED.enabled,
    provisioning_mode = EXCLUDED.provisioning_mode,
    instructions = EXCLUDED.instructions;
