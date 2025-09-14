# Ai-ebash!

Console utility for integrating artificial intelligence into a Linux terminal. Allows you to ask an AI question and execute the scripts and commands suggested by the AI in the terminal. It will be useful for novice Linux administrators.

The project is in the pre-alpha stage. In case of problems with the installation or operation of the Ai-bash utility, please contact me.

## Features

- Sends requests to LLM from the command line with a simple command and receives responses in a formatted, easy-to-read form
- Supports dialog mode (key -d). By default, the quick questions mode with a return to the console works without a key.
- In the dialog mode, it allows you to run scripts proposed by the neural network (be careful!)
  
## Requirements

- Python 3.11+

## Installation

### Debian/Ubuntu (pipx package)

1. Install pipx (if not already installed):
```bash
sudo apt update
sudo apt install pipx python3-venv -y
pipx ensurepath
```

2. Restart the terminal or update the PATH:
```bash
source ~/.bashrc
```

3. Install ai-ebash:
```bash
pipx install ai-ebash
```

1. Install the package:
```bash
sudo dpkg -i ./latest.deb
sudo apt-get install -f -y
```

### Windows (experemental)

1. Install Python v3.11+ (if not already installed):

2. Open CMD or PowerShell and install ai-ebash:
```bash
pip install ai-ebash
```
3. Restart Windows

### Example
```bash
ai Hello AI! Write example script.
```
or
```bash
ai -d Hello AI! Write example script.
```
## Uninstall

To completely remove the utility:

### If installed via pipx:
```bash
pipx uninstall ai-ebash
```

### If installed via DEB package:
```bash
sudo apt remove python3-ai-ebash
# Or for complete deletion, including configuration files:
sudo apt purge python3-ai-ebash
```

### If installed via Windows:
```bash
pip uninstall ai-ebash
```

### You can also use dpkg.:
```bash
sudo dpkg -r ai-ebash
# Or for complete deletion, including configuration files:
sudo dpkg -P ai-ebash
```

## Security

Do NOT execute arbitrary code returned by an LLM without review. Executing assistant-provided code has security and safety risks. Recommended mitigations:

## Contributing

1. Localization to any languages
2. Fork the repo and create a feature branch.
3. Add tests for new behavior.
4. Open a PR with a clear description.

## License

MIT

## Contact

andrey.bch.1976@gmail.com. Issues and PRs are welcome. Include logs and reproduction steps

