from sqlalchemy.orm import Session
from app import models
from app.services.chat_tools.statistics import count_unresolved_issues, get_system_statistics
from app.services.chat_tools.issues import get_recent_issues, get_user_reported_issues, get_issue_by_id
from app.services.chat_tools.audit_logs import get_issue_audit_history

def dispatch_tool(db: Session, current_user: models.User, tool_name: str, arguments: dict) -> dict:
    """
    Executes the Python database function chosen by the LLM.
    """
    try:
        if tool_name == "count_unresolved_issues":
            count = count_unresolved_issues(db=db, current_user=current_user)
            return {"unresolved_issues_count": count}

        elif tool_name == "get_system_statistics":
            stats = get_system_statistics(db=db, current_user=current_user)
            return {"system_statistics": stats}

        elif tool_name == "get_recent_issues":
            limit = int(arguments.get("limit", 5))
            issues = get_recent_issues(db=db, current_user=current_user, limit=min(limit, 10))
            return {"recent_issues": issues}

        elif tool_name == "get_user_reported_issues":
            user_issues = get_user_reported_issues(db=db, current_user=current_user)
            return {"user_reported_issues": user_issues, "total_found": len(user_issues)}

        elif tool_name == "get_issue_by_id":
            issue_id = int(arguments.get("issue_id", 0))
            issue = get_issue_by_id(db=db, issue_id=issue_id, current_user=current_user)
            if not issue:
                return {"error": f"No issue found with ID #{issue_id}"}
            return {"issue_details": issue}

        elif tool_name == "get_issue_audit_history":
            issue_id = int(arguments.get("issue_id", 0))
            logs = get_issue_audit_history(db=db, issue_id=issue_id, current_user=current_user)
            return {"audit_history": logs, "issue_id": issue_id}

        else:
            return {"error": f"Unknown tool name: {tool_name}"}

    except Exception as e:
        return {"error": f"Failed executing tool '{tool_name}': {str(e)}"}
