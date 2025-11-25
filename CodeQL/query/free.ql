import cpp
from Variable v, FunctionCall freeCall
where
  v.getName() = "b" and
  (
    freeCall.getTarget().getName() = "free" and
    freeCall.getArgument(0) = v.getAnAccess()
  )
select 
  freeCall,
  freeCall.getLocation().getFile().getBaseName() + ":" + 
    freeCall.getLocation().getStartLine().toString() as location,
  freeCall.getEnclosingFunction().getName() as function_location
    