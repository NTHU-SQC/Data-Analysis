#pragma rtGlobals=3		// Use modern global access method and strict wave access.

//
//*******************************************************************
//

Function scaleSet(Wname, x_start, x_end, y_start, y_end)
	wave Wname 
	variable x_start, x_end, y_start, y_end
	setscale/I x, x_start,x_end, Wname
	setscale/I y, y_start, y_end, Wname
End

//
//*******************************************************************
//

Function WaveRename(Wname, StrName)
	wave Wname
	string StrName
	rename Wname, $StrName
End 

//
//*******************************************************************
//
Function promptMessage(foldername)
	string foldername
	print "In this script, we will convert the data from LabberFormat to Igor supported\n"
	print "You select this folder: ",foldername
End

Function convertOKmessage(folderName, repositoryDataPath)
	string folderName, repositoryDataPath
	print "\n----------------------MESSAGES---------------------------\n"
	print "Data convert successfully."
	print "Now, you can view the measurement data from this folder called LabberToIgorRepository"
	print "->File Name ", folderName
	print "->Folder Path", repositoryDataPath
	print "\n----------------------FINISHED---------------------------\n"
End
Function LabberConvert_DataMode(Source, StrName)
	//
	// Before you use "LabberDataConvet" function, you need to know the following rules.
	// Q: How to activate HDF5 service?
	//	A: You can get "Help Topics" of "HDF5XOP" from "Igor Help Browser", then read "HDF5 Help.ipf" to get more detail.
	// Q: How to open "HDF5Browser"?
	// 	A: click the following step: Data -> Load Waves -> New HDF5 Browser
	// Q: How to get the experimental data via "HDF5Browser" panel?
	// 	A: Open HDF5 File, choose the Files of type as "All Files", find the folder of any HDF5 file exists , then click the specific file you want
	// Q: How to load the experimental data to Data Browser?
	// 	A: select Data (Group) -> Data (Datasets), then click "Load Dataset" button
	//        
	//        
	//
	//
	// Source: get the experimental Data from HDF5Browser()
	// StrName: designate the Wname of the destination
	// Usage: LabberDataConvert(Data, "Mag2Data")
	//
	wave Source
	string StrName
	variable m = DimSize(Source, 0), n = DimSize(Source, 2)
	variable col = n
	variable unit = 1e+9 // Hz
	variable x_start = Source[0][0][0] * unit, x_end = Source[m-1][0][0] * unit
	variable y_start = Source[0][1][0], y_end = Source[0][1][n-1]
	variable index
	make/o/n=(m, n) Destination
	
	for (index = 0 ; index < col ; index = index + 1)
		Destination[][index] = Source[p][2][index]
	endfor
	
	ScaleSet(Destination, x_start, x_end, y_start, y_end)
	WaveRename(Destination, StrName)
	
End

Function LabberConvert_TraceMode(yaxisSource, xaxisSource, Sparameter)
	// Strategy for TraceMode
	// Traces
	// X axis: Frequency (Hz)
	// Y axis: Power(dBm) or Current(mA)                     
	// Z axis:S21 parameters, VNA - S21, (real, image)
	// VNA - S21 -> VNA -S21 t0dt 
	// path test:
	// root:'Weak_loop2.5X_GlobalFlux_3.8-5.':Traces:'VNA - S21'
	// command prompt test:
	// LabberConvert_TraceMode(Data, $"VNA - S21_t0dt", $"VNA - S21")
	wave yaxisSource, xaxisSource, Sparameter
	variable yaxisStart = yaxisSource[0][0]
	variable yaxisDelta = yaxisSource[1][0]
	variable xaxisStart = xaxisSource[0][0]
	variable xaxisDelta = xaxisSource[0][1]
	variable m = dimsize(Sparameter, 0), n = dimsize(Sparameter, 2) //m:3001, n:62
	variable a, b, val
	variable indexM, indexN 

	make/o/n=(m, n) Destination       // magnitude term transform (Labber-> Igor)
	make/o/n=(m, n) Destinate_Phase // phase term transform (Labber-> Igor)
	// row:0-3001
	// col:0-1
	// layer:0-61
	
	for (indexM = 0 ; indexM < M ; indexM = indexM + 1)
		for (indexN = 0 ; indexN < N; indexN = indexN + 1)
			Destination[indexM][indexN] = sqrt(Sparameter[indexM][0][indexN] ^2 + Sparameter[indexM][1][indexN] ^2)
			Destinate_Phase[indexM][indexN] = atan2(Sparameter[indexM][0][indexN], Sparameter[indexM][1][indexN])
		endfor
	endfor
	
	
	scaleSet(Destination, xaxisStart, xaxisStart + m * xaxisDelta, yaxisStart, yaxisSource[n][0])
	scaleSet(Destinate_Phase, xaxisStart, xaxisStart + m * xaxisDelta, yaxisStart, yaxisSource[n][0])
	
