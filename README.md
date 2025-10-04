# Enterprise Data Knowledge Graph & Ontology Platform

A comprehensive ontology-driven data management system for enterprise customer and business data, focusing on compliance, data governance, and semantic interoperability.

## 🎯 Project Overview

This platform demonstrates advanced ontology engineering and semantic web technologies to create a scalable, compliant, and intelligent data management system. It showcases professional skills including:

- RDF/OWL ontology design and modeling
- SPARQL query development
- SHACL validation for data quality
- Data governance and compliance by design
- Knowledge graph construction and management
- Cross-system data integration

## 🏗️ Architecture

```
├── ontologies/              # 5 OWL/RDF ontologies + SKOS glossary
│   ├── customer_ontology.ttl
│   ├── company_ontology.ttl
│   ├── compliance_ontology.ttl
│   ├── lineage_ontology.ttl
│   └── business_glossary.ttl    # Multi-language (EN/NO)
├── validation/              # SHACL shapes for data quality
│   ├── customer_shapes.ttl
│   └── compliance_shapes.ttl
├── queries/                 # 60+ SPARQL query examples
│   ├── customer_queries.sparql
│   ├── compliance_queries.sparql
│   └── lineage_queries.sparql
├── src/
│   ├── api/                # FastAPI REST server
│   ├── core/               # Graph manager & validator
│   ├── ingestion/          # Data generation (real sources!)
│   ├── compliance/         # GDPR monitoring
│   └── utils/              # Helper functions
├── scripts/
│   ├── generate_data.py    # Generate sample data
│   └── demo.py             # Full demonstration
├── data/samples/           # Generated RDF data (~10K triples)
├── docs/                   # Comprehensive documentation
│   ├── USE_CASES.md        # Requirements engineering
├── docker-compose.yml      # Docker setup (Fuseki, PostgreSQL, Redis)
├── QUICKSTART.md           # 5-minute setup guide
└── README.md               # This file
```

## 🚀 Features

### 1. Ontology Management
- **Customer Domain Ontology**: Models customer profiles, preferences, and relationships
- **Company Domain Ontology**: Business hierarchies, industry classifications, and market segments
- **Compliance Ontology**: GDPR, CCPA, and regulatory frameworks
- **Data Lineage Ontology**: Tracks data provenance and transformations

### 2. Semantic Technologies
- **RDF/OWL Models**: Comprehensive semantic data models
- **SPARQL Endpoint**: Query interface for semantic data
- **SHACL Validation**: Automated data quality checks
- **SKOS Taxonomies**: Controlled vocabularies and business glossaries

### 3. Data Governance
- **Privacy by Design**: Built-in data protection mechanisms
- **Consent Management**: Track and enforce user consent
- **Audit Trail**: Complete history of data access and modifications
- **Compliance Reporting**: Automated regulatory reports

### 4. Integration Capabilities
- **Multi-source Ingestion**: Connect to CRM, ERP, databases
- **Real-time Synchronization**: Event-driven data updates
- **API-first Architecture**: RESTful and GraphQL endpoints
- **Data Transformation**: ETL pipelines with semantic enrichment

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+ (for dashboard)
- Apache Jena Fuseki or GraphDB (triplestore)
- Docker and Docker Compose (optional)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Enterprise Data Knowledge Graph & Ontology Platform"
```

### 2. Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp env.example .env
# Edit .env with your configuration
```

### 4. Generate Sample Data (Uses Real Data Sources!)
```bash
python scripts/generate_data.py
```
This script:
- Generates 150+ realistic customers using Faker
- Fetches 25+ real companies from **OpenCorporates API**
- Creates GDPR-compliant consent records
- Generates transaction history
- Total: ~10,000+ RDF triples

### 5. Start Triplestore (Optional - using Docker)
```bash
docker-compose up -d fuseki
```

### 6. Run Demonstration
```bash
python scripts/demo.py
```
See all features in action: SPARQL queries, SHACL validation, compliance monitoring

### 7. Start REST API Server
```bash
python src/api/server.py
```
API available at: http://localhost:8000/docs (Swagger UI)

## 📚 Usage Examples

### Generate Data with Real Sources
```python
from src.ingestion.data_generator import DataGenerator

generator = DataGenerator(locale='en_US', seed=42)

# Generate 100 customers with realistic data
graph = generator.generate_customers(count=100)

# Fetch real companies from OpenCorporates API
companies = generator.fetch_real_companies(count=20, jurisdiction="us")
graph = generator.companies_to_rdf(companies, graph)

# Generate GDPR compliance data
graph = generator.generate_compliance_data(graph)

# Save to file
graph.serialize(destination="data.ttl", format='turtle')
```

