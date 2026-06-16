# 园区综合服务平台 - 整体设计方案

## 1. 项目概述

打造一站式园区综合服务平台，覆盖三大核心业务板块：

1. **工业品交易平台** - 工业品供需对接、劳保用品、办公用品等核心品类，提供从商品展示、搜索筛选、在线询价到交易下单、线上支付的全链路闭环服务
2. **供应链平台** - 原材料物流与仓储管理，采购入库、库存周转、出库配送全流程数字化，接入港口船舶到港动态数据
3. **园区服务平台** - 企业端数据采集为入口，打通政府主管部门数据报送通道，统一汇聚能源消耗、安全生产、环保排放等关键指标

### 核心设计原则

- AI赋能全业务流程（智能搜索、智能推荐、智能填报、合规分析等）
- 三个平台独立目录和启动脚本，共享认证和AI模块
- Docker容器化部署，docker-compose统一编排
- 统一用户认证体系，角色权限跨平台管理

## 2. 架构方案

**方案A：统一单体后端 + 多前端**

每个平台拥有独立的前后端目录和启动脚本，通过共享Python包复用认证和AI能力，docker-compose统一编排所有容器。

### 2.1 目录结构

```
campusIntegratedPlatform/
├── docker-compose.yml                    # 统一编排所有服务
├── docker-compose.dev.yml                # 开发环境覆盖
├── .env.example                          # 环境变量模板
├── shared/                               # 共享模块（Python包）
│   ├── setup.py
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── auth/                         # 统一认证模块
│   │   │   ├── jwt_handler.py            # JWT令牌管理
│   │   │   ├── decorators.py             # 权限装饰器
│   │   │   └── models.py                 # 用户/角色模型
│   │   ├── ai_service/                   # AI服务层
│   │   │   ├── client.py                 # 大模型API客户端
│   │   │   ├── prompts.py                # 提示词模板
│   │   │   └── tasks.py                  # AI任务调度
│   │   ├── database/                     # 数据库工具
│   │   │   ├── db.py                     # SQLAlchemy实例
│   │   │   └── migrations.py             # 迁移工具
│   │   └── utils/                        # 通用工具
│   │       ├── response.py               # 统一响应格式
│   │       ├── validators.py             # 校验器
│   │       └── logger.py                 # 日志配置
│   └── requirements.txt
├── industrial-platform/                  # 工业品交易平台
│   ├── frontend/
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   └── src/
│   │       ├── views/                    # 页面组件
│   │       ├── components/               # 通用组件
│   │       ├── api/                      # API调用
│   │       ├── store/                    # Pinia状态
│   │       └── router/                   # 路由配置
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── run.py                        # 启动入口
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # 配置
│   │   │   ├── models/                   # 数据模型
│   │   │   ├── routes/                   # API路由
│   │   │   ├── services/                 # 业务逻辑
│   │   │   └── ai/                       # AI功能
│   │   └── start.sh                      # 启动脚本
│   └── nginx.conf                        # 反向代理配置
├── supply-chain/                         # 供应链平台（同构）
│   ├── frontend/
│   ├── backend/
│   └── nginx.conf
├── park-service/                         # 园区服务平台（同构）
│   ├── frontend/
│   ├── backend/
│   └── nginx.conf
└── infra/                                # 基础设施配置
    ├── postgres/
    │   └── init.sql                      # 数据库初始化
    ├── elasticsearch/
    │   └── mappings/                     # 索引映射
    ├── redis/
    │   └── redis.conf
    └── nginx/
        └── nginx.conf                    # 统一网关
```

### 2.2 Docker Compose 服务编排

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| nginx-gateway | nginx | 80 | 统一入口网关 |
| industrial-frontend | node | 3001 | 工业品前端 |
| industrial-backend | python | 5001 | 工业品后端 |
| supply-frontend | node | 3002 | 供应链前端 |
| supply-backend | python | 5002 | 供应链后端 |
| park-frontend | node | 3003 | 园区前端 |
| park-backend | python | 5003 | 园区后端 |
| postgres | postgres:16 | 5432 | 统一数据库 |
| redis | redis:7 | 6379 | 缓存/会话 |
| elasticsearch | es:8 | 9200 | 全文搜索 |

### 2.3 网关路由规则

```
/                    → 工业品前端（默认）
/supply/             → 供应链前端
/park/               → 园区前端
/api/industrial/     → 工业品后端
/api/supply/         → 供应链后端
/api/park/           → 园区后端
/api/auth/           → 认证服务（共享模块）
```

## 3. 数据库设计

### 3.1 选型分工

