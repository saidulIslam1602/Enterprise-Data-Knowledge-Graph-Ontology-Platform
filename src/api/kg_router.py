"""
Enhanced API Routers for Knowledge Graph Platform

Provides REST API endpoints for advanced W3C-compliant operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query as QueryParam
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from pathlib import Path
import tempfile
import logging

from rdflib import Graph

from ..core.w3c_rdf_service import W3CCompliantRDFService
from ..core.sparql_service import AdvancedSPARQLService
from ..core.shacl_validator import SHACLValidationService
from ..core.data_harmonization import DataHarmonizationService
from ..triplestore.fuseki_client import get_fuseki_client

logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api/v1/kg", tags=["knowledge-graph"])


# Pydantic Models
class SPARQLQueryRequest(BaseModel):
    query: str
    use_cache: bool = False
    timeout: int = 30


class ValidationRequest(BaseModel):
    shapes_file: str
    data_format: str = "turtle"
    shapes_format: str = "turtle"
    inference: str = "rdfs"


class HarmonizationRequest(BaseModel):
    source_ontology_id: str
    data_format: str = "turtle"
    provenance: Optional[Dict[str, str]] = None


class MappingRuleRequest(BaseModel):
    source_ontology: str
    source_class: str
    target_class: str
    property_mappings: Dict[str, str]


class EntitySearchRequest(BaseModel):
    search_text: str
    property_paths: Optional[List[str]] = None
    case_sensitive: bool = False
    limit: int = 100


# Initialize services
rdf_service = W3CCompliantRDFService()
sparql_service = None  # Will be initialized with graph
shacl_service = SHACLValidationService()
harmonization_service = DataHarmonizationService("https://enterprise-kg.local/harmonized/")


@router.on_event("startup")
async def startup():
    """Initialize services on startup."""
    global sparql_service
    logger.info("Initializing Knowledge Graph API services...")


# ========== W3C RDF Service Endpoints ==========

@router.get("/ontology/metadata")
async def get_ontology_metadata():
    """Get W3C-compliant ontology metadata."""
    try:
        stats = rdf_service.get_statistics()
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ontology/create-class")
async def create_ontology_class(
    class_uri: str,
    label: str,
    comment: str,
    parent_class: Optional[str] = None
):
    """Define a new OWL class with RDFS annotations."""
    try:
        cls = rdf_service.define_class(class_uri, label, comment, parent_class)
        return {
            "status": "success",
            "class_uri": str(cls),
            "message": "Class created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating class: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ontology/create-property")
async def create_ontology_property(
    property_uri: str,
    label: str,
    comment: str,
    property_type: str = "ObjectProperty",
    domain: Optional[str] = None,
    range_: Optional[str] = None
):
    """Define a new OWL property."""
    try:
        prop = rdf_service.define_property(
            property_uri, label, comment, property_type, domain, range_
        )
        return {
            "status": "success",
            "property_uri": str(prop),
            "message": "Property created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating property: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ontology/reasoning/rdfs")
async def apply_rdfs_reasoning():
    """Apply RDFS reasoning to infer implicit triples."""
    try:
        original_count = len(rdf_service.graph)
        rdf_service.apply_rdfs_reasoning()
        new_count = len(rdf_service.graph)
        inferred = new_count - original_count
        
        return {
            "status": "success",
            "original_triples": original_count,
            "inferred_triples": inferred,
            "total_triples": new_count
        }
    except Exception as e:
        logger.error(f"Error applying reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ontology/reasoning/owl")
async def apply_owl_reasoning(profile: str = "OWL_RL"):
    """Apply OWL 2 reasoning to infer implicit triples."""
    try:
        original_count = len(rdf_service.graph)
        rdf_service.apply_owl_reasoning(profile)
        new_count = len(rdf_service.graph)
        inferred = new_count - original_count
        
        return {
            "status": "success",
            "profile": profile,
            "original_triples": original_count,
            "inferred_triples": inferred,
            "total_triples": new_count
        }
    except Exception as e:
        logger.error(f"Error applying OWL reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ontology/class-hierarchy")
async def get_class_hierarchy():
    """Extract OWL class hierarchy from the graph."""
    try:
        hierarchy = rdf_service.get_class_hierarchy()
        return {
            "status": "success",
            "hierarchy": hierarchy
        }
    except Exception as e:
        logger.error(f"Error getting hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ontology/validate-w3c")
async def validate_w3c_compliance():
    """Validate graph for W3C standards compliance."""
    try:
        report = rdf_service.validate_w3c_compliance()
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        logger.error(f"Error validating compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Advanced SPARQL Endpoints ==========

@router.post("/sparql/query")
async def execute_sparql_query(request: SPARQLQueryRequest):
    """Execute advanced SPARQL query with caching support."""
    try:
        # Use local graph or endpoint
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        results = sparql_service.query(
            request.query,
            use_cache=request.use_cache,
            timeout=request.timeout
        )
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"SPARQL query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/find-paths")
async def find_resource_paths(
    start_uri: str,
    end_uri: str,
    predicate: Optional[str] = None,
    max_length: int = 5
):
    """Find all paths between two resources using property paths."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        paths = sparql_service.find_paths(start_uri, end_uri, predicate, max_length)
        
        return {
            "status": "success",
            "start": start_uri,
            "end": end_uri,
            "paths": paths,
            "count": len(paths)
        }
    except Exception as e:
        logger.error(f"Error finding paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/connected-resources")
