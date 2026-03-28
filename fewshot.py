# examples for agents

def get_example(type: str) -> str:
    if type == "common":
        return get_example_base("common_example", "common")
    elif type == "use-after-free":
        return get_example_base('uaf1', 'use-after-free')
    elif type == "double-free":
        return get_example_base('df1', 'double-free')
    else:
        return "Type not supported. Supported types: common, use-after-free, double-free."

def get_example_base(file_name, warning_name):

    with open(f'fewshot/{file_name}/{file_name}.cpp', 'r') as f:
        example_code = f.read()
        f.close()

    with open(f'fewshot/{file_name}/{file_name}_warning.txt', 'r') as f:
        example_warning = f.read()
        f.close()
    
    with open(f'fewshot/{file_name}/{file_name}_analysis.txt', 'r') as f:
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