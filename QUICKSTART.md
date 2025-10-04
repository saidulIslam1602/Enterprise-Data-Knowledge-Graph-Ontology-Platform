# 🚀 Quick Start Guide

Get the Enterprise Knowledge Graph Platform running in **5 minutes**!

## Prerequisites

- Python 3.9+
- pip package manager
- Internet connection (for fetching real company data)

## Installation & Setup

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

Expected installation time: **2-3 minutes**

### 2. Generate Sample Data
```bash
python scripts/generate_data.py
```

This will:
- ✅ Generate 150 realistic customers using **Faker**
- ✅ Fetch 25 real companies from **OpenCorporates API**
- ✅ Create 400+ GDPR-compliant consent records
- ✅ Generate 2000+ transaction records
- ✅ Create **~10,000 RDF triples** in total

Output: `data/samples/generated_data.ttl`

Expected runtime: **30-60 seconds**

### 3. Run the Demo
```bash
python scripts/demo.py
```

This demonstrates:
- ✅ Ontology loading (4 ontologies + SKOS glossary)
- ✅ Knowledge graph statistics
- ✅ SPARQL query examples
- ✅ SHACL data validation
- ✅ GDPR compliance monitoring

Expected runtime: **15-30 seconds**

### 4. Start the REST API (Optional)
```bash
python src/api/server.py
```

Then open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000/api/v1/statistics

## Quick Examples

### Example 1: Query High-Value Customers
```python
from src.core.graph_manager import GraphManager

gm = GraphManager()
gm.load_all_ontologies("ontologies/")
gm.load_ontology("data/samples/generated_data.ttl")

query = """
PREFIX cus: <http://enterprise.org/ontology/customer#>

SELECT ?email ?lifetimeValue
WHERE {
    ?customer cus:email ?email ;
              cus:lifetimeValue ?lifetimeValue .
    FILTER(?lifetimeValue > 10000)
}
ORDER BY DESC(?lifetimeValue)
LIMIT 10
"""

results = gm.execute_query(query)
for row in results['results']['bindings']:
    email = row['email']['value']
    ltv = row['lifetimeValue']['value']
    print(f"{email}: ${ltv}")
```

### Example 2: Validate Data Quality
```python
from src.core.validator import DataValidator

validator = DataValidator("validation/")
report = validator.validate_file("data/samples/generated_data.ttl")

print(f"Valid: {report['conforms']}")
print(f"Violations: {report['total_violations']}")
```

### Example 3: Check GDPR Compliance
```python
from src.compliance.monitor import ComplianceMonitor
from rdflib import Graph

graph = Graph()
graph.parse("data/samples/generated_data.ttl")

monitor = ComplianceMonitor(graph)
report = monitor.generate_compliance_report()

print(f"Active consents: {report['consent_summary']['ACTIVE']}")
print(f"Withdrawn consents: {report['consent_summary']['WITHDRAWN']}")
```

### Example 4: Use the REST API
```bash
# Start server in one terminal
python src/api/server.py

# In another terminal, query the API
curl "http://localhost:8000/api/v1/statistics"

curl -X POST "http://localhost:8000/api/v1/sparql/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PREFIX cus: <http://enterprise.org/ontology/customer#> SELECT (COUNT(?c) as ?count) WHERE { ?c a cus:Customer }"
  }'

curl "http://localhost:8000/api/v1/compliance/report"
```

## Project Structure

```
Enterprise Data Knowledge Graph & Ontology Platform/
├── ontologies/              # 5 OWL ontologies (Customer, Company, Compliance, Lineage, Glossary)
├── validation/              # SHACL shapes for data quality
├── queries/                 # 60+ SPARQL query examples
├── src/
│   ├── core/               # Graph manager & validator
│   ├── api/                # FastAPI REST server
│   ├── compliance/         # GDPR monitoring
│   └── ingestion/          # Data generation with real sources
├── scripts/
│   ├── generate_data.py    # Generate sample data
│   └── demo.py             # Full demonstration
└── data/samples/           # Generated RDF data
```

## Key Features Demonstrated

### ✅ Ontology Engineering
- **4 domain ontologies**: Customer, Company, Compliance, Lineage
- **1 SKOS glossary**: Multi-language business terms (EN/NO)
- **OWL/RDFS**: Classes, properties, restrictions
- **Multi-language support**: English + Norwegian (Oslo market)

### ✅ Semantic Technologies
- **RDF/OWL**: Full semantic data model
- **SPARQL**: 60+ production-ready queries
- **SHACL**: Comprehensive validation shapes
- **SKOS**: Business glossary and taxonomies

### ✅ Data Governance
- **GDPR compliance**: Consent management, DSR tracking
- **Data quality**: 6 quality dimensions with SHACL
- **Data lineage**: Provenance tracking with PROV-O
- **Audit logging**: Complete traceability

### ✅ Real Data Integration
- **OpenCorporates API**: Real company data
- **Faker**: Realistic synthetic personal data
- **Multi-locale support**: US, UK, Norway, Germany

### ✅ REST API
- **FastAPI**: Modern async API
- **Swagger UI**: Interactive documentation
- **8 endpoints**: Statistics, SPARQL, validation, compliance

## Norwegian Market Support

The platform includes Norwegian language support for the Oslo market:

```sparql
# Query business glossary in Norwegian
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?norskLabel ?definisjon
WHERE {
    ?concept skos:prefLabel ?norskLabel ;
             skos:definition ?definisjon .
    FILTER (LANG(?norskLabel) = "no")
}
```

Terms include:
- Kundeadministrasjon (Customer Management)
- Datastyrning (Data Governance)
- Datakvalitet (Data Quality)
- GDPR-overholdelse (GDPR Compliance)
- Datatilsynet (Norwegian Data Protection Authority)

## Troubleshooting

### Issue: OpenCorporates API not working
**Solution**: The generator automatically falls back to synthetic company data if the API is unavailable. No action needed.

### Issue: Import errors
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Empty query results
**Solution**: Make sure you've generated data first:
```bash
python scripts/generate_data.py
```

## Next Steps

1. **Explore SPARQL queries**: See `queries/` directory for 60+ examples
2. **Review ontologies**: Check `ontologies/` for domain models
3. **Test validation**: Try `validation/` SHACL shapes
4. **Read full docs**: See `README.md` for complete documentation

## 🎨 Optional: React Dashboard

For a visual interface, start the React dashboard:

```bash
cd dashboard
npm install
npm run dev
```

Visit: http://localhost:3000

**Dashboard Features:**
- 📊 Interactive statistics visualization
- 💻 SPARQL query editor with syntax highlighting
- 🛡️ GDPR compliance monitoring
- ✅ Data quality metrics
- 🔍 Ontology class browser

---

## Support

This is a portfolio/demonstration project showcasing:
- ✅ Semantic Web expertise (RDF, OWL, SKOS, SPARQL, SHACL)
- ✅ Data governance and GDPR compliance
- ✅ Ontology engineering and design
- ✅ Real-world data integration
- ✅ REST API development
- ✅ Multi-language support (Norwegian market)

Perfect for demonstrating semantic web and ontology engineering expertise!

---

**Total setup time: ~5 minutes** ⚡
**Generated triples: ~10,000** 📊
**Ready for demonstration** ✅
