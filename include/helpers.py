def file_safe_name(name):
    """
    Create a file-safe name by replacing spaces with underscores and removing special characters.
    """
    return "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in name).strip().replace(" ", "_")