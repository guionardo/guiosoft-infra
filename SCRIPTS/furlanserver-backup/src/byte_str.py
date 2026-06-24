def _process_comma(b: str) -> str:
    b = ''.join([c for c in b.replace(',', '.') if c == '.' or c.isdigit()])
    parts = b.split('.')
    if len(parts) <= 2:
        return b
    return ''.join(parts[:-1]) + '.' + parts[-1]


def parse_bytes(b: str) -> int:
    bv = _process_comma(b)

    if b.endswith('K'):
        mult = 1024
    elif b.endswith('M'):
        mult = 1024 * 1024
    elif b.endswith('G'):
        mult = 1024 * 1024 * 1024
    else:
        mult = 1

    return int(float(bv) * mult)
