"""
European Railway Agency (ERA) Integration Module

This module implements integration with ERA (European Railway Agency) data standards
and the European Data Interoperability Portal for cross-border railway operations.

ERA Standards Covered:
- ERA Vocabulary (data-interop.era.europa.eu)
- Technical Specifications for Interoperability (TSI)
- EU Directive 2016/797 on railway interoperability
- RINF (Register of Infrastructure) data model

Author: Saidul Islam
License: MIT
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logger = logging.getLogger(__name__)


class ERAIntegration:
    """
    Integration with European Railway Agency (ERA) ontology and data portal.
    
    Implements mappings between local knowledge graph and ERA standards for
    cross-border railway data interoperability.
    """
    
    def __init__(self, era_endpoint: str = "https://data-interop.era.europa.eu/sparql"):
        """
        Initialize ERA integration.
        
        Args:
            era_endpoint: SPARQL endpoint URL for ERA data portal
        """
        self.ERA = Namespace("https://data-interop.era.europa.eu/era-vocabulary#")
        self.ERAVOC = Namespace("https://data-interop.era.europa.eu/era-vocabulary/")
        self.RINF = Namespace("https://data-interop.era.europa.eu/rinf/")
        
        self.sparql = SPARQLWrapper(era_endpoint)
        self.sparql.setReturnFormat(JSON)
        
        self.graph = Graph()
        self._bind_namespaces()
        
        logger.info(f"ERA Integration initialized with endpoint: {era_endpoint}")
    
    def _bind_namespaces(self):
        """Bind common namespaces for ERA ontology."""
        self.graph.bind("era", self.ERA)
        self.graph.bind("eravoc", self.ERAVOC)
        self.graph.bind("rinf", self.RINF)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("skos", SKOS)
        self.graph.bind("dcterms", DCTERMS)
    
    def map_to_era_standard(self, local_data: Dict[str, Any], 
                           entity_type: str) -> Graph:
        """
        Map local ontology data to ERA standard format.
        
        Args:
            local_data: Dictionary containing local entity data
            entity_type: Type of entity (e.g., 'infrastructure', 'vehicle', 'person')
            
        Returns:
            RDF Graph with ERA-compliant triples
        """
        logger.info(f"Mapping {entity_type} to ERA standard")
        
        if entity_type == "infrastructure":
            return self._map_infrastructure(local_data)
        elif entity_type == "vehicle":
            return self._map_vehicle(local_data)
        elif entity_type == "operational_point":
            return self._map_operational_point(local_data)
        else:
            logger.warning(f"Unknown entity type: {entity_type}")
            return self.graph
    
    def _map_infrastructure(self, data: Dict) -> Graph:
        """Map infrastructure element to ERA RINF model."""
        infra_id = data.get('id', 'unknown')
        infra_uri = URIRef(f"{self.RINF}Infrastructure/{infra_id}")
        
        # Core ERA properties
        self.graph.add((infra_uri, RDF.type, self.ERA.InfrastructureElement))
        self.graph.add((infra_uri, self.ERA.identifier, 
                       Literal(infra_id, datatype=XSD.string)))
        
        if 'name' in data:
            self.graph.add((infra_uri, RDFS.label, 
                           Literal(data['name'], lang='en')))
        
        if 'description' in data:
            self.graph.add((infra_uri, DCTERMS.description, 
                           Literal(data['description'], lang='en')))
        
        # ERA-specific properties
        if 'track_gauge' in data:
            self.graph.add((infra_uri, self.ERA.trackGauge, 
                           Literal(data['track_gauge'], datatype=XSD.integer)))
        
        if 'country_code' in data:
            self.graph.add((infra_uri, self.ERA.inCountry, 
                           Literal(data['country_code'], datatype=XSD.string)))
        
        if 'operational_from' in data:
            self.graph.add((infra_uri, self.ERA.operationalFrom, 
                           Literal(data['operational_from'], datatype=XSD.date)))
        
        # Compliance metadata
        self.graph.add((infra_uri, DCTERMS.conformsTo, 
                       Literal("EU Directive 2016/797")))
        self.graph.add((infra_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        return self.graph
    
    def _map_vehicle(self, data: Dict) -> Graph:
        """Map railway vehicle to ERA vehicle register model."""
        vehicle_id = data.get('id', 'unknown')
        vehicle_uri = URIRef(f"{self.ERAVOC}Vehicle/{vehicle_id}")
        
        self.graph.add((vehicle_uri, RDF.type, self.ERA.Vehicle))
        self.graph.add((vehicle_uri, self.ERA.vehicleNumber, 
                       Literal(vehicle_id, datatype=XSD.string)))
        
        if 'vehicle_type' in data:
            self.graph.add((vehicle_uri, self.ERA.vehicleType, 
                           URIRef(f"{self.ERAVOC}VehicleType/{data['vehicle_type']}")))
        
        if 'max_speed' in data:
            self.graph.add((vehicle_uri, self.ERA.maxSpeed, 
                           Literal(data['max_speed'], datatype=XSD.integer)))
        
        if 'length' in data:
            self.graph.add((vehicle_uri, self.ERA.length, 
                           Literal(data['length'], datatype=XSD.decimal)))
        
        return self.graph
    
    def _map_operational_point(self, data: Dict) -> Graph:
        """Map operational point (station, junction, etc.) to ERA model."""
        op_id = data.get('id', 'unknown')
        op_uri = URIRef(f"{self.RINF}OperationalPoint/{op_id}")
        
        self.graph.add((op_uri, RDF.type, self.ERA.OperationalPoint))
        self.graph.add((op_uri, self.ERA.opIdentifier, 
                       Literal(op_id, datatype=XSD.string)))
        
        if 'name' in data:
            self.graph.add((op_uri, self.ERA.opName, 
                           Literal(data['name'], lang='en')))
        
        if 'latitude' in data and 'longitude' in data:
            location = BNode()
            self.graph.add((op_uri, self.ERA.location, location))
            self.graph.add((location, RDF.type, self.ERA.GeographicLocation))
            self.graph.add((location, self.ERA.latitude, 
                           Literal(data['latitude'], datatype=XSD.decimal)))
            self.graph.add((location, self.ERA.longitude, 
                           Literal(data['longitude'], datatype=XSD.decimal)))
        
        if 'op_type' in data:
            self.graph.add((op_uri, self.ERA.opType, 
                           URIRef(f"{self.ERAVOC}OPType/{data['op_type']}")))
        
        return self.graph
    
    def validate_era_compliance(self, graph: Optional[Graph] = None) -> Dict:
        """
        Validate data against ERA standards and interoperability requirements.
        
        Args:
            graph: RDF graph to validate (uses instance graph if None)
            
        Returns:
            Validation report dictionary
        """
        target_graph = graph if graph else self.graph
        
        validation_report = {
            "compliant": True,
            "standard": "ERA Interoperability Directive 2016/797",
            "validation_date": datetime.now().isoformat(),
            "violations": [],
            "warnings": [],
            "statistics": {
                "total_triples": len(target_graph),
                "infrastructure_elements": 0,
                "vehicles": 0,
                "operational_points": 0
            }
        }
        
        # Check mandatory ERA properties
        required_properties = {
            self.ERA.InfrastructureElement: [
                self.ERA.identifier,
                self.ERA.inCountry
            ],
            self.ERA.Vehicle: [
                self.ERA.vehicleNumber,
                self.ERA.vehicleType
            ],
            self.ERA.OperationalPoint: [
                self.ERA.opIdentifier,
                self.ERA.opName
            ]
        }
        
        for entity_type, properties in required_properties.items():
            entities = list(target_graph.subjects(RDF.type, entity_type))
            
            # Update statistics
            if entity_type == self.ERA.InfrastructureElement:
                validation_report["statistics"]["infrastructure_elements"] = len(entities)
            elif entity_type == self.ERA.Vehicle:
                validation_report["statistics"]["vehicles"] = len(entities)
            elif entity_type == self.ERA.OperationalPoint:
                validation_report["statistics"]["operational_points"] = len(entities)
            
            for entity in entities:
                for prop in properties:
                    if not list(target_graph.objects(entity, prop)):
                        validation_report["compliant"] = False
                        validation_report["violations"].append({
                            "entity": str(entity),
                            "missing_property": str(prop),
                            "severity": "error"
                        })
        
        # Check for recommended properties
        recommended_properties = [
            (self.ERA.InfrastructureElement, DCTERMS.description),
            (self.ERA.InfrastructureElement, self.ERA.operationalFrom),
            (self.ERA.Vehicle, self.ERA.maxSpeed),
        ]
        
        for entity_type, prop in recommended_properties:
            entities = list(target_graph.subjects(RDF.type, entity_type))
            for entity in entities:
                if not list(target_graph.objects(entity, prop)):
                    validation_report["warnings"].append({
                        "entity": str(entity),
                        "missing_property": str(prop),
                        "severity": "warning",
                        "message": "Recommended property missing"
                    })
        
        logger.info(f"ERA validation complete. Compliant: {validation_report['compliant']}")
        return validation_report
    
    def query_era_portal(self, query: str) -> List[Dict]:
        """
        Execute SPARQL query against ERA data portal.
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of query results as dictionaries
        """
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            result_list = []
            for result in results["results"]["bindings"]:
                row = {}
                for var, value in result.items():
                    row[var] = value["value"]
                result_list.append(row)
            
            logger.info(f"ERA portal query returned {len(result_list)} results")
            return result_list
            
        except Exception as e:
            logger.error(f"Error querying ERA portal: {e}")
            return []
    
    def export_era_format(self, format: str = "turtle") -> str:
        """
        Export graph in ERA-compliant RDF format.
        
        Args:
            format: Output format (turtle, xml, n3, json-ld)
            
        Returns:
            Serialized RDF string
        """
        return self.graph.serialize(format=format)
    
    def import_from_era(self, uri: str) -> Graph:
        """
        Import data from ERA portal by URI.
        
        Args:
            uri: URI of ERA resource to import
            
        Returns:
            RDF graph with imported data
        """
        query = f"""
        PREFIX era: <https://data-interop.era.europa.eu/era-vocabulary#>
        PREFIX rinf: <https://data-interop.era.europa.eu/rinf/>
        
        CONSTRUCT {{
            <{uri}> ?p ?o .
            ?o ?p2 ?o2 .
        }}
        WHERE {{
            <{uri}> ?p ?o .
            OPTIONAL {{ ?o ?p2 ?o2 }}
        }}
        LIMIT 1000
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            self.graph.parse(data=results.serialize(format='turtle'), format='turtle')
            logger.info(f"Imported ERA data from {uri}")
            return self.graph
        except Exception as e:
            logger.error(f"Error importing from ERA: {e}")
            return Graph()


# Example usage and demo
if __name__ == "__main__":
    # Initialize ERA integration
    era = ERAIntegration()
    
    # Example: Map local infrastructure data to ERA standard
    local_infrastructure = {
        "id": "INF-NO-001",
        "name": "Oslo Central Station Track 1",
        "description": "Main platform track at Oslo Central Station",
        "track_gauge": 1435,  # Standard gauge in mm
        "country_code": "NO",
        "operational_from": "2020-01-01"
    }
    
    graph = era.map_to_era_standard(local_infrastructure, "infrastructure")
    print("Mapped Infrastructure to ERA Standard:")
    print(graph.serialize(format='turtle'))
    
    # Validate compliance
    report = era.validate_era_compliance(graph)
    print("\nERA Compliance Report:")
    print(f"Compliant: {report['compliant']}")
    print(f"Violations: {len(report['violations'])}")
    print(f"Warnings: {len(report['warnings'])}")
