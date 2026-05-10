from typing import List, Dict, Any

def get_target_departments(event_type: str, customer_segment: str, loan_size: float) -> List[str]:
    """
    Determines which departments should be involved based on the event payload.
    Returns a list of department IDs.
    """
    departments = set()
    
    # Always include the relevant regional branch (mocking Sfax for now)
    departments.add("DIR_SFAX")
    
    if event_type == "early_warning":
        departments.add("DIR_RISQUE")
        departments.add("DIR_DATA")
        
        if customer_segment == "GGEI":
            departments.add("DIR_GGEI")
            
        if loan_size > 5000000: # > 5M TND
            departments.add("DIR_ALM")
            departments.add("DIR_GARANTIES")
            
    elif event_type == "default":
        departments.add("DIR_RISQUE")
        departments.add("DIR_RECOUVREMENT")
        departments.add("DIR_GARANTIES")
        
    return list(departments)
