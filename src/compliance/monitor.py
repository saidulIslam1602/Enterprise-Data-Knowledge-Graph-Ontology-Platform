"""
Compliance Monitor

Monitors GDPR/CCPA compliance, consent management, and data subject rights.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ComplianceStatus:
    """Compliance status for a data subject or processing activity"""
    is_compliant: bool
    issues: List[str]
    warnings: List[str]
    last_checked: datetime


class ComplianceMonitor:
    """
    Monitors compliance with data protection regulations (GDPR, CCPA).
    """

    def __init__(self, graph: Graph):
        """
        Initialize Compliance Monitor.

        Args:
            graph: RDF graph containing compliance data
        """
        self.graph = graph
        self.comp_ns = Namespace("http://enterprise.org/ontology/compliance#")
        self.cus_ns = Namespace("http://enterprise.org/ontology/customer#")
        
        logger.info("ComplianceMonitor initialized")

    def check_gdpr_compliance(self, data_subject_id: str) -> ComplianceStatus:
        """
        Check GDPR compliance for a specific data subject.

        Args:
            data_subject_id: ID of the data subject

        Returns:
            ComplianceStatus object
        """
        issues = []
        warnings = []
        
        # Check if data subject exists
        subject_uri = URIRef(f"http://enterprise.org/data/customer/{data_subject_id}")
        
        # Check 1: Valid consent exists
        consent_query = f"""
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            PREFIX cus: <http://enterprise.org/ontology/customer#>
            
            SELECT ?consent ?status
            WHERE {{
                <{subject_uri}> comp:hasConsent ?consent .
                ?consent comp:consentStatus ?status .
            }}
        """
        
        consent_results = list(self.graph.query(consent_query))
        if not consent_results:
            issues.append("No consent records found (GDPR Article 6)")
        else:
            active_consents = [r for r in consent_results if str(r.status) == "ACTIVE"]
            if not active_consents:
                issues.append("No active consent found")
        
        # Check 2: Processing activities have legal basis
        processing_query = f"""
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?activity
            WHERE {{
                ?activity a comp:ProcessingActivity ;
                          comp:concernsDataSubject <{subject_uri}> .
                FILTER NOT EXISTS {{
                    ?activity comp:hasLegalBasis ?basis .
                }}
            }}
        """
        
        processing_results = list(self.graph.query(processing_query))
        if processing_results:
            issues.append(f"{len(processing_results)} processing activities without legal basis")
        
        # Check 3: Audit logs exist
        audit_query = f"""
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT (COUNT(?log) AS ?count)
            WHERE {{
                ?activity comp:concernsDataSubject <{subject_uri}> ;
                          comp:hasAuditLog ?log .
            }}
        """
        
        audit_results = list(self.graph.query(audit_query))
        if audit_results and int(audit_results[0].count) == 0:
            warnings.append("No audit logs found (GDPR Article 5 - accountability)")
        
        is_compliant = len(issues) == 0
        
        return ComplianceStatus(
            is_compliant=is_compliant,
            issues=issues,
            warnings=warnings,
            last_checked=datetime.now()
        )

    def check_consent_validity(self, consent_id: str) -> Dict:
        """
        Check if a consent record is valid and not expired.

        Args:
            consent_id: Consent ID to check

        Returns:
            Dictionary with validity status and details
        """
        query = f"""
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?status ?givenDate ?expiryDate ?method
            WHERE {{
                ?consent comp:consentId "{consent_id}" ;
                         comp:consentStatus ?status ;
                         comp:consentGivenDate ?givenDate ;
                         comp:consentMethod ?method .
                OPTIONAL {{ ?consent comp:consentExpiryDate ?expiryDate }}
            }}
        """
        
        results = list(self.graph.query(query))
        
        if not results:
            return {'valid': False, 'error': 'Consent not found'}
        
        result = results[0]
        status = str(result.status)
        
        validity = {
            'valid': status == "ACTIVE",
            'status': status,
            'given_date': str(result.givenDate),
            'method': str(result.method),
            'expiry_date': str(result.expiryDate) if result.expiryDate else None,
            'issues': []
        }
        
        # Check expiry
        if result.expiryDate:
            expiry = datetime.fromisoformat(str(result.expiryDate).replace('Z', '+00:00'))
            if expiry < datetime.now(expiry.tzinfo):
                validity['valid'] = False
                validity['issues'].append('Consent has expired')
        
        # Check method compliance (GDPR requires explicit consent for sensitive data)
        if str(result.method) not in ['EXPLICIT', 'OPT_IN']:
            validity['issues'].append('Consent method may not meet GDPR explicit consent requirement')
        
        return validity

    def get_overdue_dsr_requests(self, days_overdue: int = 0) -> List[Dict]:
        """
        Get Data Subject Rights requests that are overdue.

        Args:
            days_overdue: Minimum days overdue (0 = all overdue)

        Returns:
            List of overdue requests
        """
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?requestId ?rightName ?requestDate ?deadline ?status
            WHERE {
                ?request a comp:RightExerciseRequest ;
                         comp:requestId ?requestId ;
                         comp:requestDate ?requestDate ;
                         comp:responseDeadline ?deadline ;
                         comp:requestStatus ?status ;
                         comp:requestsRight ?right .
                ?right comp:rightName ?rightName .
                FILTER (?status != "COMPLETED")
                FILTER (?deadline < NOW())
            }
            ORDER BY ?deadline
        """
        
        results = list(self.graph.query(query))
        overdue_requests = []
        
        for row in results:
            deadline = datetime.fromisoformat(str(row.deadline).replace('Z', '+00:00'))
            days_diff = (datetime.now(deadline.tzinfo) - deadline).days
            
            if days_diff >= days_overdue:
                overdue_requests.append({
                    'request_id': str(row.requestId),
                    'right_name': str(row.rightName),
                    'request_date': str(row.requestDate),
                    'deadline': str(row.deadline),
                    'status': str(row.status),
                    'days_overdue': days_diff
                })
        
        return overdue_requests

    def get_expiring_consents(self, days_ahead: int = 30) -> List[Dict]:
        """
        Get consents expiring within specified days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of expiring consents
        """
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?consentId ?expiryDate ?purpose
            WHERE {
                ?consent a comp:Consent ;
                         comp:consentId ?consentId ;
                         comp:consentExpiryDate ?expiryDate ;
                         comp:consentStatus "ACTIVE" ;
                         comp:consentFor ?purposeNode .
                ?purposeNode comp:purposeName ?purpose .
                FILTER (?expiryDate > NOW())
            }
        """
        
        results = list(self.graph.query(query))
        expiring_consents = []
        
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for row in results:
            expiry = datetime.fromisoformat(str(row.expiryDate).replace('Z', '+00:00'))
            if expiry <= cutoff_date:
                days_until_expiry = (expiry - datetime.now(expiry.tzinfo)).days
                expiring_consents.append({
                    'consent_id': str(row.consentId),
                    'expiry_date': str(row.expiryDate),
                    'purpose': str(row.purpose),
                    'days_until_expiry': days_until_expiry
                })
        
        return sorted(expiring_consents, key=lambda x: x['days_until_expiry'])

    def check_data_breach_notification(self, incident_id: str) -> Dict:
        """
        Check if a data breach requires regulatory notification (GDPR 72-hour rule).

        Args:
            incident_id: Data breach incident ID

        Returns:
            Dictionary with notification requirements
        """
        query = f"""
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?incidentDate ?severity ?affectedRecords ?notificationRequired
            WHERE {{
                ?incident comp:incidentId "{incident_id}" ;
                          comp:incidentDate ?incidentDate ;
                          comp:incidentSeverity ?severity ;
                          comp:affectedRecordsCount ?affectedRecords ;
                          comp:notificationRequired ?notificationRequired .
            }}
        """
        
        results = list(self.graph.query(query))
        
        if not results:
            return {'error': 'Incident not found'}
        
        row = results[0]
        incident_date = datetime.fromisoformat(str(row.incidentDate).replace('Z', '+00:00'))
        hours_since = (datetime.now(incident_date.tzinfo) - incident_date).total_seconds() / 3600
        
        notification = {
            'incident_id': incident_id,
            'incident_date': str(row.incidentDate),
            'severity': str(row.severity),
            'affected_records': int(row.affectedRecords),
            'notification_required': bool(row.notificationRequired),
            'hours_since_incident': round(hours_since, 2),
            'within_72h_window': hours_since <= 72,
            'status': 'COMPLIANT' if hours_since <= 72 else 'OVERDUE'
        }
        
        # GDPR Article 33: Notification within 72 hours
        if bool(row.notificationRequired) and hours_since > 72:
            notification['warning'] = 'GDPR Article 33 violation: Notification overdue (72h requirement)'
        
        return notification

    def generate_compliance_report(self) -> Dict:
        """
        Generate a comprehensive compliance report.

        Returns:
            Dictionary with compliance metrics
        """
        report = {
            'report_date': datetime.now().isoformat(),
            'consent_summary': self._get_consent_summary(),
            'dsr_summary': self._get_dsr_summary(),
            'breach_summary': self._get_breach_summary(),
            'processing_activities': self._get_processing_activity_count()
        }
        
        return report

    def _get_consent_summary(self) -> Dict:
        """Get consent statistics."""
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?status (COUNT(?consent) AS ?count)
            WHERE {
                ?consent a comp:Consent ;
                         comp:consentStatus ?status .
            }
            GROUP BY ?status
        """
        
        results = list(self.graph.query(query))
        summary = {str(row.status): int(row.count) for row in results}
        summary['total'] = sum(summary.values())
        
        return summary

    def _get_dsr_summary(self) -> Dict:
        """Get Data Subject Rights request statistics."""
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?status (COUNT(?request) AS ?count)
            WHERE {
                ?request a comp:RightExerciseRequest ;
                         comp:requestStatus ?status .
            }
            GROUP BY ?status
        """
        
        results = list(self.graph.query(query))
        summary = {str(row.status): int(row.count) for row in results}
        summary['total'] = sum(summary.values())
        
        # Add overdue count
        overdue = self.get_overdue_dsr_requests()
        summary['overdue'] = len(overdue)
        
        return summary

    def _get_breach_summary(self) -> Dict:
        """Get data breach incident statistics."""
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT ?severity (COUNT(?incident) AS ?count)
            WHERE {
                ?incident a comp:DataBreachIncident ;
                          comp:incidentSeverity ?severity .
            }
            GROUP BY ?severity
        """
        
        results = list(self.graph.query(query))
        summary = {str(row.severity): int(row.count) for row in results}
        summary['total'] = sum(summary.values())
        
        return summary

    def _get_processing_activity_count(self) -> int:
        """Get count of processing activities."""
        query = """
            PREFIX comp: <http://enterprise.org/ontology/compliance#>
            
            SELECT (COUNT(?activity) AS ?count)
            WHERE {
                ?activity a comp:ProcessingActivity .
            }
        """
        
        results = list(self.graph.query(query))
        if results and len(results) > 0:
            # Access the count value from the result row
            count_val = results[0][0] if hasattr(results[0], '__getitem__') else results[0].count
            return int(count_val) if count_val else 0
        return 0


if __name__ == "__main__":
    # Example usage
    from rdflib import Graph
    
    g = Graph()
    monitor = ComplianceMonitor(g)
    
    # Generate report
    report = monitor.generate_compliance_report()
    print("\nCompliance Report:")
    print(f"Generated: {report['report_date']}")
    print(f"Processing Activities: {report['processing_activities']}")
