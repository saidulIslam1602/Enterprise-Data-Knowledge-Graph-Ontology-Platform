"""
Knowledge Graph Manager

Handles RDF graph operations, SPARQL queries, and triplestore interactions.
"""

import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphManager:
    """
    Manages RDF knowledge graph operations including loading ontologies,
    querying with SPARQL, and interacting with triplestore.
    """

    def __init__(self, triplestore_url: Optional[str] = None):
        """
        Initialize Graph Manager.

        Args:
            triplestore_url: URL of SPARQL endpoint (e.g., Apache Jena Fuseki)
        """
        self.graph = Graph()
        self.triplestore_url = triplestore_url or os.getenv(
            "TRIPLESTORE_URL", "http://localhost:3030/enterprise_kg"
        )
        
        # Define custom namespaces
        self.ns = {
            'cus': Namespace("http://enterprise.org/ontology/customer#"),
            'comp': Namespace("http://enterprise.org/ontology/company#"),
            'compliance': Namespace("http://enterprise.org/ontology/compliance#"),
            'lineage': Namespace("http://enterprise.org/ontology/lineage#"),
        }
        
        # Bind namespaces to graph
        for prefix, namespace in self.ns.items():
            self.graph.bind(prefix, namespace)
        
        # Bind standard namespaces
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('owl', OWL)
        self.graph.bind('xsd', XSD)
        
        logger.info(f"GraphManager initialized with triplestore: {self.triplestore_url}")

    def load_ontology(self, ontology_path: Union[str, Path], format: str = 'turtle') -> bool:
        """
        Load an ontology file into the graph.

        Args:
            ontology_path: Path to ontology file
            format: RDF serialization format (turtle, xml, n3, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            ontology_path = Path(ontology_path)
            if not ontology_path.exists():
                logger.error(f"Ontology file not found: {ontology_path}")
                return False
            
            self.graph.parse(str(ontology_path), format=format)
            logger.info(f"Loaded ontology: {ontology_path} ({len(self.graph)} triples)")
            return True
        except Exception as e:
            logger.error(f"Error loading ontology {ontology_path}: {e}")
            return False

    def load_all_ontologies(self, ontology_dir: Union[str, Path]) -> Dict[str, bool]:
        """
        Load all ontology files from a directory.

        Args:
            ontology_dir: Directory containing ontology files

        Returns:
            Dictionary mapping file names to load status
        """
        ontology_dir = Path(ontology_dir)
        results = {}
        
        if not ontology_dir.exists():
            logger.error(f"Ontology directory not found: {ontology_dir}")
            return results
        
        for ont_file in ontology_dir.glob("*.ttl"):
            results[ont_file.name] = self.load_ontology(ont_file)
        
        logger.info(f"Loaded {sum(results.values())}/{len(results)} ontologies")
        return results

    def execute_query(self, query: str, return_format: str = 'json') -> Union[Dict, List, str]:
        """
        Execute a SPARQL query on the local graph.

        Args:
            query: SPARQL query string
            return_format: Return format (json, xml, n3)

        Returns:
            Query results in specified format
        """
        try:
            results = self.graph.query(query)
            
            if return_format == 'json':
                return self._results_to_json(results)
            elif return_format == 'list':
                return list(results)
            else:
                return results.serialize(format=return_format)
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {"error": str(e)}

    def execute_remote_query(self, query: str, return_format: str = JSON) -> Dict:
        """
        Execute a SPARQL query on remote triplestore.

        Args:
            query: SPARQL query string
            return_format: SPARQLWrapper format constant

        Returns:
            Query results as dictionary
        """
        try:
            sparql = SPARQLWrapper(f"{self.triplestore_url}/query")
            sparql.setQuery(query)
            sparql.setReturnFormat(return_format)
            results = sparql.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error executing remote query: {e}")
            return {"error": str(e)}

    def load_query_from_file(self, query_file: Union[str, Path]) -> str:
        """
        Load a SPARQL query from file.

        Args:
            query_file: Path to SPARQL query file

        Returns:
            Query string
        """
        query_file = Path(query_file)
        with open(query_file, 'r') as f:
            return f.read()

    def add_triple(self, subject: URIRef, predicate: URIRef, obj: Union[URIRef, Literal]) -> None:
        """
        Add a single triple to the graph.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            obj: Object (URI or Literal)
        """
        self.graph.add((subject, predicate, obj))

    def remove_triple(self, subject: URIRef, predicate: URIRef, obj: Union[URIRef, Literal]) -> None:
        """
        Remove a triple from the graph.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            obj: Object (URI or Literal)
        """
        self.graph.remove((subject, predicate, obj))

    def get_all_classes(self) -> List[str]:
        """
        Get all OWL classes defined in the ontologies.

        Returns:
            List of class URIs
        """
        query = """
            SELECT DISTINCT ?class
            WHERE {
                ?class a owl:Class .
            }
            ORDER BY ?class
        """
        results = self.execute_query(query)
        return [row['class'] for row in results.get('results', {}).get('bindings', [])]

    def get_all_properties(self) -> Dict[str, List[str]]:
        """
        Get all properties (object and data) from ontologies.

        Returns:
            Dictionary with 'object_properties' and 'data_properties' lists
        """
        obj_prop_query = """
            SELECT DISTINCT ?property
            WHERE {
                ?property a owl:ObjectProperty .
            }
            ORDER BY ?property
        """
        
        data_prop_query = """
            SELECT DISTINCT ?property
            WHERE {
                ?property a owl:DatatypeProperty .
            }
            ORDER BY ?property
        """
        
        obj_results = self.execute_query(obj_prop_query)
        data_results = self.execute_query(data_prop_query)
        
        return {
            'object_properties': [r['property'] for r in obj_results.get('results', {}).get('bindings', [])],
            'data_properties': [r['property'] for r in data_results.get('results', {}).get('bindings', [])]
        }

    def export_graph(self, output_path: Union[str, Path], format: str = 'turtle') -> bool:
        """
        Export the graph to a file.

        Args:
            output_path: Output file path
            format: RDF serialization format

        Returns:
            True if successful
        """
        try:
            output_path = Path(output_path)
            self.graph.serialize(destination=str(output_path), format=format)
            logger.info(f"Graph exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting graph: {e}")
            return False

    def get_statistics(self) -> Dict[str, int]:
        """
        Get basic statistics about the knowledge graph.

        Returns:
            Dictionary with graph statistics
        """
        stats = {
            'total_triples': len(self.graph),
            'classes': len(list(self.graph.subjects(RDF.type, OWL.Class))),
            'object_properties': len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))),
            'data_properties': len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))),
            'individuals': 0  # Count named individuals
        }
        
        # Count individuals (instances of classes)
        individual_query = """
            SELECT (COUNT(DISTINCT ?individual) AS ?count)
            WHERE {
                ?individual a ?class .
                ?class a owl:Class .
            }
        """
        results = self.execute_query(individual_query)
        if results.get('results', {}).get('bindings'):
            stats['individuals'] = int(results['results']['bindings'][0]['count']['value'])
        
        return stats

    def clear_graph(self) -> None:
        """Clear all triples from the graph."""
        self.graph.remove((None, None, None))
        logger.info("Graph cleared")

    @staticmethod
    def _results_to_json(results) -> Dict:
        """
        Convert RDFLib query results to JSON format.

        Args:
            results: RDFLib query result object

        Returns:
            JSON-compatible dictionary
        """
        bindings = []
        for row in results:
            binding = {}
            for var in results.vars:
                value = row[var]
                if value is not None:
                    binding[str(var)] = {
                        'type': 'uri' if isinstance(value, URIRef) else 'literal',
                        'value': str(value)
                    }
            bindings.append(binding)
        
        return {
            'head': {'vars': [str(v) for v in results.vars]},
            'results': {'bindings': bindings}
        }


if __name__ == "__main__":
    # Example usage
    gm = GraphManager()
    
    # Load ontologies
    ontology_dir = Path(__file__).parent.parent.parent / "ontologies"
    gm.load_all_ontologies(ontology_dir)
    
    # Get statistics
    stats = gm.get_statistics()
    print(f"\nKnowledge Graph Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get all classes
    classes = gm.get_all_classes()
    print(f"\nDefined Classes ({len(classes)}):")
    for cls in classes[:5]:  # Show first 5
        print(f"  - {cls}")
