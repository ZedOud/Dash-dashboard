def run(formula):
    def mass(formula, i=1):
        try:
            i = int(i)
        except:
            return '"i" must be an integer.'
        starti = i
        if not formula:
            return "No formula"
        DEBUG = False
        el = {
            'H': 1.008,
            'Li': 6.94,
            'C': 12.01,
            'N': 14.01,
            'O': 16.00,
            'F': 19.00,
            'Na': 22.99,
            'Mg': 24.31,
            'Al': 26.98,
            'Si': 28.09,
            'P': 30.97,
            'S': 32.07,
            'Cl': 35.45,
            'K': 39.10,
            'Ca': 40.08,
            'Cr': 52.00,
            'Mn': 54.94,
            'Fe': 55.85,
            'Co': 58.93,
            'Ni': 58.69,
            'Cu': 63.55,
            'Zn': 65.39,
            'Br': 79.90,
            'Rb': 85.47,
            'Sr': 87.62,
            'Ag': 107.87,
            'Sn': 118.71,
            'I': 126.90,
            'Cs': 132.91,
            'Ba': 137.33,
            'Au': 196.97,
            'Pb': 207.2
        }
        output = []
        m = 0
        buf = formula[0] if formula[0].isupper() else ''
        c = ''
        while i < len(formula):
            c = formula[i]
            if c.islower() or c.isdecimal():
                buf += c
            elif c.isupper() or c == '(' or c == ')':
                if not len(buf):
                    if DEBUG: output.append("Error!, nothing in buffer at: " + formula[i:])
                    else: return "Error!, nothing in buffer at: " + formula[i:]
                elif len(buf) == 1:
                    m += el[buf]
                    if DEBUG:
                        output.append(f'1:Adding mass {el[buf]} at "{c}" index {i}')
                else:
                    s = 1 + buf[1].islower()
                    temp = m
                    m += el[buf[:s]] * (int(buf[s:]) if buf[s:] else 1)
                    if DEBUG:
                        output.append(f'2:Adding mass {m - temp} at "{c}" index {i}')
                if c.isupper():
                    buf = c
                elif c == '(':
                    buf = ''
                    scangroup = mass(formula[i+1:])
                    try:
                        m_inner, i_shift = scangroup
                        m_inner, i_shift = float(m_inner), int(i_shift)
                    except:
                        return scangroup
                    i += i_shift + 2
                    num_shift = 0
                    for n in formula[i:]:
                        if n.isdecimal():
                            num_shift += 1
                        else:
                            break
                    temp = m
                    m += m_inner * (int(formula[i:i+num_shift]) if num_shift else 1)
                    i += num_shift - 1
                    if DEBUG:
                        output.append(f'3:Adding mass {m - temp} at {formula[i]} index {i}')
                elif c == ')':
                    print(m, i)
                    return m, i
                else:
                    if DEBUG: output.append("Error!, bad logic at: " + formula[i:])
                    else: return "Error!, bad logic at: " + formula[i:]
            else:
                if DEBUG: output.append("Error!, bad character at: " + formula[i:])
                else: return "Error!, bad character at: " + formula[i:]
            i += 1
        if DEBUG:
            output.append(f'Last in buf: {buf}')
        if not buf:
            pass
        elif len(buf) == 1:
            if buf in el:
                m += el[buf]
                if DEBUG:
                    output.append(f'4:Adding mass {el[buf]} at "{c}" index {i}')
            else:
                if DEBUG: output.append(f'Error!, bad element "{buf}" index {i}')
                else: return f'Error!, bad element "{buf}" index {i}'
        else:
            s = 1 + buf[1].islower()
            temp = m
            m += el[buf[:s]] * (int(buf[s:]) if buf[s:] else 1)
            if DEBUG:
                output.append(f'5:Adding mass {m - temp} at "{c}" index {i}')
        if m:
            output.append(f"Reached end of '{formula}', mass: {m}")
        else:
            output.append(f'Invalid input: "{formula}"')

        return '\n'.join(output)
    return mass(formula)
