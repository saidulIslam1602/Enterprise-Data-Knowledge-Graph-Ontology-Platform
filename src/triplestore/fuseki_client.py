"""
Apache Jena Fuseki Client

Provides interface for interacting with Jena Fuseki triplestore,
following W3C standards for RDF and SPARQL operations.
"""

import logging
from typing import Optional, Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
from rdflib import Graph
import time

logger = logging.getLogger(__name__)


class JenaFusekiClient:
    """Apache Jena Fuseki triple store client with W3C SPARQL 1.1 support."""
    
    def __init__(
        self,
        fuseki_url: str = "http://localhost:3030",
        dataset: str = "enterprise_kg",
        username: str = "admin",
        password: str = "admin123"
    ):
        """
        Initialize Fuseki client.
        
        Args:
            fuseki_url: Base URL of Fuseki server
            dataset: Dataset name in Fuseki
            username: Admin username
            password: Admin password
        """
        self.fuseki_url = fuseki_url.rstrip('/')
        self.dataset = dataset
        self.auth = HTTPBasicAuth(username, password)
        
        # SPARQL endpoints
        self.query_endpoint = f"{self.fuseki_url}/{dataset}/query"
        self.update_endpoint = f"{self.fuseki_url}/{dataset}/update"
        self.data_endpoint = f"{self.fuseki_url}/{dataset}/data"
        self.upload_endpoint = f"{self.fuseki_url}/{dataset}/upload"
        
        logger.info(f"Initialized Fuseki client for dataset: {dataset}")
    
    def create_dataset(self) -> bool:
        """
        Create a new dataset in Fuseki.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.fuseki_url}/$/datasets"
            data = {
                "dbName": self.dataset,
                "dbType": "tdb2"  # TDB2 is the recommended storage
            }
            
            response = requests.post(
                url,
                data=data,
                auth=self.auth
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Dataset '{self.dataset}' created successfully")
                return True
            elif response.status_code == 409:
                logger.info(f"Dataset '{self.dataset}' already exists")
                return True
            else:
                logger.error(f"Failed to create dataset: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            return False
    
    def upload_ontology(self, file_path: str, graph_uri: Optional[str] = None) -> bool:
        """
        Upload RDF ontology file to Fuseki.
        
        Args:
            file_path: Path to TTL/RDF file
            graph_uri: Optional named graph URI
            
        Returns:
            True if successful
        """
        try:
            url = self.data_endpoint
            if graph_uri:
                url = f"{url}?graph={graph_uri}"
            
            # Determine content type from file extension
            content_types = {
                '.ttl': 'text/turtle',
                '.rdf': 'application/rdf+xml',
                '.nt': 'application/n-triples',
                '.jsonld': 'application/ld+json'
            }
            
            file_ext = file_path[file_path.rfind('.'):]
            content_type = content_types.get(file_ext, 'text/turtle')
            
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url,
                    data=f,
                    headers={'Content-Type': content_type},
                    auth=self.auth
                )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully uploaded: {file_path}")
                return True
            else:
                logger.error(f"Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading ontology: {e}")
            return False
    
    def sparql_query(
        self,
        query: str,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Execute SPARQL SELECT/ASK/CONSTRUCT/DESCRIBE query.
        
        Args:
            query: SPARQL query string
            timeout: Query timeout in seconds
            
        Returns:
            Query results as dictionary
        """
        try:
            sparql = SPARQLWrapper(self.query_endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.setTimeout(timeout)
            
            # Add authentication
            sparql.setHTTPAuth(DIGEST)
            sparql.setCredentials(self.auth.username, self.auth.password)
            
            results = sparql.query().convert()
            
            logger.debug(f"Query executed successfully")
            return results
            
        except Exception as e:
            logger.error(f"SPARQL query error: {e}")
            return None
    
    def sparql_update(self, update: str) -> bool:
        """
        Execute SPARQL UPDATE (INSERT/DELETE) operation.
        
        Args:
            update: SPARQL UPDATE string
            
        Returns:
            True if successful
        """
        try:
            response = requests.post(
                self.update_endpoint,
                data={'update': update},
                auth=self.auth
            )
            
            if response.status_code in [200, 204]:
                logger.debug("Update executed successfully")
                return True
            else:
                logger.error(f"Update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"SPARQL update error: {e}")
            return False
    
    def insert_graph(self, graph: Graph, graph_uri: Optional[str] = None) -> bool:
        """
        Insert RDFLib graph into Fuseki.
        
        Args:
            graph: RDFLib Graph object
            graph_uri: Optional named graph URI
            
        Returns:
            True if successful
        """
        try:
            # Serialize graph to turtle
            ttl_data = graph.serialize(format='turtle')
            
            url = self.data_endpoint
            if graph_uri:
                url = f"{url}?graph={graph_uri}"
            
            response = requests.post(
                url,
                data=ttl_data,
                headers={'Content-Type': 'text/turtle'},
                auth=self.auth
            )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Inserted {len(graph)} triples")
                return True
            else:
                logger.error(f"Insert failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting graph: {e}")
            return False
    
    def get_graph(self, graph_uri: Optional[str] = None) -> Optional[Graph]:
        """
        Retrieve graph from Fuseki.
        
        Args:
            graph_uri: Optional named graph URI
            
        Returns:
            RDFLib Graph object
        """
        try:
            url = self.data_endpoint
            if graph_uri:
                url = f"{url}?graph={graph_uri}"
            
            response = requests.get(
                url,
                headers={'Accept': 'text/turtle'},
                auth=self.auth
            )
            
            if response.status_code == 200:
                graph = Graph()
                graph.parse(data=response.text, format='turtle')
                logger.info(f"Retrieved {len(graph)} triples")
                return graph
            else:
                logger.error(f"Retrieval failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving graph: {e}")
            return None
    
    def clear_graph(self, graph_uri: Optional[str] = None) -> bool:
        """
        Clear all triples from graph.
        
        Args:
            graph_uri: Optional named graph URI (if None, clears default graph)
            
        Returns:
            True if successful
        """
        try:
            if graph_uri:
                update = f"CLEAR GRAPH <{graph_uri}>"
            else:
                update = "CLEAR DEFAULT"
            
            return self.sparql_update(update)
            
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get dataset statistics.
        
        Returns:
            Statistics dictionary
        """
        query = """
        SELECT 
            (COUNT(*) AS ?tripleCount)
            (COUNT(DISTINCT ?s) AS ?subjects)
            (COUNT(DISTINCT ?p) AS ?predicates)
            (COUNT(DISTINCT ?o) AS ?objects)
        WHERE {
            ?s ?p ?o
        }
        """
        
        results = self.sparql_query(query)
        
        if results and 'results' in results:
            bindings = results['results']['bindings']
            if bindings:
                return {
                    'triple_count': int(bindings[0]['tripleCount']['value']),
                    'subjects': int(bindings[0]['subjects']['value']),
                    'predicates': int(bindings[0]['predicates']['value']),
                    'objects': int(bindings[0]['objects']['value'])
                }
        
        return None
    
    def health_check(self) -> bool:
        """
        Check if Fuseki server is healthy.
        
        Returns:
            True if server is accessible
        """
        try:
            response = requests.get(
                f"{self.fuseki_url}/$/ping",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def list_datasets(self) -> List[str]:
        """
        List all datasets on the server.
        
        Returns:
            List of dataset names
        """
        try:
            response = requests.get(
                f"{self.fuseki_url}/$/datasets",
                auth=self.auth
            )
            
            if response.status_code == 200:
                data = response.json()
                return [ds['ds.name'].replace('/', '') for ds in data.get('datasets', [])]
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []


# Singleton instance
_fuseki_client: Optional[JenaFusekiClient] = None


def get_fuseki_client(
    fuseki_url: str = "http://localhost:3030",
    dataset: str = "enterprise_kg"
) -> JenaFusekiClient:
    """
    Get or create Fuseki client singleton.
    
    Args:
        fuseki_url: Fuseki server URL
        dataset: Dataset name
        
    Returns:
        JenaFusekiClient instance
    """
    global _fuseki_client
    
    if _fuseki_client is None:
        _fuseki_client = JenaFusekiClient(fuseki_url, dataset)
    
    return _fuseki_client
