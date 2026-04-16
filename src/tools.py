import platform
import subprocess
import os
from langchain.tools import tool

def init_tools(src_path:str, database_path):
    '''Get the project path'''
    global PROJECT_PATH
    PROJECT_PATH = src_path
    global DATABASE_PATH
    DATABASE_PATH = os.path.join(database_path, "codequery_database.db")


def safe_dir(path:str) -> str:
    '''Check if the relative path is safe to access'''
    try:
        final_path = os.path.abspath(os.path.join(PROJECT_PATH, path))
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")
    
    if not final_path.startswith(PROJECT_PATH):
        raise ValueError("Access to the path is denied")
    
    return final_path
        
@tool
def list_files(path:str):
    '''\
    List file structure in the directory

        Args: 
            path: the directory to list file, using relative path to the project directory
    '''
    try: 
        path = safe_dir(path)
    except ValueError as e:
        return f"Error: {e}"
    
    system = platform.system()
    if system == "Linux":
        cmd = ["ls"]
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
            cwd = path
        )
        return result.stdout
    except Exception as e:
        return f"Error executing command: {e}"


@tool
def view_one_file(file_path:str, start_line:int = 1, end_line:int = 0):

    '''\
        View a file in the src directory

        Args:
            file_path: the path of file you want to view
            start_line: the line number to start viewing
            end_line: the line number to end viewing, use 0 to represent the end of file
    '''

    try: 
        file_path = safe_dir(file_path)
    except ValueError as e:
        return f"Error: {e}"
    
    if end_line == 0:
        awk_script = f"NR >= {start_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"
    else:
        awk_script = f"NR >= {start_line} && NR <= {end_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"

    system = platform.system()
    if system == "Linux":
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
            cwd=PROJECT_PATH
        )
        return result.stdout
    
    except Exception as e:
        return f"Error executing command: {e}"


# def search_in_directory(self, pattern:str, dir:str):
#     '''Find string in a directory
#         Args:
#             pattern: the string pattern you want to find
#             dir: the directory you want to search in
#     '''
#     try:
#         dir = self.__safe__dir__(dir)
#     except ValueError as e:
#         return f"Error: {e}"
#     if self.system == "Linux":
#         cmd = ["grep", "-r", "-n", pattern, "."]
#     else:
#         print("Only Linux for now")
#         return
    
#     try:
#         result = subprocess.run(
#             cmd,
#             timeout=300, 
#             capture_output=True,
#             text=True,
#             shell=False, 
#             cwd = dir
#         )
#         return result.stdout
#     except Exception as e:
#         return f"Error executing command: {e}"

# same as view_one_file, but not defined as an agent tool
def view_one_file_not_tool(file_path:str, start_line:int = 1, end_line:int = 0):

    '''\
        View a file in the src directory

        Args:
            file_path: the path of file you want to view
            start_line: the line number to start viewing
            end_line: the line number to end viewing, use 0 to represent the end of file
    '''

    try: 
        file_path = safe_dir(file_path)
    except ValueError as e:
        return f"Error: {e}"
    
    if end_line == 0:
        awk_script = f"NR >= {start_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"
    else:
        awk_script = f"NR >= {start_line} && NR <= {end_line} {{ printf \"%6d | %s\\n\", NR, $0 }}"

    system = platform.system()
    if system == "Linux":
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
            cwd=PROJECT_PATH
        )
        return result.stdout
    
    except Exception as e:
        return f"Error executing command: {e}"
    
@tool
def view_one_function(
    file_path: str, 
    line: int
) -> str :
    
    """\
    Return the content of the function containing the line number in the given C/C++ source file.

    Args:
        file_path: the relative path to the C/C++ source file
        line: the line number that the function is expected to contain
    """

    # check whether the source file is a C/C++ source file
    c_cpp_extentions = {
        ".c", 
        ".cpp", 
        ".cxx", 
        ".cc", 
        ".h", 
        ".hpp", 
        ".hxx", 
        ".hh"
    }

    # check the file path
    try: 
        safe_dir(file_path)
    except ValueError as e:
        return f"Error: {e}"

    _, ext = os.path.splitext(file_path)
    if not ext.lower() in c_cpp_extentions:
        return "Error: Please give a C/C++ source file"
    
    filtered_by_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    cmd = [
        "cqsearch", 
        "-s", DATABASE_PATH, 
        "-p", "13", 
        "-t", file_name, 
        "-e", 
        "-b", filtered_by_path
    ]

    try:
        
        result = subprocess.run(
            cmd, 
            timeout=300, 
            capture_output=True, 
            text=True, 
            shell=False, 
            cwd=PROJECT_PATH
        ).stdout
    
    except Exception as e:

        print(f"Query error: {e}")
        return "Error"
    
    lines = result.split("\n")
    start_line = 0
    finish_line = 0

    for l in lines:
        if l == "": continue
        elements = l.split()
        cur_line = int(elements[1].split(":")[-1])
        if cur_line <= line:
            start_line = cur_line
        else:
            finish_line = cur_line - 1
            break

    return view_one_file_not_tool(
        file_path=file_path, 
        start_line=start_line, 
        end_line=finish_line
    )