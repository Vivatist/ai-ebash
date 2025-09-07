# Ai-bash!
Console utility for integrating artificial intelligence into a Linux terminal. Allows you to ask an AI question and execute the scripts and commands suggested by the AI in the terminal. It will be useful for novice Linux administrators. 
  
The project is in the pre-alpha stage. In case of problems with the installation or operation of the Ai-bash utility, please contact me.

## Setup

```bash
# Cloning the repository
git clone https://github.com/Vivatist/ai-bash.git

# Making the installer executable
cd ai-bash
chmod +x install.sh

# Running the installation with root rights
sudo ./install.sh
```



### Run
If an error occurs on the first startup after installation, restart the terminal.
```bash
ai [-run] Your request to the AI
```

### Example
```bash
ai Write a script in bash that outputs a list of files in the current directory.
```
or
```bash
ai -run Write a script in bash that outputs a list of files in the current directory.
```

## Remove
Execute commands in the directory of the package that was downloaded during installation (ai-bash/)
```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```
