from dispatcher.actions import file_sort, reminder

TOOL_MAP = {
    "sort_files": file_sort.run,
    "set_reminder": reminder.run,
}


def dispatch(tool_call: dict) -> dict:
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})

    fn = TOOL_MAP.get(name)
    if fn is None:
        return {"summary": f"Unknown tool: {name}", "detail": ""}

    try:
        return fn(**args)
    except TypeError as e:
        return {"summary": "Bad arguments from model", "detail": str(e)}
    except Exception as e:
        return {"summary": "Action failed", "detail": str(e)}
