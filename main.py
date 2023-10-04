import json

from utils import xml_element_paths, extract_msn, get_xml_data, search_file_directory, check_for_text, get_page_blocks
from lxml import etree
import os
import pickle

fs_path = "" 
pgblk_file_paths = search_file_directory("")

fault_symptom = get_xml_data(fs_path)
fs_maskrange = fault_symptom.get('maskrange')

page_blocks = get_page_blocks(pgblk_file_paths)


def parse_fault_symptom_list(fault_symptom):
    fs_list = []
    for child in fault_symptom.findall("faultSymptom"):
        fault_symptom_ref = child.find(xml_element_paths['fault_symptom_key'])
        fault_symptom_effect = child.find(
            xml_element_paths['fault_symptom_effect'])
        maintenance_message_fault_code = []
        maintenance_message_source = []
        warning_message_description = []
        warning_message_fault_code = []
        maintenance_message_cms_message = []
        for msg in child.findall('message'):
            maintenance_message_fault_code.append(
                msg.get(xml_element_paths['maintenance_message_fault_code']))
            maintenance_message_source.append(
                msg.find(xml_element_paths['maintenance_message_source']).text)
            maintenance_message_cms_message.append(
                msg.find(xml_element_paths['maintenance_message_cms_message']).text)
        for warning in child.findall('warning'):
            warning_message_description.append(
                warning.find('warningSol/troubleDescription').text)
            warning_message_fault_code.append(warning.get('faultCode'))

        data = {
            'fault_symptom_key': check_for_text(fault_symptom_ref),
            'procedure_ref': child.find(xml_element_paths['procedure_ref']).text,
            'fault_symptom_effect': check_for_text(fault_symptom_effect),
            'maintenance_message_fault_code': maintenance_message_fault_code,
            'maintenance_message_source': maintenance_message_source,
            'warning_message_description': warning_message_description,
            'warning_message_fault_code': warning_message_fault_code,
            'maintenance_message_cms_message': maintenance_message_cms_message,
        }
        fs_list.append(data)
    return fs_list


def parse_page_block(page_block):
    # ATTRIBUTES
    maskrange = page_block.get('MASKRANGE')
    chap_nbr = page_block.get('CHAPNBR')
    attrib_key = page_block.get('KEY')

    effect = page_block.find("EFFECT/AIRCRAFT_RANGES/EFFACT/EFFRG").text
    title = page_block.find("TITLE").text

    # applic element used for EFFECT key conversion
    applic = page_block.find("EFFECT/applic/assert").attrib

    task_inv_data = []
    for child in page_block.findall("TASKINV"):
        task_dmc = child.get('DMC')
        task_key = child.get('KEY')
        dm_data = child.find("DMDATA")
        dm_title = dm_data.find("DMTITLE")
        info_name = dm_title.find("INFONAME")
        tech_name = dm_title.find("TECHNAME")
        task_title = child.find("TITLE/TXT").text

        topic_title = child.find("TASKSOL/TOPIC/TITLE").text
        topic_type = child.find("TASKSOL/TOPIC").get('TYPE')
        ref_title = child.find(
            "TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK/TITLE")
        ref_man = child.find(
            "TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK/TXTREF")
        lru_designations = []
        lru_fins = []

        if child.find("TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK") is not None:
            ref_loc = child.find(
                "TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/REFBLOCK").get("DMC")
        else:
            ref_loc = None

        for lru in child.findall("TASKSOL/TOPIC/SUBTINV/SUBTSOL/stepContent/stepBlock/action/LRU"):
            lru_designations.append(lru.find("EQUNAME/TXT").text)
            lru_fins.append(lru.find("EIN").text)

        task_inv_data.append({
            'task_dmc': task_dmc,
            'task_key': task_key,
            'info_name': info_name.text,
            'tech_name': tech_name.text,
            'task_title': task_title,
        })
    data = {
        'maskrange': maskrange,
        'chap_nbr': chap_nbr,
        'attrib_key': attrib_key,
        'effect': effect,
        'title': title,
        'applic': applic,
        'taskinv_data': task_inv_data,
        'topic_title': topic_title,
        'topic_type': topic_type,
        'lru_designations': lru_designations,
        'lru_fins': lru_fins,
        'ref_title': check_for_text(ref_title),
        'ref_loc': ref_loc,
        'ref_man': check_for_text(ref_man)
    }
    return data


fs_list = parse_fault_symptom_list(fault_symptom)

page_block_data = []
for page_block in page_blocks:
    data = parse_page_block(page_block)
    page_block_data.append(data)

test_data = []

for i in page_block_data:
    for task in i['taskinv_data']:
        for j in fs_list:
            if task['task_key'] == j['procedure_ref']:
                output = {
                    'fault_symptom_key': j['fault_symptom_key'],
                    'fault_symptom_effect': extract_msn(fs_maskrange, j['fault_symptom_effect']),
                    'maintenance_message_fault_code': j['maintenance_message_fault_code'],
                    'maintenance_message_source': j['maintenance_message_source'],
                    'procedure_ref': j['procedure_ref'],
                    'procedure_effect': extract_msn(i['maskrange'], i['effect']),
                    'procedure_key': task['task_key'],
                    'procedure_title': task['task_title'],
                    'warning_message_description': j['warning_message_description'],
                    'warning_message_fault_code': j['warning_message_fault_code'],
                    'topic_title': i['topic_title'],
                    'topic_type': i['topic_type'],
                    'ref_loc': i['ref_loc'],
                    'ref_title': i['ref_title'],
                    'ref_man': i['ref_man'],
                    'lru_designations': i['lru_designations'],
                    'lru_fin': i['lru_fins'],
                    'maintenance_message_cms_message': j['maintenance_message_cms_message'],
                    'ac_type': '350',
                    'compute_date': '',
                }
                test_data.append(output)


with open("my_file.pkl", "wb") as f:
    pickle.dump(test_data, f)
    print(pickle.dumps(test_data))

with open("data_output", "w") as fs:
    json.dump(test_data, fs)
