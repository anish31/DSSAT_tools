# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 12:20:45 2021

@author: anishholla
"""
#--------------------#
# LIBRARIES IMPORTED #
#--------------------#

import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

#------------------------#
# USER-DEFINED FUNCTIONS #
#------------------------#

#------#
# MAIN #
#------#

if __name__== "__main__":
    
    #--------#
    # INPUTS #
    #--------#
    
    # Location of DSSAT folder on your machine
    # I belive C:/ drive is default for windows OS
    tierDir = 'C:/DSSAT47'
    
    # Path to DSSAT executable
    pathDSSAT = '%s/DSCSM047.exe'%(tierDir)
    
    # DSSAT model (crop-specific)
    model = 'MZCER045' # CERES -maize
    
    # A: Run all treatments  (FileX)
    # B: Batch file name
    # E: Sensitivty analysis (FileX TN) .. TN is treatment number
    # N: Seasonal analysis   (bathfilename)
    # Q: Sequence analysis   (batchfilename)
    runmode   = 'A' 

    # Path to store your results
    resultsDir = '%s/Results'%(tierDir)
    # The overall experiment title
    EXPNAME = 'Exp_Weather_Dawson_Seasonal'
    
    # Path to .wth csv file [used to extract wth file names]
    path2wth = pd.read_csv('E:/DSSAT/Counties 45 Result/Dawson Legend.csv')
    
    # This control file will be used as the base for modifying additional experiments
    # In this script, we are just changing the weather id under the field section
    controlFile  = 'UNPH8622.SNX'
    # Path to control file
    skeletetonFile = '%s/Seasonal/%s'%(tierDir,controlFile)
    
#%%############################################################################

    # #-------------------------#
    # # Get all soils from .SOL #
    # #-------------------------#
    
    # # Iterate the .SOL file and extract all IDs
    # soilIDs = []
    # inSoil  = open(path2sol,'r')
    # for line in inSoil.readlines()[1:]: # Skip first line
    #     if line[0] == '*':
    #         soilIDs.append(line[1:11])
    # inSoil.close()
    
    # print('%d soils to perform experiments'%(len(soilIDs)))

#%%---------------------------------------------------------------------------#
    
    #---------------------------------#
    # Prepare and run the experiments #
    #---------------------------------#
    
    # List to store which weather file fails in DSSAT simulation
    errorWth = []

    # Iterate wth files in legend csv file
    # wthName = path2wth["dssat_station_name"]

    for index,row in path2wth.iterrows():
        
        wth = row['dssat_station_name']
        cli = row['climate_model']
        print ('Weather file %s associated with %s is being processed'%(wth,cli))
        
          # Create new output directories for the weather files
        oDir = '%s/%s/exp_%s_%s'%(resultsDir,EXPNAME,wth,cli)
        if not os.path.exists(oDir):
              print('Creating output directory')
              os.makedirs(oDir)
              
        # Use the skeleton file to write a new exp file to output folder using
        # a different wth class weather file
        eFile  = controlFile       
        oFile  = open('%s/%s'%(oDir,eFile),'w')            
        countI = -1000

        # Not super elegant but gets the job done
        with open(skeletetonFile, 'r+') as f:
            
            lines = f.readlines()
            
            # Iterate each line in control file
            for i in range(0, len(lines)):
                
                line = lines[i]
                
                # Parse field section of control file
                if line[:7] == '*FIELDS':
                    countI   = i+2
                    fieldRow = lines[countI]
                    outField = fieldRow.replace(fieldRow[12:16],wth)     
                
                # Write new field
                if i != countI:
                    oFile.write(line)
                else:
                    oFile.write(outField) 
        
        # Close new control file
        oFile.close()
        
        #-------#
        # DSSAT #
        #-------#
        
        try:
              print('Running DSSAT for %s, %s'%(wth,eFile))
              
              # Change directory to the location of experiment file             
              os.chdir('%s'%(oDir))
              
              # Format the full command as a string             
              command = "%s %s %s %s"%(pathDSSAT,model,runmode,eFile)
              
              # Pass the command to the system (Runs DSSAT for input options)
              subprocess.check_call(command, shell=True)
              
        except:
            errorWth.append(wth)


#%%---------------------------------------------------------------------------#
    #--------------------#
    # Output information #
    #--------------------#
    
    print('************')
    print('%d wth failed simulation'%(len(errorWth)))            
    [print('%s failed'%(we)) for we in errorWth]
    
#%%---------------------------------------------------------------------------#
    #--------------------#
    # Post processing #
    #--------------------#
    # Sets the folder to result folder
    resultFolder = '%s/%s'%(resultsDir,EXPNAME)
    
    #Creates a empty list and stores the folder names from result to it
    #Creates an empty list to store summary stats and merge it finally
    directNames = []
    statData = []
    listsdir =[]
    for base, dirs, files in os.walk(resultFolder):
        for directories in dirs:
            print('Direct:',directories)
            directNames.append(directories)
        
        # print(directNames)
    
    # Reading output file from each folder, running analysis of those files
    for i in directNames:
        inresultFile = '%s/%s/%s.OSU'%(resultFolder,i,controlFile[:8])
        # print(inresultFile)
        # print (i)
        inDSSAT = pd.read_fwf('%s'%(inresultFile),skiprows = 3)
        # Groups the inputfile by TNAM (IRFEQ and PAW), computes and save 
        # summary statistics
        anyls = inDSSAT.groupby(['TNAM.....................'])[['HWAH']].describe()
        statData.append(anyls)
        # finalStats = pd.concat(statData)
        anyls.to_excel('%s/%s/Result_%s.xlsx'%(resultFolder,i,i[-19:]))
        boxPlot = inDSSAT.boxplot(by = 'TNAM.....................', column=['HWAH'])
        plt.savefig('%s/%s/BoxPlot_%s.png'%(resultFolder,i,i[-19:]))
        plt.clf()
        
        # Create a column of year and plot against yield
        inDSSAT['Year'] = inDSSAT['SDAT'].astype(str).str[:4]
        inDSSAT = inDSSAT.set_index('Year')
        inDSSAT.groupby(['TNAM.....................'])['HWAH'].plot()
        plt.savefig("%s/%s/YieldPlot_%s.png"%(resultFolder,i,i[-19:]))
    
    finalStats = pd.concat(statData)
    finalStats.to_excel('%s/Summary_stats_all.xlsx'%(resultFolder))

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    