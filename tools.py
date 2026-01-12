import subprocess
import os
from typing import List, Dict, Any, Optional, Union
import json
import platform


class AgentTools:
    def __init__(self, src_path:str, database_path:str, build_command:str, tempfile_dir:str, language:str = 'c-cpp'):
        
        self.system = platform.system()
        
        self.database_path = database_path
        self.src_path = src_path
        self.build_command = build_command
        self.language = language
        self.result_dir = tempfile_dir+'temp/'
        self.query_file_dir = tempfile_dir+'query/'
        # if not os.path.exists(self.query_file_dir):
        #     os.mkdir(self.query_file_dir)
        # if not os.path.exists(self.result_dir):
        #     os.mkdir(self.result_dir)
    

    def run_cmd(self, cmd: str, cwd: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
        '''
        A tool for the agents to run command.
        '''
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, shell=True)
            return {"returncode": proc.returncode, "stdout": proc.stdout or "", "stderr": proc.stderr or ""}
        except subprocess.TimeoutExpired:
            return {"returncode": None, "stdout": "", "stderr": f"timeout after {timeout}s"}
        except FileNotFoundError:
            return {"returncode": None, "stdout": "", "stderr": f"executable not found: {cmd[0]}"}
        except PermissionError as e:
            return {"returncode": None, "stdout": "", "stderr": f"permission denied: {str(e)}"}
        except Exception as e:
            return {"returncode": None, "stdout": "", "stderr": f"unhandled exception: {str(e)}"}
        

    def list_files(self):
        '''
        List file structure in the src directory
        '''
        if self.system == 'Linux':
            return (self.run_cmd(cmd ='ls -R', cwd=self.src_path))['stdout']
        else:
            print('Only Linux currently')
            exit(1)
    

    def view_one_file(self, file_path:str, start_line:int = 1, end_line:Union[int, str] = '\\$'):
        '''
        View a file in the src directory
        file_path: the path of file you want to view
        start_line: the line number to start viewing
        end_line: the line number to end viewing
        '''
        if self.system == 'Linux':
            return (self.run_cmd(cmd = f'cat -n {file_path} | sed -n \"{start_line},{end_line}p\"', cwd=self.src_path))['stdout']
        else:
            print('Only Linux currently')
            exit(1)

    def grep_in_directory(self, pattern:str, dir:str):
        '''
        Find string in a directory
        pattern: the string pattern you want to find
        dir: the directory you want to search in
        '''
        if self.system == 'Linux':
            return (self.run_cmd(cmd = f'grep -r -n {pattern} {dir}', cwd=self.src_path))['stdout']
        else:
            print('Only Linux currently')
            exit(1)


    def codeql_create_database(self):
        '''
        Build database for CodeQL. 
        '''
        try:

            result = subprocess.run([
                'codeql', 'database', 'create', self.database_path, 
                '--language='+self.language, 
                '--source-root', self.src_path, 
                '--command', self.build_command,
                '--overwrite'
            ], capture_output=True, text=True, timeout=300)
            return{'database_path': self.database_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_query(self, query_name):
        query_path = self.query_file_dir+query_name+'.ql'
        try:
            result = subprocess.run([
                'codeql', 'query', 'run', query_path, 
                '--database='+self.database_path,
                '--output='+self.result_dir+'result_'+query_name+'.bqrs'
            ], capture_output=True, text=True)
        except Exception as e:
            return {"success": False, "error": str(e)}
        try:
            result = subprocess.run([
                'codeql', 'bqrs', 'decode', self.result_dir+'result_'+query_name+'.bqrs'
            ], capture_output=True, text=True)
            with open(self.result_dir+'result_'+query_name+'.txt', 'w') as f:
                f.write(result.stdout)
            f.close()
        except Exception as e:
            return {"success": False, "error": str(e)}



if __name__ == '__main__':
    at = AgentTools(src_path='.', 
                    database_path='test/database_test', 
                    build_command='g++ test.cpp -o test', 
                    tempfile_dir='CodeQL/')
    print(at.list_files())
    print(at.view_one_file('../results/double-free3/test.cpp', 1, 400))