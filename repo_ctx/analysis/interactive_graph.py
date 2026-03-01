"""Interactive HTML graph generator for architecture visualization.

Uses vis.js to create interactive, zoomable, filterable dependency graphs.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("repo_ctx.analysis.interactive_graph")

# HTML template with vis.js embedded
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
        }}
        #header {{
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #header h1 {{
            font-size: 1.5em;
            font-weight: 500;
        }}
        #controls {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        #controls label {{
            font-size: 0.9em;
        }}
        #controls select, #controls input {{
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
        }}
        #container {{
            display: flex;
            height: calc(100vh - 60px);
        }}
        #sidebar {{
            width: 280px;
            background: white;
            border-right: 1px solid #ddd;
            overflow-y: auto;
            padding: 15px;
        }}
        #sidebar h2 {{
            font-size: 1em;
            color: #666;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
        }}
        #stats {{
            margin-bottom: 20px;
        }}
        #stats div {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 0.9em;
        }}
        #stats .value {{
            font-weight: 600;
            color: #2c3e50;
        }}
        #legend {{
            margin-bottom: 20px;
        }}
        #legend .item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 0;
            font-size: 0.85em;
        }}
        #legend .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        #node-info {{
            display: none;
        }}
        #node-info.visible {{
            display: block;
        }}
        #node-info h3 {{
            font-size: 0.95em;
            color: #333;
            word-break: break-all;
        }}
        #node-info .meta {{
            font-size: 0.8em;
            color: #666;
            margin: 5px 0;
        }}
        #node-info ul {{
            list-style: none;
            max-height: 200px;
            overflow-y: auto;
            font-size: 0.85em;
        }}
        #node-info li {{
            padding: 3px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        #graph {{
            flex: 1;
            background: white;
        }}
        .highlight {{
            background: #fff3cd;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>{title}</h1>
        <div id="controls">
            <label>
                Filter:
                <select id="filter-type">
                    <option value="all">All Nodes</option>
                    <option value="high-degree">High Connectivity</option>
                    <option value="cycles">In Cycles</option>
                </select>
            </label>
            <label>
                Search:
                <input type="text" id="search" placeholder="Search nodes...">
            </label>
            <label>
                Layout:
                <select id="layout">
                    <option value="physics">Force-directed</option>
                    <option value="hierarchical">Hierarchical</option>
                </select>
            </label>
        </div>
    </div>
    <div id="container">
        <div id="sidebar">
            <div id="stats">
                <h2>Statistics</h2>
                <div><span>Nodes:</span><span class="value" id="stat-nodes">0</span></div>
                <div><span>Edges:</span><span class="value" id="stat-edges">0</span></div>
                <div><span>Cycles:</span><span class="value" id="stat-cycles">0</span></div>
                <div><span>Layers:</span><span class="value" id="stat-layers">0</span></div>
            </div>
            <div id="legend">
                <h2>Legend</h2>
                <div class="item"><span class="dot" style="background: #3498db;"></span> File</div>
                <div class="item"><span class="dot" style="background: #9b59b6;"></span> Class</div>
                <div class="item"><span class="dot" style="background: #2ecc71;"></span> Package</div>
                <div class="item"><span class="dot" style="background: #e74c3c;"></span> In Cycle</div>
            </div>
            <div id="node-info">
                <h2>Selected Node</h2>
                <h3 id="node-name">-</h3>
                <div class="meta">
                    <span id="node-type">-</span> |
                    In: <span id="node-in">0</span> |
                    Out: <span id="node-out">0</span>
                </div>
                <h2 style="margin-top: 15px;">Connections</h2>
                <ul id="node-connections"></ul>
            </div>
        </div>
        <div id="graph"></div>
    </div>
    <script type="text/javascript">
        // Graph data
        const graphData = {graph_data};

        // Configuration
        const config = {config};

        // Initialize statistics
        document.getElementById('stat-nodes').textContent = graphData.nodes.length;
        document.getElementById('stat-edges').textContent = graphData.edges.length;
        document.getElementById('stat-cycles').textContent = config.cycles_count || 0;
        document.getElementById('stat-layers').textContent = config.layers_count || 0;

        // Node colors by type
        const colorMap = {{
            'file': '#3498db',
            'class': '#9b59b6',
            'package': '#2ecc71',
            'function': '#f39c12',
            'default': '#95a5a6'
        }};

        // Prepare nodes for vis.js
        const visNodes = graphData.nodes.map(node => {{
            const inCycle = config.cycle_nodes && config.cycle_nodes.includes(node.id);
            return {{
                id: node.id,
                label: node.label || node.id.split('/').pop(),
                title: node.id,
                color: inCycle ? '#e74c3c' : (colorMap[node.type] || colorMap.default),
                font: {{ size: 12 }},
                shape: 'dot',
                size: 10 + Math.min(20, (node.degree || 0) * 2),
                borderWidth: inCycle ? 3 : 1,
                borderWidthSelected: 3,
                type: node.type || 'file',
                inDegree: node.in_degree || 0,
                outDegree: node.out_degree || 0
            }};
        }});

        // Prepare edges for vis.js
        const visEdges = graphData.edges.map((edge, idx) => ({{
            id: idx,
            from: edge.source,
            to: edge.target,
            arrows: 'to',
            color: {{ color: '#999', opacity: 0.6 }},
            smooth: {{ type: 'curvedCW', roundness: 0.2 }},
            title: edge.type || 'depends'
        }}));

        // Create network
        const container = document.getElementById('graph');
        const data = {{
            nodes: new vis.DataSet(visNodes),
            edges: new vis.DataSet(visEdges)
        }};

        const options = {{
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -50,
                    springLength: 100,
                    springConstant: 0.08
                }},
                stabilization: {{
                    iterations: 150
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            }},
            nodes: {{
                font: {{ face: 'sans-serif' }}
            }}
        }};

        const network = new vis.Network(container, data, options);

        // Node selection handler
        network.on('selectNode', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = data.nodes.get(nodeId);

                document.getElementById('node-info').classList.add('visible');
                document.getElementById('node-name').textContent = nodeId;
                document.getElementById('node-type').textContent = node.type;
                document.getElementById('node-in').textContent = node.inDegree;
                document.getElementById('node-out').textContent = node.outDegree;

                // Get connections
                const connections = document.getElementById('node-connections');
                connections.innerHTML = '';

                const connectedEdges = network.getConnectedEdges(nodeId);
                connectedEdges.forEach(edgeId => {{
                    const edge = data.edges.get(edgeId);
                    const otherNode = edge.from === nodeId ? edge.to : edge.from;
                    const direction = edge.from === nodeId ? '→' : '←';
                    const li = document.createElement('li');
                    li.textContent = direction + ' ' + otherNode.split('/').pop();
                    li.title = otherNode;
                    connections.appendChild(li);
                }});
            }}
        }});

        network.on('deselectNode', function() {{
            document.getElementById('node-info').classList.remove('visible');
        }});

        // Search functionality
        document.getElementById('search').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            if (query.length < 2) {{
                data.nodes.forEach(node => {{
                    data.nodes.update({{ id: node.id, opacity: 1 }});
                }});
                return;
            }}

            data.nodes.forEach(node => {{
                const match = node.id.toLowerCase().includes(query);
                data.nodes.update({{ id: node.id, opacity: match ? 1 : 0.2 }});
            }});
        }});

        // Filter functionality
        document.getElementById('filter-type').addEventListener('change', function(e) {{
            const filter = e.target.value;

            let visibleNodes;
            switch(filter) {{
                case 'high-degree':
                    visibleNodes = visNodes.filter(n => (n.inDegree + n.outDegree) >= 3).map(n => n.id);
                    break;
                case 'cycles':
                    visibleNodes = config.cycle_nodes || [];
                    break;
                default:
                    visibleNodes = visNodes.map(n => n.id);
            }}

            data.nodes.forEach(node => {{
                data.nodes.update({{ id: node.id, hidden: !visibleNodes.includes(node.id) }});
            }});
        }});

        // Layout switch
        document.getElementById('layout').addEventListener('change', function(e) {{
            const layout = e.target.value;
            if (layout === 'hierarchical') {{
                network.setOptions({{
                    layout: {{
                        hierarchical: {{
                            enabled: true,
                            direction: 'UD',
                            sortMethod: 'directed'
                        }}
                    }},
                    physics: {{ enabled: false }}
                }});
            }} else {{
                network.setOptions({{
                    layout: {{ hierarchical: {{ enabled: false }} }},
                    physics: {{ enabled: true }}
                }});
            }}
        }});
    </script>
</body>
</html>
"""


