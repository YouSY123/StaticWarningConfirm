from src.process import StaticAnalysisWarningsConfirmation
import asyncio

def confirm(
    project_dir: str, 
    static_analysis_result: str, 
    log_path: str, 
    result_path: str
):
    
    confirmator = StaticAnalysisWarningsConfirmation(
        root_dir=project_dir,
        static_analysis_result=static_analysis_result,
        log_path=log_path,
        result_path=result_path
    )

    result = asyncio.run(confirmator.start())
    return result[0]