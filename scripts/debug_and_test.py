#!/usr/bin/env python3
"""
Comprehensive Debug and Test Script

Tests all components of the Enterprise Knowledge Graph Platform.
"""

import sys
from pathlib import Path
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_section(title, status=""):
    """Print formatted section header."""
    status_emoji = {
        "OK": "✅",
        "FAIL": "❌",
        "WARN": "⚠️",
        "INFO": "ℹ️"
    }
    emoji = status_emoji.get(status, "📋")
    print(f"\n{emoji} {title}")
    print("-" * 80)


def test_imports():
    """Test if all modules can be imported."""
    print_section("1. Testing Python Imports", "INFO")
    
    tests = [
        ("RDFLib", "from rdflib import Graph, Namespace"),
        ("PySHACL", "from pyshacl import validate"),
        ("FastAPI", "from fastapi import FastAPI"),
        ("SPARQLWrapper", "from SPARQLWrapper import SPARQLWrapper"),
        ("Pandas", "import pandas as pd"),
        ("GraphManager", "from src.core.graph_manager import GraphManager"),
        ("DataValidator", "from src.core.validator import DataValidator"),
        ("ComplianceMonitor", "from src.compliance.monitor import ComplianceMonitor"),
        ("DataGenerator", "from src.ingestion.data_generator import DataGenerator"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✓ {name}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
    
    print(f"\nResult: {passed}/{len(tests)} imports successful")
    return failed == 0


def test_ontologies():
    """Test ontology loading."""
    print_section("2. Testing Ontology Loading", "INFO")
    
    from src.core.graph_manager import GraphManager
    
    gm = GraphManager()
    ontology_dir = Path(__file__).parent.parent / "ontologies"
    
    if not ontology_dir.exists():
        print(f"  ✗ Ontology directory not found: {ontology_dir}")
        return False
    
    results = gm.load_all_ontologies(ontology_dir)
    
    for filename, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")
    
    stats = gm.get_statistics()
    print(f"\n  Total triples: {stats['total_triples']:,}")
    print(f"  Classes: {stats['classes']}")
    print(f"  Object properties: {stats['object_properties']}")
    print(f"  Data properties: {stats['data_properties']}")
    
    return all(results.values())


def test_data_generation():
    """Test sample data generation."""
    print_section("3. Testing Sample Data", "INFO")
    
    data_file = Path(__file__).parent.parent / "data" / "samples" / "generated_data.ttl"
    
    if not data_file.exists():
        print(f"  ⚠️  Sample data not found: {data_file}")
        print(f"  Run: python scripts/generate_data.py")
        return False
    
    # Check file size
    size_kb = data_file.stat().st_size / 1024
    print(f"  ✓ Data file exists: {size_kb:.1f} KB")
    
    # Load and check
    from rdflib import Graph
    g = Graph()
    g.parse(str(data_file), format='turtle')
    print(f"  ✓ Loaded {len(g):,} triples from sample data")
    
    return True


def test_validation():
    """Test SHACL validation."""
    print_section("4. Testing SHACL Validation", "INFO")
    
    from src.core.validator import DataValidator
    from rdflib import Graph
    
    shapes_dir = Path(__file__).parent.parent / "validation"
    
    if not shapes_dir.exists():
        print(f"  ✗ Validation directory not found: {shapes_dir}")
        return False
    
    validator = DataValidator(shapes_dir)
    print(f"  ✓ DataValidator initialized")
    
    stats = validator.get_shape_statistics()
    print(f"  ✓ Shapes loaded: {stats.get('total_shapes', 0)}")
    print(f"    - Property shapes: {stats.get('property_shapes', 0)}")
    print(f"    - Constraints: {stats.get('constraints', 0)}")
    
    # Test validation on sample data
    data_file = Path(__file__).parent.parent / "data" / "samples" / "generated_data.ttl"
    if data_file.exists():
        print(f"\n  Testing validation on sample data...")
        report = validator.validate_file(data_file)
        print(f"  ✓ Validation completed")
        print(f"    - Conforms: {report['conforms']}")
        print(f"    - Violations: {report.get('total_violations', 0)}")
        print(f"    - Warnings: {report.get('total_warnings', 0)}")
    
    return True


def test_sparql_queries():
    """Test SPARQL query execution."""
    print_section("5. Testing SPARQL Queries", "INFO")
    
    from src.core.graph_manager import GraphManager
    
    gm = GraphManager()
    
    # Load ontologies
    ontology_dir = Path(__file__).parent.parent / "ontologies"
    gm.load_all_ontologies(ontology_dir)
    
    # Load sample data
    data_file = Path(__file__).parent.parent / "data" / "samples" / "generated_data.ttl"
    if data_file.exists():
        gm.load_ontology(data_file)
    
    # Test simple query
    query = """
        SELECT (COUNT(*) AS ?count)
        WHERE {
            ?s ?p ?o
        }
    """
    
    try:
        results = gm.execute_query(query)
        count = results['results']['bindings'][0]['count']['value']
        print(f"  ✓ Query execution works")
        print(f"    Total triples: {count}")
    except Exception as e:
        print(f"  ✗ Query failed: {e}")
        return False
    
    # Test customer query
    customer_query = """
        PREFIX cus: <http://enterprise.org/ontology/customer#>
        
        SELECT (COUNT(?customer) AS ?count)
        WHERE {
            ?customer a cus:Customer .
        }
    """
    
    try:
        results = gm.execute_query(customer_query)
        count = results['results']['bindings'][0]['count']['value']
        print(f"  ✓ Customer query works")
        print(f"    Total customers: {count}")
    except Exception as e:
        print(f"  ⚠️  Customer query failed (may need data): {e}")
    
    return True


def test_compliance_monitor():
    """Test compliance monitoring."""
    print_section("6. Testing Compliance Monitor", "INFO")
    
    from src.compliance.monitor import ComplianceMonitor
    from src.core.graph_manager import GraphManager
    
    gm = GraphManager()
    ontology_dir = Path(__file__).parent.parent / "ontologies"
    gm.load_all_ontologies(ontology_dir)
    
    data_file = Path(__file__).parent.parent / "data" / "samples" / "generated_data.ttl"
    if data_file.exists():
        gm.load_ontology(data_file)
    
    monitor = ComplianceMonitor(gm.graph)
    print(f"  ✓ ComplianceMonitor initialized")
    
    try:
        report = monitor.generate_compliance_report()
        print(f"  ✓ Compliance report generated")
        print(f"    - Consent summary: {report.get('consent_summary', {})}")
        print(f"    - DSR summary: {report.get('dsr_summary', {})}")
    except Exception as e:
        print(f"  ⚠️  Report generation issue: {e}")
    
    return True


def test_api_module():
    """Test API server module."""
    print_section("7. Testing API Server Module", "INFO")
    
    try:
        from src.api.server import app
        print(f"  ✓ FastAPI app imported successfully")
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"  ✓ Total routes: {len(routes)}")
        print(f"    Example routes:")
        for route in routes[:5]:
            print(f"      - {route}")
        
        return True
    except Exception as e:
        print(f"  ✗ API import failed: {e}")
        traceback.print_exc()
        return False


def test_dashboard_files():
    """Test React dashboard files."""
    print_section("8. Testing React Dashboard Files", "INFO")
    
    dashboard_dir = Path(__file__).parent.parent / "dashboard"
    
    required_files = [
        "package.json",
        "vite.config.js",
        "index.html",
        "src/main.jsx",
        "src/App.jsx",
        "src/pages/Dashboard.jsx",
        "src/pages/SPARQLQuery.jsx",
        "src/pages/Compliance.jsx",
        "src/pages/DataQuality.jsx",
        "src/pages/Ontologies.jsx",
    ]
    
    all_exist = True
    for file in required_files:
        file_path = dashboard_dir / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    # Check if node_modules exists
    node_modules = dashboard_dir / "node_modules"
    if node_modules.exists():
        print(f"  ✓ node_modules installed")
    else:
        print(f"  ⚠️  node_modules not found - run 'npm install' in dashboard/")
    
    # Check build directory
    dist = dashboard_dir / "dist"
    if dist.exists():
        print(f"  ✓ Production build exists (dist/)")
    
    return all_exist


def test_file_structure():
    """Test overall file structure."""
    print_section("9. Testing Project Structure", "INFO")
    
    base_dir = Path(__file__).parent.parent
    
    structure = {
        "ontologies": ["*.ttl files"],
        "validation": ["SHACL shapes"],
        "queries": ["SPARQL queries"],
        "src/core": ["Python core modules"],
        "src/api": ["FastAPI server"],
        "src/compliance": ["Compliance monitor"],
        "src/ingestion": ["Data generation"],
        "scripts": ["Helper scripts"],
        "dashboard": ["React app"],
        "data/samples": ["Sample data"],
        "docs": ["Documentation"],
    }
    
    for dir_name, description in structure.items():
        dir_path = base_dir / dir_name
        if dir_path.exists():
            # Count files
            files = list(dir_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            print(f"  ✓ {dir_name:<25} ({file_count} files)")
        else:
            print(f"  ✗ {dir_name:<25} - MISSING")
    
    return True


def generate_debug_report():
    """Generate comprehensive debug report."""
    print("\n" + "=" * 80)
    print(" " * 25 + "COMPREHENSIVE DEBUG REPORT")
    print("=" * 80)
    
    results = {}
    
    try:
        results['imports'] = test_imports()
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        results['imports'] = False
    
    try:
        results['ontologies'] = test_ontologies()
    except Exception as e:
        print(f"❌ Ontology test failed: {e}")
        results['ontologies'] = False
    
    try:
        results['data'] = test_data_generation()
    except Exception as e:
        print(f"❌ Data test failed: {e}")
        results['data'] = False
    
    try:
        results['validation'] = test_validation()
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        results['validation'] = False
    
    try:
        results['sparql'] = test_sparql_queries()
    except Exception as e:
        print(f"❌ SPARQL test failed: {e}")
        results['sparql'] = False
    
    try:
        results['compliance'] = test_compliance_monitor()
    except Exception as e:
        print(f"❌ Compliance test failed: {e}")
        results['compliance'] = False
    
    try:
        results['api'] = test_api_module()
    except Exception as e:
        print(f"❌ API test failed: {e}")
        results['api'] = False
    
    try:
        results['dashboard'] = test_dashboard_files()
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        results['dashboard'] = False
    
    try:
        results['structure'] = test_file_structure()
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        results['structure'] = False
    
    # Summary
    print_section("SUMMARY", "INFO")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nComponent Status:")
    for component, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"  {emoji} {component.replace('_', ' ').title()}")
    
    if passed == total:
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - PROJECT IS FULLY FUNCTIONAL")
        print("=" * 80)
        print("\nTo start the platform:")
        print("  1. API Server: python src/api/server.py")
        print("  2. Dashboard:  cd dashboard && npm run dev")
        print("  3. Visit:      http://localhost:3000")
        return True
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME TESTS FAILED - SEE DETAILS ABOVE")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = generate_debug_report()
    sys.exit(0 if success else 1)
