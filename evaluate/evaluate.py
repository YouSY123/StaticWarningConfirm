import sys
import json
import os
sys.path.append("src/")

from confirm import confirm_project

def eval_ours_on_SAFP_Bench_C_one_type(
    type_name, 
    warning_fp, 
    type_des,
    project
):

    with open(warning_fp, "r") as f:
        dataset = json.load(f)
    f.close()

    res = {
        "TT": [], 
        "TF": [], 
        "TU": [], 
        "FT": [], 
        "FF": [], 
        "FU": []
    }

    if not os.path.exists(f"../results-ours-gpt/{project}"):
        os.mkdir(f"../results-ours-gpt/{project}")

    if not os.path.exists(f"../results-ours-gpt/{project}/{type_name}"):
        os.mkdir(f"../results-ours-gpt/{project}/{type_name}")

    static_analysis_result_list = []
    log_path_list = []
    result_path_list = []
    statistics_path = f"../results.txt"
    ground_truth_list = []

    for idx, warning in enumerate(dataset):

        if "result" in warning:
            ground_truth = warning["result"]
            warning.pop("result")
        else:
            continue
        if "explain" in warning:
            warning.pop("explain")
        if "bug_line_constraints" in warning:
            warning.pop("bug_line_constraints")
        if "var_assign_conditions" in warning:
            warning.pop("var_assign_conditions")
        if "pointer_null_postconditions" in warning:
            warning.pop("pointer_null_postconditions")
        if "early_jump_constraints" in warning:
            warning.pop("early_jump_constraints")
        warning["bug type"] = type_des

        if ground_truth != 0 and ground_truth != 1:
            print(type_name, warning_fp, ground_truth)

        ground_truth_list.append(ground_truth)

        if not os.path.exists(f"../results-ours-gpt/{project}/{type_name}/{idx}"):
            os.mkdir(f"../results-ours-gpt/{project}/{type_name}/{idx}")

        static_analysis_result_list.append(str(warning))
        log_path_list.append(f"../results-ours-gpt/{project}/{type_name}/{idx}/log.txt")
        result_path_list.append(f"../results-ours-gpt/{project}/{type_name}/{idx}/result.txt")

        

    result_list = confirm_project(
        project_dir=f"/home/tcz/Static-Warning-Confirmation/{project}", 
        static_analysis_result_list=static_analysis_result_list, 
        log_path_list=log_path_list, 
        result_path_list=result_path_list, 
        database_path="../temp",
        statistics_path = statistics_path, 
        project_name=project
    )

    for idx, result in enumerate(result_list):

        if ground_truth_list[idx] == 1:
            if result == "True positive":
                res["TT"].append(idx)
            elif result == "False positive":
                res["TF"].append(idx)
            else:
                res["TU"].append(idx)
        else:
            if result == "True positive":
                res["FT"].append(idx)
            elif result == "False positive":
                res["FF"].append(idx)
            else:
                res["FU"].append(idx)
        
    with open(f"../results-ours-gpt/{project}/{type_name}/{type_name}_statistics.json", "w") as f:
        json.dump(res, f, indent = 4)



def eval_ours_on_SAFP_Bench_C_openssl():

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="BOF", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/BOF/codeql_openssl_cwe122.json", 
        type_des="Buffer overflow",
        project="openssl"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="UAF", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/UAF/codeql_openssl_cwe416.json", 
        type_des="Use after free", 
        project="openssl"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_codeql", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/codeql/codeql_openssl_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="openssl"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_cppcheck", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/cppcheck/cppcheck_openssl_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="openssl"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_infer", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/infer/infer_openssl_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="openssl"
    )


def eval_ours_on_SAFP_Bench_C_libav():

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_codeql", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/codeql/codeql_libav_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="libav"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_cppcheck", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/cppcheck/cppcheck_libav_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="libav"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_infer", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/infer/infer_libav_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="libav"
    )


def eval_ours_on_SAFP_Bench_C_linux():

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="NPD_codeql", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/NPD/codeql/codeql_kernel69_nullpointer.json", 
        type_des="Null pointer dereference", 
        project="linux"
    )

    eval_ours_on_SAFP_Bench_C_one_type(
        type_name="UAF", 
        warning_fp="../LLM-Enhanced-Path-Feasibility-Analysis/benchmark/UAF/codeql_kernel69_cwe416.json", 
        type_des="Use after free", 
        project="linux"
    )




if __name__ == "__main__":
    eval_ours_on_SAFP_Bench_C_libav()
    eval_ours_on_SAFP_Bench_C_openssl()