def escape_single_quotes(data) -> str:
    if type(data) != str:
        return data
    
    return data.replace("'", r"\'")