# Enterprise Knowledge Graph - Use Cases & Requirements

## Document Purpose
This document demonstrates requirements engineering for ontology development, capturing stakeholder needs and translating them into semantic models.

---

## Use Case 1: GDPR Compliance Monitoring

### Business Context
**Stakeholder**: Data Protection Officer (DPO)  
**Priority**: Critical  
**Regulation**: GDPR Articles 5, 6, 12, 15-22, 33

### Business Requirements
1. Track all customer consents across purposes
2. Monitor data subject rights (DSR) request timelines
3. Generate compliance reports for audits
4. Alert on overdue DSR responses (30-day deadline)
5. Identify data breaches requiring notification (72-hour rule)

### Functional Requirements
```
FR-1.1: System SHALL track consent status (ACTIVE, WITHDRAWN, EXPIRED)
FR-1.2: System SHALL link consents to specific processing purposes
FR-1.3: System SHALL calculate days remaining until DSR deadline
FR-1.4: System SHALL generate alerts for consents expiring within 30 days
FR-1.5: System SHALL validate consent records against SHACL shapes
```

### Ontology Implementation
**Ontology**: `compliance_ontology.ttl`

**Key Classes**:
- `compliance:Consent` - Tracks user consent
- `compliance:ConsentPurpose` - Defines processing purposes
- `compliance:RightExerciseRequest` - DSR requests
- `compliance:DataBreachIncident` - Security incidents

**Key Properties**:
- `compliance:consentStatus` - Current consent state
- `compliance:consentGivenDate` - When consent was granted
- `compliance:responseDeadline` - DSR response due date
- `compliance:notificationRequired` - Breach notification flag

### SPARQL Queries
```sparql
# Check overdue DSR requests
PREFIX comp: <http://enterprise.org/ontology/compliance#>

SELECT ?requestId ?deadline ?daysOverdue
WHERE {
    ?request comp:requestId ?requestId ;
             comp:responseDeadline ?deadline ;
             comp:requestStatus ?status .
    FILTER (?status != "COMPLETED")
    FILTER (?deadline < NOW())
    BIND((NOW() - ?deadline) AS ?daysOverdue)
}
```

### Validation Rules (SHACL)
```turtle
# Withdrawn consent must have withdrawal date
:WithdrawnConsentShape
    sh:targetClass comp:Consent ;
    sh:sparql [
        sh:message "Withdrawn consent must have withdrawal date (GDPR Article 7)" ;
        sh:select """
            SELECT $this WHERE {
                $this comp:consentStatus "WITHDRAWN" .
                FILTER NOT EXISTS { $this comp:consentWithdrawnDate ?date }
            }
        """
    ] .
```

### Success Metrics
- ✅ 100% consent coverage for active customers
- ✅ 0 overdue DSR requests
- ✅ All data breaches logged within 2 hours
- ✅ 99%+ SHACL validation pass rate

---

## Use Case 2: Customer 360° View

### Business Context
**Stakeholder**: Marketing Director, Sales Team  
**Priority**: High  
**Business Goal**: Unified customer understanding

### Business Requirements
1. Single view of customer across all touchpoints
2. Track customer lifetime value and segment
3. Link transactions to customer profiles
4. Support both individual and business customers
5. Enable cross-sell and upsell opportunities

### Functional Requirements
```
FR-2.1: System SHALL maintain unique customer identifier
FR-2.2: System SHALL link all customer interactions and transactions
FR-2.3: System SHALL calculate lifetime value from transaction history
FR-2.4: System SHALL support customer segmentation (Premium, Standard, Enterprise)
FR-2.5: System SHALL validate email uniqueness across customers
```

### Ontology Implementation
**Ontology**: `customer_ontology.ttl`

**Key Classes**:
- `customer:Customer` - Base customer class
- `customer:IndividualCustomer` - B2C customers
- `customer:BusinessCustomer` - B2B customers
- `customer:Transaction` - Purchase/refund events
- `customer:CustomerSegment` - Grouping categories

**Class Hierarchy**:
```
foaf:Agent
  └── customer:Customer
        ├── customer:IndividualCustomer (extends foaf:Person)
        └── customer:BusinessCustomer (extends foaf:Organization)
```

