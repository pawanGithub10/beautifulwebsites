# Analytics & Insights Website - Architecture Design

## Overview

A data analytics and statistical insights platform that connects to multiple data sources, processes data, generates insights, and presents them through interactive dashboards and reports.

## Site Type: `analytics`

### Target Users
- Business analysts
- Data scientists
- Management teams
- Marketing professionals
- Operations teams

### Key Features
- Multi-source data integration
- Real-time and batch data processing
- Interactive dashboards
- Statistical analysis and insights
- Custom report generation
- Scheduled reports
- Data export capabilities
- Alert and notification system

## Architecture Components

### 1. Analytics Service (Port 8016)

**Responsibilities:**
- Manage data sources and connections
- Handle data ingestion pipelines
- Store processed analytics data
- Generate insights and statistics
- Manage dashboards and widgets
- Handle report generation

**Database Tables:**

```sql
-- Data Sources
CREATE TABLE data_sources (
    source_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- database, api, file, webhook
    name VARCHAR(200) NOT NULL,
    description TEXT,
    connection_config JSONB NOT NULL,  -- credentials, endpoints, etc.
    refresh_schedule VARCHAR(100),     -- cron expression
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Connectors Configuration
CREATE TABLE data_connectors (
    connector_id UUID PRIMARY KEY,
    source_id UUID REFERENCES data_sources(source_id),
    connector_type VARCHAR(50),  -- postgres, mysql, rest_api, csv, excel, sheets
    schema_mapping JSONB,        -- field mappings and transformations
    filters JSONB,               -- data filtering rules
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Datasets (processed data)
CREATE TABLE datasets (
    dataset_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    source_id UUID REFERENCES data_sources(source_id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    schema JSONB NOT NULL,           -- column definitions
    data_type VARCHAR(50),           -- timeseries, categorical, numerical
    row_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dataset Records (actual data)
CREATE TABLE dataset_records (
    record_id UUID PRIMARY KEY,
    dataset_id UUID REFERENCES datasets(dataset_id),
    record_data JSONB NOT NULL,      -- flexible storage for any data shape
    record_date DATE,                -- for time-series data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Dashboards
CREATE TABLE dashboards (
    dashboard_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    layout JSONB,                    -- dashboard layout configuration
    is_public BOOLEAN DEFAULT false,
    owner_user_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard Widgets
CREATE TABLE dashboard_widgets (
    widget_id UUID PRIMARY KEY,
    dashboard_id UUID REFERENCES dashboards(dashboard_id),
    widget_type VARCHAR(50),         -- chart, table, metric, map, custom
    title VARCHAR(200),
    position JSONB,                  -- x, y, width, height
    config JSONB NOT NULL,           -- widget-specific configuration
    data_query JSONB,                -- query definition for widget data
    refresh_interval INTEGER,        -- seconds, null = manual only
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insights (AI/ML generated)
CREATE TABLE insights (
    insight_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    dataset_id UUID REFERENCES datasets(dataset_id),
    insight_type VARCHAR(50),        -- trend, anomaly, correlation, prediction
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20),            -- info, warning, critical
    data JSONB,                      -- insight details and metrics
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    report_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    report_type VARCHAR(50),         -- pdf, excel, csv, html
    template_config JSONB,           -- report template configuration
    schedule JSONB,                  -- scheduling configuration
    recipients JSONB,                -- email list for scheduled reports
    last_generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report Executions
CREATE TABLE report_executions (
    execution_id UUID PRIMARY KEY,
    report_id UUID REFERENCES reports(report_id),
    status VARCHAR(20),              -- pending, processing, completed, failed
    file_url VARCHAR(500),
    parameters JSONB,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Data Alerts
CREATE TABLE data_alerts (
    alert_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    dataset_id UUID REFERENCES datasets(dataset_id),
    condition JSONB NOT NULL,        -- alert condition/rule
    alert_type VARCHAR(50),          -- threshold, change, anomaly
    notification_config JSONB,       -- channels and recipients
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Data Connector Framework

**Supported Data Sources:**

#### Database Connectors
- PostgreSQL
- MySQL
- MongoDB
- SQL Server
- Oracle

#### API Connectors
- REST APIs
- GraphQL
- SOAP
- Webhooks

#### File Connectors
- CSV
- Excel (XLSX)
- JSON
- XML

#### Cloud Connectors
- Google Sheets
- Google Analytics
- Salesforce
- Shopify
- Stripe
- AWS S3
- Azure Blob Storage

#### Custom Connectors
- Plugin architecture for custom integrations

**Connector Architecture:**

```python
# Base connector interface
class BaseConnector(ABC):
    @abstractmethod
    async def connect(self, config: dict) -> bool:
        """Establish connection to data source"""
        pass

    @abstractmethod
    async def fetch_data(self, query: dict) -> List[dict]:
        """Fetch data from source"""
        pass

    @abstractmethod
    async def validate_schema(self) -> bool:
        """Validate data schema"""
        pass

