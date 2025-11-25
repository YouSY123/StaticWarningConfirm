import cpp
import semmle.code.cpp.dataflow.DataFlow

from 
    AllocationExpr alloc, Variable v, DataFlow::Node source, DataFlow::Node sink
where
    v.getName() = "b" and
    DataFlow::localFlow(source, sink) and
    source.asExpr() = alloc and
    sink.asExpr() = v.getAnAccess()
select 
    alloc, 
    alloc.getLocation().getFile().getBaseName() + ":" + alloc.getLocation().getStartLine().toString() as location,
    alloc.getEnclosingFunction().getName() as function_location
    