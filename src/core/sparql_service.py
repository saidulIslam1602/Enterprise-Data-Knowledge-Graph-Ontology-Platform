"""
Advanced SPARQL Query Service

Provides sophisticated SPARQL 1.1 querying capabilities including:
- Property paths
- Aggregations
- Federated queries
- Named graphs
- Complex filtering
- Query optimization
"""

import logging
from typing import Optional, Dict, Any, List, Union
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.processor import SPARQLResult
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF as SPARQL_RDF
import time

logger = logging.getLogger(__name__)


class AdvancedSPARQLService:
    """
    Advanced SPARQL 1.1 query service with support for complex operations.
    
    Features:
    - Property paths for transitive queries
    - Aggregation functions (COUNT, SUM, AVG, MIN, MAX)
    - Federated queries (SERVICE)
    - Named graph operations
    - OPTIONAL, UNION, MINUS
    - Query result caching
    - Performance monitoring
    """
    
    def __init__(self, graph: Optional[Graph] = None, endpoint: Optional[str] = None):
        """
        Initialize SPARQL service.
        
        Args:
            graph: RDFLib Graph for local queries
            endpoint: SPARQL endpoint URL for remote queries
        """
        self.graph = graph or Graph()
        self.endpoint = endpoint
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: List[Dict[str, Any]] = []
        
        logger.info("Initialized Advanced SPARQL service")
    
    def query(
        self,
        query_string: str,
        use_cache: bool = False,
        timeout: int = 30
    ) -> Optional[Union[List[Dict[str, Any]], SPARQLResult]]:
        """
        Execute SPARQL query (SELECT, ASK, CONSTRUCT, DESCRIBE).
        
        Args:
            query_string: SPARQL query
            use_cache: Enable query result caching
            timeout: Query timeout in seconds
            
        Returns:
            Query results as list of dictionaries or SPARQLResult
        """
        # Check cache
        if use_cache and query_string in self.query_cache:
            logger.debug("Returning cached query result")
            return self.query_cache[query_string]
        
        start_time = time.time()
        
        try:
            if self.endpoint:
                # Remote SPARQL endpoint
                results = self._query_endpoint(query_string, timeout)
            else:
                # Local RDFLib graph
                results = self._query_local(query_string)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Store statistics
            self.query_stats.append({
                'query': query_string[:100],
                'execution_time_ms': execution_time,
                'timestamp': time.time(),
                'result_count': len(results) if isinstance(results, list) else None
            })
            
            # Cache results
            if use_cache:
                self.query_cache[query_string] = results
            
            logger.info(f"Query executed in {execution_time:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    def _query_local(self, query_string: str) -> List[Dict[str, Any]]:
        """Execute query on local RDFLib graph."""
        results = self.graph.query(query_string)
        
        # Convert to list of dictionaries
        result_list = []
        for row in results:
            row_dict = {}
            for var in results.vars:
                value = getattr(row, str(var), None)
                row_dict[str(var)] = str(value) if value else None
            result_list.append(row_dict)
        
        return result_list
    
    def _query_endpoint(self, query_string: str, timeout: int) -> List[Dict[str, Any]]:
        """Execute query on remote SPARQL endpoint."""
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setQuery(query_string)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(timeout)
        
        results = sparql.query().convert()
        
        # Parse JSON results
        if 'results' in results and 'bindings' in results['results']:
            return [
                {k: v.get('value') for k, v in binding.items()}
                for binding in results['results']['bindings']
            ]
        
        return []
    
    def find_paths(
        self,
        start_uri: str,
        end_uri: str,
        predicate: Optional[str] = None,
        max_length: int = 5
    ) -> List[List[str]]:
        """
        Find all paths between two resources using property paths.
        
        Args:
            start_uri: Starting resource URI
            end_uri: Ending resource URI
            predicate: Optional specific predicate to follow
            max_length: Maximum path length
            
        Returns:
            List of paths (each path is a list of URIs)
        """
        if predicate:
            # Specific predicate path
            path_pattern = f"<{predicate}>{{1,{max_length}}}"
        else:
            # Any predicate path
            path_pattern = f"!<>{{1,{max_length}}}"
        
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?intermediate
        WHERE {{
            <{start_uri}> {path_pattern} ?intermediate .
            ?intermediate {path_pattern} <{end_uri}> .
        }}
        LIMIT 100
        """
        
        results = self.query(query)
        
        if results:
            return [[start_uri, r.get('intermediate'), end_uri] for r in results]
        return []
    
    def find_connected_resources(
        self,
        resource_uri: str,
        depth: int = 2,
        predicate: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all resources connected to a given resource up to specified depth.
        
        Args:
            resource_uri: Resource URI
            depth: Connection depth (1-5)
            predicate: Optional specific predicate
            
        Returns:
            List of connected resources with their predicates
        """
        if predicate:
            path_pattern = f"<{predicate}>{{1,{depth}}}"
        else:
            path_pattern = f"!<>{{1,{depth}}}"
        
        query = f"""
        SELECT DISTINCT ?connected ?predicate ?label
        WHERE {{
            {{
                <{resource_uri}> {path_pattern} ?connected .
            }} UNION {{
                ?connected {path_pattern} <{resource_uri}> .
            }}
            
            OPTIONAL {{ ?connected rdfs:label ?label }}
        }}
        LIMIT 500
        """
        
        return self.query(query) or []
    
    def aggregate_statistics(
        self,
        subject_class: str,
        property_path: str,
        aggregation: str = "COUNT"
    ) -> Dict[str, Any]:
        """
        Perform aggregation queries (COUNT, SUM, AVG, MIN, MAX).
        
        Args:
            subject_class: Class of subjects
            property_path: Property to aggregate
            aggregation: Aggregation function
            
        Returns:
            Aggregation results
        """
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT 
            ({aggregation}(?value) AS ?result)
            (COUNT(DISTINCT ?subject) AS ?count)
        WHERE {{
            ?subject a <{subject_class}> ;
                     <{property_path}> ?value .
        }}
        """
        
        results = self.query(query)
        
        if results and len(results) > 0:
            return {
                'aggregation': aggregation,
                'result': results[0].get('result'),
                'count': results[0].get('count'),
                'class': subject_class,
                'property': property_path
            }
        
        return {}
    
    def group_by_property(
        self,
        subject_class: str,
        group_property: str,
        aggregation: str = "COUNT"
    ) -> List[Dict[str, Any]]:
        """
        Group subjects by property value and aggregate.
        
        Args:
            subject_class: Class of subjects
            group_property: Property to group by
            aggregation: Aggregation function
            
        Returns:
            List of grouped results
        """
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?groupValue ({aggregation}(*) AS ?count)
        WHERE {{
            ?subject a <{subject_class}> ;
                     <{group_property}> ?groupValue .
        }}
        GROUP BY ?groupValue
        ORDER BY DESC(?count)
        LIMIT 100
        """
        
        return self.query(query) or []
    
    def federated_query(
        self,
        local_class: str,
        remote_endpoint: str,
        remote_property: str
    ) -> List[Dict[str, Any]]:
        """
        Execute federated query across multiple endpoints.
        
        Args:
            local_class: Local class to query
            remote_endpoint: Remote SPARQL endpoint URL
            remote_property: Property to fetch from remote
            
        Returns:
            Combined results
        """
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?local ?localLabel ?remoteValue
        WHERE {{
            ?local a <{local_class}> ;
                   rdfs:label ?localLabel .
            
            SERVICE <{remote_endpoint}> {{
                ?local <{remote_property}> ?remoteValue .
            }}
        }}
        LIMIT 100
        """
        
        return self.query(query) or []
    
    def construct_subgraph(
        self,
        resource_uri: str,
        depth: int = 2
    ) -> Graph:
        """
        Construct a subgraph around a resource using CONSTRUCT query.
        
        Args:
            resource_uri: Center resource URI
            depth: Depth of subgraph
            
        Returns:
            RDFLib Graph
        """
        query = f"""
        CONSTRUCT {{
            ?s ?p ?o .
        }}
        WHERE {{
            {{
                <{resource_uri}> (!<>){{0,{depth}}} ?s .
                ?s ?p ?o .
            }} UNION {{
                ?s (!<>){{0,{depth}}} <{resource_uri}> .
                ?s ?p ?o .
            }}
        }}
        LIMIT 1000
        """
        
        if self.endpoint:
            # Use SPARQLWrapper for remote CONSTRUCT
            sparql = SPARQLWrapper(self.endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(SPARQL_RDF)
            return sparql.query().convert()
        else:
            # Local graph
            return self.graph.query(query).graph
    
    def search_by_text(
        self,
        search_text: str,
        property_paths: Optional[List[str]] = None,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Full-text search across specified properties.
        
        Args:
            search_text: Text to search for
            property_paths: List of property URIs to search in
            case_sensitive: Case-sensitive search
            
        Returns:
            List of matching resources
        """
        if not property_paths:
            property_paths = [
                "http://www.w3.org/2000/01/rdf-schema#label",
                "http://www.w3.org/2000/01/rdf-schema#comment",
                "http://purl.org/dc/terms/description"
            ]
        
        filters = []
        for prop in property_paths:
            if case_sensitive:
                filters.append(f'CONTAINS(?value, "{search_text}")')
            else:
                filters.append(f'CONTAINS(LCASE(?value), LCASE("{search_text}"))')
        
        filter_clause = " || ".join(filters)
        
        property_patterns = " UNION ".join([
            f"{{ ?resource <{prop}> ?value }}" for prop in property_paths
        ])
        
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?resource ?value ?type
        WHERE {{
            {property_patterns}
            
            OPTIONAL {{ ?resource a ?type }}
            
            FILTER({filter_clause})
        }}
        LIMIT 100
        """
        
        return self.query(query) or []
    
    def get_class_instances_count(self) -> List[Dict[str, Any]]:
        """
        Count instances for each class in the graph.
        
        Returns:
            List of classes with instance counts
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?class ?classLabel (COUNT(?instance) AS ?count)
        WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:label ?classLabel }
            OPTIONAL { ?instance a ?class }
        }
        GROUP BY ?class ?classLabel
        HAVING (COUNT(?instance) > 0)
        ORDER BY DESC(?count)
        """
        
        return self.query(query) or []
    
    def get_property_usage_stats(self) -> List[Dict[str, Any]]:
        """
        Get usage statistics for all properties.
        
        Returns:
            List of properties with usage counts
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?property ?label (COUNT(*) AS ?usageCount)
        WHERE {
            ?s ?property ?o .
            OPTIONAL { ?property rdfs:label ?label }
            FILTER(isURI(?property))
        }
        GROUP BY ?property ?label
        ORDER BY DESC(?usageCount)
        LIMIT 100
        """
        
        return self.query(query) or []
    
    def find_similar_resources(
        self,
        resource_uri: str,
        similarity_properties: List[str],
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find resources similar to a given resource based on shared properties.
        
        Args:
            resource_uri: Resource URI
            similarity_properties: Properties to compare
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar resources with similarity scores
        """
        # This is a simplified similarity - in production you'd use more sophisticated algorithms
        property_patterns = " ".join([
            f"{{ <{resource_uri}> <{prop}> ?value . ?similar <{prop}> ?value }}"
            for prop in similarity_properties
        ])
        
        query = f"""
        SELECT ?similar (COUNT(?value) AS ?sharedProperties)
        WHERE {{
            {property_patterns}
            
            FILTER(?similar != <{resource_uri}>)
        }}
        GROUP BY ?similar
        HAVING (COUNT(?value) >= {int(threshold * len(similarity_properties))})
        ORDER BY DESC(?sharedProperties)
        LIMIT 50
        """
        
        return self.query(query) or []
    
    def explain_query_plan(self, query_string: str) -> Dict[str, Any]:
        """
        Analyze and explain query execution plan.
        
        Args:
            query_string: SPARQL query
            
        Returns:
            Query plan analysis
        """
        # Count triple patterns
        triple_pattern_count = query_string.count('?') // 2
        
        # Detect query features
        features = {
            'has_optional': 'OPTIONAL' in query_string.upper(),
            'has_union': 'UNION' in query_string.upper(),
            'has_filter': 'FILTER' in query_string.upper(),
            'has_aggregation': any(agg in query_string.upper() for agg in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']),
            'has_property_path': '*' in query_string or '+' in query_string,
            'has_subquery': 'SELECT' in query_string[query_string.find('WHERE'):] if 'WHERE' in query_string else False
        }
        
        return {
            'estimated_triple_patterns': triple_pattern_count,
            'features': features,
            'complexity': 'high' if sum(features.values()) > 3 else 'medium' if sum(features.values()) > 1 else 'low'
        }
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """
        Get query execution statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.query_stats:
            return {'total_queries': 0}
        
        execution_times = [stat['execution_time_ms'] for stat in self.query_stats]
        
        return {
            'total_queries': len(self.query_stats),
            'avg_execution_time_ms': sum(execution_times) / len(execution_times),
            'min_execution_time_ms': min(execution_times),
            'max_execution_time_ms': max(execution_times),
            'cache_size': len(self.query_cache)
        }
    
    def clear_cache(self):
        """Clear query cache."""
        self.query_cache.clear()
        logger.info("Query cache cleared")
