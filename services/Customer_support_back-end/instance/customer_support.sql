
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) CHECK (role IN ('admin', 'support', 'supervisor')) DEFAULT 'support', -- Role-based access
    permissions JSONB, -- Stores agent-specific permissions (flexible, can be added/removed)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,  -- Assuming Auth service uses UUID
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',  -- open, in_progress, resolved, closed
    priority VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, urgent
    category VARCHAR(100),  -- Category of the ticket (e.g., billing, technical)
    escalation_level INTEGER DEFAULT 0,  -- 0=No Escalation, 1=Supervisor, 2=Admin, etc.
    assigned_agent_id INTEGER REFERENCES agents(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP -- null until closed
);


CREATE TABLE ticket_messages (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    sender_type VARCHAR(10) CHECK (sender_type IN ('user', 'agent')) NOT NULL,
    sender_id UUID NOT NULL,  -- ID of the sender (user/agent)
    message TEXT,
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'file', 'image')) DEFAULT 'text', -- Type of message
    file_url VARCHAR(255), -- If message_type is file or image, URL to the file
    is_read BOOLEAN DEFAULT FALSE,  -- Whether the message has been read by the recipient
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE ticket_status_history (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by UUID,  -- Either user or agent
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255)  -- Reason for status change
);


CREATE TABLE ticket_tags (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE ticket_workflows (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    workflow_type VARCHAR(50) CHECK (workflow_type IN ('auto_escalation', 'sla_violation', 'auto_assignment')),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_by UUID,  -- Either system or an agent
    description TEXT
);

CREATE TABLE ticket_feedback (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- Assuming users are in Auth service
    rating INTEGER CHECK (rating BETWEEN 1 AND 5), -- 1 to 5 stars
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Support_Tickets (
    ticket_id SERIAL PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    priority VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT REFERENCES Users(user_id),
    assigned_to INT REFERENCES Users(user_id)
);
