# A Sound of Distant Thunder - Setup Guide

This guide explains how to set up the necessary environment to run this text-based adventure game.

## 1. Install Python 3

If you don't already have Python 3 installed, you'll need to get it.

* **Windows:**
    * Download the latest stable Python 3 installer from [python.org/downloads/windows/](https://www.python.org/downloads/windows/).
    * Run the installer.
    * **Important:** On the first screen of the installer, make sure to check the box that says **"Add python.exe to PATH"** or **"Add Python <version> to PATH"**.
    * Proceed with the default installation options.
* **macOS:**
    * Python 3 might already be installed. Open the Terminal app and type `python3 --version`. If it's installed, you'll see a version number.
    * If not installed, download the macOS installer from [python.org/downloads/mac-osx/](https://www.python.org/downloads/mac-osx/) and run it. The installer usually handles adding Python to your PATH.
* **Linux:**
    * Python 3 is usually pre-installed on most modern Linux distributions. Open your terminal and type `python3 --version`.
    * If it's not installed, use your distribution's package manager. Examples:
        * Debian/Ubuntu: `sudo apt update && sudo apt install python3 python3-venv python3-pip`
        * Fedora: `sudo dnf install python3 python3-pip`

## 2. Clone the Repository

If you haven't already, clone this project repository to your local machine using Git:

```bash
git clone <repository_url> # Replace <repository_url> with the actual URL
cd a_sound_of_distant_thunder # Navigate into the project directory
3. Create and Activate a Virtual EnvironmentUsing a virtual environment keeps project dependencies separate.Navigate to the project root directory (a_sound_of_distant_thunder) in your terminal or Git Bash.Create the virtual environment (this creates a folder named venv):# On Windows (using python launcher or full path if needed)
py -m venv venv 
# OR (if 'py' doesn't work)
python -m venv venv 

# On macOS/Linux
python3 -m venv venv
Activate the virtual environment:Windows (Git Bash):source venv/Scripts/activate
Windows (Command Prompt/PowerShell):.\venv\Scripts\activate 
macOS/Linux:source venv/bin/activate
Your terminal prompt should now start with (venv).4. Install DependenciesWith the virtual environment active, install the required packages from the requirements.txt file:pip install -r requirements.txt
(If pip needs upgrading, you might see a message suggesting python -m pip install --upgrade pip)-5. Run the GameMake sure you are still in the project root directory (a_sound_of_distant_thunder) and the virtual environment (venv) is active. Run the game using the following command:python -m
-