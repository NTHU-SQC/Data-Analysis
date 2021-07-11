#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : file_renamer.py
# Author            : Liam Lin
# Date              : 12.07.2021
# Last Modified Date: 12.07.2021
# Last Modified By  : Liam Lin
import os
import sys
from searcher import * 


#search_dir = "THE DIRECTORY WHERE THE FILES OF INTEREST ARE LOCATED" 
search_dir = "./"            #Default: 
sys.path.append(search_dir)
file_dir = os.getcwd()       #return Absolute Path of the files

#print(file_dir)


file_list = directory_branch(file_dir)

#print(directory_branch(file_dir))

for files in file_list:
    #print(file_list[files])
    newnames = file_list[files].replace(" ","_")
    if newnames != file_list[files]:
        os.rename(file_list[files],newnames)
    
    print(file_list[files])

