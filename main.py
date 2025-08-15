# Imports
import os
import cv_bridge
import cv2
from argparse import ArgumentParser
from pathlib import Path
from time import time
from time import sleep
from yaml import safe_load
# Local imports 
from utils.sqlite_manager import connect
from utils.sqlite_manager import close_connection
from utils.sqlite_manager import get_topic_id
from utils.sqlite_manager import get_data_by_id
from utils.files_manager import get_all_dirs
from utils.files_manager import create_processed_folder
from utils.files_manager import extract_topics_as_dict
from utils.files_manager import save_topic_to_csv

bridge = cv_bridge.CvBridge()

# Main Function to get info
def main():
    print("CLI app to get parameters and convert topic to csv")

    ap_ = ArgumentParser(description = "Convert data information from bag db to csv")
    ap_.add_argument('--bags_dir', default = "./bags", required = False, type = Path, help = "Consider include complete path or relative path using '/' and that dir have the bags directories to convert")
    ap_.add_argument('--docs_dir', default = "./docs", required = False, type = Path, help = "Path to record all csv outputs files.")
    ap_.add_argument('--processed_dir', default = "./processed", required = False, type = Path, help = "Directory path to record processed bags from db to csv.")
    local_args = ap_.parse_args() 

    if not local_args.bags_dir.exists():
        raise FileNotFoundError(local_args.bags_dir)
    if not local_args.docs_dir.exists():
        raise FileNotFoundError(local_args.docs_dir)
    if not local_args.processed_dir.exists():
        raise FileNotFoundError(local_args.processed_dir)

    bag_to_pocess = get_all_dirs(local_args.bags_dir)
    bag_processed = local_args.processed_dir

    while True:
        # Actual loop validation
        if len(bag_to_pocess) == 0:
            break

        print("""
              
####################################################
              Nuevo Procesamiento
####################################################

              """)
        start_time, current_time = time(), 0.0
        
        
        current_bag = list(bag_to_pocess.keys())[0]
        current_files = list(bag_to_pocess.values())[0]
        print(f"Proceso iniciado para los datos de bag name: {current_bag}.")

        processed_folder, cvs_folder, img_folder = create_processed_folder(bag_processed, current_bag)

        with open(current_files[0], "r", encoding = "utf-8") as f:
            current_yaml_data = safe_load(f)["rosbag2_bagfile_information"]
            
        topic_data = current_yaml_data["topics_with_message_count"]
        file_db: str = current_files[1]
        # print(current_yaml_data["relative_file_paths"])
        
        if not file_db.endswith(current_yaml_data["relative_file_paths"][0]):
            print(f"Error el archivo no concuerda con el descrito")
            exit()
        
        topics_values = extract_topics_as_dict(topic_data)
        sqlite_connection, cursor = connect(file_db)

        for topic in topics_values.keys():
            print(f"Iniciando procesamiento de topico {topic}.")
            topic_time = time()
            # Data extraction
            topics_values[topic]["id"] = get_topic_id(cursor, topic)
            topics_values[topic]["data"] = get_data_by_id(cursor, topics_values[topic]["id"], topics_values[topic]["type"])
            final_topic_time = time() - topic_time
            if "image" not in topic:
                save_topic_to_csv(topic, topics_values[topic]["data"], cvs_folder)
            else:
                imgs_temp = topics_values[topic]["data"]
                for num, img in enumerate(imgs_temp):
                    # print(type(img[-1]))
                    cv_image = bridge.imgmsg_to_cv2(img[-1], desired_encoding="bgr8")
                    stamp = f"{img[-1].header.stamp.sec}_{img[-1].header.stamp.nanosec}"
                    file_path_ = os.path.join(img_folder, f"{stamp}.png")

                    # Guardar imagen
                    cv2.imwrite(file_path_, cv_image)
                
            print(f"Finalizando procesamiento de topico {topic}. Tiempo de procesamiento: {final_topic_time} sg")
            

        close_connection(sqlite_connection)
        # print(topics_values)
        del bag_to_pocess[current_bag]
        current_time = time() - start_time
        print(f"Proceso finalizado para los datos del bag name: {current_bag}. Tiempo transcurrido: {current_time} sg")
        
    
    print("final process")


if __name__ == "__main__":
    main()