- **PostgreSQL 16**：所有业务数据，利用JSONB存储灵活字段
- **Redis 7**：会话管理、JWT黑名单、缓存热数据、限流计数
- **Elasticsearch 8**：商品搜索、供应商搜索、日志分析

### 3.2 统一认证库（shared_auth）

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 用户-角色关联
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 平台权限表
CREATE TABLE platform_permissions (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(30) NOT NULL,  -- industrial / supply / park
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(30) NOT NULL,
    role_id INTEGER REFERENCES roles(id),
    UNIQUE(platform, resource, action, role_id)
);
```

### 3.3 工业品交易库（industrial）

```sql
-- 供应商
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

-- 商品分类
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    icon VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active'
);

-- 商品
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

-- 商品SKU
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

-- 询价单
CREATE TABLE inquiries (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_items INTEGER DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 询价明细
CREATE TABLE inquiry_items (
    id SERIAL PRIMARY KEY,
    inquiry_id INTEGER REFERENCES inquiries(id),
    product_sku_id INTEGER REFERENCES product_skus(id),
    qty INTEGER NOT NULL,
    target_price DECIMAL(12,2),
    remark TEXT
);

-- 询价报价
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

-- 订单
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

-- 订单明细
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_sku_id INTEGER REFERENCES product_skus(id),
    qty INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL
);

-- 支付记录
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    payment_no VARCHAR(100) UNIQUE,
    channel VARCHAR(30) NOT NULL,  -- alipay / wechat / bank_transfer
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 供应链库（supply_chain）

```sql
-- 仓库
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

-- 库位
CREATE TABLE warehouse_locations (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    zone VARCHAR(30),
    shelf VARCHAR(30),
    bin VARCHAR(30),
    status VARCHAR(20) DEFAULT 'active',
    UNIQUE(warehouse_id, zone, shelf, bin)
);

-- 入库单
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

-- 入库明细
CREATE TABLE inbound_items (
    id SERIAL PRIMARY KEY,
    inbound_order_id INTEGER REFERENCES inbound_orders(id),
    product_sku_id INTEGER,
    qty INTEGER NOT NULL,
    batch_no VARCHAR(50),
    location_id INTEGER REFERENCES warehouse_locations(id),
    status VARCHAR(20) DEFAULT 'pending'
);

-- 出库单
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

-- 出库明细
CREATE TABLE outbound_items (
    id SERIAL PRIMARY KEY,
    outbound_order_id INTEGER REFERENCES outbound_orders(id),
    product_sku_id INTEGER,
    qty INTEGER NOT NULL,
    batch_no VARCHAR(50),
    location_id INTEGER REFERENCES warehouse_locations(id)
);

-- 库存
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

-- 船舶动态（数据来源：港口API对接 / 手动录入）
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

-- 物流追踪
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
```

### 3.5 园区服务库（park_service）

```sql
-- 企业信息
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

-- 能源消耗
CREATE TABLE energy_consumption (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id),
    type VARCHAR(30) NOT NULL,  -- electric / gas / water
    period DATE NOT NULL,
    value DECIMAL(12,2) NOT NULL,
    unit VARCHAR(20),
    reported BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(enterprise_id, type, period)
);

-- 安全生产
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

-- 环保排放
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

-- 报表模板
CREATE TABLE report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    format_config JSONB DEFAULT '{}',
    period_type VARCHAR(30) NOT NULL,  -- daily / monthly / quarterly / yearly
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 填报表单
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

-- 报送记录
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    form_id INTEGER REFERENCES report_forms(id),
    department VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT NOW(),
    feedback TEXT,
    reviewed_at TIMESTAMP
);
```

## 4. 统一认证设计

### 4.1 认证流程

1. 用户登录 → JWT Token（包含用户ID、角色、平台权限）
2. 请求到达后端 → `@require_auth` 装饰器校验Token
3. `@require_permission(platform, resource, action)` 校验平台级权限
4. Token刷新机制（短期Access Token + 长期Refresh Token）

### 4.2 角色体系

| 角色 | 工业品平台 | 供应链平台 | 园区平台 |
|------|-----------|-----------|---------|
| admin | 全部权限 | 全部权限 | 全部权限 |
| buyer | 采购、询价、下单 | 查看物流 | 数据填报 |
| supplier | 商品管理、报价 | 入库、发货 | - |
| warehouse_keeper | - | 库存管理 | - |
| park_admin | - | - | 报表管理、报送审核 |
| government | - | - | 查看报送数据 |

## 5. AI赋能设计

### 5.1 统一AI客户端

