import json
import urllib.request
import urllib.error
import webbrowser
from PyQt6.QtWidgets import QMessageBox

VERSION = "0.4.1"

class Updater:
    def __init__(self, parent=None):
        self.parent = parent
        self.repo_url = "https://github.com/21tesla/ldgraph"
        self.api_url = "https://api.github.com/repos/21tesla/ldgraph/releases/latest"

    def check_for_updates(self):
        try:
            req = urllib.request.Request(self.api_url, headers={'User-Agent': 'ldgraph-updater'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if latest_version and latest_version != VERSION:
                    msg = QMessageBox(self.parent)
                    msg.setWindowTitle("Update Available")
                    msg.setText(f"A new version (v{latest_version}) is available!\nYou are currently running v{VERSION}.")
                    msg.setInformativeText("Would you like to visit the GitHub releases page to download it?")
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
                    if msg.exec() == QMessageBox.StandardButton.Yes:
                        webbrowser.open(self.repo_url + "/releases/latest")
                else:
                    QMessageBox.information(self.parent, "Up to Date", f"You are already running the latest version of ldgraph (v{VERSION}).")
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                 QMessageBox.information(self.parent, "No Releases", f"You are running v{VERSION}.\n\nNo releases have been published on GitHub yet.")
            else:
                 QMessageBox.warning(self.parent, "Update Check Failed", f"Could not check for updates.\nHTTP Error: {e.code}")
        except Exception as e:
            QMessageBox.warning(self.parent, "Update Check Failed", f"Could not connect to GitHub to check for updates.\nError: {str(e)}")