async def get_connected_resources(
    resource_uri: str,
    depth: int = 2,
    predicate: Optional[str] = None
):
    """Find all resources connected to a given resource."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        connected = sparql_service.find_connected_resources(resource_uri, depth, predicate)
        
        return {
            "status": "success",
            "resource": resource_uri,
            "depth": depth,
            "connected_resources": connected,
            "count": len(connected)
        }
    except Exception as e:
        logger.error(f"Error finding connected resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/aggregate")
async def aggregate_statistics(
    subject_class: str,
    property_path: str,
    aggregation: str = "COUNT"
):
    """Perform aggregation queries (COUNT, SUM, AVG, MIN, MAX)."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        stats = sparql_service.aggregate_statistics(subject_class, property_path, aggregation)
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error in aggregation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sparql/search")
async def search_by_text(request: EntitySearchRequest):
    """Full-text search across RDF properties."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        results = sparql_service.search_by_text(
            request.search_text,
            request.property_paths,
            request.case_sensitive
        )
        
        return {
            "status": "success",
            "search_term": request.search_text,
            "results": results[:request.limit],
            "total_found": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/class-instances")
async def get_class_instances_count():
    """Count instances for each class in the graph."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        counts = sparql_service.get_class_instances_count()
        
        return {
            "status": "success",
            "class_counts": counts
        }
    except Exception as e:
        logger.error(f"Error counting instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/property-usage")
async def get_property_usage_stats():
    """Get usage statistics for all properties."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        stats = sparql_service.get_property_usage_stats()
        
        return {
            "status": "success",
            "property_statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting property stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sparql/statistics")
async def get_query_statistics():
    """Get SPARQL query execution statistics."""
    try:
        global sparql_service
        if sparql_service is None:
            sparql_service = AdvancedSPARQLService(rdf_service.graph)
        
        stats = sparql_service.get_query_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== SHACL Validation Endpoints ==========

@router.post("/validation/validate-file")
async def validate_rdf_file(
    data_file: UploadFile = File(...),
    shapes_file: UploadFile = File(...)
):
    """Validate RDF data file against SHACL shapes file."""
    try:
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl") as data_temp:
            data_temp.write(await data_file.read())
            data_path = data_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl") as shapes_temp:
            shapes_temp.write(await shapes_file.read())
            shapes_path = shapes_temp.name
        
        # Validate
        validation_report = shacl_service.validate_from_files(data_path, shapes_path)
        
        # Clean up
        Path(data_path).unlink()
        Path(shapes_path).unlink()
        
        return {
            "status": "success",
            "validation_report": validation_report
        }
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validation/quality-report")
async def generate_quality_report(validation_report: Dict[str, Any]):
    """Generate data quality metrics report from validation results."""
    try:
        quality_report = shacl_service.create_quality_report(validation_report)
        
        return {
            "status": "success",
            "quality_report": quality_report
        }
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation/history")
async def get_validation_history():
    """Get validation history."""
    try:
        history = shacl_service.get_validation_history()
        
        return {
            "status": "success",
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Data Harmonization Endpoints ==========

@router.post("/harmonization/add-mapping")
async def add_mapping_rule(request: MappingRuleRequest):
    """Add schema mapping rule for data harmonization."""
    try:
        harmonization_service.add_mapping_rule(
            request.source_ontology,
            request.source_class,
            request.target_class,
            request.property_mappings
        )
        
        return {
            "status": "success",
            "message": "Mapping rule added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/harmonization/harmonize")
async def harmonize_data(
    request: HarmonizationRequest,
    data_file: UploadFile = File(...)
):
    """Harmonize data from uploaded file."""
    try:
        # Load source graph
        source_graph = Graph()
        content = await data_file.read()
        source_graph.parse(data=content, format=request.data_format)
        
        # Harmonize
        harmonized = harmonization_service.harmonize_graph(
            source_graph,
            request.source_ontology_id,
            request.provenance
        )
        
        return {
            "status": "success",
            "source_triples": len(source_graph),
            "harmonized_triples": len(harmonized),
            "message": "Data harmonized successfully"
        }
    except Exception as e:
        logger.error(f"Harmonization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/harmonization/conflicts")
async def detect_conflicts():
    """Detect conflicts in harmonized data."""
    try:
        conflicts = harmonization_service.detect_conflicts()
        
        return {
            "status": "success",
            "conflicts": conflicts,
            "count": len(conflicts)
        }
    except Exception as e:
        logger.error(f"Error detecting conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/harmonization/resolve-conflicts")
async def resolve_conflicts(strategy: str = "most_recent"):
    """Resolve conflicts in harmonized data."""
    try:
        resolved_count = harmonization_service.resolve_conflicts(strategy)
        
        return {
            "status": "success",
            "strategy": strategy,
            "resolved_count": resolved_count
        }
    except Exception as e:
        logger.error(f"Error resolving conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/harmonization/quality")
async def validate_harmonization_quality():
    """Validate harmonized data quality."""
    try:
        quality_report = harmonization_service.validate_data_quality()
        
        return {
            "status": "success",
            "quality_report": quality_report
        }
    except Exception as e:
        logger.error(f"Error validating quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/harmonization/statistics")
async def get_harmonization_statistics():
    """Get harmonization statistics."""
    try:
        stats = harmonization_service.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Triplestore Integration Endpoints ==========

@router.get("/triplestore/health")
async def check_triplestore_health():
    """Check Jena Fuseki health status."""
    try:
        client = get_fuseki_client()
        is_healthy = client.health_check()
        
        return {
            "status": "success",
            "healthy": is_healthy,
            "endpoint": client.fuseki_url
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triplestore/statistics")
async def get_triplestore_statistics():
    """Get triplestore dataset statistics."""
    try:
        client = get_fuseki_client()
        stats = client.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting triplestore stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triplestore/datasets")
async def list_datasets():
    """List all datasets in Fuseki."""
    try:
        client = get_fuseki_client()
        datasets = client.list_datasets()
        
        return {
            "status": "success",
            "datasets": datasets,
            "count": len(datasets)
        }
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
