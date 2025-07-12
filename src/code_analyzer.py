import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from config import Config

class CodeAnalyzer:
    def __init__(self):
        self.supported_extensions = Config.SUPPORTED_EXTENSIONS
    
    def get_folder_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Give the complete folder structure
        """
        def build_tree(path: Path, max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {}
            
            tree = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        tree[item.name] = {
                            'type': 'file',
                            'size': item.stat().st_size,
                            'extension': item.suffix
                        }
                    elif item.is_dir():
                        tree[item.name] = {
                            'type': 'directory',
                            'children': build_tree(item, max_depth, current_depth + 1)
                        }
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(Path(repo_path))
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze python files and return classes , function and there path in temp_file;
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'methods': [],
                        'docstring': ast.get_docstring(node) or "No docstring provided"
                    }
                    
                    # Get class methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'line_number': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                                'docstring': ast.get_docstring(item) or "No docstring provided"
                            }
                            class_info['methods'].append(method_info)
                    
                    classes.append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                    function_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or "No docstring provided"
                    }
                    functions.append(function_info)
            
            return {
                'classes': classes,
                'functions': functions,
                'file_path': file_path
            }
            
        except Exception as e:
            print(f"Error analyzing Python file {file_path}: {str(e)}")
            return {'classes': [], 'functions': [], 'file_path': file_path, 'error': str(e)}
    
    def analyze_cpp_file(self, file_path: str) -> Dict[str, Any]:
        """analyze cpp file and return class and unction with """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classes = []
            functions = []
            
            # Basic regex patterns for C++ parsing
            class_pattern = r'class\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*(?::\\s*(?:public|private|protected)\\s+[A-Za-z_][A-Za-z0-9_]*)?\\s*\\{'
            function_pattern = r'(?:(?:inline|static|virtual|explicit|const)?\\s+)*([A-Za-z_][A-Za-z0-9_]*(?:\\s*::\\s*[A-Za-z_][A-Za-z0-9_]*)*)\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\([^)]*\\)\\s*(?:const)?\\s*(?:override)?\\s*(?:;|\\{)'
            
            # Find classes
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                line_number = content[:match.start()].count('\\n') + 1
                
                class_info = {
                    'name': class_name,
                    'line_number': line_number,
                    'methods': [],
                    'docstring': f"C++ class {class_name}"
                }
                classes.append(class_info)
            
            # Find functions
            for match in re.finditer(function_pattern, content):
                return_type = match.group(1)
                function_name = match.group(2)
                line_number = content[:match.start()].count('\\n') + 1
                
                # Skip common C++ keywords that might be matched
                if function_name in ['if', 'while', 'for', 'switch', 'return', 'class', 'struct']:
                    continue
                
                function_info = {
                    'name': function_name,
                    'line_number': line_number,
                    'return_type': return_type,
                    'docstring': f"C++ function {function_name} returning {return_type}"
                }
                functions.append(function_info)
            
            return {
                'classes': classes,
                'functions': functions,
                'file_path': file_path
            }
            
        except Exception as e:
            print(f"Error analyzing C++ file {file_path}: {str(e)}")
            return {'classes': [], 'functions': [], 'file_path': file_path, 'error': str(e)}
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """analyze whole repository"""
        print("Analyzing repository structure...")
        folder_structure = self.get_folder_structure(repo_path)
        
        print("Analyzing code files...")
        code_analysis = {
            'python_files': [],
            'cpp_files': []
        }
        
        # Walk through all files
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                if file_ext == '.py':
                    analysis = self.analyze_python_file(file_path)
                    code_analysis['python_files'].append(analysis)
                elif file_ext in {'.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp'}:
                    analysis = self.analyze_cpp_file(file_path)
                    code_analysis['cpp_files'].append(analysis)
        
        return {
            'folder_structure': folder_structure,
            'code_analysis': code_analysis,
            'repo_path': repo_path
        }
    

code_analyzer = CodeAnalyzer()
result = code_analyzer.analyze_python_file("temp_repos/Repo-Data-Parser")