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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 MCP Navigator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🤝 Contributing

We welcome contributions to MCP Navigator! This project thrives on community involvement and we appreciate any help you can provide.

### How to Contribute

1. **Fork the Repository**
   - Fork this repository to your GitHub account
   - Clone your fork locally: `git clone https://github.com/yourusername/MCP_Navigator.git`

2. **Set Up Development Environment**
   ```bash
   cd MCP_Navigator
   uv sync
   # Install Node.js dependencies if working on browser MCPs
   npx @playwright/mcp@latest
   npx @openbnb/mcp-server-airbnb
   npx duckduckgo-mcp-server
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes
   git checkout -b fix/your-bug-description
   ```

4. **Make Your Changes**
   - Follow the existing code style and conventions
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all existing tests pass

5. **Test Your Changes**
   ```bash
   # Run the application to test your changes
   uv run client.py
   
   # Test specific functionality
   # Add any new test files to the tests/ directory
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new MCP server integration"
   # Use conventional commit messages:
   # feat: new feature
   # fix: bug fix
   # docs: documentation changes
   # style: formatting changes
   # refactor: code refactoring
   # test: adding tests
   # chore: maintenance tasks
   ```

7. **Push and Create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Provide a clear description of your changes
   - Reference any related issues

### Contribution Guidelines

#### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add type hints where appropriate
- Include docstrings for functions and classes

#### MCP Server Development
- When adding new MCP servers, follow the existing pattern in `servers/`
- Use FastMCP for Python servers when possible
- Document any new environment variables or configuration options
- Update the main client configuration in `client.py`

#### Testing
- Add tests for new functionality in the `tests/` directory
- Ensure browser automation tests work in both headless and visible modes
- Test MCP server integrations thoroughly

#### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Document any breaking changes clearly

### Areas for Contribution

- **New MCP Servers**: Add integrations with additional services
- **Enhanced Browser Automation**: Improve Playwright integration
- **UI/UX Improvements**: Better CLI interface or web interface
- **Testing**: Expand test coverage
- **Documentation**: Improve guides and examples
- **Performance**: Optimize agent response times
- **Error Handling**: Better error messages and recovery

### Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code Review**: All contributions require review before merging

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

Thank you for contributing to MCP Navigator! 🚀

---

**MCP Navigator** demonstrates the power of Model Context Protocol integration, providing a unified interface for diverse AI capabilities through intelligent agent orchestration.
