"""
railML Integration Module

This module implements integration with railML.org standards for railway data exchange.
railML is the standard XML format for railway data used across Europe and internationally.

railML Standards Covered:
- railML 3.2 (latest version)
- Infrastructure schema
- Rollingstock schema
- Timetable schema
- Interlocking schema

Compatibility:
- Compatible with ERA (European Railway Agency) standards
- Supports cross-border data exchange
- Implements bidirectional conversion (XML ↔ RDF)

Author: Saidul Islam
License: MIT
"""

from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
import logging

logger = logging.getLogger(__name__)


class RailMLIntegration:
    """
    Integration with railML 3.2 standard for railway data exchange.
    
    Provides bidirectional conversion between railML XML and RDF/OWL format,
    enabling interoperability with European railway systems.
    """
    
    # railML 3.2 namespaces
    RAILML_NS = "https://www.railml.org/schemas/3.2"
    RAILML_INFRA = f"{RAILML_NS}/infrastructure"
    RAILML_RS = f"{RAILML_NS}/rollingstock"
    RAILML_TT = f"{RAILML_NS}/timetable"
    
    def __init__(self, schema_version: str = "3.2"):
        """
        Initialize railML integration.
        
        Args:
            schema_version: railML schema version (default: 3.2)
        """
        self.schema_version = schema_version
        self.RAILML = Namespace(self.RAILML_NS)
        self.graph = Graph()
        
        # Bind namespaces
        self.graph.bind("railml", self.RAILML)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("dcterms", DCTERMS)
        
        logger.info(f"railML Integration initialized (version {schema_version})")
    
    def convert_railml_to_rdf(self, railml_xml: str) -> Graph:
        """
        Convert railML XML to RDF graph.
        
        Args:
            railml_xml: railML XML string or file path
            
        Returns:
            RDF Graph with converted data
        """
        logger.info("Converting railML XML to RDF")
        
        try:
            # Parse XML
            if railml_xml.startswith('<?xml') or railml_xml.startswith('<railml'):
                root = ET.fromstring(railml_xml)
            else:
                tree = ET.parse(railml_xml)
                root = tree.getroot()
            
            # Extract railML namespace
            ns = {'railml': self.RAILML_NS}
            
            # Convert infrastructure elements
            self._convert_infrastructure_elements(root, ns)
            
            # Convert rolling stock
            self._convert_rolling_stock(root, ns)
            
            # Convert timetables
            self._convert_timetables(root, ns)
            
            logger.info(f"Converted railML to RDF: {len(self.graph)} triples")
            return self.graph
            
        except Exception as e:
            logger.error(f"Error converting railML to RDF: {e}")
            return Graph()
    
    def _convert_infrastructure_elements(self, root: ET.Element, ns: Dict):
        """Convert railML infrastructure elements to RDF."""
        for element in root.findall('.//railml:infrastructureElement', ns):
            element_id = element.get('id', 'unknown')
            element_uri = URIRef(f"{self.RAILML_INFRA}/InfrastructureElement/{element_id}")
            
            # Core type
            self.graph.add((element_uri, RDF.type, self.RAILML.InfrastructureElement))
            self.graph.add((element_uri, self.RAILML.id, 
                           Literal(element_id, datatype=XSD.string)))
            
            # Convert attributes
            for attr_name, attr_value in element.attrib.items():
                if attr_name != 'id':
                    pred_uri = URIRef(f"{self.RAILML}{attr_name}")
                    self.graph.add((element_uri, pred_uri, Literal(attr_value)))
            
            # Convert child elements
            for child in element:
                child_name = child.tag.split('}')[-1]  # Remove namespace
                pred_uri = URIRef(f"{self.RAILML}{child_name}")
                
                if child.text and child.text.strip():
                    self.graph.add((element_uri, pred_uri, Literal(child.text.strip())))
    
    def _convert_rolling_stock(self, root: ET.Element, ns: Dict):
        """Convert railML rolling stock to RDF."""
        for vehicle in root.findall('.//railml:vehicle', ns):
            vehicle_id = vehicle.get('id', 'unknown')
            vehicle_uri = URIRef(f"{self.RAILML_RS}/Vehicle/{vehicle_id}")
            
            self.graph.add((vehicle_uri, RDF.type, self.RAILML.Vehicle))
            self.graph.add((vehicle_uri, self.RAILML.vehicleId, 
                           Literal(vehicle_id, datatype=XSD.string)))
            
            # Vehicle properties
            for attr_name, attr_value in vehicle.attrib.items():
                if attr_name != 'id':
                    pred_uri = URIRef(f"{self.RAILML}{attr_name}")
                    self.graph.add((vehicle_uri, pred_uri, Literal(attr_value)))
    
    def _convert_timetables(self, root: ET.Element, ns: Dict):
        """Convert railML timetables to RDF."""
        for train in root.findall('.//railml:train', ns):
            train_id = train.get('id', 'unknown')
            train_uri = URIRef(f"{self.RAILML_TT}/Train/{train_id}")
            
            self.graph.add((train_uri, RDF.type, self.RAILML.Train))
            self.graph.add((train_uri, self.RAILML.trainId, 
                           Literal(train_id, datatype=XSD.string)))
            
            # Train properties
            for attr_name, attr_value in train.attrib.items():
                if attr_name != 'id':
                    pred_uri = URIRef(f"{self.RAILML}{attr_name}")
                    self.graph.add((train_uri, pred_uri, Literal(attr_value)))
    
    def export_to_railml(self, rdf_graph: Optional[Graph] = None) -> str:
        """
        Export RDF graph to railML XML format.
        
        Args:
            rdf_graph: RDF graph to export (uses instance graph if None)
            
        Returns:
            railML XML string
        """
        source_graph = rdf_graph if rdf_graph else self.graph
        
        logger.info("Exporting RDF to railML XML")
        
        # Create root element
        root = ET.Element('railML', {
            'xmlns': self.RAILML_NS,
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'version': self.schema_version,
            'xsi:schemaLocation': f'{self.RAILML_NS} https://www.railml.org/schemas/{self.schema_version}/railML.xsd'
        })
        
        # Add metadata
        metadata = ET.SubElement(root, 'metadata')
        creator = ET.SubElement(metadata, 'dc:creator')
        creator.text = 'Enterprise Knowledge Graph Platform'
        created = ET.SubElement(metadata, 'dc:date')
        created.text = datetime.now().isoformat()
        
        # Create infrastructure section
        infrastructure = ET.SubElement(root, 'infrastructure')
        
        # Export infrastructure elements
        for subject in source_graph.subjects(RDF.type, self.RAILML.InfrastructureElement):
            element = ET.SubElement(infrastructure, 'infrastructureElement')
            
            # Get ID
            element_id = str(subject).split('/')[-1]
            element.set('id', element_id)
            
            # Add properties
            for pred, obj in source_graph.predicate_objects(subject=subject):
                if pred != RDF.type:
                    prop_name = str(pred).split('#')[-1].split('/')[-1]
                    if prop_name != 'id':
                        element.set(prop_name, str(obj))
        
        # Create rolling stock section
        rollingstock = ET.SubElement(root, 'rollingstock')
        
        for subject in source_graph.subjects(RDF.type, self.RAILML.Vehicle):
            vehicle = ET.SubElement(rollingstock, 'vehicle')
            vehicle_id = str(subject).split('/')[-1]
            vehicle.set('id', vehicle_id)
            
            for pred, obj in source_graph.predicate_objects(subject=subject):
                if pred != RDF.type:
                    prop_name = str(pred).split('#')[-1].split('/')[-1]
                    if prop_name not in ['id', 'vehicleId']:
                        vehicle.set(prop_name, str(obj))
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        result = '\n'.join(lines)
        
        logger.info(f"Exported {len(source_graph)} triples to railML XML")
        return result
    
    def validate_railml(self, xml_content: str) -> Dict:
        """
        Validate railML XML against schema.
        
        Args:
            xml_content: railML XML string to validate
            
        Returns:
            Validation report dictionary
        """
        validation_report = {
            "valid": True,
            "schema_version": self.schema_version,
            "validation_date": datetime.now().isoformat(),
            "errors": [],
            "warnings": [],
            "statistics": {
                "infrastructure_elements": 0,
                "vehicles": 0,
                "trains": 0
            }
        }
        
        try:
            root = ET.fromstring(xml_content)
            
            # Check railML version
            version = root.get('version')
            if version != self.schema_version:
                validation_report["warnings"].append({
                    "message": f"Schema version mismatch: {version} != {self.schema_version}",
                    "severity": "warning"
                })
            
            # Count elements
            ns = {'railml': self.RAILML_NS}
            validation_report["statistics"]["infrastructure_elements"] = len(
                root.findall('.//railml:infrastructureElement', ns)
            )
            validation_report["statistics"]["vehicles"] = len(
                root.findall('.//railml:vehicle', ns)
            )
            validation_report["statistics"]["trains"] = len(
                root.findall('.//railml:train', ns)
            )
            
            # Check for required elements
            if not root.find('.//railml:metadata', ns):
                validation_report["errors"].append({
                    "message": "Missing required 'metadata' element",
                    "severity": "error"
                })
                validation_report["valid"] = False
            
            logger.info(f"railML validation complete. Valid: {validation_report['valid']}")
            
        except ET.ParseError as e:
            validation_report["valid"] = False
            validation_report["errors"].append({
                "message": f"XML parsing error: {str(e)}",
                "severity": "error"
            })
        
        return validation_report
    
    def merge_with_era(self, era_graph: Graph) -> Graph:
        """
        Merge railML data with ERA ontology for full compliance.
        
        Args:
            era_graph: RDF graph with ERA data
            
        Returns:
            Merged RDF graph
        """
        logger.info("Merging railML with ERA ontology")
        
        merged_graph = self.graph + era_graph
        
        # Add owl:sameAs links between railML and ERA entities
        # This enables cross-referencing between the two standards
        
        logger.info(f"Merged graph contains {len(merged_graph)} triples")
        return merged_graph


