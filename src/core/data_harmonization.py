"""
Data Harmonization Service

Harmonizes data from multiple heterogeneous sources into a unified knowledge graph.
Handles schema mapping, entity resolution, and data quality checks.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataHarmonizationService:
    """
    Service for harmonizing data from multiple sources.
    
    Features:
    - Schema mapping and transformation
    - Entity resolution and deduplication
    - Data quality validation
    - Provenance tracking
    - Conflict resolution
    - Multi-source integration
    """
    
    def __init__(self, target_namespace: str):
        """
        Initialize harmonization service.
        
        Args:
            target_namespace: Target namespace for harmonized data
        """
        self.target_ns = Namespace(target_namespace)
        self.mapping_rules: Dict[str, Dict[str, str]] = {}
        self.entity_cache: Dict[str, URIRef] = {}
        self.harmonized_graph = Graph()
        
        # Provenance namespace
        self.PROV = Namespace("http://www.w3.org/ns/prov#")
        
        self._setup_namespaces()
        
        logger.info("Initialized Data Harmonization Service")
    
    def _setup_namespaces(self):
        """Setup standard and custom namespaces."""
        self.harmonized_graph.bind("target", self.target_ns)
        self.harmonized_graph.bind("prov", self.PROV)
        self.harmonized_graph.bind("owl", OWL)
        self.harmonized_graph.bind("skos", SKOS)
    
    def add_mapping_rule(
        self,
        source_ontology: str,
        source_class: str,
        target_class: str,
        property_mappings: Dict[str, str]
    ):
        """
        Add schema mapping rule for harmonization.
        
        Args:
            source_ontology: Source ontology identifier
            source_class: Source class URI
            target_class: Target class URI
            property_mappings: Dict mapping source properties to target properties
        """
        rule_id = f"{source_ontology}_{source_class}"
        
        self.mapping_rules[rule_id] = {
            'source_ontology': source_ontology,
            'source_class': source_class,
            'target_class': target_class,
            'property_mappings': property_mappings
        }
        
        logger.info(f"Added mapping rule: {source_class} -> {target_class}")
    
    def harmonize_graph(
        self,
        source_graph: Graph,
        source_ontology_id: str,
        provenance_info: Optional[Dict[str, str]] = None
    ) -> Graph:
        """
        Harmonize a source graph into the target schema.
        
        Args:
            source_graph: Source RDF graph
            source_ontology_id: Identifier for source ontology
            provenance_info: Optional provenance metadata
            
        Returns:
            Harmonized graph
        """
        logger.info(f"Harmonizing graph from: {source_ontology_id}")
        start_time = datetime.now()
        
        harmonized_count = 0
        
        # Find all instances in source graph
        for source_class_uri in set(source_graph.objects(predicate=RDF.type)):
            if not isinstance(source_class_uri, URIRef):
                continue
            
            # Check if we have a mapping rule
            rule_id = f"{source_ontology_id}_{source_class_uri}"
            
            if rule_id in self.mapping_rules:
                rule = self.mapping_rules[rule_id]
                
                # Get all instances of this class
                instances = list(source_graph.subjects(RDF.type, source_class_uri))
                
                for instance in instances:
                    self._harmonize_instance(
                        source_graph,
                        instance,
                        rule,
                        provenance_info
                    )
                    harmonized_count += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"Harmonized {harmonized_count} instances in {duration:.2f}s"
        )
        
        return self.harmonized_graph
    
    def _harmonize_instance(
        self,
        source_graph: Graph,
        instance: URIRef,
        rule: Dict[str, Any],
        provenance_info: Optional[Dict[str, str]]
    ):
        """Harmonize a single instance according to mapping rule."""
        # Create or resolve target entity
        target_entity = self._resolve_entity(source_graph, instance, rule)
        
        # Map class
        target_class = URIRef(rule['target_class'])
        self.harmonized_graph.add((target_entity, RDF.type, target_class))
        
        # Map properties
        for source_prop, target_prop in rule['property_mappings'].items():
            source_prop_uri = URIRef(source_prop)
            target_prop_uri = URIRef(target_prop)
            
            # Copy all values for this property
            for obj in source_graph.objects(instance, source_prop_uri):
                # Transform value if needed
                transformed_value = self._transform_value(obj, source_prop, target_prop)
                self.harmonized_graph.add((target_entity, target_prop_uri, transformed_value))
        
        # Add provenance
        if provenance_info:
            self._add_provenance(target_entity, instance, provenance_info)
    
    def _resolve_entity(
        self,
        source_graph: Graph,
        instance: URIRef,
        rule: Dict[str, Any]
    ) -> URIRef:
        """
        Resolve entity identity (handle duplicates and create stable URIs).
        
        Args:
            source_graph: Source graph
            instance: Source instance URI
            rule: Mapping rule
            
        Returns:
            Target entity URI
        """
        # Create fingerprint for entity matching
        fingerprint = self._create_entity_fingerprint(source_graph, instance, rule)
        
        if fingerprint in self.entity_cache:
            # Entity already exists (duplicate)
            logger.debug(f"Entity match found: {instance}")
            return self.entity_cache[fingerprint]
        
        # Create new entity URI
        entity_id = hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
        target_entity = self.target_ns[f"entity_{entity_id}"]
        
        self.entity_cache[fingerprint] = target_entity
        
        return target_entity
    
    def _create_entity_fingerprint(
        self,
        graph: Graph,
        instance: URIRef,
        rule: Dict[str, Any]
    ) -> str:
        """
        Create unique fingerprint for entity based on key properties.
        
        Args:
            graph: Source graph
            instance: Instance URI
            rule: Mapping rule
            
        Returns:
            Fingerprint string
        """
        # Use key properties for fingerprinting (e.g., email, ID, name)
        key_properties = ['email', 'id', 'identifier', 'name']
        
        fingerprint_parts = [rule['target_class']]
        
        for source_prop in rule['property_mappings'].keys():
            prop_uri = URIRef(source_prop)
            
            # Check if this is a key property
            if any(key in source_prop.lower() for key in key_properties):
                for obj in graph.objects(instance, prop_uri):
                    fingerprint_parts.append(str(obj).lower().strip())
        
        return "|".join(fingerprint_parts)
    
    def _transform_value(self, value: Any, source_prop: str, target_prop: str) -> Any:
        """
        Transform value during harmonization (e.g., unit conversion, format change).
        
        Args:
            value: Original value
            source_prop: Source property URI
            target_prop: Target property URI
            
        Returns:
            Transformed value
        """
        # Production-ready transformations
        
        # Date/DateTime standardization to ISO 8601
        if 'date' in target_prop.lower() and isinstance(value, Literal):
            try:
                from dateutil import parser
                # Parse various date formats and standardize
                parsed_date = parser.parse(str(value))
                return Literal(parsed_date.isoformat(), datatype=XSD.dateTime)
            except Exception as e:
                logger.warning(f"Could not parse date '{value}': {e}")
                return value
        
        # Numeric value standardization
        if any(keyword in target_prop.lower() for keyword in ['currency', 'price', 'amount', 'value']):
            if isinstance(value, Literal):
                try:
                    # Remove currency symbols and parse
                    cleaned = str(value).replace('$', '').replace('€', '').replace(',', '').strip()
                    numeric_value = float(cleaned)
                    return Literal(numeric_value, datatype=XSD.decimal)
                except Exception as e:
                    logger.warning(f"Could not parse numeric value '{value}': {e}")
                    return value
        
        # Email standardization (lowercase)
        if 'email' in target_prop.lower() and isinstance(value, Literal):
            return Literal(str(value).lower().strip(), datatype=XSD.string)
        
        # Phone number standardization (remove non-digits for comparison)
        if 'phone' in target_prop.lower() and isinstance(value, Literal):
            # Keep original format but ensure string type
            return Literal(str(value).strip(), datatype=XSD.string)
        
        # URL/URI standardization
        if 'url' in target_prop.lower() or 'uri' in target_prop.lower():
            if isinstance(value, Literal):
                url_str = str(value).strip()
                # Ensure proper URL format
                if not url_str.startswith(('http://', 'https://')):
                    url_str = 'https://' + url_str
                return Literal(url_str, datatype=XSD.anyURI)
        
        # Default: return unchanged
        return value
    
    def _add_provenance(
        self,
        target_entity: URIRef,
        source_entity: URIRef,
        provenance_info: Dict[str, str]
    ):
        """Add provenance information using W3C PROV ontology."""
        # Create provenance activity
        activity = BNode()
        
        self.harmonized_graph.add((target_entity, self.PROV.wasDerivedFrom, source_entity))
        self.harmonized_graph.add((target_entity, self.PROV.wasGeneratedBy, activity))
        
        self.harmonized_graph.add((activity, RDF.type, self.PROV.Activity))
        self.harmonized_graph.add((activity, self.PROV.startedAtTime, 
                                   Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Add custom provenance metadata
        for key, value in provenance_info.items():
            self.harmonized_graph.add((activity, self.target_ns[key], Literal(value)))
    
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect conflicts in harmonized data (e.g., inconsistent property values).
        
        Returns:
            List of conflicts
        """
        conflicts = []
        
        # Find entities with multiple values for functional properties
        query = """
        SELECT ?entity ?property (COUNT(?value) AS ?valueCount)
        WHERE {
            ?entity ?property ?value .
        }
        GROUP BY ?entity ?property
        HAVING (COUNT(?value) > 1)
        """
        
        results = self.harmonized_graph.query(query)
        
        for row in results:
            entity = row.entity
            prop = row.property
            
            # Get all conflicting values
            values = list(self.harmonized_graph.objects(entity, prop))
            
            conflicts.append({
                'entity': str(entity),
                'property': str(prop),
                'conflicting_values': [str(v) for v in values],
                'count': len(values)
            })
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts
    
    def resolve_conflicts(
        self,
        resolution_strategy: str = 'most_recent'
    ) -> int:
        """
        Resolve conflicts in harmonized data.
        
        Args:
            resolution_strategy: Strategy ('most_recent', 'most_common', 'trusted_source')
            
        Returns:
            Number of conflicts resolved
        """
        conflicts = self.detect_conflicts()
        resolved_count = 0
        
        for conflict in conflicts:
            entity = URIRef(conflict['entity'])
            prop = URIRef(conflict['property'])
            
            if resolution_strategy == 'most_recent':
                # Keep most recent value (requires provenance with timestamps)
                # Simplified: keep first value, remove others
                values = list(self.harmonized_graph.objects(entity, prop))
                
                if len(values) > 1:
                    # Remove all values
                    for v in values:
                        self.harmonized_graph.remove((entity, prop, v))
                    
                    # Add back the first one
                    self.harmonized_graph.add((entity, prop, values[0]))
                    resolved_count += 1
            
            elif resolution_strategy == 'most_common':
                # Keep most common value
                values = list(self.harmonized_graph.objects(entity, prop))
                value_counts = defaultdict(int)
                
                for v in values:
                    value_counts[str(v)] += 1
                
                most_common = max(value_counts, key=value_counts.get)
                
                # Remove all and add most common
                for v in values:
                    self.harmonized_graph.remove((entity, prop, v))
                
                self.harmonized_graph.add((entity, prop, Literal(most_common)))
                resolved_count += 1
        
        logger.info(f"Resolved {resolved_count} conflicts using strategy: {resolution_strategy}")
        return resolved_count
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate harmonized data quality.
        
        Returns:
            Quality report
        """
        report = {
            'total_entities': len(set(self.harmonized_graph.subjects())),
            'total_triples': len(self.harmonized_graph),
            'issues': []
        }
        
        # Check for missing required properties
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?entity ?type
        WHERE {
            ?entity a ?type .
            FILTER NOT EXISTS { ?entity rdfs:label ?label }
        }
        """
        
        missing_labels = list(self.harmonized_graph.query(query))
        
        if missing_labels:
            report['issues'].append({
                'type': 'missing_labels',
                'count': len(missing_labels),
                'severity': 'warning'
            })
        
        # Check for orphaned entities (no incoming or outgoing relationships)
        all_subjects = set(self.harmonized_graph.subjects())
        all_objects = set(o for o in self.harmonized_graph.objects() if isinstance(o, URIRef))
        
        connected_entities = all_subjects.union(all_objects)
        
        orphaned = []
        for entity in all_subjects:
            # Check if entity has any relationships (beyond rdf:type)
            relationships = [
                (s, p, o) for s, p, o in self.harmonized_graph.triples((entity, None, None))
                if p != RDF.type
            ]
            
            if not relationships:
                orphaned.append(entity)
        
        if orphaned:
            report['issues'].append({
                'type': 'orphaned_entities',
                'count': len(orphaned),
                'severity': 'info'
            })
        
        # Calculate quality score
        total_issues = sum(issue['count'] for issue in report['issues'])
        report['quality_score'] = max(0, 100 - (total_issues / report['total_entities'] * 100) if report['total_entities'] > 0 else 100)
        
        return report
    
    def generate_mapping_suggestions(
        self,
        source_graph: Graph
    ) -> List[Dict[str, Any]]:
        """
        Automatically suggest schema mappings based on similarity.
        
        Args:
            source_graph: Source graph to analyze
            
        Returns:
            List of suggested mappings
        """
        suggestions = []
        
        # Extract source schema
        source_classes = set(source_graph.subjects(RDF.type, OWL.Class))
        target_classes = set(self.harmonized_graph.subjects(RDF.type, OWL.Class))
        
        # Simple label-based matching
        for source_class in source_classes:
            source_label = str(source_graph.value(source_class, RDFS.label, default=source_class)).lower()
            
            for target_class in target_classes:
                target_label = str(self.harmonized_graph.value(target_class, RDFS.label, default=target_class)).lower()
                
                # Calculate simple similarity
                similarity = self._calculate_string_similarity(source_label, target_label)
                
                if similarity > 0.6:  # Threshold
                    suggestions.append({
                        'source_class': str(source_class),
                        'target_class': str(target_class),
                        'similarity': similarity,
                        'confidence': 'high' if similarity > 0.8 else 'medium'
                    })
        
        return sorted(suggestions, key=lambda x: x['similarity'], reverse=True)
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity (Jaccard similarity on words)."""
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def export_harmonized_data(
        self,
        output_file: str,
        format: str = 'turtle'
    ):
        """
        Export harmonized graph to file.
        
        Args:
            output_file: Output file path
            format: RDF format (turtle, xml, nt, json-ld)
        """
        self.harmonized_graph.serialize(destination=output_file, format=format)
        logger.info(f"Exported harmonized data to: {output_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get harmonization statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_entities': len(set(self.harmonized_graph.subjects())),
            'total_triples': len(self.harmonized_graph),
            'total_classes': len(set(self.harmonized_graph.subjects(RDF.type, OWL.Class))),
            'mapping_rules': len(self.mapping_rules),
            'entity_cache_size': len(self.entity_cache),
            'namespaces': list(self.harmonized_graph.namespaces())
        }
