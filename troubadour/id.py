NEXT_ID = 0


def get_id() -> int:
    global NEXT_ID
    result = NEXT_ID
    NEXT_ID += 1
    return result
