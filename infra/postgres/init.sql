-- Create databases for each platform
CREATE DATABASE industrial;
CREATE DATABASE supply_chain;
CREATE DATABASE park_service;

-- Connect to industrial database and create tables
\c industrial;

-- Users table (shared across all platforms)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User roles association
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Platform permissions
CREATE TABLE platform_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(role_id, platform, resource, action)
);

-- Insert default roles
INSERT INTO roles (name, code, description) VALUES
    ('系统管理员', 'admin', '系统管理员，拥有所有权限'),
    ('平台管理员', 'platform_admin', '平台管理员'),
    ('普通用户', 'user', '普通用户');

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, status) VALUES
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qVh.N9NJ.KQXCK', 'active');

-- Assign admin role to default user
INSERT INTO user_roles (user_id, role_id) VALUES (1, 1);

-- Insert admin permissions
INSERT INTO platform_permissions (role_id, platform, resource, action) VALUES
    (1, 'industrial', '*', '*'),
    (1, 'supply', '*', '*'),
    (1, 'park', '*', '*'),
    (2, 'industrial', 'products', 'read'),
    (2, 'industrial', 'orders', 'read'),
    (2, 'supply', 'inventory', 'read'),
    (2, 'park', 'enterprises', 'read');

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    contact_person VARCHAR(50),
    contact_phone VARCHAR(20),
    business_license VARCHAR(100),
    address TEXT,
    status VARCHAR(20) DEFAULT 'active',
    audit_status VARCHAR(20) DEFAULT 'pending',
    audit_remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    icon VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    specs JSONB DEFAULT '{}',
    unit VARCHAR(20),
    description TEXT,
    images JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE product_skus (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    attributes JSONB DEFAULT '{}',
    price DECIMAL(12,2) NOT NULL,
    original_price DECIMAL(12,2),
    stock INTEGER DEFAULT 0,
    min_order_qty INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE inquiries (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_items INTEGER DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inquiry_items (
    id SERIAL PRIMARY KEY,
    inquiry_id INTEGER REFERENCES inquiries(id),
    product_sku_id INTEGER REFERENCES product_skus(id),
    qty INTEGER NOT NULL,
    target_price DECIMAL(12,2),
    remark TEXT
);

CREATE TABLE inquiry_quotes (
    id SERIAL PRIMARY KEY,
    inquiry_item_id INTEGER REFERENCES inquiry_items(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    price DECIMAL(12,2) NOT NULL,
    delivery_days INTEGER,
    remark TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    buyer_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    delivery_address JSONB DEFAULT '{}',
    remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_sku_id INTEGER REFERENCES product_skus(id),
    qty INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    payment_no VARCHAR(100) UNIQUE,
    channel VARCHAR(30) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Connect to supply_chain database
\c supply_chain;

CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    location JSONB DEFAULT '{}',
    capacity DECIMAL(12,2),
    used_capacity DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE warehouse_locations (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    zone VARCHAR(30),
    shelf VARCHAR(30),
    bin VARCHAR(30),
    status VARCHAR(20) DEFAULT 'active',
    UNIQUE(warehouse_id, zone, shelf, bin)
);

CREATE TABLE inbound_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    warehouse_id INTEGER REFERENCES warehouses(id),
    supplier_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    total_qty INTEGER DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inbound_items (
    id SERIAL PRIMARY KEY,
    inbound_order_id INTEGER REFERENCES inbound_orders(id),
    product_sku_id INTEGER,
    qty INTEGER NOT NULL,
    batch_no VARCHAR(50),
    location_id INTEGER REFERENCES warehouse_locations(id),
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE outbound_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    warehouse_id INTEGER REFERENCES warehouses(id),
    type VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_qty INTEGER DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE outbound_items (
    id SERIAL PRIMARY KEY,
    outbound_order_id INTEGER REFERENCES outbound_orders(id),
    product_sku_id INTEGER,
    qty INTEGER NOT NULL,
    batch_no VARCHAR(50),
    location_id INTEGER REFERENCES warehouse_locations(id)
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    product_sku_id INTEGER NOT NULL,
    qty INTEGER DEFAULT 0,
    locked_qty INTEGER DEFAULT 0,
    batch_no VARCHAR(50),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(warehouse_id, product_sku_id, batch_no)
);

CREATE TABLE vessel_dynamics (
    id SERIAL PRIMARY KEY,
    vessel_name VARCHAR(100) NOT NULL,
    imo VARCHAR(20),
    port VARCHAR(100),
    eta TIMESTAMP,
    ata TIMESTAMP,
    berth_status VARCHAR(30),
    cargo_progress DECIMAL(5,2) DEFAULT 0,
    raw_data JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    tracking_no VARCHAR(100) UNIQUE NOT NULL,
    origin VARCHAR(200),
    destination VARCHAR(200),
    carrier VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    current_location JSONB DEFAULT '{}',
    eta TIMESTAMP,
    actual_arrival TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Connect to park_service database
\c park_service;

CREATE TABLE enterprises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    unified_code VARCHAR(50) UNIQUE NOT NULL,
    contact_person VARCHAR(50),
    contact_phone VARCHAR(20),
    address TEXT,
    industry VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE energy_consumption (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id),
    type VARCHAR(30) NOT NULL,
    period DATE NOT NULL,
    value DECIMAL(12,2) NOT NULL,
    unit VARCHAR(20),
    reported BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(enterprise_id, type, period)
);

CREATE TABLE safety_records (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id),
    type VARCHAR(50) NOT NULL,
    incident_date DATE,
    description TEXT,
    severity VARCHAR(20),
    measures TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE emission_records (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id),
    type VARCHAR(50) NOT NULL,
    period DATE NOT NULL,
    value DECIMAL(12,2) NOT NULL,
    limit_value DECIMAL(12,2),
    unit VARCHAR(20),
    is_exceeding BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(enterprise_id, type, period)
);

CREATE TABLE report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    format_config JSONB DEFAULT '{}',
    period_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE report_forms (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id),
    template_id INTEGER REFERENCES report_templates(id),
    period VARCHAR(50) NOT NULL,
    data JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft',
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    form_id INTEGER REFERENCES report_forms(id),
    department VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT NOW(),
    feedback TEXT,
    reviewed_at TIMESTAMP
);
