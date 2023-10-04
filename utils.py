from lxml import etree
import os

"""
    Column values: Path to element in XML
"""
xml_element_paths = {
    'fault_symptom_key': 'faultSymptomRef',
    'fault_symptom_effect': './/EFFECT/AIRCRAFT_RANGES/EFFACT/EFFRG',
    'maintenance_message_fault_code': 'faultCode',
    'maintenance_message_source': 'standardBMessageDisplay',
    'procedure_ref': 'refProcedure',
    'procedure_effect': 'TASKSOL/EFFECT/AIRCRAFT_RANGES/EFFACT/EFFRG',
    'procedure_key': 'TASKSOL',
    'procedure_title': 'TASKSOL/DMDATA/DMTITLE/INFONAME',
    'warning_message_description': 'faultCode',
    'warning_message_fault_code': 'warningSol/troubleDescription',
    'topic_title': 'TASKSOL/TOPIC/TITLE',
    'topic_type': 'TASKSOL/TOPIC',
    'ref_loc': 'TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK',
    'ref_title': 'TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK/TITLE',
    'ref_man': 'TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK/TXTREF',
    'lru_designations': 'TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/LRU/EQUNAME/TXT',
    'lru_fin': 'TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/LRU/EIN',
    'maintenance_message_cms_message': 'standardBMessageDisplay',
    'ac_type': '',
    'compute_date': '',
}


def extract_msn(mask_range, applicability_msn):
    mask_blocks = [mask_range[i:i + 4] for i in range(0, len(mask_range), 4)]

    mask_ranges = [(int(mask_blocks[i], 16), int(mask_blocks[i + 1], 16)) for i in range(0, len(mask_blocks), 2)]

    modified_msn = ''
    last_end = 0
    for start, end in mask_ranges:
        modified_msn += '0' * (start - last_end - 1)
        modified_msn += applicability_msn[start - 1:end]
        last_end = end

    binary_msn = ''.join(format(int(char, 16), '04b') for char in modified_msn)

    msn_values = [i + 1 for i, bit in enumerate(binary_msn) if bit == '1']

    return msn_values


def get_xml_data(file_path):
    data = etree.parse(file_path)
    root = data.getroot()
    return root


def search_file_directory(directory):
    files = []
    for root, dirs, filenames in os.walk(directory):
        for file in filenames:
            if "PGBLK" in file and file.endswith(".xml") or file.endswith(".XML"):
                files.append(os.path.join(root, file))
    return files


def check_for_text(element):
    if element is not None:
        return element.text
    else:
        return None


def get_page_blocks(file_paths):
    page_blocks = []
    for file in file_paths:
        page_block = get_xml_data(file)
        page_blocks.append(page_block)
    return page_blocks