class InteractiveGraphGenerator:
    """Generates interactive HTML dependency graphs using vis.js."""

    def __init__(self):
        pass

    def generate(
        self,
        nodes: list[dict],
        edges: list[tuple],
        output_path: Path,
        title: str = "Dependency Graph",
        cycles: Optional[list] = None,
        layers: Optional[list] = None,
    ) -> Path:
        """Generate an interactive HTML graph.

        Args:
            nodes: List of node dicts with 'id', optional 'label', 'type'.
            edges: List of (source, target, type) tuples.
            output_path: Path to write HTML file.
            title: Graph title.
            cycles: Optional list of cycle node lists.
            layers: Optional list of layer dicts.

        Returns:
            Path to generated HTML file.
        """
        # Calculate node degrees
        in_degree = {}
        out_degree = {}
        for source, target, _ in edges:
            out_degree[source] = out_degree.get(source, 0) + 1
            in_degree[target] = in_degree.get(target, 0) + 1

        # Prepare node data
        graph_nodes = []
        for node in nodes:
            node_id = node if isinstance(node, str) else node.get('id', str(node))
            node_type = 'file'
            if isinstance(node, dict):
                node_type = node.get('type', 'file')

            # Determine short label
            label = node_id.split('/')[-1] if '/' in node_id else node_id
            if ':' in label:
                label = label.split(':')[-1]

            graph_nodes.append({
                'id': node_id,
                'label': label,
                'type': node_type,
                'in_degree': in_degree.get(node_id, 0),
                'out_degree': out_degree.get(node_id, 0),
                'degree': in_degree.get(node_id, 0) + out_degree.get(node_id, 0),
            })

        # Prepare edge data
        graph_edges = []
        for source, target, edge_type in edges:
            graph_edges.append({
                'source': source,
                'target': target,
                'type': edge_type or 'depends',
            })

        # Collect cycle nodes
        cycle_nodes = []
        if cycles:
            for cycle in cycles:
                if isinstance(cycle, dict):
                    cycle_nodes.extend(cycle.get('nodes', []))
                elif isinstance(cycle, list):
                    cycle_nodes.extend(cycle)
        cycle_nodes = list(set(cycle_nodes))

        # Prepare config
        config = {
            'cycles_count': len(cycles) if cycles else 0,
            'layers_count': len(layers) if layers else 0,
            'cycle_nodes': cycle_nodes,
        }

        # Generate HTML
        html = HTML_TEMPLATE.format(
            title=title,
            graph_data=json.dumps({'nodes': graph_nodes, 'edges': graph_edges}),
            config=json.dumps(config),
        )

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        logger.info(f"Generated interactive graph: {output_path}")

        return output_path

    def generate_from_arch_data(
        self,
        arch_data: dict,
        output_path: Path,
        title: str = "Architecture Overview",
    ) -> Path:
        """Generate interactive graph from architecture data dict.

        Args:
            arch_data: Architecture data from DumpService._generate_architecture.
            output_path: Path to write HTML file.
            title: Graph title.

        Returns:
            Path to generated HTML file.
        """
        nodes = arch_data.get('nodes', [])
        edges = arch_data.get('edges', [])
        cycles = arch_data.get('cycles', {}).get('cycles', [])
        layers = arch_data.get('layers', {}).get('layers', [])

        # Convert nodes to proper format
        node_dicts = [{'id': n, 'type': 'file'} for n in nodes]

        return self.generate(
            nodes=node_dicts,
            edges=edges,
            output_path=output_path,
            title=title,
            cycles=cycles,
            layers=layers,
        )
