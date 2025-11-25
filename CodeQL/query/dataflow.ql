import cpp
import semmle.code.cpp.dataflow.new.DataFlow

module FilteredFlowConfig implements DataFlow::ConfigSig {

    predicate isSource(DataFlow::Node source) {
        exists(Variable v |
            v.getName() = "b" and
            source.asExpr() = v.getAnAccess() and
            not source.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%")
        )
    }

     predicate isSink(DataFlow::Node sink) {
        not exists(Variable v | 
            v.getName() = "b" and 
            sink.asExpr() = v.getAnAccess()
        )
        and
        not sink.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%") and
        not sink.getLocation().getFile().getAbsolutePath().matches("%/usr/lib/%")

    }

    predicate isBarrier(DataFlow::Node node) {
        node.getLocation().getFile().getAbsolutePath().matches("%/usr/include/%") or
        node.getLocation().getFile().getAbsolutePath().matches("%/usr/lib/%")
    }
}

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
  