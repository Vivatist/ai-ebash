# Ai-ebash!

Console utility for integrating artificial intelligence into a Linux terminal. Allows you to ask an AI question and execute the scripts and commands suggested by the AI in the terminal. It will be useful for novice Linux administrators.

The project is in the pre-alpha stage. In case of problems with the installation or operation of the Ai-bash utility, please contact me.

## Features

- Send chat-style prompts to an LLM (configurable model and endpoint).
- Parse Markdown responses and highlight/number fenced `bash` code blocks.
- Interactive selection and (optional) execution of code blocks.
- Rich console output via `rich`.
- Configurable via `config.toml`.

## Requirements

- Python 3.9+

## Installation Ubuntu/Debian

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

### Example
```bash
ai Hello AI! Write example script.
```
or
```bash
ai -run Hello AI! Write example script.
```
## Removal

To completely remove the utility:
```bash
pipx uninstall ai-ebash
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