### SPARQL Queries
```sparql
# Customer 360° view
PREFIX cus: <http://enterprise.org/ontology/customer#>

SELECT ?email ?status ?ltv ?segment
       (COUNT(?txn) AS ?transactionCount)
       (SUM(?amount) AS ?totalSpent)
WHERE {
    ?customer cus:email ?email ;
              cus:customerStatus ?status ;
              cus:lifetimeValue ?ltv ;
              cus:belongsToSegment ?seg ;
              cus:hasTransaction ?txn .
    ?seg cus:segmentName ?segment .
    ?txn cus:transactionAmount ?amount .
}
GROUP BY ?customer ?email ?status ?ltv ?segment
```

### Validation Rules (SHACL)
```turtle
# Email must be unique
:EmailUniquenessShape
    sh:targetClass cus:Customer ;
    sh:sparql [
        sh:message "Email address must be unique across all customers" ;
        sh:select """
            SELECT $this ?email WHERE {
                $this cus:email ?email .
                FILTER EXISTS {
                    ?other cus:email ?email .
                    FILTER (?other != $this)
                }
            }
        """
    ] .
```

---

## Use Case 3: Data Lineage Tracking

### Business Context
**Stakeholder**: Data Engineer, Data Governance Team  
**Priority**: High  
**Business Goal**: Impact analysis and data trustworthiness

### Business Requirements
1. Track data from source systems to reports
2. Identify upstream and downstream dependencies
3. Enable impact analysis for schema changes
4. Document transformation logic and rules
5. Support data quality root cause analysis

### Functional Requirements
```
FR-3.1: System SHALL record data asset provenance
FR-3.2: System SHALL track transformation steps in pipelines
FR-3.3: System SHALL support transitive dependency queries
FR-3.4: System SHALL link data quality issues to source
FR-3.5: System SHALL version data assets with checksums
```

### Ontology Implementation
**Ontology**: `lineage_ontology.ttl` (extends W3C PROV-O)

**Key Classes**:
- `lineage:DataAsset` - Any trackable data entity
- `lineage:DataTransformation` - ETL/transformation activity
- `lineage:DataPipeline` - Series of transformations
- `lineage:DataSource` - Origin system
- `lineage:DataVersion` - Versioned state

**Key Properties**:
- `lineage:derivedFrom` - Provenance link (transitive)
- `lineage:transformedBy` - Processing activity
- `lineage:usesInput` / `lineage:producesOutput` - Data flow
- `lineage:dependsOn` - Transitive dependency

### SPARQL Queries
```sparql
# Complete upstream lineage
PREFIX lin: <http://enterprise.org/ontology/lineage#>

SELECT ?asset ?sourceAsset ?transformation
WHERE {
    ?asset lin:assetName "customer_master_table" ;
           lin:derivedFrom+ ?sourceAsset .
    ?sourceAsset lin:assetName ?sourceName .
    OPTIONAL {
        ?asset lin:transformedBy ?transformation .
    }
}
```

### Impact Analysis Query
```sparql
# Find all downstream assets affected by changes
PREFIX lin: <http://enterprise.org/ontology/lineage#>

SELECT ?impactedAsset ?depth
WHERE {
    ?sourceAsset lin:assetName "raw_customer_data" .
    ?impactedAsset lin:dependsOn+ ?sourceAsset .
    # Calculate dependency depth for prioritization
}
```

---

## Use Case 4: Multi-Language Business Glossary

### Business Context
**Stakeholder**: International Teams (Oslo/Norway market)  
**Priority**: Medium  
**Business Goal**: Consistent terminology across markets

### Business Requirements
1. Define business terms in multiple languages
2. Support Norwegian (Bokmål) for local market
3. Map to external vocabularies (Wikidata, DBpedia)
4. Enable semantic search across languages
5. Maintain taxonomies for industries and domains

### Functional Requirements
```
FR-4.1: System SHALL support SKOS concept schemes
FR-4.2: System SHALL provide labels in English and Norwegian
FR-4.3: System SHALL define hierarchical relationships (broader/narrower)
FR-4.4: System SHALL link related concepts across domains
FR-4.5: System SHALL map to external authority sources
```

### Ontology Implementation
**Ontology**: `business_glossary.ttl` (SKOS-based)

**Concept Schemes**:
- Business Domain Taxonomy
- Data Quality Dimensions
- Compliance Framework Taxonomy
- Industry Classification (NACE codes for Norway)

**Example Concepts**:
```turtle
:DataGovernance a skos:Concept ;
    skos:prefLabel "Data Governance"@en ,
                   "Datastyrning"@no ;
    skos:definition "Overall management of data..."@en ,
                    "Den overordnede styringen av data..."@no ;
    skos:narrower :DataQuality , :DataStewardship ;
    skos:related :ComplianceManagement .
```

