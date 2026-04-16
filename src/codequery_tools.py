import subprocess
from langchain.tools import tool
import os

def build_codequery_db(
    project_dir:str, 
    db_dir: str
):
    
    global CODEQUERY_PROJECT_PATH
    global CODEQUERY_DB_PATH

    CODEQUERY_PROJECT_PATH = project_dir

    cscope_files_path = os.path.join(db_dir, "cscope.files")
    cscope_out_path = os.path.join(db_dir, "cscope.out")
    ctags_out_path = os.path.join(db_dir, "tags")

    CODEQUERY_DB_PATH = os.path.join(db_dir, "codequery_database.db")

    cmd_list = [
        f"find . -iname \"*.c\" > {cscope_files_path}",
        f"find . -iname \"*.cpp\" >> {cscope_files_path}", 
        f"find . -iname \"*.cxx\" >> {cscope_files_path}", 
        f"find . -iname \"*.cc\" >> {cscope_files_path}", 
        f"find . -iname \"*.h\" >> {cscope_files_path}", 
        f"find . -iname \"*.hpp\" >> {cscope_files_path}", 
        f"find . -iname \"*.hxx\" >> {cscope_files_path}", 
        f"find . -iname \"*.hh\" >> {cscope_files_path}", 
        f"cscope -cb -i {cscope_files_path} -f {cscope_out_path}", 
        f"ctags --fields=+i -n -R -L {cscope_files_path} -f {ctags_out_path}", 
        f"cqmakedb -s {CODEQUERY_DB_PATH} -c {cscope_out_path} -t {ctags_out_path}"
    ]

    try: 

        for cmd in cmd_list:

            subprocess.run(
                cmd, 
                timeout=600, 
                capture_output=True, 
                text=True, 
                shell=True, 
                cwd=CODEQUERY_PROJECT_PATH
            )

    except Exception as e:

        print(f"Error building database: {e}")
        return "Fail"
    
    return "Succeed"


#@tool
def get_information_of_project(
    option: int, 
    target: str, 
    filtered_by_path: str = ""
) -> str:
    
    """Get information from source code of the project

        Args:
        ----------
        option: int
            Determines the type of information you want to get. Accepted values:
            1: The position of the target symbol
            2: The position of the target function or macro definition
            3: The position of the target class or struct
            4: Files including the target file
            5: Full file path of the target file
            6: Functions calling the target function
            7: Functions called by the target function
            8: Calls of the target function or macro
            9: Members and methods of the target class
            10: Class which owns the target member or method
            11: Children of the target class (inheritance)
            12: Parent of the target class (inheritance)
            13: Functions or macros inside the target file
        
        target: str
            The target of the search. Refer to "option" for more details.
            Attention: "(", ")", "{", "}" are not needed for functions, structs and classes. For files, only input name and do not input the path

        filtered_by_path: str
            Whether to filter the result by path.
            If you input a path, the result will be filtered by files in the path.
            If you keep the value "", the result will be based on the whole project.
        ----------

        Files in the result of the function only contain name, without any path information 

        Example:
        ----------
        get_information_of_project(option=2, target="func") will return the position of the definition of function "func"
        ----------
    """

    if filtered_by_path == "":

        cmd = ["cqsearch", 
               "-s", CODEQUERY_DB_PATH, 
               "-p", str(option), 
               "-t", target, 
               "-e"]

    else:

        cmd = ["cqsearch", 
               "-s", CODEQUERY_DB_PATH, 
               "-p", str(option), 
               "-t", target, 
               "-e", 
               "-b", filtered_by_path]

    try:
        result = subprocess.run(
            cmd, 
            timeout=300, 
            capture_output=True, 
            text=True, 
            shell=False, 
            cwd=CODEQUERY_PROJECT_PATH
        )
        
        return result.stdout
    
    except Exception as e:

        print(f"Query error: {e}")
        return 