End

Function LabberConvert_LogMode()
	// Data Stored Structure
	// -Data
	// - Log_2/Data
	// - Log_3/Data
	// - Log_4/Data
	// - Log_5/Data
	// - Log_6/Data
	// etc
	//
	// Strategy for LogMode
	// go to each above folder, and do LabberConvert_DataMode to convert it as a igor format
	// rename each segmented file as the format, like "temp_1"
	// move all files in Log  to Data folder
	// combine all segmented waves into a complete image(wave)
	// move a complete wave to root:LabberToIgorRepository
	
	//variable 
	
End
Function SearchFolder(keyword)
	string keyword
	string currentFolder = getdatafolder(0)
	string destFolder = getbrowserselection(0)
	variable found =  0
	if (stringmatch(currentFolder, destFolder) != 1)
		setdatafolder $destFolder
		if (datafolderexists(keyword))
			setdatafolder $keyword
			found = 1
//		else 
//			printf "No, the folder: %s can't be found in this path\n %s.\n", keyword, destFolder
		endif
//	else
//		print "Please click your experimental folder in Data Browser, and then try again."
	endif
	setdatafolder root:
	return found
End

function main()
	string folderName = replacestring("'",replacestring("root:", getbrowserselection(0), ""),"")
	string repository = "LabberToIgorRepository"
	string repositoryDataPath
	sprintf repositoryDataPath, "root:%s:%s", repository, folderName
	string ModePath = getbrowserselection(0)
	setdatafolder root:
	
	if (datafolderexists(repository) == 0)
		newdatafolder LabberToIgorRepository
	endif
	
	if (searchFolder("Data") == searchFolder("Traces"))
//		string repositoryDataPath
//		sprintf repositoryDataPath, "root:%s:%s", repository, folderName
		
		setdatafolder ModePath
		wave yaxisInfo = $":Data:Data"
		
		setdatafolder $(":Traces")
		wave xaxisInfo = $"VNA - S21_t0dt"
		wave xaxis_Sparameter = $"VNA - S21"
		
		print "Traces Mode\n"
		promptMessage(folderName)
		
		if (waveexists($folderName) == 0)
			LabberConvert_TraceMode(yaxisInfo, xaxisInfo, xaxis_Sparameter)
			rename Destination, $folderName
			if (waveexists(root:$(repository):$(folderName)) == 0)
				movewave :$(folderName), root:$(repository):$(folderName)
			else
				//killwaves/z repositoryDataPath
				killwaves/z root:$(repository):$(folderName)
				setdatafolder destPath
				movewave $(folderName), root:$(repository):$(folderName)
			endif
			convertOKmessage(folderName, repositoryDataPath)
		endif
		
	elseif (searchFolder("Data") == searchFolder("Log_2"))
		print "Log Mode(Hello, World!)\n"
		
	elseif (searchFolder("Data"))
//		string repositoryDataPath
//		sprintf repositoryDataPath, "root:%s:%s", repository, folderName
		string destFolder = "Data"
		string destPath 
		sprintf destPath, "%s:%s", ModePath, destFolder 
		setdatafolder destPath
		wave Data

		print "Data Mode:\n" 
		promptMessage(folderName)
		//print repositoryDataPath
		if (waveexists($folderName) == 0)
			LabberConvert_DataMode(Data,"result")
			rename result, $folderName
			if (waveexists(root:$(repository):$(folderName)) == 0)
				movewave :$(folderName), root:$(repository):$(folderName)
			else
				//killwaves/z repositoryDataPath
				killwaves/z root:$(repository):$(folderName)
				setdatafolder destPath
				movewave $(folderName), root:$(repository):$(folderName)
			endif
			convertOKmessage(folderName, repositoryDataPath)
		endif
	endif
//	else
//		print "When you see this bug, it implies that you need to save your current environment as an Experiment format"
//    print "Report this bug to me."
	setdatafolder root:
end

function show()
	wave photo = $getbrowserselection(0)
	variable colorInverse = 1
	
	display/k=2
	appendimage photo
	//modifyimage photo ctab={*, *, RedWhiteBlue,0}
	setaxis/A left
end