```python
class AIClient:
    def chat(self, messages, model, temperature) -> str
    def structured_output(self, messages, schema) -> dict
    def embedding(self, text) -> list[float]
```

支持多供应商切换：OpenAI / 文心一言 / 通义千问，通过环境变量配置。默认使用OpenAI兼容接口，便于接入国内代理或自建网关。

### 5.2 AI应用场景

| 平台 | 场景 | 实现方式 |
|------|------|----------|
| 工业品交易 | 智能搜索 | 商品embedding → ES向量搜索，自然语言转搜索条件 |
| 工业品交易 | 商品推荐 | 基于浏览/采购历史的协同过滤 + LLM推荐理由生成 |
| 工业品交易 | 智能询价 | LLM分析询价需求，自动匹配供应商和报价 |
| 工业品交易 | 风险预警 | LLM分析供应商资质、交易异常，生成风险报告 |
| 供应链 | 库存预测 | 历史数据 + LLM分析季节/市场因素，生成采购建议 |
| 供应链 | 物流优化 | LLM分析船舶/运输数据，推荐最优物流方案 |
| 供应链 | 异常检测 | LLM监控库存/物流异常，自动告警和建议 |
| 园区服务 | 智能填报 | LLM理解企业数据，自动填充报表字段 |
| 园区服务 | 合规分析 | LLM检查数据是否符合政策要求，生成合规建议 |
| 园区服务 | 报告生成 | LLM汇总数据，自动生成分析报告 |

## 6. 技术栈

| 层级 | 技术选型 | 版本 |
|------|----------|------|
| 前端框架 | Vue 3 + Vite | 3.4+ / 5.x |
| UI组件库 | Element Plus | 2.x |
| 状态管理 | Pinia | 2.x |
| 路由 | Vue Router | 4.x |
| HTTP客户端 | Axios | 1.x |
| 图表 | ECharts | 5.x |
| 后端框架 | Flask | 3.x |
| ORM | SQLAlchemy | 2.x |
| 数据库迁移 | Alembic | 1.x |
| 数据库 | PostgreSQL | 16 |
| 缓存 | Redis | 7 |
| 搜索 | Elasticsearch | 8 |
| AI | OpenAI SDK / HTTP API | - |
| 容器 | Docker + docker-compose | - |
| 反向代理 | Nginx | 1.25 |

## 7. 前端路由设计

### 7.1 工业品交易平台（/）

```
/                       首页
/products               商品中心
/products/:id           商品详情
/inquiries              询价管理
/inquiries/create       发起询价
/inquiries/:id          询价详情
/orders                 订单管理
/orders/:id             订单详情
/suppliers              供应商管理
/suppliers/:id          供应商详情
/admin/products         后台-商品管理
/admin/inventory        后台-库存管理
/admin/pricing          后台-价格管理
/admin/dashboard        后台-数据看板
```

### 7.2 供应链平台（/supply/）

```
/supply/                仓储看板
/supply/inbound         入库管理
/supply/outbound        出库管理
/supply/inventory       库存管理
/supply/vessels         船舶动态
/supply/vessels/:id     船舶详情
/supply/shipments       物流追踪
/supply/shipments/:id   物流详情
```

### 7.3 园区服务平台（/park/）

```
/park/                  服务首页
/park/enterprises       企业管理
/park/enterprises/:id   企业详情
/park/energy            能源监控
/park/safety            安全生产
/park/emission          环保排放
/park/reports           报表中心
/park/reports/:id       报表填报
/park/submissions       报送管理
```

## 8. 共享前端组件

```
shared-frontend/
├── components/
│   ├── AuthForm.vue          # 登录/注册表单
│   ├── UserAvatar.vue        # 用户头像
│   ├── PlatformNav.vue       # 平台切换导航
│   └── AiChat.vue            # AI对话组件
├── composables/
│   ├── useAuth.ts            # 认证逻辑
│   ├── useAi.ts              # AI调用逻辑
│   └── useApi.ts             # API请求封装
└── styles/
    └── variables.css          # 统一主题变量
```

## 9. 实施计划

### Phase 1 - 工业品交易平台（优先实施）

1. 统一认证 + 共享模块
2. 商品管理 + 搜索
3. 询价 + 订单 + 支付
4. 供应商管理
5. AI智能搜索 + 推荐

### Phase 2 - 供应链平台

1. 仓储管理（入库/出库/库存）
2. 船舶动态接入
3. 物流追踪
4. AI库存预测 + 物流优化

### Phase 3 - 园区服务平台

1. 企业数据采集
2. 能源/安全/环保数据管理
3. 报表模板 + 自动填报
4. 报送管理
5. AI智能填报 + 合规分析
