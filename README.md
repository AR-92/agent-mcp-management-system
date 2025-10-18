# Improved FZF Enhanced MCP Server Manager

An enhanced command-line interface for managing MCP (Model Context Protocol) servers with fzf integration for the ultimate fuzzy selection experience. This improved version includes streamlined menus, batch operations, and enhanced UX.

## 🔄 FZF-Powered Interface (Default)

This is now the improved fzf-enhanced version that provides an interactive interface with powerful fuzzy search capabilities for all MCP server management operations, featuring streamlined navigation and enhanced functionality.

## 🚀 Features

- **FZF Integration**: Full integration with system fzf for powerful fuzzy search and selection
- **Interactive Menus**: Navigate all options through fzf-driven menus
- **Fuzzy Server Selection**: Find and select servers with partial names and fuzzy matching
- **Comprehensive Management**: Start, stop, restart, and monitor MCP servers
- **Qwen Integration**: Seamlessly integrate with Qwen for enhanced functionality
- **Dual Mode**: Command-line interface with fzf fallback for interactive mode
- **Enhanced Discovery**: Fuzzy matching helps find servers even with partial names
- **Streamlined Menu Structure**: Reduced redundancy and improved navigation flow
- **Dashboard View**: Comprehensive overview of all server statuses in one view
- **Batch Operations**: Manage multiple servers simultaneously with multi-select capability
- **Quick Actions**: Common operations accessible from the main menu
- **Direct Config Toggles**: Quick configuration changes without deep navigation
- **Simplified Exit**: Direct exit without confirmation prompts
- **Environment (.env) Management**: Create, edit, view, delete, and validate .env files

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-server-manager.git
cd mcp-server-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install fzf on your system (recommended):
```bash
# Arch Linux
sudo pacman -S fzf

# Ubuntu/Debian  
sudo apt install fzf

# macOS
brew install fzf
```

## 🛠️ Usage

### Command Line Interface

```bash
# Show help
python cli.py --help

# Server management
python cli.py start my-server
python cli.py stop my-server
python cli.py status
python cli.py restart my-server

# Configuration management
python cli.py config-show
python cli.py integrate
python cli.py list-qwen

# Use partial server names for fuzzy matching
python cli.py start backup    # Will match 'backup_restore_mcp_server'
python cli.py stop dokploy    # Will match 'dokploy_openapi_mcp_server'

# Interactive mode with full fzf navigation
python cli.py --fzf
python cli.py interactive
python cli.py fzf

# Run without arguments to enter interactive mode (if in TTY)
python cli.py
```

### Interactive Mode Features

When run without arguments in an interactive terminal (or with --fzf flag), the CLI provides:

- **Main Menu**: Navigate between server management, configuration, and Qwen integration
- **Server Management**: Start, stop, restart servers with fzf selection
- **Configuration Management**: View and manage server configurations
- **Qwen Integration**: Integrate servers with Qwen using fzf
- **Status Display**: Show server status with one click

## ⚡ Quick Start Examples

```bash
# Start interactive fzf mode (recommended)
python cli.py

# Or start directly with fzf flag
python cli.py --fzf

# Command line with fuzzy matching
python cli.py start backup    # Fuzzy matches server names
python cli.py status          # Show all server statuses
python cli.py integrate       # Integrate with Qwen
```

## Configuration

The tool uses a `config.json` file in the project root to manage server configurations:

```json
{
  "server_config": {
    "start_on_boot": false,
    "shutdown_on_exit": false,
    "environment": "development",
    "servers": {
      "my-server": {
        "enabled": true,
        "start_on_boot": false,
        "add_to_qwen": true
      }
    }
  }
}
```

## Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `status` | `st` | Show status of all servers |
| `dashboard` | - | Show comprehensive dashboard view |
| `start <server>` | `s <server>` | Start a specific server |
| `stop <server>` | `sp <server>` | Stop a specific server |
| `restart <server>` | `r <server>` | Restart a specific server |
| `start-all` | `sa` | Start all servers |
| `stop-all` | `spa` | Stop all servers |
| `restart-all` | `ra` | Restart all servers |
| `integrate` | `int` | Integrate MCPs with Qwen |
| `list-qwen` | `lq` | List integrated MCPs |
| `remove-all-qwen` | - | Remove all MCPs from Qwen |
| `qwen-config-path` | `qcp` | Show Qwen config path |
| `config-show` | `cfg` | Show current configuration |
| `config-list` | `clist` | List server configurations |
| `config-edit` | `cedit` | Edit server configuration |
| `list` | `ls` | List discovered servers |
| `env` | - | Manage environment (.env) files |
| `env-create` | - | Create .env file |
| `env-edit` | - | Edit .env file |
| `env-view` | - | View .env file contents |
| `env-delete` | - | Delete .env file |
| `env-validate` | - | Validate .env file format |
| `interactive`/`fzf` | - | Start interactive fzf mode |
| `--fzf` | flag | Start interactive fzf mode |

## FZF Integration

This CLI is built around system-wide fzf (fuzzy finder) integration, providing:

- Rich, interactive search interface
- Preview capabilities
- Better performance with large lists
- Multi-selection support
- Keyboard shortcuts and navigation
- Fuzzy matching for all selection operations

## 🏗️ Architecture

The application is designed around fzf integration:

- **FZF Interface**: Main application logic with fzf-driven selection
- **Server Manager**: Handles server lifecycle (start, stop, restart, status)
- **Qwen Manager**: Handles Qwen integration and settings
- **Configuration Management**: Manages server configurations with fzf selection
- **Dual Mode**: Supports both command-line and interactive fzf modes

## 🛠️ Customization

You can customize the application by:

1. Modifying the configuration in `config.json`
2. Adding new MCP server files to the `mcps/` directory
3. Adjusting fzf options in the CLI code
4. Extending the interactive menus as needed

## 🔧 Troubleshooting

- If you see "fzf not found" errors, install fzf on your system
- If interactive mode doesn't start, ensure you're running in an interactive terminal
- For issues with partial name matching, ensure server names exist in your configuration
- Check the log file `manager.log` for detailed error information
- Use `python cli.py --help` for command assistance

## License

MIT