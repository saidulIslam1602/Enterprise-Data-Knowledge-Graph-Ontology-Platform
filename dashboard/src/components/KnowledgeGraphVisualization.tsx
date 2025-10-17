import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './KnowledgeGraphVisualization.css';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  predicate: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

const KnowledgeGraphVisualization: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch knowledge graph data
  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      
      // Fetch actual graph data using SPARQL
      const query = `
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?subject ?subjectLabel ?subjectType ?predicate ?object ?objectLabel
        WHERE {
          ?subject ?predicate ?object .
          OPTIONAL { ?subject rdfs:label ?subjectLabel }
          OPTIONAL { ?subject a ?subjectType }
          OPTIONAL { ?object rdfs:label ?objectLabel }
          
          FILTER(isURI(?subject) && isURI(?object))
          FILTER(?predicate != rdf:type || ?object = owl:Class)
        }
        LIMIT 100
      `;
      
      const response = await fetch('/api/v1/kg/sparql/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, use_cache: true })
      });
      
      const data = await response.json();
      
      if (data.status === 'success' && data.results) {
        const transformedData = transformToGraphData(data.results);
        setGraphData(transformedData);
      }
    } catch (error) {
      console.error('Error fetching graph data:', error);
      // Fallback to metadata if SPARQL fails
      try {
        const response = await fetch('/api/v1/kg/ontology/metadata');
        const data = await response.json();
        const transformedData = transformFallbackData(data);
        setGraphData(transformedData);
      } catch (err) {
        console.error('Fallback also failed:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const transformToGraphData = (results: any[]): GraphData => {
    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];
    const nodeMap = new Map<string, GraphNode>();

    // Process SPARQL results
    results.forEach((result: any) => {
      const subjectId = result.subject;
      const objectId = result.object;
      
      // Add subject node if not exists
      if (!nodeMap.has(subjectId)) {
        const node: GraphNode = {
          id: subjectId,
          label: result.subjectLabel || subjectId.split('/').pop() || subjectId,
          type: result.subjectType ? 'class' : 'individual'
        };
        nodeMap.set(subjectId, node);
        nodes.push(node);
      }
      
      // Add object node if not exists
      if (!nodeMap.has(objectId)) {
        const node: GraphNode = {
          id: objectId,
          label: result.objectLabel || objectId.split('/').pop() || objectId,
          type: 'individual'
        };
        nodeMap.set(objectId, node);
        nodes.push(node);
      }
      
      // Add link
      links.push({
        source: subjectId,
        target: objectId,
        predicate: result.predicate.split('#').pop() || result.predicate.split('/').pop() || 'related'
      });
    });

    return { nodes, links };
  };

  const transformFallbackData = (data: any): GraphData => {
    // Fallback: create minimal graph from statistics
    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];

    if (data.statistics) {
      const classCount = Math.min(data.statistics.classes || 5, 10);
      const individualCount = Math.min(data.statistics.individuals || 10, 20);
      
      // Create class nodes
      for (let i = 0; i < classCount; i++) {
        nodes.push({
          id: `class-${i}`,
          label: `Class ${i + 1}`,
          type: 'class'
        });
      }

      // Create individual nodes and link to classes
      for (let i = 0; i < individualCount; i++) {
        const id = `entity-${i}`;
        nodes.push({
          id,
          label: `Entity ${i + 1}`,
          type: 'individual'
        });

        // Link to a class
        if (classCount > 0) {
          links.push({
            source: id,
            target: `class-${i % classCount}`,
            predicate: 'type'
          });
        }
      }
    }

    return { nodes, links };
  };

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    renderGraph(graphData);
  }, [graphData]);

  const renderGraph = (data: GraphData) => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    const width = 1200;
    const height = 800;

    svg.attr('width', width).attr('height', height);

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
      .data(['end'])
      .enter().append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Color scale for node types
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['class', 'individual', 'property'])
      .range(['#FF6B6B', '#4ECDC4', '#FFE66D']);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(data.links)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create container for zoom
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)');

    // Draw link labels
    const linkLabels = g.append('g')
      .selectAll('text')
      .data(data.links)
      .enter().append('text')
      .attr('class', 'link-label')
      .attr('font-size', 10)
      .attr('fill', '#666')
      .text((d: GraphLink) => d.predicate);

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', (d: GraphNode) => d.type === 'class' ? 15 : 10)
      .attr('fill', (d: GraphNode) => colorScale(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any)
      .on('click', (event, d: GraphNode) => {
        setSelectedNode(d);
      })
      .on('mouseover', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', (d: any) => (d.type === 'class' ? 15 : 10) * 1.3);
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', (d: any) => d.type === 'class' ? 15 : 10);
      });

    // Add labels
    const labels = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('class', 'node-label')
      .attr('font-size', 12)
      .attr('dx', 15)
      .attr('dy', 4)
      .text((d: GraphNode) => d.label);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      linkLabels
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  const handleSearch = async () => {
    if (!searchTerm) return;

    try {
      const response = await fetch('/api/v1/kg/sparql/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_text: searchTerm,
          limit: 50
        })
      });

      const data = await response.json();
      console.log('Search results:', data);
      // Transform and update graph with search results
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  return (
    <div className="knowledge-graph-container">
      <div className="controls-panel">
        <h2>Enterprise Knowledge Graph</h2>
        
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search entities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        <div className="legend">
          <h3>Legend</h3>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#FF6B6B' }}></div>
            <span>OWL Classes</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#4ECDC4' }}></div>
            <span>Individuals</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ background: '#FFE66D' }}></div>
            <span>Properties</span>
          </div>
        </div>

        {selectedNode && (
          <div className="node-details">
            <h3>Selected Node</h3>
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Label:</strong> {selectedNode.label}</p>
            <p><strong>Type:</strong> {selectedNode.type}</p>
            <button onClick={() => setSelectedNode(null)}>Close</button>
          </div>
        )}

        <div className="actions">
          <button onClick={fetchGraphData}>Refresh</button>
          <button onClick={() => {
            // Reset zoom
            const svg = d3.select(svgRef.current);
            svg.transition().duration(750).call(
              d3.zoom<SVGSVGElement, unknown>().transform as any,
              d3.zoomIdentity
            );
          }}>Reset View</button>
        </div>
      </div>

      <div className="graph-canvas">
        {loading ? (
          <div className="loading">Loading knowledge graph...</div>
        ) : (
          <svg ref={svgRef}></svg>
        )}
      </div>
    </div>
  );
};

export default KnowledgeGraphVisualization;
