import cpp
from Variable v, DeleteArrayExpr freeOperation
where
  v.getName() = "b" and
  freeOperation.getExpr().toString() = v.getName()
select
  freeOperation,
  freeOperation.getLocation().getFile().getBaseName() + ":" + 
    freeOperation.getLocation().getStartLine().toString() as location,
  freeOperation.getEnclosingFunction().getName() as function_location
    