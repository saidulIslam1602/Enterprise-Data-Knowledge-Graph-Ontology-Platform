"""
Enhanced SHACL Validation Service

Provides comprehensive data quality assurance using SHACL (Shapes Constraint Language).
Follows W3C SHACL specification for RDF data validation.
"""

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SH, XSD
import pyshacl
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """SHACL validation severity levels."""
    VIOLATION = "Violation"
    WARNING = "Warning"
    INFO = "Info"


class SHACLValidationService:
    """
    Enhanced SHACL validation service for data quality assurance.
    
    Features:
    - W3C SHACL Core and SHACL-AF validation
    - Custom validation reports
    - Quality metrics
    - Validation history tracking
    """
    
    def __init__(self):
        """Initialize SHACL validation service."""
        self.validation_history: List[Dict[str, Any]] = []
        self.SH = SH
        logger.info("Initialized SHACL validation service")
    
    def validate(
        self,
        data_graph: Graph,
        shapes_graph: Graph,
        inference: str = 'rdfs',
        abort_on_first: bool = False,
        advanced: bool = True
    ) -> Dict[str, Any]:
        """
        Validate RDF data against SHACL shapes.
        
        Args:
            data_graph: Graph containing data to validate
            shapes_graph: Graph containing SHACL shapes
            inference: Inference engine ('rdfs', 'owlrl', 'both', 'none')
            abort_on_first: Stop on first violation
            advanced: Use SHACL Advanced Features
            
        Returns:
            Validation report dictionary
        """
        logger.info("Starting SHACL validation...")
        start_time = datetime.now()
        
        try:
            # Perform validation
            conforms, results_graph, results_text = pyshacl.validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference=inference,
                abort_on_first=abort_on_first,
                advanced=advanced,
                meta_shacl=False,
                debug=False
            )
            
            # Parse validation results
            violations = self._parse_validation_results(results_graph)
            
            # Create comprehensive report
            report = {
                'conforms': conforms,
                'timestamp': start_time.isoformat(),
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'data_triples': len(data_graph),
                'shapes_triples': len(shapes_graph),
                'violations': violations,
                'violation_count': len([v for v in violations if v['severity'] == 'Violation']),
                'warning_count': len([v for v in violations if v['severity'] == 'Warning']),
                'info_count': len([v for v in violations if v['severity'] == 'Info']),
                'inference': inference,
                'results_text': results_text
            }
            
            # Store in history
            self.validation_history.append({
                'timestamp': report['timestamp'],
                'conforms': conforms,
                'violation_count': report['violation_count']
            })
            
            logger.info(
                f"Validation {'passed' if conforms else 'failed'}: "
                f"{report['violation_count']} violations, "
                f"{report['warning_count']} warnings"
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                'conforms': False,
                'error': str(e),
                'timestamp': start_time.isoformat()
            }
    
    def validate_from_files(
        self,
        data_file: str,
        shapes_file: str,
        data_format: str = 'turtle',
        shapes_format: str = 'turtle'
    ) -> Dict[str, Any]:
        """
        Validate RDF files.
        
        Args:
            data_file: Path to data file
            shapes_file: Path to shapes file
            data_format: Data file format
            shapes_format: Shapes file format
            
        Returns:
            Validation report
        """
        # Load graphs
        data_graph = Graph()
        data_graph.parse(data_file, format=data_format)
        
        shapes_graph = Graph()
        shapes_graph.parse(shapes_file, format=shapes_format)
        
        return self.validate(data_graph, shapes_graph)
    
    def _parse_validation_results(self, results_graph: Graph) -> List[Dict[str, Any]]:
        """
        Parse SHACL validation results graph.
        
        Args:
            results_graph: Graph containing validation results
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        # Query for validation results
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        
        SELECT ?result ?focusNode ?path ?value ?message ?severity ?sourceShape ?sourceConstraintComponent
        WHERE {
            ?result a sh:ValidationResult ;
                    sh:focusNode ?focusNode ;
                    sh:resultSeverity ?severity .
            
            OPTIONAL { ?result sh:resultPath ?path }
            OPTIONAL { ?result sh:value ?value }
            OPTIONAL { ?result sh:resultMessage ?message }
            OPTIONAL { ?result sh:sourceShape ?sourceShape }
            OPTIONAL { ?result sh:sourceConstraintComponent ?sourceConstraintComponent }
        }
        """
        
        for row in results_graph.query(query):
            violation = {
                'focus_node': str(row.focusNode) if row.focusNode else None,
                'path': str(row.path) if row.path else None,
                'value': str(row.value) if row.value else None,
                'message': str(row.message) if row.message else "Constraint violation",
                'severity': self._parse_severity(row.severity),
                'source_shape': str(row.sourceShape) if row.sourceShape else None,
                'constraint_component': str(row.sourceConstraintComponent) if row.sourceConstraintComponent else None
            }
            violations.append(violation)
        
        return violations
    
    def _parse_severity(self, severity_uri) -> str:
        """Parse severity URI to human-readable string."""
        severity_str = str(severity_uri)
        if 'Violation' in severity_str:
            return 'Violation'
        elif 'Warning' in severity_str:
            return 'Warning'
        elif 'Info' in severity_str:
            return 'Info'
        return 'Unknown'
    
    def create_quality_report(
        self,
        validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create data quality metrics report.
        
        Args:
            validation_report: Validation report from validate()
            
        Returns:
            Quality metrics dictionary
        """
        if not validation_report.get('conforms'):
            violations = validation_report.get('violations', [])
            
            # Group violations by type
            violation_types = {}
            for v in violations:
                constraint = v.get('constraint_component', 'Unknown')
                if constraint not in violation_types:
                    violation_types[constraint] = []
                violation_types[constraint].append(v)
            
            # Group violations by severity
            by_severity = {
                'Violation': [v for v in violations if v['severity'] == 'Violation'],
                'Warning': [v for v in violations if v['severity'] == 'Warning'],
                'Info': [v for v in violations if v['severity'] == 'Info']
            }
            
            # Calculate quality score (0-100)
            total_issues = len(violations)
            violation_weight = 1.0
            warning_weight = 0.5
            info_weight = 0.1
            
            weighted_issues = (
                len(by_severity['Violation']) * violation_weight +
                len(by_severity['Warning']) * warning_weight +
                len(by_severity['Info']) * info_weight
            )
            
            # Quality score (100 - penalties)
            quality_score = max(0, 100 - (weighted_issues * 2))
            
            quality_report = {
                'quality_score': round(quality_score, 2),
                'conforms': validation_report['conforms'],
                'total_issues': total_issues,
                'by_severity': {
                    'violations': len(by_severity['Violation']),
                    'warnings': len(by_severity['Warning']),
                    'info': len(by_severity['Info'])
                },
                'by_constraint_type': {
                    constraint: len(violations)
                    for constraint, violations in violation_types.items()
                },
                'most_common_issues': sorted(
                    violation_types.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:5],
                'timestamp': validation_report['timestamp']
            }
        else:
            quality_report = {
                'quality_score': 100.0,
                'conforms': True,
                'total_issues': 0,
                'by_severity': {
                    'violations': 0,
                    'warnings': 0,
                    'info': 0
                },
                'timestamp': validation_report['timestamp']
            }
        
        return quality_report
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """
        Get validation history.
        
        Returns:
            List of historical validation results
        """
        return self.validation_history
    
    def export_validation_report(
        self,
        validation_report: Dict[str, Any],
        output_file: str,
        format: str = 'json'
    ):
        """
        Export validation report to file.
        
        Args:
            validation_report: Validation report dictionary
            output_file: Output file path
            format: Export format ('json', 'html', 'csv')
        """
        import json
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(validation_report, f, indent=2)
            logger.info(f"Exported validation report to {output_file}")
        
        elif format == 'html':
            html_content = self._generate_html_report(validation_report)
            with open(output_file, 'w') as f:
                f.write(html_content)
            logger.info(f"Exported HTML report to {output_file}")
        
        elif format == 'csv':
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['focus_node', 'path', 'value', 'message', 'severity']
                )
                writer.writeheader()
                for violation in validation_report.get('violations', []):
                    writer.writerow({
                        'focus_node': violation.get('focus_node', ''),
                        'path': violation.get('path', ''),
                        'value': violation.get('value', ''),
                        'message': violation.get('message', ''),
                        'severity': violation.get('severity', '')
                    })
            logger.info(f"Exported CSV report to {output_file}")
    
    def _generate_html_report(self, validation_report: Dict[str, Any]) -> str:
        """Generate HTML validation report."""
        conforms = validation_report.get('conforms', False)
        violations = validation_report.get('violations', [])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SHACL Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: {'#4CAF50' if conforms else '#f44336'}; color: white; padding: 20px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f5f5f5; padding: 15px; border-radius: 5px; flex: 1; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        .violation {{ background: #ffebee; }}
        .warning {{ background: #fff3e0; }}
        .info {{ background: #e3f2fd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SHACL Validation Report</h1>
        <p>Status: {'✓ PASSED' if conforms else '✗ FAILED'}</p>
        <p>Generated: {validation_report.get('timestamp', '')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Total Issues</h3>
            <h2>{len(violations)}</h2>
        </div>
        <div class="stat-card">
            <h3>Violations</h3>
            <h2>{validation_report.get('violation_count', 0)}</h2>
        </div>
        <div class="stat-card">
            <h3>Warnings</h3>
            <h2>{validation_report.get('warning_count', 0)}</h2>
        </div>
        <div class="stat-card">
            <h3>Info</h3>
            <h2>{validation_report.get('info_count', 0)}</h2>
        </div>
    </div>
    
    <h2>Validation Results</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Focus Node</th>
            <th>Property Path</th>
            <th>Value</th>
            <th>Message</th>
        </tr>
"""
        
        for v in violations:
            severity_class = v['severity'].lower()
            html += f"""
        <tr class="{severity_class}">
            <td>{v['severity']}</td>
            <td>{v.get('focus_node', '')[:50]}...</td>
            <td>{v.get('path', 'N/A')}</td>
            <td>{v.get('value', 'N/A')[:30]}</td>
            <td>{v['message']}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html


def create_basic_shapes(namespace: str) -> Graph:
    """
    Create basic SHACL shapes for common validations.
    
    Args:
        namespace: Base namespace for shapes
        
    Returns:
        Graph containing SHACL shapes
    """
    shapes = Graph()
    NS = Namespace(namespace)
    
    shapes.bind("sh", SH)
    shapes.bind("ns", NS)
    
    # Example: Person shape
    person_shape = NS.PersonShape
    shapes.add((person_shape, RDF.type, SH.NodeShape))
    shapes.add((person_shape, SH.targetClass, NS.Person))
    
    # Required name property
    name_property = URIRef(f"{person_shape}#nameProperty")
    shapes.add((person_shape, SH.property, name_property))
    shapes.add((name_property, SH.path, NS.hasName))
    shapes.add((name_property, SH.minCount, Literal(1)))
    shapes.add((name_property, SH.datatype, XSD.string))
    shapes.add((name_property, SH.message, Literal("Person must have a name")))
    
    # Optional email with pattern
    email_property = URIRef(f"{person_shape}#emailProperty")
    shapes.add((person_shape, SH.property, email_property))
    shapes.add((email_property, SH.path, NS.hasEmail))
    shapes.add((email_property, SH.pattern, Literal(r'^[\w\.-]+@[\w\.-]+\.\w+$')))
    shapes.add((email_property, SH.message, Literal("Invalid email format")))
    
    return shapes