# Example: PostgreSQL Connector
class PostgreSQLConnector(BaseConnector):
    async def connect(self, config):
        self.conn = await asyncpg.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )

    async def fetch_data(self, query):
        sql = query.get('sql')
        return await self.conn.fetch(sql)

# Example: REST API Connector
class RestAPIConnector(BaseConnector):
    async def fetch_data(self, query):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                query['endpoint'],
                headers=query.get('headers'),
                params=query.get('params')
            )
            return response.json()
```

### 3. Analytics Engine

**Processing Capabilities:**

#### Statistical Analysis
- Descriptive statistics (mean, median, mode, std dev)
- Correlation analysis
- Regression analysis
- Time series analysis
- Forecasting (ARIMA, Prophet)

#### Data Transformations
- Aggregations (sum, count, avg, min, max)
- Grouping and pivoting
- Filtering and sorting
- Calculated fields
- Data cleansing

#### Insight Generation
- Trend detection
- Anomaly detection
- Pattern recognition
- Predictive analytics
- Recommendation engine

**Processing Pipeline:**

```python
# Analytics Pipeline
class AnalyticsPipeline:
    async def process_dataset(self, dataset_id: str):
        # 1. Extract data from source
        data = await self.extract_data(dataset_id)

        # 2. Transform data
        transformed = await self.transform_data(data)

        # 3. Load into dataset records
        await self.load_data(dataset_id, transformed)

        # 4. Generate insights
        insights = await self.generate_insights(dataset_id)

        # 5. Trigger alerts if needed
        await self.check_alerts(dataset_id, insights)

        return insights
```

### 4. Dashboard Types

#### Pre-built Dashboard Templates

**1. Sales Analytics Dashboard**
- Revenue trends
- Top products
- Customer segments
- Geographic distribution
- Sales funnel

**2. Website Analytics Dashboard**
- Traffic overview
- User behavior
- Conversion rates
- Page performance
- Referral sources

**3. Operational Dashboard**
- KPI overview
- Real-time metrics
- Performance indicators
- Resource utilization
- System health

**4. Financial Dashboard**
- Revenue & expenses
- Profit margins
- Cash flow
- Budget vs actual
- Financial ratios

**5. Marketing Dashboard**
- Campaign performance
- Lead generation
- Customer acquisition cost
- ROI metrics
- Channel attribution

**6. Custom Dashboard**
- Drag-and-drop builder
- Widget library
- Custom queries
- Flexible layouts

### 5. Visualization Types

**Chart Types:**
- Line chart (time series)
- Bar chart (categorical)
- Pie/Donut chart (proportions)
- Area chart (trends)
- Scatter plot (correlations)
- Heatmap (distributions)
- Map (geographic data)
- Gauge (KPI)
- Funnel (conversion)
- Sankey (flow)
- Treemap (hierarchy)
- Candlestick (financial)

**Table Types:**
- Data table (sortable, filterable)
- Pivot table
- Comparison table

**Metric Cards:**
- Single value
- Comparison (vs previous period)
- Progress bar
- Sparkline

### 6. Report Generation

**Report Types:**
- **PDF Reports** - Professional formatted documents
- **Excel Reports** - Data with charts and formatting
- **CSV Exports** - Raw data export
- **HTML Reports** - Web-viewable reports
- **PowerPoint** - Presentation slides

**Scheduling:**
- Daily, weekly, monthly
- Custom cron schedules
- Event-triggered
- On-demand

**Distribution:**
- Email delivery
- FTP/SFTP upload
- Cloud storage (S3, Google Drive)
- Download portal

### 7. Real-time Features

**Live Data Streaming:**
- WebSocket connections for real-time updates
- Server-Sent Events (SSE) for dashboard refresh
- Polling for legacy browsers

**Real-time Metrics:**
- Active users
- Current sales
- System metrics
- Social media mentions
- Stock prices

### 8. Data Security & Privacy

**Security Features:**
- Row-level security
- Column-level masking
- Role-based access control
- Data encryption (at rest and in transit)
- Audit logging

**Privacy Compliance:**
- GDPR compliance
- Data anonymization
- PII detection and handling
- Data retention policies

## Frontend Components

### Dashboard Builder

```typescript
// components/analytics/DashboardBuilder.tsx
interface Widget {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'map';
  title: string;
  config: WidgetConfig;
  position: { x: number; y: number; w: number; h: number };
}

