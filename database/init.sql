-- LibProxy Database Initialization Script
-- This script creates the initial database structure

-- Create database if it doesn't exist
-- (This is handled by PostgreSQL container initialization)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Create journals table
CREATE TABLE IF NOT EXISTS journals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    base_url VARCHAR(500) NOT NULL,
    proxy_path VARCHAR(100) UNIQUE NOT NULL,
    requires_auth BOOLEAN DEFAULT TRUE NOT NULL,
    auth_method VARCHAR(50) DEFAULT 'ip',
    custom_headers JSON,
    timeout INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    access_level VARCHAR(20) DEFAULT 'public',
    publisher VARCHAR(200),
    issn VARCHAR(20),
    e_issn VARCHAR(20),
    subject_areas JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for journals
CREATE INDEX IF NOT EXISTS idx_journals_slug ON journals(slug);
CREATE INDEX IF NOT EXISTS idx_journals_proxy_path ON journals(proxy_path);
CREATE INDEX IF NOT EXISTS idx_journals_is_active ON journals(is_active);
CREATE INDEX IF NOT EXISTS idx_journals_access_level ON journals(access_level);

-- Create proxy_configs table
CREATE TABLE IF NOT EXISTS proxy_configs (
    id SERIAL PRIMARY KEY,
    journal_id INTEGER NOT NULL REFERENCES journals(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    config_name VARCHAR(100) NOT NULL,
    haproxy_rule TEXT NOT NULL,
    nginx_rule TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    referer VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for proxy_configs
CREATE INDEX IF NOT EXISTS idx_proxy_configs_journal_id ON proxy_configs(journal_id);
CREATE INDEX IF NOT EXISTS idx_proxy_configs_user_id ON proxy_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_proxy_configs_is_active ON proxy_configs(is_active);
CREATE INDEX IF NOT EXISTS idx_proxy_configs_expires_at ON proxy_configs(expires_at);

-- Create access_logs table
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    journal_id INTEGER NOT NULL REFERENCES journals(id) ON DELETE CASCADE,
    proxy_config_id INTEGER REFERENCES proxy_configs(id) ON DELETE SET NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),
    referer VARCHAR(500),
    request_method VARCHAR(10) DEFAULT 'GET',
    request_path VARCHAR(500),
    request_query VARCHAR(1000),
    response_status INTEGER,
    response_size INTEGER,
    response_time FLOAT,
    session_id VARCHAR(100),
    request_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for access_logs
CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_journal_id ON access_logs(journal_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_access_logs_ip_address ON access_logs(ip_address);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_journals_updated_at BEFORE UPDATE ON journals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proxy_configs_updated_at BEFORE UPDATE ON proxy_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin) VALUES
('admin', 'admin@libproxy.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9yQK8i2', 'Admin', 'User', TRUE),
('testuser', 'test@libproxy.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9yQK8i2', 'Test', 'User', FALSE)
ON CONFLICT (username) DO NOTHING;

-- Insert sample journals
INSERT INTO journals (name, slug, description, base_url, proxy_path, publisher, issn, subject_areas, access_level) VALUES
('Nature', 'nature', 'International weekly journal of science', 'https://www.nature.com', 'nature', 'Nature Publishing Group', '0028-0836', '["Science", "Biology", "Physics", "Chemistry"]', 'public'),
('Science', 'science', 'American Association for the Advancement of Science', 'https://www.science.org', 'science', 'AAAS', '0036-8075', '["Science", "Research", "Technology"]', 'public'),
('The Lancet', 'lancet', 'Global health journal', 'https://www.thelancet.com', 'lancet', 'Elsevier', '0140-6736', '["Medicine", "Health", "Public Health"]', 'restricted'),
('JAMA', 'jama', 'Journal of the American Medical Association', 'https://jamanetwork.com', 'jama', 'American Medical Association', '0098-7484', '["Medicine", "Health", "Clinical Research"]', 'restricted')
ON CONFLICT (slug) DO NOTHING;

-- Create a view for active proxy configurations
CREATE OR REPLACE VIEW active_proxy_configs AS
SELECT 
    pc.*,
    j.name as journal_name,
    j.slug as journal_slug,
    j.base_url as journal_base_url,
    u.username,
    u.first_name,
    u.last_name
FROM proxy_configs pc
JOIN journals j ON pc.journal_id = j.id
LEFT JOIN users u ON pc.user_id = u.id
WHERE pc.is_active = TRUE 
AND (pc.expires_at IS NULL OR pc.expires_at > CURRENT_TIMESTAMP)
AND j.is_active = TRUE;

-- Create a view for access statistics
CREATE OR REPLACE VIEW journal_access_stats AS
SELECT 
    j.id as journal_id,
    j.name as journal_name,
    j.slug as journal_slug,
    COUNT(al.id) as total_accesses,
    COUNT(DISTINCT al.user_id) as unique_users,
    COUNT(DISTINCT al.ip_address) as unique_ips,
    MAX(al.timestamp) as last_access,
    AVG(al.response_time) as avg_response_time
FROM journals j
LEFT JOIN access_logs al ON j.id = al.journal_id
WHERE j.is_active = TRUE
GROUP BY j.id, j.name, j.slug;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO libproxy_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO libproxy_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO libproxy_user;
