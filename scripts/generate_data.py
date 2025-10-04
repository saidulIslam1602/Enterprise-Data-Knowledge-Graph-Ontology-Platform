#!/usr/bin/env python3
"""
Generate Sample Data Script

Generates realistic customer, company, and compliance data using real data sources.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.data_generator import DataGenerator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Generate all sample data."""
    print("=" * 80)
    print("ENTERPRISE KNOWLEDGE GRAPH DATA GENERATION")
    print("=" * 80)
    print()
    
    # Initialize generator with seed for reproducibility
    generator = DataGenerator(locale='en_US', seed=42)
    
    # Generate customers
    print("📊 Generating customer data...")
    graph = generator.generate_customers(count=150)
    print(f"   ✓ Generated 150 individual customers")
    
    # Generate business customers
    print("🏢 Generating business customer data...")
    graph = generator.generate_business_customers(count=30, graph=graph)
    print(f"   ✓ Generated 30 business customers")
    
    # Generate compliance data
    print("📋 Generating GDPR compliance data...")
    graph = generator.generate_compliance_data(graph)
    print(f"   ✓ Generated consent records and compliance data")
    
    # Fetch real companies
    print("🌐 Fetching real company data from OpenCorporates API...")
    try:
        companies = generator.fetch_real_companies(count=25, jurisdiction="us")
        graph = generator.companies_to_rdf(companies, graph)
        print(f"   ✓ Fetched and converted 25 real companies")
    except Exception as e:
        logger.warning(f"Could not fetch real companies: {e}")
        print(f"   ⚠ Using generated company data instead")
    
    # Save to file
    output_dir = Path(__file__).parent.parent / "data" / "samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "generated_data.ttl"
    
    print(f"\n💾 Saving data to file...")
    graph.serialize(destination=str(output_file), format='turtle')
    
    print()
    print("=" * 80)
    print("✅ DATA GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total triples generated: {len(graph):,}")
    print(f"Output file: {output_file}")
    print()
    print("Next steps:")
    print("  1. Load ontologies: python scripts/load_ontologies.py")
    print("  2. Validate data: python scripts/demo.py")
    print("  3. Start API server: python src/api/server.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
