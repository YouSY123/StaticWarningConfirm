def build_dataflow_query(var_name:str):
    return f'''\
import cpp
import semmle.code.cpp.dataflow.new.DataFlow

module FilteredFlowConfig implements DataFlow::ConfigSig {{

    predicate isSource(DataFlow::Node source) {{
        exists(Variable v |
            v.getName() = "{var_name}" and
            source.asExpr() = v.getAnAccess() and
            not source.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%")
        )
    }}

     predicate isSink(DataFlow::Node sink) {{
        not exists(Variable v | 
            v.getName() = "{var_name}" and 
            sink.asExpr() = v.getAnAccess()
        )
        and
        not sink.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%") and
        not sink.getLocation().getFile().getAbsolutePath().matches("%/usr/lib/%")

    }}

    predicate isBarrier(DataFlow::Node node) {{
        node.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%") or
        node.getLocation().getFile().getAbsolutePath().matches("%/usr/lib/%")
    }}
}}

module FilteredFlow = DataFlow::Global<FilteredFlowConfig>;

from DataFlow::Node source, DataFlow::Node sink
where FilteredFlow::flow(source, sink)
select 
  source,
  source.getLocation().getFile().getBaseName() + ":" + 
    source.getLocation().getStartLine().toString() as source_location,
  source.asExpr().getEnclosingFunction() as source_function,
  sink,
  sink.getLocation().getFile().getBaseName() + ":" + 
    sink.getLocation().getStartLine().toString() as sink_location,
  sink.asExpr().getEnclosingFunction() as sink_function
  '''



def build_allocation_query(var_name:str):
    return f'''\
import cpp
import semmle.code.cpp.dataflow.DataFlow

from 
    AllocationExpr alloc, Variable v, DataFlow::Node source, DataFlow::Node sink
where
    v.getName() = "{var_name}" and
    DataFlow::localFlow(source, sink) and
    source.asExpr() = alloc and
    sink.asExpr() = v.getAnAccess()
select 
    alloc, 
    alloc.getLocation().getFile().getBaseName() + ":" + alloc.getLocation().getStartLine().toString() as location,
    alloc.getEnclosingFunction().getName() as function_location
    '''

def build_free_query(var_name:str):
    return f'''\
import cpp
from Variable v, FunctionCall freeCall
where
  v.getName() = "{var_name}" and
  (
    freeCall.getTarget().getName() = "free" and
    freeCall.getArgument(0) = v.getAnAccess()
  )
select 
  freeCall,
  freeCall.getLocation().getFile().getBaseName() + ":" + 
    freeCall.getLocation().getStartLine().toString() as location,
  freeCall.getEnclosingFunction().getName() as function_location
    '''

def build_delete_query(var_name:str):
    return f'''\
import cpp
from Variable v, DeleteExpr freeOperation
where
  v.getName() = "{var_name}" and
  freeOperation.getExpr().toString() = v.getName()
select
  freeOperation,
  freeOperation.getLocation().getFile().getBaseName() + ":" + 
    freeOperation.getLocation().getStartLine().toString() as location,
  freeOperation.getEnclosingFunction().getName() as function_location
    '''

def build_delete_array_query(var_name:str):
    return f'''\
import cpp
from Variable v, DeleteArrayExpr freeOperation
where
  v.getName() = "{var_name}" and
  freeOperation.getExpr().toString() = v.getName()
select
  freeOperation,
  freeOperation.getLocation().getFile().getBaseName() + ":" + 
    freeOperation.getLocation().getStartLine().toString() as location,
  freeOperation.getEnclosingFunction().getName() as function_location
    '''