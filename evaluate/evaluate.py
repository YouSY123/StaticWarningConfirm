from src.process import StaticAnalysisWarningsConfirmation
import asyncio
import json
import subprocess
import os

def evaluate_once(root_dir, static_analysis_result, log_path, result_path, project_name, ground_truth:bool, statistics_file, cve):

    sawc = StaticAnalysisWarningsConfirmation(
        root_dir = root_dir,
        static_analysis_result = static_analysis_result, 
        log_path = log_path, 
        result_path = result_path, 
    )

    with open(statistics_file, 'a') as f:
        result = asyncio.run(sawc.start())
        result = result[0]
        if result == "True positive": 
            if ground_truth == True:
                f.write(f'[{cve}] {project_name}: Correct. Result: {result}, Ground Truth: True positive\n')
                return True
            else:
                f.write(f'[{cve}] {project_name}: Incorrect. Result: {result}, Ground Truth: False positive\n')
                return False
        elif result == "False positive":
            if ground_truth == False:
                f.write(f'[{cve}] {project_name}: Correct. Result: {result}, Ground Truth: False positive\n')
                return True
            else:
                f.write(f'[{cve}] {project_name}: Incorrect. Result: {result}, Ground Truth: True positive\n')
                return False
        else:
            f.write(f'[{cve}] {project_name}: Uncertain. Result: {result}, Ground Truth: {"True positive" if ground_truth else "False positive"}\n')
            return None
        

def eval_primevul_dataset():

    git_problem = ["gpac", "redis", "libtiff", "php-src", "tensorflow", "linux"]

    statistics_file = "../statistics.txt"
    git_log_path = "../git_log.txt"

    with open(git_log_path, 'w') as f:
        f.write('')
    f.close()

    cwe_statistics_file = "../cwe_statistics.json"

    with open("../final_data.json", "r") as f:
        dataset = json.load(f)
    f.close()

    warning_cnt = 0

    for project in dataset:

        if project in git_problem: continue

        project_path = f"/home/tcz/Static-Warning-Confirmation/dataset/{project}"
        if not os.path.exists(f"/home/tcz/Static-Warning-Confirmation/dataset/{project}"):
            print(project)
            continue

        if not os.path.exists(f"../result/{project}"):
            os.mkdir(f"../result/{project}")

        for commit in dataset[project]["warnings"]:
            # switch to the commit
            try: 
                subprocess.run(["git", "checkout", commit], cwd = project_path, capture_output=True)

                last_commit = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd = project_path, capture_output=True).stdout[:-1].decode("utf-8")

                subprocess.run(["git", "checkout", "HEAD~1"], cwd = project_path, capture_output=True)

                now_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd = project_path, capture_output=True).stdout[:-1].decode("utf-8")

                diff = subprocess.run(["git", "diff"], cwd = project_path, capture_output=True).stdout.decode("utf-8")

                with open(git_log_path, 'a') as log_file:
                    log_file.write(f"Checked out commit {now_commit} for project {project}, fixed bug commit: {commit}\n")

                if diff != "" or now_commit != last_commit:
                    print(project, commit)
                    continue

            except Exception as e:
                with open(git_log_path, 'a') as log_file:
                    log_file.write(f"Failed to checkout commit {commit} for project {project}. Error: {str(e)}\n")
                continue

            for warning in dataset[project]["warnings"][commit]:

                warning_cnt += 1
                if warning_cnt <= 30:
                    continue

                warning_path = warning["project_file_path"]
                warning_abs_path = os.path.join(project_path, warning_path)
                warning_dir = os.path.dirname(warning_abs_path)
                warning["project_file_path"] = os.path.basename(warning_path)

                cve = warning["cve"]
                if not os.path.exists(f"../result/{project}/{cve}"):
                    os.mkdir(f"../result/{project}/{cve}")

                cwe = warning["cwe"]
                cwe = cwe[0]
                with open(cwe_statistics_file, 'r') as f:
                    cwe_json = json.loads(f.read())
                f.close()
                if cwe not in cwe_json:
                    cwe_json[cwe] = {"count": 0, "correct": 0, "incorrect": 0}

                result = evaluate_once(
                    root_dir=warning_dir, 
                    static_analysis_result=str(warning), 
                    log_path=f"../result/{project}/{cve}/log.txt", 
                    result_path=f"../result/{project}/{cve}/result.txt",
                    project_name=project, 
                    ground_truth=True,
                    statistics_file=statistics_file, 
                    cve = cve
                )

                cwe_json[cwe]["count"] += 1
                if result == True:
                    cwe_json[cwe]["correct"] += 1
                elif result == False:
                    cwe_json[cwe]["incorrect"] += 1

                with open(cwe_statistics_file, 'w') as f:
                    f.write(json.dumps(cwe_json, indent=4))
                f.close()
    
    print(warning_cnt)

if __name__ == "__main__":
    eval_primevul_dataset()