export function DashboardBuilder() {
  const [widgets, setWidgets] = useState<Widget[]>([]);

  return (
    <GridLayout
      layout={widgets.map(w => w.position)}
      onLayoutChange={handleLayoutChange}
    >
      {widgets.map(widget => (
        <div key={widget.id}>
          <WidgetRenderer widget={widget} />
        </div>
      ))}
    </GridLayout>
  );
}
```

### Chart Components

```typescript
// Using Recharts or Chart.js
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function TimeSeriesChart({ data, config }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

### Data Source Connection

```typescript
// components/analytics/DataSourceForm.tsx
export function DataSourceForm() {
  const connectorTypes = [
    { value: 'postgres', label: 'PostgreSQL' },
    { value: 'mysql', label: 'MySQL' },
    { value: 'rest_api', label: 'REST API' },
    { value: 'google_sheets', label: 'Google Sheets' },
  ];

  return (
    <Form onSubmit={handleSubmit}>
      <Select name="connector_type" options={connectorTypes} />
      {selectedType === 'postgres' && <PostgreSQLConfig />}
      {selectedType === 'rest_api' && <RestAPIConfig />}
      <Button type="submit">Test Connection</Button>
    </Form>
  );
}
```

## Workflow Orchestration

### Data Refresh Workflow

```python
@workflow.defn
class DataRefreshWorkflow:
    """
    Scheduled data refresh from all sources.
    """

    @workflow.run
    async def run(self, source_id: str):
        # 1. Connect to data source
        connection = await workflow.execute_activity(
            connect_to_source,
            source_id,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 2. Fetch new data
        data = await workflow.execute_activity(
            fetch_data_from_source,
            source_id,
            start_to_close_timeout=timedelta(minutes=30)
        )

        # 3. Process and transform
        processed = await workflow.execute_activity(
            process_data,
            data,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # 4. Generate insights
        insights = await workflow.execute_activity(
            generate_insights,
            processed,
            start_to_close_timeout=timedelta(minutes=15)
        )

        # 5. Check for alerts
        alerts = await workflow.execute_activity(
            check_alert_conditions,
            insights,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 6. Send notifications if alerts triggered
        if alerts:
            await workflow.execute_activity(
                send_alert_notifications,
                alerts,
                start_to_close_timeout=timedelta(minutes=2)
            )

        return {"status": "completed", "insights": insights}
```

### Report Generation Workflow

```python
@workflow.defn
class ReportGenerationWorkflow:
    """
    Generate and distribute scheduled reports.
    """

    @workflow.run
    async def run(self, report_id: str):
        # 1. Fetch report configuration
        config = await workflow.execute_activity(
            get_report_config,
            report_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 2. Gather data for report
        data = await workflow.execute_activity(
            gather_report_data,
            config,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # 3. Generate report file
        report_file = await workflow.execute_activity(
            generate_report_file,
            {"config": config, "data": data},
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 4. Upload to storage
        file_url = await workflow.execute_activity(
            upload_report,
            report_file,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 5. Send to recipients
        await workflow.execute_activity(
            distribute_report,
            {"url": file_url, "recipients": config['recipients']},
            start_to_close_timeout=timedelta(minutes=2)
        )

        return {"status": "completed", "url": file_url}
```

## Technology Stack Additions

### Analytics Libraries
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **scipy** - Scientific computing
- **statsmodels** - Statistical modeling
- **scikit-learn** - Machine learning
- **prophet** - Time series forecasting

### Visualization
- **matplotlib** - Static plots
- **seaborn** - Statistical visualizations
- **plotly** - Interactive charts
- **Recharts** (frontend) - React charting library

### Data Processing
- **Apache Airflow** - Workflow orchestration (alternative to Temporal for ETL)
- **Celery** - Distributed task queue
- **Redis** - Caching and queue

### Storage
- **TimescaleDB** - Time-series data
- **ClickHouse** - OLAP database (for large datasets)

## API Endpoints

### Data Sources

```python
# Create data source
POST /api/v1/{site_id}/analytics/sources
{
  "name": "Production Database",
  "source_type": "postgres",
  "connection_config": {
    "host": "db.example.com",
    "database": "production",
    "user": "analytics",
    "password": "encrypted"
  },
  "refresh_schedule": "0 */6 * * *"  # Every 6 hours
}

# Test connection
POST /api/v1/{site_id}/analytics/sources/{source_id}/test

# Sync data source
POST /api/v1/{site_id}/analytics/sources/{source_id}/sync

# List data sources
GET /api/v1/{site_id}/analytics/sources
```

### Datasets

```python
# Create dataset
POST /api/v1/{site_id}/analytics/datasets
{
  "name": "Sales Data",
  "source_id": "uuid",
  "schema": {
    "columns": [
      {"name": "date", "type": "date"},
      {"name": "revenue", "type": "decimal"},
      {"name": "orders", "type": "integer"}
    ]
  }
}

# Query dataset
POST /api/v1/{site_id}/analytics/datasets/{dataset_id}/query
{
  "filters": [{"column": "date", "operator": ">=", "value": "2024-01-01"}],
  "aggregations": [{"column": "revenue", "function": "sum"}],
  "group_by": ["date"]
}

# Get dataset statistics
GET /api/v1/{site_id}/analytics/datasets/{dataset_id}/stats
```

### Dashboards

```python
# Create dashboard
POST /api/v1/{site_id}/analytics/dashboards
{
  "name": "Sales Overview",
  "layout": {"columns": 12, "rows": 8},
  "is_public": false
}

# Add widget to dashboard
POST /api/v1/{site_id}/analytics/dashboards/{dashboard_id}/widgets
{
  "widget_type": "line_chart",
  "title": "Revenue Trend",
  "position": {"x": 0, "y": 0, "w": 6, "h": 4},
  "config": {
    "dataset_id": "uuid",
    "x_axis": "date",
    "y_axis": "revenue",
    "aggregation": "sum"
  }
}

# Get dashboard with data
GET /api/v1/{site_id}/analytics/dashboards/{dashboard_id}?include_data=true
```

### Insights

```python
# Get insights
GET /api/v1/{site_id}/analytics/insights
?dataset_id=uuid
&insight_type=anomaly
&unread=true

# Mark insight as read
PUT /api/v1/{site_id}/analytics/insights/{insight_id}/read
```

### Reports

```python
# Create report
POST /api/v1/{site_id}/analytics/reports
{
  "name": "Weekly Sales Report",
  "report_type": "pdf",
  "template_config": {...},
  "schedule": {
    "frequency": "weekly",
    "day": "monday",
    "time": "09:00"
  },
  "recipients": ["email@example.com"]
}

# Generate report on-demand
POST /api/v1/{site_id}/analytics/reports/{report_id}/generate

# Download report
GET /api/v1/{site_id}/analytics/reports/executions/{execution_id}/download
```

## Integration Examples

### Example 1: E-commerce Sales Analytics

**Data Sources:**
1. Storefront Service database (orders, products)
2. Google Analytics (website traffic)
3. Marketing platform API (ad spend)

**Dashboards:**
- Revenue trends
- Product performance
- Marketing ROI
- Customer lifetime value

### Example 2: Booking Analytics

**Data Sources:**
1. Booking Service database
2. Calendar system
3. Customer feedback forms

**Dashboards:**
- Booking patterns
- Provider utilization
- Revenue per service
- Customer satisfaction

### Example 3: Multi-Site Analytics

**Data Sources:**
- All site databases
- Aggregated metrics

**Dashboards:**
- Site comparison
- Platform-wide KPIs
- Growth trends
- Resource allocation

## Future Site Types Integration

### Hotel Website Analytics
- Occupancy rates
- Revenue per available room (RevPAR)
- Booking lead times
- Seasonal trends
- Market segment analysis

### Grocery Store Analytics
- Inventory turnover
- Product category performance
- Delivery efficiency
- Customer basket analysis
- Demand forecasting

## Implementation Phases

### Phase 1: Core Analytics Service (MVP)
- Data source management
- Basic connectors (PostgreSQL, MySQL, CSV)
- Simple dashboards
- Chart widgets
- Manual data refresh

### Phase 2: Advanced Features
- Scheduled data refresh
- Insight generation
- Alert system
- Report generation
- More connectors (APIs, cloud services)

### Phase 3: AI/ML Integration
- Predictive analytics
- Anomaly detection
- Automated insights
- Recommendation engine
- Natural language queries

### Phase 4: Enterprise Features
- Multi-tenancy at org level
- White-labeling
- Custom branding
- SSO integration
- Advanced security

## Success Metrics

- Number of data sources connected
- Data refresh frequency
- Dashboard view count
- Report generation frequency
- Insight accuracy
- User engagement (daily active users)
- Query performance (< 3s for most queries)

## Pricing Model

**Tiers:**
1. **Starter** - 2 data sources, 5 dashboards, 1GB storage
2. **Professional** - 10 data sources, unlimited dashboards, 10GB storage
3. **Enterprise** - Unlimited sources, custom connectors, 100GB+ storage

This analytics website type will be a powerful addition to the platform, enabling small businesses to make data-driven decisions! 📊
