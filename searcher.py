import os 
import pprint as pp


def current_directory() -> str:
    """
    Description:
        回傳searcher.py本身存放目錄的絕對路徑
    """
    return os.getcwd()


def measure_directory() -> str:
    """
    Description:
        回傳MeasureData本身目錄的絕對路徑
    """
    target = 'MeasureData'
    target_exist = target in os.listdir(current_directory())

    if target_exist:
        pass
    else:
        os.mkdir(target)

    return os.path.join(os.getcwd(), target)


def measuredata_existfile() -> None:
    """
    Description:
        檢查MeasureDate資料夾中
        是否含有任何的實驗數據
    """
    without_flag = os.listdir(measure_directory())

    if without_flag:
        return True
    else:
        print('Hi, The folder called MeasureData is empty.\
               \nPlease put some experimental files (*.hdf5) here.') 


def directory_branch(path:str, FileDirectory={}) -> dict:
    """
    Description:
        search all files inside the current directory
    Arguments:
        path: 當下目錄絕對路徑
    """
                                                        # See details about how we use the "os" module at the following site
                                                        # https://www.runoob.com/python/python-os-path.html
    
    for element in os.listdir(path):                    # 輸出特定目錄中的所有元素
        element_path = os.path.join(path, element)   
                                                   
        if os.path.isdir(element_path):                 # 判斷特定元素是否為資料夾
            directory_branch(element_path)              # 若該元素為資料夾，則判定下層還有其他資料
        else:
            FileDirectory[element] = element_path
    
    return FileDirectory


def file_getabspath(filename:str, source_collection:dict) -> dict:
    """
    Description:
        搜尋特定檔案是否在source_collection內，如果存在
        則回傳該檔案的絕對路徑
    Arguments:
        filename: 檔案完整名稱
        source_collection: 目錄，另外可用directory_branch()建立檔案目錄
    """
    if filename in source_collection:
        return source_collection[filename]
    else:
        pass


def keyword_getabspath(keyword:str, source_collection:dict) -> dict:
    """
    Description:
        透過關鍵字找出符合的實驗紀錄檔及對應的絕對路徑
    Arguments:
        keyword:
        source_collection: 
    """
    found_result = {}

    for key, path in source_collection.items():
        if keyword in key:
            found_result[key] = path
        else:
            continue

    return found_result


