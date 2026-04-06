# examples for agents
from langchain.tools import tool

@tool
def get_example(type: str) -> str:

    """Get example for condition generation. 

    Args: 
        type: The type of example, can be one of the following:
        (1) "common"
        (2) "use-after-free and double-free"
        (3) "null-pointer-dereference"
        (4) "memory-leak"
        (5) "divided-by-zero"
        (6) "uninitialized-variable"
        (7) "buffer-overflow"
    """

    if type == "common":
        return get_example_base("common_example", "common")
    elif type == "use-after-free and double-free":
        return get_example_base('uaf1', 'use-after-free') + "\n\n" + get_example_base('df1', 'double-free')
    elif type == "null-pointer-dereference":
        return get_example_base("npd1", "null-pointer-dereference") + "\n\n" + get_example_base("npd2", "null-pointer-dereference")
    elif type == "memory-leak":
        return get_example_base("ml1", "memory-leak")
    elif type == "divided-by-zero":
        return get_example_base("dbz1", "divided-by-zero")
    elif type == "uninitialized-variable":
        return get_example_base("uv1", "uninitialized-variable")
    elif type == "buffer-overflow":
        return get_example_base("bof1", "buffer-overflow") + "\n\n" + get_example_base("bof2", "buffer-overflow")
    else:
        return "Type not supported. Supported types: common, use-after-free and double-free, null-pointer-dereference, memory-leak, divided-by-zero, uninitialized-variable."

def get_example_base(file_name, warning_name):

    with open(f'src/fewshot/{file_name}/{file_name}.cpp', 'r') as f:
        example_code = f.read()
        f.close()

    with open(f'src/fewshot/{file_name}/{file_name}_warning.txt', 'r') as f:
        example_warning = f.read()
        f.close()
    
    with open(f'src/fewshot/{file_name}/{file_name}_analysis.txt', 'r') as f:
        example_analysis = f.read()
        f.close()


    return f'''\
These are examples for how to generate confirmation conditions for typical {warning_name} warnings.

---------- The example ----------
The source cpp code:
```cpp
{example_code}
```

The warnings of the static analyzer:
{example_warning}

Then we try to analyze the code and give conditions for confirming the correctness of the warnings.
{example_analysis}
---------- End of the example ----------
'''