"""
W3C Standards-Compliant RDF Service

Provides comprehensive RDF operations following W3C standards:
- RDF 1.1 specification
- RDFS inference
- OWL reasoning
- SKOS vocabulary support
- Dublin Core metadata
"""

import logging
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS, FOAF
from rdflib.plugins.sparql import prepareQuery
import owlrl

logger = logging.getLogger(__name__)


class W3CCompliantRDFService:
    """
    W3C standards-compliant RDF service for enterprise knowledge graphs.
    
    Supports:
    - RDF 1.1 (Turtle, N-Triples, JSON-LD, RDF/XML)
    - RDFS reasoning
    - OWL 2 RL reasoning
    - SKOS for taxonomies
    - Dublin Core for metadata
    """
    
    def __init__(self, base_uri: str = "https://enterprise-kg.local/"):
        """
        Initialize RDF service with W3C standard namespaces.
        
        Args:
            base_uri: Base URI for the knowledge graph (configure in production)
        """
        self.graph = Graph()
        self.base_uri = base_uri
        
        # Define custom namespaces (keeping your existing ontologies)
        self.NS = Namespace(f"{base_uri}ontology/")
        self.CUST = Namespace(f"{base_uri}customer/")
        self.COMP = Namespace(f"{base_uri}company/")
        self.COMPL = Namespace(f"{base_uri}compliance/")
        self.DATA = Namespace(f"{base_uri}data/")
        
        # Bind all namespaces
        self._bind_namespaces()
        
        logger.info("Initialized W3C-compliant RDF service")
    
    def _bind_namespaces(self):
        """Bind W3C and custom namespaces to the graph."""
        # W3C Standard namespaces
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("skos", SKOS)
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("foaf", FOAF)
        
        # Custom namespaces (your existing ontologies)
        self.graph.bind("ns", self.NS)
        self.graph.bind("cust", self.CUST)
        self.graph.bind("comp", self.COMP)
        self.graph.bind("compl", self.COMPL)
        self.graph.bind("data", self.DATA)
    
    def create_ontology_metadata(
        self,
        ontology_uri: str,
        title: str,
        description: str,
        version: str,
        creators: List[str]
    ) -> Graph:
        """
        Create W3C-compliant ontology metadata using Dublin Core.
        
        Args:
            ontology_uri: URI of the ontology
            title: Ontology title
            description: Ontology description
            version: Version string
            creators: List of creator names
            
        Returns:
            Graph with metadata
        """
        ontology = URIRef(ontology_uri)
        
        # OWL Ontology declaration
        self.graph.add((ontology, RDF.type, OWL.Ontology))
        
        # Dublin Core metadata
        self.graph.add((ontology, DCTERMS.title, Literal(title, lang="en")))
        self.graph.add((ontology, DCTERMS.description, Literal(description, lang="en")))
        self.graph.add((ontology, OWL.versionInfo, Literal(version)))
        self.graph.add((ontology, DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Creators
        for creator in creators:
            self.graph.add((ontology, DCTERMS.creator, Literal(creator)))
        
        logger.info(f"Created ontology metadata for: {ontology_uri}")
        return self.graph
    
    def define_class(
        self,
        class_uri: str,
        label: str,
        comment: str,
        parent_class: Optional[str] = None
    ) -> URIRef:
        """
        Define an OWL class with RDFS annotations.
        
        Args:
            class_uri: URI of the class
            label: Human-readable label
            comment: Class description
            parent_class: Optional parent class URI
            
        Returns:
            URIRef of the created class
        """
        cls = URIRef(class_uri)
        
        # Class definition
        self.graph.add((cls, RDF.type, OWL.Class))
        self.graph.add((cls, RDFS.label, Literal(label, lang="en")))
        self.graph.add((cls, RDFS.comment, Literal(comment, lang="en")))
        
        # Inheritance
        if parent_class:
            self.graph.add((cls, RDFS.subClassOf, URIRef(parent_class)))
        
        return cls
    
    def define_property(
        self,
        property_uri: str,
        label: str,
        comment: str,
        property_type: str = "ObjectProperty",
        domain: Optional[str] = None,
        range_: Optional[str] = None
    ) -> URIRef:
        """
        Define an OWL property (Object or Datatype).
        
        Args:
            property_uri: URI of the property
            label: Human-readable label
            comment: Property description
            property_type: "ObjectProperty" or "DatatypeProperty"
            domain: Domain class URI
            range_: Range class or datatype URI
            
        Returns:
            URIRef of the created property
        """
        prop = URIRef(property_uri)
        
        # Property type
        if property_type == "ObjectProperty":
            self.graph.add((prop, RDF.type, OWL.ObjectProperty))
        else:
            self.graph.add((prop, RDF.type, OWL.DatatypeProperty))
        
        # Annotations
        self.graph.add((prop, RDFS.label, Literal(label, lang="en")))
        self.graph.add((prop, RDFS.comment, Literal(comment, lang="en")))
        
        # Domain and range
        if domain:
            self.graph.add((prop, RDFS.domain, URIRef(domain)))
        if range_:
            self.graph.add((prop, RDFS.range, URIRef(range_)))
        
        return prop
    
    def create_skos_concept_scheme(
        self,
        scheme_uri: str,
        title: str,
        description: str
    ) -> URIRef:
        """
        Create a SKOS Concept Scheme for taxonomies/vocabularies.
        
        Args:
            scheme_uri: URI of the concept scheme
            title: Scheme title
            description: Scheme description
            
        Returns:
            URIRef of the concept scheme
        """
        scheme = URIRef(scheme_uri)
        
        self.graph.add((scheme, RDF.type, SKOS.ConceptScheme))
        self.graph.add((scheme, SKOS.prefLabel, Literal(title, lang="en")))
        self.graph.add((scheme, SKOS.definition, Literal(description, lang="en")))
        self.graph.add((scheme, DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        logger.info(f"Created SKOS concept scheme: {scheme_uri}")
        return scheme
    
    def create_skos_concept(
        self,
        concept_uri: str,
        pref_label: str,
        definition: str,
        scheme_uri: str,
        broader: Optional[str] = None,
        alt_labels: Optional[List[str]] = None
    ) -> URIRef:
        """
        Create a SKOS Concept within a scheme.
        
        Args:
            concept_uri: URI of the concept
            pref_label: Preferred label
            definition: Concept definition
            scheme_uri: Parent concept scheme URI
            broader: Broader concept URI (for hierarchy)
            alt_labels: Alternative labels
            
        Returns:
            URIRef of the concept
        """
        concept = URIRef(concept_uri)
        scheme = URIRef(scheme_uri)
        
        self.graph.add((concept, RDF.type, SKOS.Concept))
        self.graph.add((concept, SKOS.prefLabel, Literal(pref_label, lang="en")))
        self.graph.add((concept, SKOS.definition, Literal(definition, lang="en")))
        self.graph.add((concept, SKOS.inScheme, scheme))
        
        # Hierarchical relationship
        if broader:
            self.graph.add((concept, SKOS.broader, URIRef(broader)))
        
        # Alternative labels
        if alt_labels:
            for alt in alt_labels:
                self.graph.add((concept, SKOS.altLabel, Literal(alt, lang="en")))
        
        return concept
    
    def apply_rdfs_reasoning(self) -> Graph:
        """
        Apply RDFS reasoning to infer implicit triples.
        
        Returns:
            Graph with inferred triples
        """
        original_size = len(self.graph)
        
        # Apply RDFS reasoning
        owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(self.graph)
        
        inferred_count = len(self.graph) - original_size
        logger.info(f"RDFS reasoning: inferred {inferred_count} triples")
        
        return self.graph
    
    def apply_owl_reasoning(self, profile: str = "OWL_RL") -> Graph:
        """
        Apply OWL 2 reasoning to infer implicit triples.
        
        Args:
            profile: "OWL_RL" or "OWL_RL_Extension"
            
        Returns:
            Graph with inferred triples
        """
        original_size = len(self.graph)
        
        # Apply OWL reasoning
        if profile == "OWL_RL":
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(self.graph)
        else:
            owlrl.DeductiveClosure(owlrl.OWLRL_Extension).expand(self.graph)
        
        inferred_count = len(self.graph) - original_size
        logger.info(f"OWL reasoning: inferred {inferred_count} triples")
        
        return self.graph
    
    def serialize(
        self,
        format: str = "turtle",
        destination: Optional[str] = None
    ) -> str:
        """
        Serialize graph to W3C-compliant format.
        
        Args:
            format: Output format (turtle, xml, nt, json-ld, n3)
            destination: Optional file path
            
        Returns:
            Serialized string
        """
        return self.graph.serialize(format=format, destination=destination)
    
    def parse(
        self,
        source: str,
        format: str = "turtle"
    ) -> Graph:
        """
        Parse RDF data into the graph.
        
        Args:
            source: File path or URL
            format: Input format
            
        Returns:
            Updated graph
        """
        self.graph.parse(source, format=format)
        logger.info(f"Parsed {len(self.graph)} triples from {source}")
        return self.graph
    
    def merge_graphs(self, *graphs: Graph) -> Graph:
        """
        Merge multiple graphs into this graph.
        
        Args:
            *graphs: Variable number of Graph objects
            
        Returns:
            Merged graph
        """
        for g in graphs:
            self.graph += g
        
        logger.info(f"Merged graphs, total triples: {len(self.graph)}")
        return self.graph
    
    def get_class_hierarchy(self) -> Dict[str, List[str]]:
        """
        Extract class hierarchy from the graph.
        
        Returns:
            Dictionary mapping parent classes to child classes
        """
        query = """
        SELECT ?parent ?child
        WHERE {
            ?child rdfs:subClassOf ?parent .
            FILTER(isURI(?parent) && isURI(?child))
        }
        """
        
        hierarchy = {}
        results = self.graph.query(query)
        
        for row in results:
            parent = str(row.parent)
            child = str(row.child)
            
            if parent not in hierarchy:
                hierarchy[parent] = []
            hierarchy[parent].append(child)
        
        return hierarchy
    
    def get_property_restrictions(self, class_uri: str) -> List[Dict[str, Any]]:
        """
        Get OWL property restrictions for a class.
        
        Args:
            class_uri: URI of the class
            
        Returns:
            List of restriction dictionaries
        """
        query = prepareQuery("""
        SELECT ?property ?restrictionType ?value
        WHERE {
            ?class rdfs:subClassOf ?restriction .
            ?restriction a owl:Restriction ;
                         owl:onProperty ?property .
            
            OPTIONAL { ?restriction owl:someValuesFrom ?value . BIND("someValuesFrom" AS ?restrictionType) }
            OPTIONAL { ?restriction owl:allValuesFrom ?value . BIND("allValuesFrom" AS ?restrictionType) }
            OPTIONAL { ?restriction owl:hasValue ?value . BIND("hasValue" AS ?restrictionType) }
            OPTIONAL { ?restriction owl:minCardinality ?value . BIND("minCardinality" AS ?restrictionType) }
            OPTIONAL { ?restriction owl:maxCardinality ?value . BIND("maxCardinality" AS ?restrictionType) }
            OPTIONAL { ?restriction owl:cardinality ?value . BIND("cardinality" AS ?restrictionType) }
        }
        """)
        
        results = self.graph.query(query, initBindings={'class': URIRef(class_uri)})
        
        restrictions = []
        for row in results:
            restrictions.append({
                'property': str(row.property),
                'type': str(row.restrictionType) if row.restrictionType else None,
                'value': str(row.value) if row.value else None
            })
        
        return restrictions
    
    def validate_w3c_compliance(self) -> Dict[str, Any]:
        """
        Validate graph for W3C standards compliance.
        
        Returns:
            Validation report
        """
        report = {
            'total_triples': len(self.graph),
            'namespaces': list(self.graph.namespaces()),
            'issues': [],
            'warnings': []
        }
        
        # Check for undefined prefixes
        for s, p, o in self.graph:
            for term in [s, p, o]:
                if isinstance(term, URIRef):
                    uri_str = str(term)
                    if '#' in uri_str or '/' in uri_str:
                        namespace = uri_str[:uri_str.rfind('#' if '#' in uri_str else '/') + 1]
                        if not any(ns == namespace for _, ns in self.graph.namespaces()):
                            if namespace not in [issue['namespace'] for issue in report['issues']]:
                                report['warnings'].append({
                                    'type': 'undefined_namespace',
                                    'namespace': namespace
                                })
        
        # Check for literals without language tags or datatypes
        for s, p, o in self.graph:
            if isinstance(o, Literal) and o.datatype is None and o.language is None:
                if len(str(o)) > 0:
                    report['warnings'].append({
                        'type': 'literal_without_type',
                        'subject': str(s),
                        'predicate': str(p),
                        'value': str(o)[:50]
                    })
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_triples': len(self.graph),
            'subjects': len(set(self.graph.subjects())),
            'predicates': len(set(self.graph.predicates())),
            'objects': len(set(self.graph.objects())),
            'classes': len(list(self.graph.subjects(RDF.type, OWL.Class))),
            'object_properties': len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))),
            'datatype_properties': len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))),
            'individuals': 0
        }
        
        # Count individuals (instances of classes)
        for cls in self.graph.subjects(RDF.type, OWL.Class):
            stats['individuals'] += len(list(self.graph.subjects(RDF.type, cls)))
        
        return stats
