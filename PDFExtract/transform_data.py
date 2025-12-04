import pandas as pd
def indices_with_letters(lst):
    """
    Return a list of indices for items that contain any alphabetic character.
    """
    return [i for i, item in enumerate(lst) if any(ch.isalpha() for ch in str(item))]


def split_consecutive_chars(s: str) -> list:
    """Split string into groups of consecutive identical characters.
    Example: 'aabbbcd' -> ['aa', 'bbb', 'c', 'd']
    """
    if not s:
        return []
    
    groups = []
    current_group = s[0]
    
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            # Same character, add to current group
            current_group += s[i]
        else:
            # Different character, save current group and start new one
            groups.append(current_group)
            current_group = s[i]
    
    # Don't forget the last group
    groups.append(current_group)
    return groups


# s = 'RRRRRRRRRRaaaaaaaaaaiiiiiiiiiinnnnnnnnnn'

def split_into_chunks(s: str, chunk_size: int = 3) -> list:
    """Split string into chunks of given size.
    Example: 'Hello' with chunk_size=3 -> ['Hel', 'llo']
    Example: 'Hello' with chunk_size=2 -> ['He', 'el', 'll', 'lo']
    """
    chunks = []
    for i in range(len(s)//chunk_size):
        chunks.append(s[i:i + chunk_size])
    return chunks



def get_refined_string(s: str) -> str:
    if not s[0] == s[1]:
        return s
    groups = split_consecutive_chars(s)
    result = []
    for data in groups:
        if len(data) > 10:
            chunks = split_into_chunks(data, 10)
            result.extend([char[0] for char in chunks])
        else:
            result.append(data[0])
    return ''.join(result)

def get_schema() -> dict:
    schema = {
        'Rainfall': {
            'Depth (mm)': '',
            'Peak (mm/hr)': '',
            'Average (mm/hr)': ''
        },
        'Depth': {
            'Min (m)': '',
            'Max (m)': ''
        },
        'Flow': {
            'Min (m3/s)': '',
            'Max (m3/s)': '',
            'Volume (m3)': ''
        },
        'Velocity': {
            'Min (m/s)': '',
            'Max (m/s)': ''
        }
    }
    return schema

def get_data_list(file_path):
    dic = {}
    lis = []
    with open(file_path, "r", encoding="utf-8") as f:
        data_flow_started = False
        for data in f.readlines():
            data = data.strip()
            if 'Flow Survey Location' in data:
                parts = data.split(',')
                dic['header'] = parts
            if 'Rainfall Depth Flow Velocity' in data:
                data_flow_started = True
                continue
            if data and data_flow_started and 'Depth (mm)' not in data:
                parts = data.split()
                string_indexes = indices_with_letters(parts)[-1]
                string_to_refine = parts[string_indexes]
                dic[get_refined_string(string_to_refine)] = parts[string_indexes+1:]

    for key, value in dic.items():
        data_values = get_schema()
        if key == 'header':
            lis.append(value)
            continue
        if key == 'Rain':
            data_values['Rainfall']['Depth (mm)'] = value[0]
            data_values['Rainfall']['Peak (mm/hr)'] = value[1]
            data_values['Rainfall']['Average (mm/hr)'] = value[2]
        else:
            data_values['Depth']['Min (m)'] = value[0]
            data_values['Depth']['Max (m)'] = value[1]
                
            data_values['Flow']['Min (m3/s)'] = value[2]
            data_values['Flow']['Max (m3/s)'] = value[3]
            data_values['Flow']['Volume (m3)'] = value[4]
            data_values['Velocity']['Min (m/s)'] = value[5]
            data_values['Velocity']['Max (m/s)'] = value[6]
        d = {key: data_values}
        lis.append(d)
    return lis
        
        


            

