import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import tempfile
import shutil
from git import Repo
from pathlib import Path
from typing import Optional
from config import Config

class RepoDownloader:
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
        self.ensure_temp_dir()
    
    def ensure_temp_dir(self):
        """
        Create a temp directory if not exirst
        """
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def download_repo(self, repo_url: str) -> Optional[str]:
        """
        Download the github repo and return the path if exist else none
        """
        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            local_path = os.path.join(self.temp_dir, repo_name)
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            Repo.clone_from(repo_url, local_path)
            print(f"Repo downloaded at :  {local_path}")
            
            return local_path
            
        except Exception as e:
            print(f"Error downloading repository: {str(e)}")
            return None
    
    def cleanup(self, repo_path: str):
        """removing the temp folder"""
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                print(f"Cleaned up: {repo_path}")
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")


repo = RepoDownloader()
result = repo.download_repo("https://github.com/Alok-Kumar2005/Project-Kisan")
print(result)

# repo.cleanup(result)