/**
 * MCP Client for React App
 * 
 * Provides WebSocket and HTTP connections to the KGAS MCP server
 * for orchestrating analysis workflows through 44+ available tools.
 */

class MCPClient {
  constructor(serverUrl = 'ws://localhost:8000/mcp') {
    this.serverUrl = serverUrl;
    this.httpUrl = serverUrl.replace('ws://', 'http://').replace('/mcp', '');
    this.websocket = null;
    this.isConnected = false;
    this.messageId = 0;
    this.pendingRequests = new Map();
    this.tools = new Map();
    this.eventListeners = new Map();
    
    // Initialize connection
    this.connect();
  }

  /**
   * Connect to MCP server via WebSocket
   */
  async connect() {
    try {
      this.websocket = new WebSocket(this.serverUrl);
      
      this.websocket.onopen = () => {
        console.log('✅ MCP WebSocket connected');
        this.isConnected = true;
        this.emit('connected');
        
        // Initialize by listing available tools
        this.listTools();
      };
      
      this.websocket.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };
      
      this.websocket.onclose = () => {
        console.log('⚠️ MCP WebSocket disconnected');
        this.isConnected = false;
        this.emit('disconnected');
        
        // Attempt reconnection after 5 seconds
        setTimeout(() => this.connect(), 5000);
      };
      
      this.websocket.onerror = (error) => {
        console.error('❌ MCP WebSocket error:', error);
        this.emit('error', error);
      };
      
    } catch (error) {
      console.error('❌ Failed to connect to MCP server:', error);
      // Fallback to HTTP-only mode
      this.initializeHttpFallback();
    }
  }

  /**
   * Fallback to HTTP-only communication
   */
  async initializeHttpFallback() {
    console.log('🔄 Initializing HTTP fallback mode');
    try {
      await this.listToolsHttp();
      this.emit('connected');
    } catch (error) {
      console.error('❌ HTTP fallback failed:', error);
      this.emit('error', error);
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(message) {
    const { id, result, error } = message;
    
    if (this.pendingRequests.has(id)) {
      const { resolve, reject } = this.pendingRequests.get(id);
      this.pendingRequests.delete(id);
      
      if (error) {
        reject(new Error(error.message || 'MCP request failed'));
      } else {
        resolve(result);
      }
    }
  }

  /**
   * Send MCP request via WebSocket
   */
  async sendRequest(method, params = {}) {
    if (!this.isConnected) {
      throw new Error('MCP client not connected');
    }

    const id = ++this.messageId;
    const message = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      
      try {
        this.websocket.send(JSON.stringify(message));
        
        // Set timeout for request
        setTimeout(() => {
          if (this.pendingRequests.has(id)) {
            this.pendingRequests.delete(id);
            reject(new Error('MCP request timeout'));
          }
        }, 30000); // 30 second timeout
        
      } catch (error) {
        this.pendingRequests.delete(id);
        reject(error);
      }
    });
  }

  /**
   * Send HTTP request as fallback
   */
  async sendHttpRequest(endpoint, data = {}) {
    const response = await fetch(`${this.httpUrl}/api/mcp/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * List all available tools
   */
  async listTools() {
    try {
      const result = this.isConnected 
        ? await this.sendRequest('tools/list')
        : await this.listToolsHttp();
      
      // Cache tools for easy access
      if (result.tools) {
        result.tools.forEach(tool => {
          this.tools.set(tool.name, tool);
        });
      }
      
      console.log(`📋 Loaded ${this.tools.size} MCP tools`);
      this.emit('toolsLoaded', Array.from(this.tools.values()));
      
      return Array.from(this.tools.values());
    } catch (error) {
      console.error('❌ Failed to list tools:', error);
      throw error;
    }
  }

  /**
   * List tools via HTTP
   */
  async listToolsHttp() {
    // For now, return a static list of known tools
    // In production, this would call an HTTP endpoint
    const staticTools = [
      // Core Service Tools
      { name: 'create_mention', description: 'Create entity mention with identity resolution' },
      { name: 'log_operation', description: 'Track operation for provenance' },
      { name: 'assess_quality', description: 'Assess confidence and quality' },
      { name: 'save_workflow_state', description: 'Save workflow checkpoint' },
      
      // Phase 1 Document Processing Tools
      { name: 'load_pdf_document', description: 'Load and extract text from PDF' },
      { name: 'chunk_text', description: 'Split text into processable chunks' },
      { name: 'extract_entities_from_text', description: 'Extract named entities using spaCy' },
      { name: 'extract_relationships', description: 'Find entity relationships' },
      { name: 'build_graph_entities', description: 'Create graph nodes in Neo4j' },
      { name: 'build_graph_edges', description: 'Create graph relationships' },
      { name: 'calculate_pagerank', description: 'Calculate PageRank centrality scores' },
      { name: 'query_graph', description: 'Multi-hop graph queries' },
      
      // Pipeline Tools
      { name: 'process_document_complete_pipeline', description: 'Complete PDF → PageRank → Answer pipeline' },
      { name: 'get_kgas_system_status', description: 'Get system health and status' }
    ];

    staticTools.forEach(tool => {
      this.tools.set(tool.name, tool);
    });

    return { tools: staticTools };
  }

  /**
   * Call a specific tool with parameters
   */
  async callTool(toolName, parameters = {}) {
    try {
      console.log(`🔧 Calling tool: ${toolName}`, parameters);
      
      const result = this.isConnected
        ? await this.sendRequest('tools/call', { name: toolName, arguments: parameters })
        : await this.sendHttpRequest('tools/call', { name: toolName, arguments: parameters });
      
      console.log(`✅ Tool ${toolName} completed:`, result);
      this.emit('toolComplete', { toolName, parameters, result });
      
      return result;
    } catch (error) {
      console.error(`❌ Tool ${toolName} failed:`, error);
      this.emit('toolError', { toolName, parameters, error });
      throw error;
    }
  }

  /**
   * Get tool information
   */
  getTool(toolName) {
    return this.tools.get(toolName);
  }

  /**
   * Get all tools by category
   */
  getToolsByCategory() {
    const categories = {
      'Core Services': [],
      'Document Processing': [],
      'Graph Building': [],
      'Analysis': [],
      'Pipeline': []
    };

    for (const tool of this.tools.values()) {
      if (tool.name.includes('mention') || tool.name.includes('operation') || 
          tool.name.includes('quality') || tool.name.includes('workflow')) {
        categories['Core Services'].push(tool);
      } else if (tool.name.includes('load') || tool.name.includes('chunk') || tool.name.includes('extract')) {
        categories['Document Processing'].push(tool);
      } else if (tool.name.includes('build') || tool.name.includes('graph')) {
        categories['Graph Building'].push(tool);
      } else if (tool.name.includes('pagerank') || tool.name.includes('query')) {
        categories['Analysis'].push(tool);
      } else if (tool.name.includes('pipeline') || tool.name.includes('status')) {
        categories['Pipeline'].push(tool);
      }
    }

    return categories;
  }

  /**
   * Execute a complete document processing workflow
   */
  async processDocument(filePath, options = {}) {
    const {
      includePageRank = true,
      includeQuery = false,
      queryText = null,
      workflowId = null
    } = options;

    try {
      console.log('🔄 Starting document processing workflow');
      
      // Use the complete pipeline tool if available
      const result = await this.callTool('process_document_complete_pipeline', {
        file_path: filePath,
        workflow_id: workflowId,
        include_pagerank: includePageRank,
        include_query: includeQuery,
        query_text: queryText
      });

      this.emit('workflowComplete', result);
      return result;
      
    } catch (error) {
      console.error('❌ Document processing workflow failed:', error);
      
      // Fallback to manual tool orchestration
      return await this.processDocumentManual(filePath, options);
    }
  }

  /**
   * Manual document processing using individual tools
   */
  async processDocumentManual(filePath, options = {}) {
    const results = {
      workflow_id: options.workflowId || `manual_${Date.now()}`,
      steps: []
    };

    try {
      // Step 1: Load PDF
      const pdfResult = await this.callTool('load_pdf_document', {
        file_path: filePath,
        workflow_id: results.workflow_id
      });
      results.steps.push({ tool: 'load_pdf_document', result: pdfResult });

      // Step 2: Extract entities (requires text from PDF result)
      if (pdfResult.text_content) {
        const entitiesResult = await this.callTool('extract_entities_from_text', {
          chunk_ref: `doc_${results.workflow_id}`,
          text_content: pdfResult.text_content,
          base_confidence: 0.8
        });
        results.steps.push({ tool: 'extract_entities_from_text', result: entitiesResult });
      }

      // Additional steps would be added here based on available data
      
      return {
        status: 'success',
        workflow_id: results.workflow_id,
        results: results.steps
      };

    } catch (error) {
      return {
        status: 'error',
        error: error.message,
        workflow_id: results.workflow_id,
        results: results.steps
      };
    }
  }

  /**
   * Get system status
   */
  async getSystemStatus() {
    try {
      return await this.callTool('get_kgas_system_status');
    } catch (error) {
      console.error('❌ Failed to get system status:', error);
      return {
        status: 'error',
        error: error.message,
        tools_available: { total_mcp_tools: this.tools.size }
      };
    }
  }

  /**
   * Event system
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const callbacks = this.eventListeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`❌ Event callback error for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Disconnect and cleanup
   */
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
    }
    this.isConnected = false;
    this.pendingRequests.clear();
    this.eventListeners.clear();
  }
}

// Export singleton instance
const mcpClient = new MCPClient();
export default mcpClient;

// Also export the class for testing
export { MCPClient };