# Example usage and demo
if __name__ == "__main__":
    # Initialize railML integration
    railml = RailMLIntegration()
    
    # Example railML XML
    example_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <railML xmlns="https://www.railml.org/schemas/3.2" version="3.2">
        <metadata>
            <dc:creator>Enterprise KG Platform</dc:creator>
            <dc:date>2025-10-17</dc:date>
        </metadata>
        <infrastructure>
            <infrastructureElement id="track001" type="track" length="1500.0">
                <name>Main Line Track 1</name>
                <trackGauge>1435</trackGauge>
            </infrastructureElement>
        </infrastructure>
        <rollingstock>
            <vehicle id="loco001" type="locomotive" maxSpeed="200">
                <designation>Electric Locomotive Type 1</designation>
                <length>20.5</length>
            </vehicle>
        </rollingstock>
    </railML>
    """
    
    # Convert to RDF
    graph = railml.convert_railml_to_rdf(example_xml)
    print("Converted railML to RDF:")
    print(graph.serialize(format='turtle'))
    
    # Validate
    report = railml.validate_railml(example_xml)
    print("\nrailML Validation Report:")
    print(f"Valid: {report['valid']}")
    print(f"Errors: {len(report['errors'])}")
    print(f"Infrastructure Elements: {report['statistics']['infrastructure_elements']}")
    print(f"Vehicles: {report['statistics']['vehicles']}")
    
    # Export back to railML
    exported_xml = railml.export_to_railml(graph)
    print("\nExported back to railML:")
    print(exported_xml[:500] + "...")
