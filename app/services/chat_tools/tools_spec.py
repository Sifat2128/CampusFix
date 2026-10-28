# Tool definitions in standard JSON Schema format for OpenAI / Ollama Function Calling
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "count_unresolved_issues",
            "description": "Counts how many campus issues are currently active/unresolved (OPEN, IN_PROGRESS, or ASSIGNED). Use this when the user asks about the count, number, or total of pending/unfixed issues.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_statistics",
            "description": "Retrieves high-level platform maintenance statistics: total issues reported, open count, in-progress count, resolved count, and closed count.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_issues",
            "description": "Retrieves the most recently reported campus issues with their titles, statuses, categories, and priorities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of issues to retrieve (default is 5, max 10)",
                        "default": 5
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_reported_issues",
            "description": "Retrieves the maintenance issues that were reported/submitted specifically by the currently logged-in user.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_issue_by_id",
            "description": "Looks up full details of a single campus issue by its numerical ID (e.g. issue #5 or issue 12).",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "integer",
                        "description": "The unique numerical identifier of the issue"
                    }
                },
                "required": ["issue_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_issue_audit_history",
            "description": "Looks up the timeline of historical events, status updates, or reassignments for a specific issue ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "integer",
                        "description": "The numerical ID of the issue to check audit logs for"
                    }
                },
                "required": ["issue_id"]
            }
        }
    }
]
