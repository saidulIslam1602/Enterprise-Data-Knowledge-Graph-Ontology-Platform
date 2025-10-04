"""
Data Validator using SHACL

Validates RDF data against SHACL shapes for data quality enforcement.
"""

import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

from rdflib import Graph
from pyshacl import validate
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates RDF data against SHACL shapes for data quality and compliance.
    """

    def __init__(self, shapes_dir: Optional[Union[str, Path]] = None):
        """
        Initialize Data Validator.

        Args:
            shapes_dir: Directory containing SHACL shape files
        """
        self.shapes_graph = Graph()
        self.shapes_dir = shapes_dir
        
        if shapes_dir:
            self.load_all_shapes(shapes_dir)
        
        logger.info("DataValidator initialized")

    def load_shape(self, shape_path: Union[str, Path], format: str = 'turtle') -> bool:
        """
        Load a SHACL shape file.

        Args:
            shape_path: Path to SHACL shape file
            format: RDF serialization format

        Returns:
            True if successful
        """
        try:
            shape_path = Path(shape_path)
            if not shape_path.exists():
                logger.error(f"Shape file not found: {shape_path}")
                return False
            
            self.shapes_graph.parse(str(shape_path), format=format)
            logger.info(f"Loaded SHACL shapes: {shape_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading shape {shape_path}: {e}")
            return False

    def load_all_shapes(self, shapes_dir: Union[str, Path]) -> Dict[str, bool]:
        """
        Load all SHACL shape files from a directory.

        Args:
            shapes_dir: Directory containing shape files

        Returns:
            Dictionary mapping file names to load status
        """
        shapes_dir = Path(shapes_dir)
        results = {}
        
        if not shapes_dir.exists():
            logger.error(f"Shapes directory not found: {shapes_dir}")
            return results
        
        for shape_file in shapes_dir.glob("*.ttl"):
            results[shape_file.name] = self.load_shape(shape_file)
        
        logger.info(f"Loaded {sum(results.values())}/{len(results)} shape files")
        return results

    def validate_graph(
        self, 
        data_graph: Graph, 
        shapes_graph: Optional[Graph] = None,
        inference: str = 'rdfs',
        abort_on_first: bool = False
    ) -> Dict:
        """
        Validate a data graph against SHACL shapes.

        Args:
            data_graph: RDF graph to validate
            shapes_graph: SHACL shapes graph (uses default if None)
            inference: Inference type (rdfs, owlrl, both, none)
            abort_on_first: Stop on first validation error

        Returns:
            Validation report dictionary
        """
        try:
            shapes = shapes_graph or self.shapes_graph
            
            if len(shapes) == 0:
                logger.warning("No SHACL shapes loaded for validation")
                return {
                    'conforms': True,
                    'violations': [],
                    'warnings': ['No SHACL shapes loaded for validation']
                }
            
            # Perform SHACL validation
            conforms, results_graph, results_text = validate(
                data_graph=data_graph,
                shacl_graph=shapes,
                inference=inference,
                abort_on_first=abort_on_first,
                allow_warnings=True
            )
            
            # Parse validation results
            report = self._parse_validation_report(results_graph, conforms)
            report['results_text'] = results_text
            
            logger.info(f"Validation complete: {'PASSED' if conforms else 'FAILED'}")
            return report
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                'conforms': False,
                'error': str(e),
                'violations': [],
                'warnings': []
            }

    def validate_file(
        self,
        data_file: Union[str, Path],
        format: str = 'turtle',
        shapes_graph: Optional[Graph] = None
    ) -> Dict:
        """
        Validate an RDF file against SHACL shapes.

        Args:
            data_file: Path to data file
            format: RDF serialization format
            shapes_graph: Optional custom shapes graph

        Returns:
            Validation report dictionary
        """
        try:
            data_file = Path(data_file)
            if not data_file.exists():
                logger.error(f"Data file not found: {data_file}")
                return {'conforms': False, 'error': 'File not found'}
            
            # Load data graph
            data_graph = Graph()
            data_graph.parse(str(data_file), format=format)
            
            # Validate
            return self.validate_graph(data_graph, shapes_graph)
            
        except Exception as e:
            logger.error(f"Error validating file {data_file}: {e}")
            return {'conforms': False, 'error': str(e)}

    def _parse_validation_report(self, results_graph: Graph, conforms: bool) -> Dict:
        """
        Parse SHACL validation results into structured report.

        Args:
            results_graph: RDF graph containing validation results
            conforms: Whether validation passed

        Returns:
            Structured validation report
        """
        from rdflib.namespace import SH
        
        violations = []
        warnings = []
        
        # Query for validation results
        query = """
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            
            SELECT ?result ?severity ?focusNode ?path ?value ?message ?sourceShape
            WHERE {
                ?report a sh:ValidationReport ;
                        sh:result ?result .
                ?result sh:resultSeverity ?severity ;
                        sh:focusNode ?focusNode .
                OPTIONAL { ?result sh:resultPath ?path }
                OPTIONAL { ?result sh:value ?value }
                OPTIONAL { ?result sh:resultMessage ?message }
                OPTIONAL { ?result sh:sourceShape ?sourceShape }
            }
        """
        
        for row in results_graph.query(query):
            result = {
                'severity': str(row.severity).split('#')[-1],
                'focus_node': str(row.focusNode),
                'path': str(row.path) if row.path else None,
                'value': str(row.value) if row.value else None,
                'message': str(row.message) if row.message else 'No message provided',
                'source_shape': str(row.sourceShape) if row.sourceShape else None
            }
            
            if result['severity'] == 'Violation':
                violations.append(result)
            elif result['severity'] == 'Warning':
                warnings.append(result)
        
        return {
            'conforms': conforms,
            'total_violations': len(violations),
            'total_warnings': len(warnings),
            'violations': violations,
            'warnings': warnings
        }

    def generate_report(self, validation_result: Dict, output_format: str = 'json') -> str:
        """
        Generate a formatted validation report.

        Args:
            validation_result: Validation result dictionary
            output_format: Format (json, text, html)

        Returns:
            Formatted report string
        """
        if output_format == 'json':
            return json.dumps(validation_result, indent=2)
        
        elif output_format == 'text':
            report = []
            report.append("=" * 80)
            report.append("SHACL VALIDATION REPORT")
            report.append("=" * 80)
            report.append(f"Status: {'✓ PASSED' if validation_result['conforms'] else '✗ FAILED'}")
            report.append(f"Violations: {validation_result.get('total_violations', 0)}")
            report.append(f"Warnings: {validation_result.get('total_warnings', 0)}")
            report.append("")
            
            if validation_result.get('violations'):
                report.append("VIOLATIONS:")
                report.append("-" * 80)
                for i, v in enumerate(validation_result['violations'], 1):
                    report.append(f"\n{i}. {v['message']}")
                    report.append(f"   Focus Node: {v['focus_node']}")
                    if v.get('path'):
                        report.append(f"   Property: {v['path']}")
                    if v.get('value'):
                        report.append(f"   Value: {v['value']}")
            
            if validation_result.get('warnings'):
                report.append("\nWARNINGS:")
                report.append("-" * 80)
                for i, w in enumerate(validation_result['warnings'], 1):
                    report.append(f"\n{i}. {w['message']}")
                    report.append(f"   Focus Node: {w['focus_node']}")
            
            report.append("\n" + "=" * 80)
            return "\n".join(report)
        
        elif output_format == 'html':
            # Simple HTML report
            html = ['<html><head><title>Validation Report</title></head><body>']
            html.append('<h1>SHACL Validation Report</h1>')
            status = 'PASSED' if validation_result['conforms'] else 'FAILED'
            color = 'green' if validation_result['conforms'] else 'red'
            html.append(f'<p style="color: {color}; font-weight: bold;">Status: {status}</p>')
            html.append(f'<p>Violations: {validation_result.get("total_violations", 0)}</p>')
            html.append(f'<p>Warnings: {validation_result.get("total_warnings", 0)}</p>')
            
            if validation_result.get('violations'):
                html.append('<h2>Violations</h2>')
                html.append('<ul>')
                for v in validation_result['violations']:
                    html.append(f'<li>{v["message"]}<br/>')
                    html.append(f'<small>Focus: {v["focus_node"]}</small></li>')
                html.append('</ul>')
            
            html.append('</body></html>')
            return ''.join(html)
        
        return str(validation_result)

    def get_shape_statistics(self) -> Dict:
        """
        Get statistics about loaded SHACL shapes.

        Returns:
            Dictionary with shape statistics
        """
        from rdflib.namespace import SH
        
        stats = {
            'total_shapes': len(list(self.shapes_graph.subjects(None, SH.NodeShape))),
            'property_shapes': 0,
            'constraints': 0
        }
        
        # Count property shapes and constraints
        query = """
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            
            SELECT 
                (COUNT(DISTINCT ?propShape) AS ?propShapeCount)
                (COUNT(DISTINCT ?constraint) AS ?constraintCount)
            WHERE {
                {
                    ?nodeShape sh:property ?propShape .
                } UNION {
                    ?shape ?constraintType ?constraint .
                    FILTER (
                        ?constraintType IN (
                            sh:minCount, sh:maxCount, sh:pattern, 
                            sh:minLength, sh:maxLength, sh:datatype,
                            sh:class, sh:in, sh:minInclusive, sh:maxInclusive
                        )
                    )
                }
            }
        """
        
        for row in self.shapes_graph.query(query):
            stats['property_shapes'] = int(row.propShapeCount)
            stats['constraints'] = int(row.constraintCount)
        
        return stats


if __name__ == "__main__":
    # Example usage
    validator = DataValidator()
    
    # Load shapes
    shapes_dir = Path(__file__).parent.parent.parent / "validation"
    validator.load_all_shapes(shapes_dir)
    
    # Get statistics
    stats = validator.get_shape_statistics()
    print("\nSHACL Shape Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