### Query Customer Data with SPARQL
```python
from src.core.graph_manager import GraphManager

gm = GraphManager()

# Load ontologies and data
gm.load_all_ontologies("ontologies/")
gm.load_ontology("data/samples/generated_data.ttl")

# Execute SPARQL query
query = """
PREFIX cus: <http://enterprise.org/ontology/customer#>

SELECT ?email ?lifetimeValue
WHERE {
    ?customer a cus:Customer ;
              cus:email ?email ;
              cus:lifetimeValue ?lifetimeValue .
    FILTER(?lifetimeValue > 10000)
}
ORDER BY DESC(?lifetimeValue)
LIMIT 10
"""
results = gm.execute_query(query)
```

### Validate Data Quality
```python
from src.core.validator import DataValidator

# Initialize with SHACL shapes
validator = DataValidator(shapes_dir="validation/")

# Validate data
validation_report = validator.validate_file("data/samples/generated_data.ttl")

print(f"Valid: {validation_report['conforms']}")
print(f"Violations: {validation_report['total_violations']}")

# Generate detailed report
report = validator.generate_report(validation_report, output_format='text')
print(report)
```

### Check Compliance Status
```python
from src.compliance.monitor import ComplianceMonitor
from rdflib import Graph

# Load data
graph = Graph()
graph.parse("data/samples/generated_data.ttl")

# Initialize monitor
monitor = ComplianceMonitor(graph)

# Check GDPR compliance
status = monitor.check_gdpr_compliance("CUS-000001")
print(f"GDPR Compliant: {status.is_compliant}")
print(f"Issues: {status.issues}")

# Get overdue data subject rights requests
overdue = monitor.get_overdue_dsr_requests()
print(f"Overdue requests: {len(overdue)}")

# Generate compliance report
report = monitor.generate_compliance_report()
print(f"Total consents: {report['consent_summary']['total']}")
```

### Use REST API
```bash
# Start the server
python src/api/server.py

# Query via API (from another terminal)
curl -X POST "http://localhost:8000/api/v1/sparql/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 10"}'

# Get compliance report
curl "http://localhost:8000/api/v1/compliance/report"

# Check GDPR compliance for a customer
curl "http://localhost:8000/api/v1/compliance/gdpr/CUS-000001"
```

## 🌐 Real Data Sources

This platform integrates with **real, free data sources**:

### OpenCorporates API
- **World's largest open database of companies**
- Free tier: 500 requests/month
- Provides real company data: names, registration numbers, addresses
- Used in `data_generator.py` to fetch authentic company information

### Faker Library
- Generates realistic synthetic personal data
- Supports multiple locales (US, UK, Germany, etc.)
- Creates authentic-looking:
  - Names, emails, phone numbers
  - Addresses with real city/state/country data
  - Transaction histories
  - Dates and timestamps

### Generated Data Statistics
Running `python scripts/generate_data.py` creates:
- **150** Individual Customers
- **30** Business Customers
- **25** Real Companies (from OpenCorporates)
- **400+** Consent Records
- **2000+** Transactions
- **Total: ~10,000 RDF triples**

## 🎨 REST API & Documentation

Start the API server:
```bash
python src/api/server.py
```

Access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Available endpoints:
- `/api/v1/statistics` - Graph statistics
- `/api/v1/sparql/query` - Execute SPARQL queries
- `/api/v1/validate` - SHACL validation
- `/api/v1/compliance/report` - Compliance report
- `/api/v1/compliance/gdpr/{id}` - GDPR compliance check
- `/api/v1/compliance/dsr/overdue` - Overdue DSR requests

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/test_ontology.py
```

## 📖 Documentation

Comprehensive documentation is available in the `/docs` directory:

### Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes! ⚡

### Project Documentation
- **[USE_CASES.md](docs/USE_CASES.md)** - Requirements engineering & use cases

### Technical Documentation
- **README.md** (this file) - Complete project overview
- **API Documentation** - http://localhost:8000/docs (when server running)
- **Ontology Files** - See `ontologies/` directory (5 ontologies)
- **SPARQL Queries** - See `queries/` directory (60+ queries)
- **SHACL Shapes** - See `validation/` directory

## 🔐 Security & Compliance

- **GDPR Ready**: Built-in support for data subject rights
- **Audit Logging**: Complete tracking of all operations
- **Access Control**: Role-based permissions
- **Data Encryption**: At-rest and in-transit encryption
- **Privacy by Design**: Core architectural principle

## 🤝 Contributing

This is a portfolio/demonstration project. For improvements or suggestions:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Developed as a professional demonstration project showcasing:
- Advanced semantic web technologies
- Enterprise data architecture
- Compliance and governance expertise
- Cross-functional technical skills

## 🙏 Acknowledgments

- W3C for Semantic Web standards
- Apache Jena project
- RDFLib community
- Protégé ontology editor

## 📞 Contact

For questions or opportunities: [Your Contact Information]

---

**Note**: This project demonstrates proficiency in ontology engineering, semantic technologies, data governance, and enterprise architecture - essential skills for data-driven organizations.
