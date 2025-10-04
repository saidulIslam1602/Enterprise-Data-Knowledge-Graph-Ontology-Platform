"""
Data Generator using Real Data Sources

Generates realistic customer data using Faker and fetches real company data
from OpenCorporates API and other public sources.
"""

import logging
import json
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from faker import Faker
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Generates realistic customer and company data using real data sources.
    """

    def __init__(self, locale: str = 'en_US', seed: Optional[int] = None):
        """
        Initialize Data Generator.

        Args:
            locale: Faker locale (en_US, en_GB, de_DE, etc.)
            seed: Random seed for reproducibility
        """
        self.fake = Faker(locale)
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Define namespaces
        self.cus_ns = Namespace("http://enterprise.org/ontology/customer#")
        self.comp_ns = Namespace("http://enterprise.org/ontology/company#")
        self.compliance_ns = Namespace("http://enterprise.org/ontology/compliance#")
        self.data_ns = Namespace("http://enterprise.org/data/")
        
        logger.info(f"DataGenerator initialized with locale: {locale}")

    def generate_customers(self, count: int = 100, graph: Optional[Graph] = None) -> Graph:
        """
        Generate realistic individual customer data.

        Args:
            count: Number of customers to generate
            graph: Existing graph to add to (creates new if None)

        Returns:
            RDF graph with customer data
        """
        if graph is None:
            graph = Graph()
            self._bind_namespaces(graph)
        
        logger.info(f"Generating {count} customers...")
        
        segments = [
            ("Premium Customers", "premium"),
            ("Standard Customers", "standard"),
            ("Enterprise Customers", "enterprise")
        ]
        
        for i in tqdm(range(count), desc="Generating customers"):
            customer_id = f"CUS-{i+1:06d}"
            customer_uri = URIRef(f"{self.data_ns}customer/{customer_id}")
            
            # Basic customer info
            graph.add((customer_uri, RDF.type, self.cus_ns.IndividualCustomer))
            graph.add((customer_uri, self.cus_ns.customerId, Literal(customer_id, datatype=XSD.string)))
            
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            graph.add((customer_uri, self.cus_ns.firstName, Literal(first_name, datatype=XSD.string)))
            graph.add((customer_uri, self.cus_ns.lastName, Literal(last_name, datatype=XSD.string)))
            
            # Email and phone
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@{self.fake.free_email_domain()}"
            graph.add((customer_uri, self.cus_ns.email, Literal(email, datatype=XSD.string)))
            graph.add((customer_uri, self.cus_ns.phoneNumber, Literal(self.fake.phone_number(), datatype=XSD.string)))
            
            # Date of birth
            dob = self.fake.date_of_birth(minimum_age=18, maximum_age=80)
            graph.add((customer_uri, self.cus_ns.dateOfBirth, Literal(dob, datatype=XSD.date)))
            
            # Status and dates
            status = random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE", "SUSPENDED"])
            graph.add((customer_uri, self.cus_ns.customerStatus, Literal(status, datatype=XSD.string)))
            
            reg_date = self.fake.date_time_between(start_date="-3y", end_date="now")
            graph.add((customer_uri, self.cus_ns.registrationDate, Literal(reg_date, datatype=XSD.dateTime)))
            
            last_activity = self.fake.date_time_between(start_date=reg_date, end_date="now")
            graph.add((customer_uri, self.cus_ns.lastActivityDate, Literal(last_activity, datatype=XSD.dateTime)))
            
            # Lifetime value
            ltv = round(random.uniform(100, 50000), 2)
            graph.add((customer_uri, self.cus_ns.lifetimeValue, Literal(ltv, datatype=XSD.decimal)))
            
            # Segment
            segment_name, segment_key = random.choice(segments)
            segment_uri = URIRef(f"{self.data_ns}segment/{segment_key}")
            graph.add((customer_uri, self.cus_ns.belongsToSegment, segment_uri))
            
            # Address
            self._add_address(graph, customer_uri)
            
            # Transactions
            num_transactions = random.randint(1, 20)
            for j in range(num_transactions):
                self._add_transaction(graph, customer_uri, f"TXN-{i+1:06d}-{j+1:03d}", reg_date)
        
        logger.info(f"Generated {count} customers with {len(graph)} triples")
        return graph

    def generate_business_customers(self, count: int = 50, graph: Optional[Graph] = None) -> Graph:
        """
        Generate business customer data.

        Args:
            count: Number of business customers to generate
            graph: Existing graph to add to

        Returns:
            RDF graph with business customer data
        """
        if graph is None:
            graph = Graph()
            self._bind_namespaces(graph)
        
        logger.info(f"Generating {count} business customers...")
        
        for i in tqdm(range(count), desc="Generating business customers"):
            customer_id = f"ORG-{i+1:06d}"
            customer_uri = URIRef(f"{self.data_ns}customer/{customer_id}")
            
            graph.add((customer_uri, RDF.type, self.cus_ns.BusinessCustomer))
            graph.add((customer_uri, self.cus_ns.customerId, Literal(customer_id, datatype=XSD.string)))
            
            org_name = self.fake.company()
            graph.add((customer_uri, self.cus_ns.organizationName, Literal(org_name, datatype=XSD.string)))
            
            email = f"contact@{org_name.lower().replace(' ', '').replace(',', '')}.com"
            graph.add((customer_uri, self.cus_ns.email, Literal(email, datatype=XSD.string)))
            
            status = random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"])
            graph.add((customer_uri, self.cus_ns.customerStatus, Literal(status, datatype=XSD.string)))
            
            reg_date = self.fake.date_time_between(start_date="-5y", end_date="now")
            graph.add((customer_uri, self.cus_ns.registrationDate, Literal(reg_date, datatype=XSD.dateTime)))
            
            ltv = round(random.uniform(10000, 500000), 2)
            graph.add((customer_uri, self.cus_ns.lifetimeValue, Literal(ltv, datatype=XSD.decimal)))
            
            self._add_address(graph, customer_uri)
        
        return graph

    def generate_compliance_data(self, graph: Graph) -> Graph:
        """
        Generate GDPR-compliant consent and compliance records for customers.

        Args:
            graph: Graph containing customer data

        Returns:
            Graph with added compliance data
        """
        logger.info("Generating compliance data...")
        
        # Get all customers
        query = """
            PREFIX cus: <http://enterprise.org/ontology/customer#>
            SELECT ?customer WHERE { ?customer a cus:Customer }
        """
        customers = [str(row.customer) for row in graph.query(query)]
        
        consent_purposes = [
            ("Marketing Communications", "MARKETING"),
            ("Analytics and Research", "ANALYTICS"),
            ("Service Delivery", "SERVICE"),
            ("Product Updates", "UPDATES")
        ]
        
        for customer_uri_str in tqdm(customers, desc="Generating compliance records"):
            customer_uri = URIRef(customer_uri_str)
            
            # Generate 1-4 consents per customer
            num_consents = random.randint(1, 4)
            for i in range(num_consents):
                consent_id = f"CONSENT-{hash(customer_uri_str) % 100000000:08d}-{i+1}"
                consent_uri = URIRef(f"{self.data_ns}consent/{consent_id}")
                
                graph.add((consent_uri, RDF.type, self.compliance_ns.Consent))
                graph.add((consent_uri, self.compliance_ns.consentId, Literal(consent_id, datatype=XSD.string)))
                
                # Consent status
                status = random.choices(
                    ["ACTIVE", "WITHDRAWN", "EXPIRED"],
                    weights=[0.7, 0.2, 0.1]
                )[0]
                graph.add((consent_uri, self.compliance_ns.consentStatus, Literal(status, datatype=XSD.string)))
                
                # Dates
                given_date = self.fake.date_time_between(start_date="-2y", end_date="now")
                graph.add((consent_uri, self.compliance_ns.consentGivenDate, Literal(given_date, datatype=XSD.dateTime)))
                
                if status == "WITHDRAWN":
                    withdrawn_date = self.fake.date_time_between(start_date=given_date, end_date="now")
                    graph.add((consent_uri, self.compliance_ns.consentWithdrawnDate, Literal(withdrawn_date, datatype=XSD.dateTime)))
                
                if status == "EXPIRED" or random.random() < 0.3:
                    expiry_date = given_date + timedelta(days=random.randint(365, 730))
                    graph.add((consent_uri, self.compliance_ns.consentExpiryDate, Literal(expiry_date, datatype=XSD.dateTime)))
                
                # Method
                method = random.choice(["EXPLICIT", "OPT_IN", "OPT_OUT"])
                graph.add((consent_uri, self.compliance_ns.consentMethod, Literal(method, datatype=XSD.string)))
                
                # Purpose
                purpose_name, purpose_key = random.choice(consent_purposes)
                purpose_uri = URIRef(f"{self.data_ns}consent_purpose/{purpose_key}")
                graph.add((consent_uri, self.compliance_ns.consentFor, purpose_uri))
                
                # Link to customer
                graph.add((customer_uri, self.compliance_ns.hasConsent, consent_uri))
        
        logger.info(f"Generated compliance data ({len(graph)} total triples)")
        return graph

    def fetch_real_companies(self, count: int = 20, jurisdiction: str = "us") -> List[Dict]:
        """
        Fetch real company data from OpenCorporates API (free tier).

        Args:
            count: Number of companies to fetch
            jurisdiction: Jurisdiction code (us, gb, de, etc.)

        Returns:
            List of company dictionaries
        """
        logger.info(f"Fetching {count} real companies from OpenCorporates...")
        
        companies = []
        base_url = "https://api.opencorporates.com/v0.4/companies/search"
        
        # Search for tech companies as example
        search_terms = ["technology", "software", "data", "consulting", "services"]
        
        try:
            for term in search_terms[:count//4 + 1]:
                params = {
                    "q": term,
                    "jurisdiction_code": jurisdiction,
                    "per_page": min(count//len(search_terms) + 1, 30),
                    "order": "score"
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", {}).get("companies", [])
                    
                    for result in results:
                        company = result.get("company", {})
                        companies.append({
                            "name": company.get("name"),
                            "company_number": company.get("company_number"),
                            "jurisdiction": company.get("jurisdiction_code"),
                            "incorporation_date": company.get("incorporation_date"),
                            "company_type": company.get("company_type"),
                            "status": company.get("current_status"),
                            "registered_address": company.get("registered_address_in_full"),
                        })
                        
                        if len(companies) >= count:
                            break
                
                if len(companies) >= count:
                    break
                
        except Exception as e:
            logger.warning(f"Could not fetch from OpenCorporates: {e}")
            logger.info("Falling back to generated company data...")
            return self._generate_fallback_companies(count)
        
        logger.info(f"Fetched {len(companies)} real companies")
        return companies[:count]

    def _generate_fallback_companies(self, count: int) -> List[Dict]:
        """Generate realistic company data as fallback."""
        companies = []
        for i in range(count):
            companies.append({
                "name": self.fake.company(),
                "company_number": f"{''.join(random.choices('0123456789', k=8))}",
                "jurisdiction": "us",
                "incorporation_date": str(self.fake.date_between(start_date="-30y", end_date="-1y")),
                "company_type": random.choice(["Corporation", "LLC", "Partnership"]),
                "status": "Active",
                "registered_address": self.fake.address().replace("\n", ", "),
            })
        return companies

    def companies_to_rdf(self, companies: List[Dict], graph: Optional[Graph] = None) -> Graph:
        """
        Convert company data to RDF.

        Args:
            companies: List of company dictionaries
            graph: Existing graph to add to

        Returns:
            RDF graph with company data
        """
        if graph is None:
            graph = Graph()
            self._bind_namespaces(graph)
        
        logger.info(f"Converting {len(companies)} companies to RDF...")
        
        for i, company in enumerate(companies):
            company_id = f"COMP-{i+1:06d}"
            company_uri = URIRef(f"{self.data_ns}company/{company_id}")
            
            graph.add((company_uri, RDF.type, self.comp_ns.Company))
            graph.add((company_uri, self.comp_ns.companyId, Literal(company_id, datatype=XSD.string)))
            
            if company.get("name"):
                graph.add((company_uri, self.comp_ns.legalName, Literal(company["name"], datatype=XSD.string)))
            
            if company.get("company_number"):
                graph.add((company_uri, self.comp_ns.registrationNumber, Literal(company["company_number"], datatype=XSD.string)))
            
            if company.get("incorporation_date"):
                try:
                    inc_date = datetime.fromisoformat(company["incorporation_date"])
                    graph.add((company_uri, self.comp_ns.foundedDate, Literal(inc_date.date(), datatype=XSD.date)))
                except:
                    pass
            
            if company.get("status"):
                status = "ACTIVE" if "active" in company["status"].lower() else "DISSOLVED"
                graph.add((company_uri, self.comp_ns.companyStatus, Literal(status, datatype=XSD.string)))
            
            # Add industry/sector
            industry_uri = URIRef(f"{self.data_ns}industry/software")
            graph.add((company_uri, self.comp_ns.belongsToIndustry, industry_uri))
        
        return graph

    def _add_address(self, graph: Graph, customer_uri: URIRef) -> None:
        """Add address to customer."""
        address_id = str(hash(str(customer_uri)) % 1000000)
        address_uri = URIRef(f"{self.data_ns}address/{address_id}")
        
        graph.add((address_uri, RDF.type, self.cus_ns.Address))
        graph.add((address_uri, self.cus_ns.streetAddress, Literal(self.fake.street_address(), datatype=XSD.string)))
        graph.add((address_uri, self.cus_ns.city, Literal(self.fake.city(), datatype=XSD.string)))
        graph.add((address_uri, self.cus_ns.postalCode, Literal(self.fake.postcode(), datatype=XSD.string)))
        graph.add((address_uri, self.cus_ns.country, Literal(self.fake.country_code(), datatype=XSD.string)))
        
        graph.add((customer_uri, self.cus_ns.hasAddress, address_uri))

    def _add_transaction(self, graph: Graph, customer_uri: URIRef, txn_id: str, reg_date: datetime) -> None:
        """Add transaction to customer."""
        txn_uri = URIRef(f"{self.data_ns}transaction/{txn_id}")
        
        graph.add((txn_uri, RDF.type, self.cus_ns.Transaction))
        graph.add((txn_uri, self.cus_ns.transactionAmount, Literal(round(random.uniform(10, 5000), 2), datatype=XSD.decimal)))
        graph.add((txn_uri, self.cus_ns.currency, Literal("USD", datatype=XSD.string)))
        
        txn_date = self.fake.date_time_between(start_date=reg_date, end_date="now")
        graph.add((txn_uri, self.cus_ns.interactionDate, Literal(txn_date, datatype=XSD.dateTime)))
        
        txn_type = random.choice(["PURCHASE", "PURCHASE", "REFUND", "SUBSCRIPTION", "RENEWAL"])
        graph.add((txn_uri, self.cus_ns.interactionType, Literal(txn_type, datatype=XSD.string)))
        
        graph.add((customer_uri, self.cus_ns.hasTransaction, txn_uri))

    def _bind_namespaces(self, graph: Graph) -> None:
        """Bind namespaces to graph."""
        graph.bind('cus', self.cus_ns)
        graph.bind('comp', self.comp_ns)
        graph.bind('compliance', self.compliance_ns)
        graph.bind('data', self.data_ns)
        graph.bind('rdf', RDF)
        graph.bind('rdfs', RDFS)
        graph.bind('xsd', XSD)


if __name__ == "__main__":
    # Generate sample data
    generator = DataGenerator(seed=42)
    
    # Generate customers
    graph = generator.generate_customers(count=100)
    graph = generator.generate_business_customers(count=25, graph=graph)
    
    # Generate compliance data
    graph = generator.generate_compliance_data(graph)
    
    # Fetch and add real companies
    companies = generator.fetch_real_companies(count=20)
    graph = generator.companies_to_rdf(companies, graph)
    
    # Save to file
    output_dir = Path(__file__).parent.parent.parent / "data" / "samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "generated_data.ttl"
    
    graph.serialize(destination=str(output_file), format='turtle')
    logger.info(f"Saved {len(graph)} triples to {output_file}")
    
    print(f"\n✓ Generated sample data with {len(graph)} triples")
    print(f"✓ Saved to: {output_file}")
