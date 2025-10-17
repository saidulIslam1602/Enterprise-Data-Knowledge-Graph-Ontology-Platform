"""
FastAPI Server for Enterprise Knowledge Graph Platform

Provides REST API endpoints for querying, validation, and compliance monitoring.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from pathlib import Path
import logging

from ..core.graph_manager import GraphManager
from ..core.validator import DataValidator
from ..compliance.monitor import ComplianceMonitor

# Import new enhanced router
from .kg_router import router as kg_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise Knowledge Graph & Ontology Platform",
    description="W3C-compliant semantic data management platform with SPARQL, SHACL, and compliance monitoring",
    version="2.0.0"
)

# Include enhanced Knowledge Graph router
app.include_router(kg_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
graph_manager = None
validator = None
compliance_monitor = None


# Pydantic models
class SPARQLQuery(BaseModel):
    query: str
    format: str = "json"


class ValidationRequest(BaseModel):
    data: str
    format: str = "turtle"


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global graph_manager, validator, compliance_monitor
    
    logger.info("Starting Enterprise Knowledge Graph Platform...")
    
    # Initialize graph manager
    graph_manager = GraphManager()
    
    # Load ontologies
    ontology_dir = Path(__file__).parent.parent.parent / "ontologies"
    if ontology_dir.exists():
        graph_manager.load_all_ontologies(ontology_dir)
        logger.info(f"Loaded ontologies from {ontology_dir}")
    
    # Initialize validator
    shapes_dir = Path(__file__).parent.parent.parent / "validation"
    validator = DataValidator(shapes_dir if shapes_dir.exists() else None)
    
    # Initialize compliance monitor
    compliance_monitor = ComplianceMonitor(graph_manager.graph)
    
    logger.info("Platform started successfully")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Enterprise Knowledge Graph & Ontology Platform",
        "version": "2.0.0",
        "description": "W3C-compliant semantic knowledge graph platform",
        "technologies": [
            "RDF 1.1",
            "SPARQL 1.1",
            "SHACL",
            "OWL 2",
            "Apache Jena Fuseki",
            "Ontotext GraphDB"
        ],
        "endpoints": {
            "docs": "/docs",
            "statistics": "/api/v1/statistics",
            "query": "/api/v1/sparql/query",
            "validate": "/api/v1/validate",
            "compliance": "/api/v1/compliance/report",
            "knowledge_graph": "/api/v1/kg/*"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "graph_manager": graph_manager is not None,
            "validator": validator is not None,
            "compliance_monitor": compliance_monitor is not None
        }
    }


@app.get("/api/v1/statistics")
async def get_statistics():
    """Get knowledge graph statistics."""
    if not graph_manager:
        raise HTTPException(status_code=503, detail="Graph manager not initialized")
    
    try:
        stats = graph_manager.get_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sparql/query")
async def execute_sparql_query(query_request: SPARQLQuery):
    """
    Execute a SPARQL query on the knowledge graph.
    
    Args:
        query_request: SPARQLQuery object with query and format
    
    Returns:
        Query results in specified format
    """
    if not graph_manager:
        raise HTTPException(status_code=503, detail="Graph manager not initialized")
    
    try:
        results = graph_manager.execute_query(
            query_request.query,
            return_format=query_request.format
        )
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/ontology/classes")
async def get_classes():
    """Get all OWL classes defined in ontologies."""
    if not graph_manager:
        raise HTTPException(status_code=503, detail="Graph manager not initialized")
    
    try:
        classes = graph_manager.get_all_classes()
        return JSONResponse(content={"classes": classes, "count": len(classes)})
    except Exception as e:
        logger.error(f"Error getting classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ontology/properties")
async def get_properties():
    """Get all properties (object and data) from ontologies."""
    if not graph_manager:
        raise HTTPException(status_code=503, detail="Graph manager not initialized")
    
    try:
        properties = graph_manager.get_all_properties()
        return JSONResponse(content=properties)
    except Exception as e:
        logger.error(f"Error getting properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/validate")
async def validate_data(validation_request: ValidationRequest):
    """
    Validate RDF data against SHACL shapes.
    
    Args:
        validation_request: ValidationRequest with data and format
    
    Returns:
        Validation report
    """
    if not validator:
        raise HTTPException(status_code=503, detail="Validator not initialized")
    
    try:
        from rdflib import Graph
        
        # Parse data into graph
        data_graph = Graph()
        data_graph.parse(data=validation_request.data, format=validation_request.format)
        
        # Validate
        report = validator.validate_graph(data_graph)
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/validation/shapes/statistics")
async def get_shape_statistics():
    """Get SHACL shape statistics."""
    if not validator:
        raise HTTPException(status_code=503, detail="Validator not initialized")
    
    try:
        stats = validator.get_shape_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting shape statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/report")
async def get_compliance_report():
    """Get comprehensive compliance report."""
    if not compliance_monitor:
        raise HTTPException(status_code=503, detail="Compliance monitor not initialized")
    
    try:
        report = compliance_monitor.generate_compliance_report()
        return JSONResponse(content=report)
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/gdpr/{data_subject_id}")
async def check_gdpr_compliance(data_subject_id: str):
    """
    Check GDPR compliance for a data subject.
    
    Args:
        data_subject_id: Data subject ID
    
    Returns:
        Compliance status
    """
    if not compliance_monitor:
        raise HTTPException(status_code=503, detail="Compliance monitor not initialized")
    
    try:
        status = compliance_monitor.check_gdpr_compliance(data_subject_id)
        return JSONResponse(content={
            "data_subject_id": data_subject_id,
            "is_compliant": status.is_compliant,
            "issues": status.issues,
            "warnings": status.warnings,
            "last_checked": status.last_checked.isoformat()
        })
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/dsr/overdue")
async def get_overdue_dsr_requests(days_overdue: int = Query(0, ge=0)):
    """
    Get overdue Data Subject Rights requests.
    
    Args:
        days_overdue: Minimum days overdue (default: 0)
    
    Returns:
        List of overdue requests
    """
    if not compliance_monitor:
        raise HTTPException(status_code=503, detail="Compliance monitor not initialized")
    
    try:
        overdue_requests = compliance_monitor.get_overdue_dsr_requests(days_overdue)
        return JSONResponse(content={
            "count": len(overdue_requests),
            "requests": overdue_requests
        })
    except Exception as e:
        logger.error(f"Error getting overdue DSR requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/consents/expiring")
async def get_expiring_consents(days_ahead: int = Query(30, ge=1, le=365)):
    """
    Get consents expiring within specified days.
    
    Args:
        days_ahead: Number of days to look ahead (1-365)
    
    Returns:
        List of expiring consents
    """
    if not compliance_monitor:
        raise HTTPException(status_code=503, detail="Compliance monitor not initialized")
    
    try:
        expiring = compliance_monitor.get_expiring_consents(days_ahead)
        return JSONResponse(content={
            "count": len(expiring),
            "days_ahead": days_ahead,
            "consents": expiring
        })
    except Exception as e:
        logger.error(f"Error getting expiring consents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/compliance/breach/{incident_id}")
async def check_breach_notification(incident_id: str):
    """
    Check data breach notification requirements.
    
    Args:
        incident_id: Data breach incident ID
    
    Returns:
        Notification requirements and status
    """
    if not compliance_monitor:
        raise HTTPException(status_code=503, detail="Compliance monitor not initialized")
    
    try:
        notification = compliance_monitor.check_data_breach_notification(incident_id)
        if 'error' in notification:
            raise HTTPException(status_code=404, detail=notification['error'])
        return JSONResponse(content=notification)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking breach notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
