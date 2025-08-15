# Imports
import sqlite3
from sqlite3 import Connection
from sqlite3 import Cursor
# Ros2 imports 
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

def connect(sqlite_path: str) -> tuple[Connection, sqlite3.Cursor]:
    """
    Establish a connection to a SQLite database and return both the connection and cursor.

    Args:
        sqlite_path (str): Path to the SQLite database file.

    Returns:
        tuple[Connection, sqlite3.Cursor]: A tuple containing the database connection object
        and a cursor object for executing SQL queries.

    Raises:
        ConnectionError: If the connection to the database fails.
    """
    try:
        conn_ = sqlite3.connect(sqlite_path)
    except Exception as e:
        raise ConnectionError(f"Error trying to connect to {sqlite_path}. Error: {e}")
    
    cursor_ = conn_.cursor()
    print("Connection successfully.")
    return conn_, cursor_ 
    
def close_connection(conn_: Connection) -> None:
    """
    Safely close an existing SQLite database connection.

    Args:
        conn_ (Connection): The active SQLite database connection to close.

    Raises:
        RuntimeError: If the connection cannot be closed.

    Prints:
        A confirmation message when the connection is closed successfully.
    """
    try:
        conn_.close()
    except Exception as e:
        raise RuntimeError(f"Error trying to close the SQLite connection. Error: {e}")
    
    print("Connection closed successfully")

# function for get general information of specific topic
def get_topic_id(cursor: Cursor, topic_name: str):
    
    # Get current id of topic 
    try:
        cursor.execute("SELECT id FROM topics WHERE name = ?;", (topic_name, ))
        result = cursor.fetchone()

    except Exception as e:
        raise TimeoutError(f"Error getting information from table. Error: {e}")

    return result[0]

def get_data_by_id(cursor: Cursor, topic_id: int, topic_type: str):
    # Get current id of topic 
    result = list()
    topic_type_ = get_message(topic_type)
    
    try:
        cursor.execute("SELECT * FROM messages WHERE topic_id = ?;", (topic_id, ))
        records = cursor.fetchall()
    
    except Exception as e:
        raise TimeoutError(f"Error getting information from table. Error: {e}")
    
    try:
        for row in records:
            list_from_row = list(row).copy()
            # if "Image" not in topic_type:
            list_from_row[-1] = deserialize_message(list_from_row[-1], topic_type_)
            # print(type(list_from_row[-1]))
            if not topic_type.endswith("Image"):
                list_from_row[-1] = ros_message_to_dict(list_from_row[-1])
            result.append(list_from_row)
    except Exception as e:
        raise TimeoutError(f"Error converting information from extract data. Error: {e}")
    # print(result[-1])
    return result

# local utilitaries
def ros_message_to_dict(msg):
    """
    Convierte cualquier mensaje ROS 2 en un diccionario de Python.
    Soporta mensajes anidados y listas de mensajes.
    """
    if hasattr(msg, "__slots__") and hasattr(msg, "_fields_and_field_types"):
        result = {}
        for slot in msg.__slots__:
            value = getattr(msg, slot)
            result[slot] = ros_message_to_dict(value)
        return result

    elif isinstance(msg, (list, tuple)):
        return [ros_message_to_dict(v) for v in msg]

    else:
        return msg
