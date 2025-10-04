#!/usr/bin/env python3
"""
Platform Demonstration Script

Demonstrates all major features of the Enterprise Knowledge Graph Platform.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.graph_manager import GraphManager
from src.core.validator import DataValidator
from src.compliance.monitor import ComplianceMonitor
from rdflib import Graph
import json


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_ontology_loading():
    """Demonstrate ontology loading."""
    print_section("1. ONTOLOGY LOADING")
    
    gm = GraphManager()
    ontology_dir = Path(__file__).parent.parent / "ontologies"
    
    print("Loading ontologies from:", ontology_dir)
    results = gm.load_all_ontologies(ontology_dir)
    
    for filename, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")
    
    print(f"\nTotal triples loaded: {len(gm.graph):,}")
    
    return gm


def demo_statistics(gm: GraphManager):
    """Demonstrate graph statistics."""
    print_section("2. KNOWLEDGE GRAPH STATISTICS")
    
    stats = gm.get_statistics()
    
    print("Graph Statistics:")
    for key, value in stats.items():
        print(f"  • {key.replace('_', ' ').title()}: {value:,}")


def demo_sparql_queries(gm: GraphManager):
    """Demonstrate SPARQL querying."""
    print_section("3. SPARQL QUERY EXAMPLES")
    
    # Load sample data
    sample_data = Path(__file__).parent.parent / "data" / "samples" / "generated_data.ttl"
    if sample_data.exists():
        print(f"Loading sample data from: {sample_data}")
        gm.load_ontology(sample_data)
        print(f"Total triples after loading data: {len(gm.graph):,}\n")
    else:
        print("⚠ Sample data not found. Run 'python scripts/generate_data.py' first.\n")
        return gm
    
    # Query 1: Count customers by status
    print("Query 1: Customer Status Distribution")
    print("-" * 80)
    query1 = """
        PREFIX cus: <http://enterprise.org/ontology/customer#>
        
        SELECT ?status (COUNT(?customer) AS ?count)
        WHERE {
            ?customer a cus:Customer ;
                      cus:customerStatus ?status .
        }
        GROUP BY ?status
        ORDER BY DESC(?count)
    """
    
    results1 = gm.execute_query(query1)
    for row in results1.get('results', {}).get('bindings', []):
        status = row['status']['value']
        count = row['count']['value']
        print(f"  • {status}: {count}")
    
    # Query 2: High-value customers
    print("\nQuery 2: Top 5 High-Value Customers")
    print("-" * 80)
    query2 = """
        PREFIX cus: <http://enterprise.org/ontology/customer#>
        
        SELECT ?email ?lifetimeValue
        WHERE {
            ?customer a cus:Customer ;
                      cus:email ?email ;
                      cus:lifetimeValue ?lifetimeValue .
        }
        ORDER BY DESC(?lifetimeValue)
        LIMIT 5
    """
    
    results2 = gm.execute_query(query2)
    for i, row in enumerate(results2.get('results', {}).get('bindings', []), 1):
        email = row['email']['value']
        ltv = float(row['lifetimeValue']['value'])
        print(f"  {i}. {email}: ${ltv:,.2f}")
    
    # Query 3: Consent status
    print("\nQuery 3: Consent Status Distribution")
    print("-" * 80)
    query3 = """
        PREFIX comp: <http://enterprise.org/ontology/compliance#>
        
        SELECT ?status (COUNT(?consent) AS ?count)
        WHERE {
            ?consent a comp:Consent ;
                     comp:consentStatus ?status .
        }
        GROUP BY ?status
        ORDER BY DESC(?count)
    """
    
    results3 = gm.execute_query(query3)
    for row in results3.get('results', {}).get('bindings', []):
        status = row['status']['value']
        count = row['count']['value']
        print(f"  • {status}: {count}")
    
    return gm


def demo_data_validation(gm: GraphManager):
    """Demonstrate SHACL validation."""
    print_section("4. DATA QUALITY VALIDATION (SHACL)")
    
    shapes_dir = Path(__file__).parent.parent / "validation"
    validator = DataValidator(shapes_dir)
    
    print(f"Loaded SHACL shapes from: {shapes_dir}")
    shape_stats = validator.get_shape_statistics()
    print(f"Total shapes: {shape_stats['total_shapes']}")
    print(f"Property shapes: {shape_stats['property_shapes']}")
    print(f"Constraints: {shape_stats['constraints']}\n")
    
    print("Validating data against SHACL shapes...")
    report = validator.validate_graph(gm.graph, inference='rdfs')
    
    print(f"\nValidation Result: {'✓ PASSED' if report['conforms'] else '✗ FAILED'}")
    print(f"Total violations: {report.get('total_violations', 0)}")
    print(f"Total warnings: {report.get('total_warnings', 0)}")
    
    if report.get('violations'):
        print("\nTop 5 Violations:")
        for i, violation in enumerate(report['violations'][:5], 1):
            print(f"\n  {i}. {violation['message']}")
            print(f"     Focus: {violation['focus_node']}")
            if violation.get('path'):
                print(f"     Property: {violation['path']}")


def demo_compliance_monitoring(gm: GraphManager):
    """Demonstrate compliance monitoring."""
    print_section("5. GDPR COMPLIANCE MONITORING")
    
    monitor = ComplianceMonitor(gm.graph)
    
    # Generate compliance report
    print("Generating compliance report...\n")
    report = monitor.generate_compliance_report()
    
    print("Consent Summary:")
    for status, count in report['consent_summary'].items():
        print(f"  • {status}: {count}")
    
    print("\nData Subject Rights Requests:")
    for status, count in report['dsr_summary'].items():
        print(f"  • {status}: {count}")
    
    # Check for expiring consents
    print("\nExpiring Consents (next 30 days):")
    expiring = monitor.get_expiring_consents(days_ahead=30)
    if expiring:
        for consent in expiring[:5]:
            print(f"  • {consent['consent_id']}: {consent['days_until_expiry']} days until expiry")
            print(f"    Purpose: {consent['purpose']}")
    else:
        print("  ✓ No consents expiring in the next 30 days")


def demo_api_endpoints():
    """Show available API endpoints."""
    print_section("6. REST API ENDPOINTS")
    
    print("The platform provides a comprehensive REST API. Start the server with:")
    print("  $ python src/api/server.py\n")
    
    print("Available endpoints:")
    endpoints = [
        ("GET", "/api/v1/statistics", "Get knowledge graph statistics"),
        ("POST", "/api/v1/sparql/query", "Execute SPARQL queries"),
        ("GET", "/api/v1/ontology/classes", "List all OWL classes"),
        ("POST", "/api/v1/validate", "Validate RDF data against SHACL"),
        ("GET", "/api/v1/compliance/report", "Generate compliance report"),
        ("GET", "/api/v1/compliance/gdpr/{id}", "Check GDPR compliance"),
        ("GET", "/api/v1/compliance/dsr/overdue", "Get overdue DSR requests"),
        ("GET", "/docs", "Interactive API documentation (Swagger UI)"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"  • {method:6} {endpoint:35} - {description}")


def main():
    """Run complete demonstration."""
    print("\n" + "=" * 80)
    print(" " * 20 + "ENTERPRISE KNOWLEDGE GRAPH PLATFORM")
    print(" " * 25 + "DEMONSTRATION SCRIPT")
    print("=" * 80)
    
    try:
        # Demo 1: Load ontologies
        gm = demo_ontology_loading()
        
        # Demo 2: Statistics
        demo_statistics(gm)
        
        # Demo 3: SPARQL queries
        gm = demo_sparql_queries(gm)
        
        # Demo 4: Validation
        demo_data_validation(gm)
        
        # Demo 5: Compliance monitoring
        demo_compliance_monitoring(gm)
        
        # Demo 6: API endpoints
        demo_api_endpoints()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nThis platform demonstrates:")
        print("  ✓ Ontology engineering (OWL/RDF)")
        print("  ✓ SPARQL query development")
        print("  ✓ SHACL data validation")
        print("  ✓ GDPR compliance monitoring")
        print("  ✓ Data lineage tracking")
        print("  ✓ REST API development")
        print("\nPerfect demonstration of semantic web and ontology engineering expertise!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
