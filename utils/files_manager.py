# Imports 
import csv
import os
import shutil
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

def get_all_dirs(bagpath: str | Path):
    """
    Build a dictionary mapping each subdirectory in `bagpath` to the list of files inside it.

    Parameters
    ----------
    bagpath : str
        Path to the directory containing bag subfolders.

    Returns
    -------
    dict
        Keys are subdirectory names, values are lists of file paths.

    Raises
    ------
    FileNotFoundError
        If `bagpath` does not exist.
    NotADirectoryError
        If `bagpath` is not a directory.
    """
     # Ensure base path exists
    if not os.path.exists(bagpath):
        raise FileNotFoundError(f"Path does not exist: {bagpath}")
    # Ensure it is a directory
    if not os.path.isdir(bagpath):
        raise NotADirectoryError(f"Path is not a directory: {bagpath}")

    tree = dict()
    try:
        bag_dirs = os.listdir(bagpath)  # May raise PermissionError
    except PermissionError as e:
        raise PermissionError(f"Cannot access directory: {bagpath}") from e

    for dir_ in bag_dirs:
        full_dir = os.path.join(bagpath, dir_)
        if dir_ not in tree.keys():
            tree[dir_] = list()
        
        for file in os.listdir(full_dir):
            file_ = os.path.join(full_dir, file)
            tree[dir_].append(file_)
        
    return tree

def extract_topics_as_dict(data):
    if isinstance(data, dict) and "topics_with_message_count" in data:
        items: Union[List[dict], None] = data.get("topics_with_message_count")
    elif isinstance(data, list):
        items = data
    else:
        items = None

    if not items:
        return {}
    
    out: Dict[str, Dict[str, Any]] = {}
    for entry in items:
        meta = entry.get("topic_metadata", {}) if isinstance(entry, dict) else {}
        name: Optional[str] = meta.get("name")
        if not name:
            # Skip malformed entries without a topic name
            continue

        qos = meta.get("offered_qos_profiles")
        if qos is None or (isinstance(qos, str) and qos.strip() == ""):
            qos = None  # normalize missing/empty QoS

        out[name] = {
            "type": meta.get("type"),
            "serialization_format": meta.get("serialization_format"),
            # "offered_qos_profiles": qos,
            "message_count": int(entry.get("message_count", 0)),
        }
    
    return out

def create_processed_folder(path: str|Path, processed_: str|Path, img: bool = True):
    final_folder = os.path.join(path, processed_)
    img_files = None
    if os.path.exists(final_folder):
        if os.path.isdir(final_folder):
            print(f"[INFO] Removing existing directory and its contents: {final_folder}")
            shutil.rmtree(final_folder)  # Deletes directory and all its contents
        else:
            print(f"[WARNING] Path exists but is a file. Removing: {final_folder}")
            os.remove(final_folder)
    csv_files = os.path.join(final_folder, "csv_files")
    os.makedirs(final_folder, exist_ok=True)
    os.makedirs(csv_files, exist_ok=True)
    if img:
        img_files = os.path.join(final_folder, "image_files")
        os.makedirs(img_files, exist_ok=True)
    print(f"[INFO] Directory created: {final_folder}, {csv_files} and {img_files}")
    return final_folder, csv_files, img_files


def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)

def save_topic_to_csv(topic_name, messages, output_dir="csv_topics"):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, topic_name.strip('/').replace('/', '_') + ".csv")

    # Aplanar todos los mensajes
    flattened_msgs = [flatten_dict(m[-1]) for m in messages]

    # Obtener todas las columnas presentes en todos los mensajes
    fieldnames = sorted({key for fm in flattened_msgs for key in fm.keys()})

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fm in flattened_msgs:
            writer.writerow(fm)

    print(f"✅ {topic_name}: {len(messages)} mensajes guardados en {csv_path}")
