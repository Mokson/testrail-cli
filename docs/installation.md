# Installation Guide

This guide covers various ways to install TestRail CLI on your system.

## Requirements

- Python 3.11 or higher
- pip (Python package installer)
- (Optional) pipx for isolated CLI tool installation

## Installation Methods

### Method 1: Using pip (Simple)

The simplest way to install TestRail CLI:

```bash
pip install testrail-cli
```

Verify the installation:

```bash
testrail --version
```

### Method 2: Using pipx (Recommended for CLI Tools)

[pipx](https://pypa.github.io/pipx/) installs CLI tools in isolated environments, preventing dependency conflicts:

1. Install pipx if you haven't already:

```bash
# On macOS
brew install pipx
pipx ensurepath

# On Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# On Windows
python -m pip install --user pipx
python -m pipx ensurepath
```

2. Install TestRail CLI:

```bash
pipx install testrail-cli
```

3. Verify:

```bash
testrail --version
```

### Method 3: Using Poetry (For Development)

If you're contributing to the project or want the latest development version:

1. Clone the repository:

```bash
git clone https://github.com/mokson/testrail-cli.git
cd testrail-cli
```

2. Install Poetry if needed:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies and the project:

```bash
poetry install
```

4. Run the CLI through Poetry:

```bash
poetry run testrail --version
```

### Method 4: Install from Source (Without Poetry)

```bash
git clone https://github.com/mokson/testrail-cli.git
cd testrail-cli
pip install -e .
```

## Upgrading

### If installed with pip:

```bash
pip install --upgrade testrail-cli
```

### If installed with pipx:

```bash
pipx upgrade testrail-cli
```

### If using Poetry:

```bash
cd testrail-cli
git pull
poetry install
```

## Verifying Installation

After installation, verify everything works:

```bash
# Check version
testrail --version

# View help
testrail --help

# Initialize configuration
testrail config init
```

## Platform-Specific Notes

### macOS

If you encounter SSL certificate issues:

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Linux

Ensure Python 3.11+ is installed:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip

# Fedora
sudo dnf install python3.11 python3-pip

# Arch
sudo pacman -S python python-pip
```

### Windows

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Ensure "Add Python to PATH" is checked during installation
3. Open Command Prompt or PowerShell and run:

```powershell
pip install testrail-cli
```

## Troubleshooting

### Command not found after installation

Ensure Python's scripts directory is in your PATH:

```bash
# macOS/Linux
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows
# Add %APPDATA%\Python\Scripts to your PATH environment variable
```

### Permission denied errors

Use the `--user` flag:

```bash
pip install --user testrail-cli
```

### SSL/TLS errors

Update pip and try again:

```bash
pip install --upgrade pip
pip install testrail-cli
```

### Dependency conflicts

Use pipx or a virtual environment to avoid conflicts:

```bash
# Using pipx (recommended)
pipx install testrail-cli

# Or using venv
python3 -m venv testrail-env
source testrail-env/bin/activate  # On Windows: testrail-env\Scripts\activate
pip install testrail-cli
```

## Next Steps

After installation, proceed to:

- [Configuration Guide](configuration.md) - Set up your TestRail credentials
- [Quick Start](../README.md#quick-start) - Start using the CLI
- [Command Reference](commands/) - Learn about available commands
