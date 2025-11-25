import subprocess
import os
from typing import List, Dict, Any, Optional
import json


class AgentTools:
    def __init__(self, src_path:str, database_path:str, build_command:str, tempfile_dir:str, language:str = 'c-cpp'):
        self.database_path = database_path
        self.src_path = src_path
        self.build_command = build_command
        self.language = language
        self.result_dir = tempfile_dir+'temp/'
        self.query_file_dir = tempfile_dir+'query/'
        if not os.path.exists(self.query_file_dir):
            os.mkdir(self.query_file_dir)
        if not os.path.exists(self.result_dir):
            os.mkdir(self.result_dir)
    

    def run_cmd(self, cmd: List[str], cwd: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
        '''
        A tool for the agents to run command.
        '''
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
            return {"returncode": proc.returncode, "stdout": proc.stdout or "", "stderr": proc.stderr or ""}
        except subprocess.TimeoutExpired:
            return {"returncode": None, "stdout": "", "stderr": f"timeout after {timeout}s"}
        except FileNotFoundError:
            return {"returncode": None, "stdout": "", "stderr": f"executable not found: {cmd[0]}"}
        except PermissionError as e:
            return {"returncode": None, "stdout": "", "stderr": f"permission denied: {str(e)}"}
        except Exception as e:
            return {"returncode": None, "stdout": "", "stderr": f"unhandled exception: {str(e)}"}
        

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


    # CodeQL query functions: 
    def codeql_query_variable_allocfree(self, var_name: str):
        from template import build_allocation_query, build_free_query, build_delete_array_query, build_delete_query
        queries = ['allocation', 'free', 'delete', 'delete_array']
        # build query file for each kind
        for query in queries:
            with open(f'{self.query_file_dir}{query}.ql', 'w') as f:
                if query == 'allocation':
                    f.write(build_allocation_query(var_name))
                elif query == 'free':
                    f.write(build_free_query(var_name))
                elif query == 'delete':
                    f.write(build_delete_query(var_name))
                elif query == 'delete_array':
                    f.write(build_delete_array_query(var_name))

        for query in queries:
            self.execute_query(query)

    
    def codeql_query_variable_dataflow(self, var_name:str):
        from template import build_dataflow_query
        with open(f'{self.query_file_dir}dataflow.ql', 'w') as f:
            f.write(build_dataflow_query(var_name=var_name))
        f.close()
        self.execute_query('dataflow')


if __name__ == '__main__':
    at = AgentTools(src_path='test/', 
                    database_path='test/database_test', 
                    build_command='g++ test.cpp -o test', 
                    tempfile_dir='CodeQL/',)
    at.codeql_create_database()
    at.codeql_query_variable_allocfree('b')
    at.codeql_query_variable_dataflow('b')