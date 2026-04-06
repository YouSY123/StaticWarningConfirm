from process import StaticAnalysisWarningsConfirmation
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

if __name__ == "__main__":

    sar = "Potential Double free\nFirst free at cmd-source-file.c:196\nSecond free at cmd-source-file.c:227"

    confirm(
        project_dir="/home/shuyang/Project/Static-Inspection-bugs/tmux-check", 
        static_analysis_result=sar,
        log_path="../log.txt", 
        result_path="../result.txt"
    )