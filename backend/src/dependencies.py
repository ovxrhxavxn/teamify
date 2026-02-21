from fastapi import Query


def pagination(
        
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
    
    ):
    return {"limit": limit, "offset": offset}