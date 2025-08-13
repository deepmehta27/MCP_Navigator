# MCP Navigator

A sophisticated LangGraph-powered agent client that integrates multiple Model Context Protocol (MCP) servers for enhanced AI capabilities. This project demonstrates a unified interface for managing notes, retrieving weather data, performing web searches, and executing browser automation tasks through a single conversational interface.

## 🚀 Features

### Core Capabilities
- **📝 Notes Management**: Create, read, update, delete, and search local notes with persistent storage
- **🌤️ Weather Information**: Real-time weather data for any city worldwide
- **🔍 Web Search**: DuckDuckGo-powered search capabilities for quick information retrieval
- **🏠 Airbnb Integration**: Search and browse Airbnb listings with advanced filtering
- **🌐 Browser Automation**: Playwright-powered web automation with persistent sessions

### Technical Highlights
- **LangGraph Integration**: Built on LangGraph's ReAct agent architecture for intelligent tool routing
- **Multi-MCP Architecture**: Seamlessly integrates multiple MCP servers via different transport protocols
- **Session Persistence**: Browser automation maintains state across multi-step operations
- **Real-time Feedback**: Step-by-step execution visibility with detailed tool call logging
- **Modular Design**: Extensible server architecture for easy capability additions

## 🛠️ Installation

### Prerequisites
- Python 3.12 or higher
- Node.js (for MCP server dependencies)
- OpenAI API key

### Setup
1. **Clone and install dependencies**:
   ```bash
   git clone <repository-url>
   cd MCP_Navigator
   
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o
   ```

3. **Install Node.js dependencies**:
   ```bash
   # The system will automatically install required npm packages on first run
   # or manually install for development:
   npx @playwright/mcp@latest
   npx @openbnb/mcp-server-airbnb
   npx duckduckgo-mcp-server
   ```

## 🎯 Usage

### Starting the Application
```bash
python client.py
```

### Example Interactions

#### Notes Management
```
You: Create a note titled 'Project Ideas' with content 'Build MCP integration for calendar management'
You: List my notes
You: Search notes for 'calendar'
You: Get note 'Project Ideas'
You: Delete note 'Project Ideas'
```

#### Weather Queries
```
You: Weather in New York
You: What's the weather in Tokyo?
You: Get weather for London
```

#### Web Search
```
You: Search for latest AI developments
You: Find information about Python async programming
```

#### Airbnb Search
```
You: Find Airbnb listings in Paris for next weekend
You: Search for pet-friendly stays in San Francisco
```

#### Browser Automation
```
You: browse: open google.com, search for "MCP protocol documentation"
You: browse: go to github.com and find trending Python repositories
You: browse: visit airbnb.com and search for NYC stays on August 15th
```

## 🏗️ Architecture

### MCP Server Integration
The system integrates multiple MCP servers through different transport protocols:

- **Notes Server** (`servers/notes_server.py`): Local note management via stdio transport
- **Weather Server** (`servers/weather.py`): Weather data via HTTP transport (port 8000)
- **Browser MCPs** (`servers/browser_mcp.json`): Playwright, Airbnb, and DuckDuckGo via Node.js stdio

### Agent Architecture
- **LangGraph ReAct Agent**: Intelligent tool selection and execution
- **MultiServerMCPClient**: Unified interface for multiple MCP servers
- **Step-by-Step Tracing**: Real-time visibility into agent decision-making
- **Conversation Memory**: Maintains context across multiple interactions

### Data Persistence
- **Notes Storage**: JSON-based local storage in `data/notes.json`
- **Session Management**: Browser sessions persist across multi-step operations
- **Configuration**: MCP server configurations stored in JSON format

## 🔧 Configuration

### MCP Server Configuration
The `servers/browser_mcp.json` file configures Node.js-based MCP servers:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "airbnb": {
      "command": "npx", 
      "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt", "--session-persistent"]
    },
    "duckduckgo-search": {
      "command": "npx",
      "args": ["-y", "duckduckgo-mcp-server"]
    }
  }
}
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o)

## 🧪 Development

### Project Structure
```
MCP_Navigator/
├── client.py              # Main CLI application
├── main.py                # Entry point (placeholder)
├── pyproject.toml         # Project configuration
├── servers/               # MCP server implementations
│   ├── notes_server.py    # Notes management server
│   ├── weather.py         # Weather data server
│   └── browser_mcp.json   # Browser MCP configuration
├── data/                  # Persistent data storage
└── logs/                  # Application logs
```

### Adding New Capabilities
1. **Create MCP Server**: Implement new server in `servers/` directory
2. **Update Configuration**: Add server to connection configuration in `client.py`
3. **Update System Prompt**: Modify agent system guidance for new tools
4. **Test Integration**: Verify tool discovery and execution

## 🐛 Troubleshooting

### Common Issues

**Browser Automation Not Working**
- Ensure Node.js is installed and accessible
- Check that Playwright MCP server is properly installed
- Verify browser automation commands start with "browse:"

**Weather Server Connection Issues**
- Weather server starts automatically on port 8000
- Check if port 8000 is available and not blocked by firewall
- Verify internet connectivity for weather API calls

**Notes Not Persisting**
- Check write permissions for `data/` directory
- Verify `data/notes.json` file is not corrupted
- Ensure sufficient disk space

**MCP Server Connection Failures**
- Verify all required npm packages are installed
- Check Node.js version compatibility
- Review MCP server configuration in `browser_mcp.json`

### Debug Mode
Enable debug mode for browser automation:
```bash
export PWDEBUG=1
export PLAYWRIGHT_HEADLESS=0
uv run client.py
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

---

**MCP Navigator** demonstrates the power of Model Context Protocol integration, providing a unified interface for diverse AI capabilities through intelligent agent orchestration.