### Norwegian Market Specific Terms
```turtle
:Datatilsynet a skos:Concept ;
    skos:prefLabel "Datatilsynet"@no ,
                   "Norwegian Data Protection Authority"@en ;
    skos:definition "Norway's national data protection authority"@en ,
                    "Norges nasjonale tilsynsmyndighet for personvern"@no .
```

---

## Use Case 5: Real-Time Data Quality Monitoring

### Business Context
**Stakeholder**: Data Quality Team, System Administrators  
**Priority**: High  
**Business Goal**: Proactive data quality management

### Business Requirements
1. Validate data against business rules in real-time
2. Detect and alert on quality issues immediately
3. Track quality metrics over time
4. Prevent invalid data from entering the system
5. Generate data quality dashboards

### Functional Requirements
```
FR-5.1: System SHALL validate all customer data on ingestion
FR-5.2: System SHALL reject data failing critical validations
FR-5.3: System SHALL log all validation violations
FR-5.4: System SHALL track quality scores by dimension
FR-5.5: System SHALL provide validation reports in multiple formats
```

### Ontology Implementation
**Validation**: `customer_shapes.ttl`, `compliance_shapes.ttl` (SHACL)

**Quality Dimensions** (from business glossary):
- Accuracy - Correct representation
- Completeness - No missing required fields
- Consistency - Uniform across systems
- Timeliness - Up-to-date and fresh
- Validity - Conforms to formats/rules
- Uniqueness - No duplicates

### Validation Examples
```turtle
# Customer ID format validation
:IndividualCustomerShape
    sh:property [
        sh:path cus:customerId ;
        sh:pattern "^CUS-[0-9]{6}$" ;
        sh:message "Customer ID must be format CUS-XXXXXX" ;
    ] .

# Email format and uniqueness
:IndividualCustomerShape
    sh:property [
        sh:path cus:email ;
        sh:pattern "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" ;
    ] .
```

### Business Rule Example
```turtle
# Active customers must have recent activity
:ActiveCustomerActivityShape
    sh:sparql [
        sh:message "Active customers must have activity within 365 days" ;
        sh:select """
            SELECT $this WHERE {
                $this cus:customerStatus "ACTIVE" ;
                      cus:lastActivityDate ?lastActivity .
                FILTER ((NOW() - ?lastActivity) > 365)
            }
        """
    ] .
```

---

## Cross-Cutting Requirements

### Performance Requirements
- **NFR-1**: SPARQL queries SHALL complete in < 2 seconds for 90th percentile
- **NFR-2**: SHACL validation SHALL process 1000 triples/second minimum
- **NFR-3**: API endpoints SHALL respond in < 500ms average

### Security Requirements
- **NFR-4**: All customer PII SHALL be encrypted at rest and in transit
- **NFR-5**: Audit logs SHALL be immutable and tamper-proof
- **NFR-6**: Access control SHALL follow principle of least privilege

### Scalability Requirements
- **NFR-7**: System SHALL support 1M+ customer records
- **NFR-8**: System SHALL handle 10K+ transactions per day
- **NFR-9**: Knowledge graph SHALL scale to 100M+ triples

---

## Requirements Traceability Matrix

| Requirement | Use Case | Ontology | SHACL Shape | SPARQL Query | Test Coverage |
|-------------|----------|----------|-------------|--------------|---------------|
| FR-1.1 | UC-1 | compliance_ontology.ttl | ConsentShape | compliance_queries.sparql#Q1 | ✅ |
| FR-1.4 | UC-1 | compliance_ontology.ttl | - | compliance_queries.sparql#Q3 | ✅ |
| FR-2.1 | UC-2 | customer_ontology.ttl | IndividualCustomerShape | customer_queries.sparql#Q1 | ✅ |
| FR-2.5 | UC-2 | customer_ontology.ttl | EmailUniquenessShape | - | ✅ |
| FR-3.2 | UC-3 | lineage_ontology.ttl | - | lineage_queries.sparql#Q1 | ✅ |
| FR-4.2 | UC-4 | business_glossary.ttl | - | glossary_queries.sparql | ✅ |
| FR-5.1 | UC-5 | - | customer_shapes.ttl | - | ✅ |

---

## Stakeholder Sign-Off

This requirements document demonstrates:
- ✅ Requirements engineering methodology
- ✅ Stakeholder needs analysis
- ✅ Translation of business needs to semantic models
- ✅ Traceability from requirements to implementation
- ✅ Cross-functional collaboration approach

Demonstrates professional requirements engineering and semantic modeling expertise!
