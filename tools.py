import subprocess
import os
from typing import List, Dict, Any, Optional
import json


class AgentTools:
    def __init__(self, src_path:str, database_path:str, build_command:str, result_dir, language:str = 'c-cpp'):
        self.database_path = database_path
        self.src_path = src_path
        self.build_command = build_command
        self.language = language
        self.result_dir = result_dir
    

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


    # CodeQL query functions: 
    def codeql_execute_query(self, query_content:str, temp_query_file_path:str, output_format: str = 'bqrs'):
        '''
        '''
        with open(temp_query_file_path, 'w') as f:
            f.write(query_content)

        try:
            cmd = [
                'codeql',
                "query",
                "run",
                temp_query_file_path,
                '--database='+self.database_path,
                '--output='+ self.result_dir +'temp_results.'+output_format
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"CodeQL查询失败: {result.stderr}")

        except Exception as e:
            return {"success": False, "error": str(e)}
        
        try:
            cmd = [
                'codeql',
                'bqrs', 
                'decode',
                self.result_dir+'temp_results.'+output_format
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)

            with open(self.result_dir+'temp_result.txt', 'w') as f:
                f.write(result.stdout)
            f.close()

            return result.stdout

        except Exception as e:
            return {"success": False, "error": str(e)}



    def codeql_variable_get_all_operations(self, variable_name:str, target_file) -> str:
        '''
        '''
        query = f"""
import cpp

from Variable v, Stmt s, File f
where 
  v.getName() = "{variable_name}" and
  v.getAnAccess().getEnclosingStmt() = s and
  s.getLocation().getFile() = f and
  (f.getBaseName() = "{os.path.basename(target_file)}" or f.getRelativePath() = "{target_file}")
select 
  v.getName() as variable_name,
  s.getLocation().getFile().getBaseName() as file_name,
  s.getLocation().getStartLine() as start_line,
  s.getLocation().getStartColumn() as start_column,
  s.getLocation().getEndLine() as end_line,
  s.getLocation().getEndColumn() as end_column
"""
        return self.codeql_execute_query(query, self.result_dir+'temp_query.ql')


if __name__ == '__main__':
    at = AgentTools(src_path='test/', database_path='test/database_test', build_command='g++ test.cpp -o test', result_dir='CodeQL/')
    print(at.codeql_create_database())
    print(at.codeql_variable_get_all_operations('test', 'test/test.cpp'))