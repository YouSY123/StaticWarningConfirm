from process import StaticAnalysisWarningsConfirmation
import asyncio
from codequery_tools import build_codequery_db

def confirm(
    project_dir: str, 
    static_analysis_result: str, 
    log_path: str, 
    result_path: str, 
    database_path: str
):
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        return "build database fail"

    confirmator = StaticAnalysisWarningsConfirmation(
        root_dir=project_dir,
        static_analysis_result=static_analysis_result,
        log_path=log_path,
        result_path=result_path
    )

    result = asyncio.run(confirmator.start())
    return result[0]