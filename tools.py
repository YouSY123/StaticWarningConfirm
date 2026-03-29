from typing import List, Dict, Any, Optional, Union
import platform
import subprocess
import os


class AgentTools:

    def __init__(self, src_path:str, language:str = 'c-cpp'):
        self.system = platform.system()
        self.src_path = src_path
        self.language = language


    def __safe__dir__(self, path:str) -> str:
        '''Check if the relative path is safe to access'''

        try:
            final_path = os.path.abspath(os.path.join(self.src_path, path))
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")
        
        if not final_path.startswith(self.src_path):
            raise ValueError("Access to the path is denied")
        
        return final_path
        

    def list_files(self):
        '''List file structure in the src directory'''

        if self.system == "Linux":
            cmd = ["ls", "-R"]
        else:
            print("Only Linux for now")
            return
        
        try: 
        
            result = subprocess.run(
                cmd,
                timeout=300, 
                capture_output=True,
                text=True,
                shell=False, 
                cwd = self.src_path
            )
            return result.stdout

        except Exception as e:
            print(f"Error executing command: {e}")
            return



    def view_one_file(self, file_path:str, start_line:int = 1, end_line:int = 0):
        '''View a file in the src directory

            Args:

                file_path: the path of file you want to view
                start_line: the line number to start viewing
                end_line: the line number to end viewing, use 0 to represent the end of file
        '''

        try: 
            file_path = self.__safe__dir__(file_path)
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        if end_line == 0:
            awk_script = f"NR >= {start_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"
        else:
            awk_script = f"NR >= {start_line} && NR <= {end_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"

        if self.system == "Linux":
            cmd = ["awk", awk_script, file_path]
        else:
            print("Only Linux for now")
            return
        
        try:
            result = subprocess.run(
                cmd,
                timeout=300, 
                capture_output=True,
                text=True,
                shell=False, 
                cwd = self.src_path
            )
            return result.stdout
        except Exception as e:
            print(f"Error executing command: {e}")
            return


    def search_in_directory(self, pattern:str, dir:str):
        '''Find string in a directory

            Args:

                pattern: the string pattern you want to find
                dir: the directory you want to search in
        '''

        try:
            dir = self.__safe__dir__(dir)
        except ValueError as e:
            print(f"Error: {e}")
            return

        if self.system == "Linux":
            cmd = ["grep", "-r", "-n", pattern, dir]
        else:
            print("Only Linux for now")
            return
        
        try:

            result = subprocess.run(
                cmd,
                timeout=300, 
                capture_output=True,
                text=True,
                shell=False, 
                cwd = self.src_path
            )
            return result.stdout

        except Exception as e:
            print(f"Error executing command: {e}")
            return
        


if __name__ == "__main__":
    tools = AgentTools(src_path="/home/shuyang/Project/results")
    print(tools.view_one_file("double-free1/test.cpp", 1, 10))