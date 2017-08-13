import pandas as pd
import os
from glob import glob
from random import randint
import numpy as np
import re
from ast import literal_eval
import sys
import json

def createPRTs(**kwargs):
    for key in kwargs:
        if key == 'experimentname_input':
            experimentName = kwargs[key]
        elif key == 'path':
            loaded_path = kwargs[key]
        elif key == 'color_config_exists':
            color_config_exists = kwargs[key]
        elif key == 'colors_config':
            colors_config = kwargs[key]
        elif key == 'object_id':
            parent_object = kwargs[key]
        elif key == 'duration_input':
            trialDuration = [int(kwargs[key])]
        elif key == 'jitterswitch':
            if kwargs[key]:
                jitter = 'yes'
            else:
                jitter = 'no'
        elif key == 'jittername_input':
            jitterColumnName = kwargs[key]
        elif key == 'nullswitch':
            if kwargs[key]:
                includeNull = 'yes'
            else:
                includeNull = 'no'
        elif key == 'nullcondswitch':
            if kwargs[key]:
                nullCondition = 'yes'
            else:
                nullCondition = 'no'
        elif key == 'nullname_input':
            nullConditionName = kwargs[key]
        elif key == 'onsettime_input':
            baselineOnsetColumnName = kwargs[key]
        elif key == 'conditionname1_input':
            conditionColumnName = kwargs[key]
        elif key == 'conditionname2_input':
            trialColumnName = kwargs[key]
        elif key == 'onsetcolumn_input':
            onsetTimeNames = kwargs[key]
        elif key == 'parametricswitch':
            if kwargs[key]:
                parametricDesign = 'yes'
            else:
                parametricDesign = 'no'
        elif key == 'parametricname_input':
            stimuliColumnName = kwargs[key]
        elif key == 'parametricweights_input':
            stimuliweights = kwargs[key]
        elif key == 'errorswitch':
            if kwargs[key]:
                modelErrorSeparately = 'yes'
            else:
                modelErrorSeparately = 'no'
        elif key == 'seperrorswitch':
            if kwargs[key]:
                groupError = 'yes'
            else:
                groupError = 'no'
        elif key == 'error_input':
            errorColumnName = kwargs[key]
        elif key == 'gapswitch':
            if kwargs[key]:
                gaps = 'yes'
            else:
                gaps = 'no'
        elif key == 'gapcolnames_input':
            gapColumns = kwargs[key]
        elif key == 'gapname_input':
            gapName = kwargs[key]
        elif key == 'csv_files':
            CSVfiles = kwargs[key]
        else:
            pass
            
    if 'errorColumnName' not in locals():
        errorColumnName = []
        
    if 'nullConditionName' not in locals():
        nullConditionName = 'Null'

    # =============================================================================
    modelSeparately = 'no'
    modelSeparatelyGroupNames = []
    
    if 'stimuliWeights' in locals():
        stimuliWeights['none'] = ''
    else:
        stimuliWeights = {}
        stimuliWeights['none'] = ''
    if parametricDesign == 'yes':
        if jitter == 'yes':
            columns = [conditionColumnName,stimuliColumnName,trialColumnName,jitterColumnName] + errorColumnName
        else:
            columns = [conditionColumnName,stimuliColumnName,trialColumnName] + errorColumnName
    else:
        if jitter == 'yes':
            columns = [conditionColumnName,trialColumnName,jitterColumnName] + errorColumnName
        else:
            columns = [conditionColumnName,trialColumnName] + errorColumnName

    columns.extend(onsetTimeNames)

    if gaps == 'yes':
        addGap = 1
    else:
        addGap = 0
        
    PRTfilenames = ([s.replace('.csv', '.prt') for s in CSVfiles]) 

    dataframes = []
    dataframesGaps = []
    baselineTime = []
    totIter = len(CSVfiles)
    currentIter = 0.0
    parent_object.complete_label.text = 'Loading CSV Files'

    for file in CSVfiles:
        currentIter += 1
        df = pd.read_csv(file)
        baselineTime.append(df[baselineOnsetColumnName][0])
        if gaps=='yes':
            dfgaps = df.copy()
            for column in dfgaps.columns:
                if column not in gapColumns:
                    dfgaps = dfgaps.drop(column,axis=1)
                    dfgaps = dfgaps.reset_index(drop = True)
            dataframesGaps.append(dfgaps)
        for column in df.columns:
            if column not in columns:
                df = df.drop(column,axis=1)
                df = df.reset_index(drop = True)
        df = df.reset_index(drop = True)
        if jitter == 'no':
            df['jitter'] = pd.Series(0,index=df.index)
            jitterColumnName = 'jitter'
        
        dataframes.append(df)
        ratio = currentIter/totIter * 100
        parent_object.my_prbar.bar_value = ratio
        
        
    for index,dataframe in enumerate(dataframes):
        dataframes[index][conditionColumnName].fillna(dataframe[trialColumnName],inplace=True)
        if jitter == 'yes':
            dataframes[index][jitterColumnName].fillna(0,inplace=True)

    for dataindex,dataframe in enumerate(dataframes):
        if modelSeparately == 'no':
            dataframe['uniqueCombinedName'] = dataframe[trialColumnName].astype(str) + ' ' + dataframe[conditionColumnName].astype(str)
        if modelSeparately == 'yes':
            dataframe[stimuliColumnName].fillna('',inplace=True)
            dataframe['uniqueCombinedName'] = dataframe[trialColumnName].astype(str) + ' ' + dataframe[conditionColumnName].astype(str) + ' ' + dataframe[stimuliColumnName].astype(str)
            dataframe.ix[dataframe[conditionColumnName].isin(modelSeparatelyGroupNames),'uniqueCombinedName'] = dataframe.ix[dataframe[conditionColumnName].isin(modelSeparatelyGroupNames),trialColumnName].astype(str) + ' ' + dataframe.ix[dataframe[conditionColumnName].isin(modelSeparatelyGroupNames),conditionColumnName].astype(str)
    
    uniqueNames = {tName for tName in dataframes[0]['uniqueCombinedName']}
    uniqueNamesNoNull = {name for name in uniqueNames if nullConditionName.lower() not in name.lower()}
       
    if color_config_exists:
        RGBCollection = colors_config
        configExist = True
    else:
        configExist = False

    totIter = len(dataframes)
    currentIter = 0.0
    parent_object.complete_label.text = 'Creating PRT Files'
    ratio = currentIter/totIter * 100
    parent_object.my_prbar.bar_value = ratio
    
    
    uniqueConditionsMaster = []
    for dataindex,dataframe in enumerate(dataframes):
        uniqueNames = {tName for tName in dataframe['uniqueCombinedName']}
        blockDataframes = []
        for key in uniqueNames:
            appBlock = False
            tempdf = dataframe.loc[dataframe['uniqueCombinedName'] == key]
            tempdf = tempdf.dropna(axis=1,how='all')
            
            nanOnsetTempMerge = pd.DataFrame()
            for column in tempdf.columns:
                if 'OnsetTime' in re.split('\.|\[',column):
                    tDat = tempdf[column]
                    nanOnsetTempMerge[column] = tDat
            nanOnsetTempMerge['OnsetTime'] = nanOnsetTempMerge.sum(axis=1) 
            nanOnsetTempMerge = nanOnsetTempMerge.dropna(axis=1)
            for column in tempdf.columns:
                if 'OnsetTime' in re.split('\.|\[',column):
                    tempdf = tempdf.drop(column,1)
                    try:
                        nanOnsetTempMerge = nanOnsetTempMerge.drop(column,1)
                    except:
                        pass

            tempdf['OnsetTime'] = nanOnsetTempMerge
            tempdf = tempdf.dropna(axis=0,thresh=2)
            tempdf = tempdf.reset_index()

            for column in tempdf.columns:
                if tempdf[column].isnull().any() and column != stimuliColumnName:
                    tempdf = tempdf.drop(column,axis=1)
            tempdf = tempdf.reset_index(drop = True)
            for column in tempdf.columns:
                if 'OnsetTime' in re.split('\.|\[',column):
                    appBlock = True
            if appBlock and not tempdf.empty:
                if parametricDesign.lower() == 'yes':
                    if stimuliColumnName in tempdf.columns.values:
                        blockDataframes.append(tempdf)
                    else:
                        tempdf[stimuliColumnName] = 'none'
                        blockDataframes.append(tempdf)
                else:
                    blockDataframes.append(tempdf)
        f = open(PRTfilenames[dataindex],'w')
        
        if modelErrorSeparately == 'yes':
            newNames = []
            tempBlockDataframes = []
            for block in blockDataframes:
                for errCol in errorColumnName:
                    if errCol in block.columns:
                        block.loc[block[errCol] == 1,'uniqueCombinedName'] = block['uniqueCombinedName'] + ' - ' + 'Correct'
                        block.loc[block[errCol] == 0,'uniqueCombinedName'] = block['uniqueCombinedName'] + ' - ' + 'Incorrect'
                try:
                    titlist = block['uniqueCombinedName'].tolist()
                    titlist = [i.split(' - ')[1] for i in titlist]
                    if ('Correct' not in titlist) and ('Incorrect' in titlist):
                        tempBlock = block.copy()
                        tempRow = tempBlock.ix[0:0]
                        tempRow.reset_index()
                        tempRow.set_value(0,'uniqueCombinedName',str(tempRow[trialColumnName][0]) + ' ' + str(tempRow[conditionColumnName][0]) + ' - Correct (NoneCorr)')
                        tempRow.set_value(0,'OnsetTime',baselineTime[0])
                        tempBlockDataframes.append(tempRow)
                        
                except IndexError:
                    pass
                newNames = newNames + block['uniqueCombinedName'].unique().tolist()
            
            for x in tempBlockDataframes:
                blockDataframes.append(x)
            block2Dataframes = []
            for block in blockDataframes:
                block1 = block[block.uniqueCombinedName == block.uniqueCombinedName[0]]
                block1 = block1.reset_index()
                block2 = block[block.uniqueCombinedName != block.uniqueCombinedName[0]]
                block2 = block2.reset_index()
                if not block1.empty:
                    block2Dataframes.append(block1)
                if not block2.empty:
                    block2Dataframes.append(block2)
            if groupError.lower() == 'yes':
                newBlock = []
                errBlock = []
                start = 0
                for blockIndex, block in enumerate(block2Dataframes):
                    if '- Incorrect' in block.uniqueCombinedName[0]:
                        if start == 0:
                            errBlock = block
                            start = 1
                        else:
                            errBlock = pd.concat([errBlock,block])
                    else:
                        newBlock.append(block)
                try:
                    errBlock = errBlock.reset_index(drop=True)
                    errBlock['uniqueCombinedName'] = 'Errors'
                    onsetColsErr = [x for x in errBlock.columns if '.OnsetTime' in x]
                    errBlock['errorConcat.OnsetTime'] = np.nan
                    while len(onsetColsErr) > 0:
                        tempCol = onsetColsErr.pop()
                        errBlock['errorConcat.OnsetTime'] = errBlock['errorConcat.OnsetTime'].combine_first(errBlock[tempCol])
                    errBlock = errBlock.dropna(axis=1)
                    newBlock.append(errBlock)
                    block2Dataframes = newBlock
                    passthrough = 0
                except NameError:
                    passthrough = 1
                except AttributeError:
                    pass
            if passthrough == 0:
                blockDataframes = block2Dataframes
        
        if parametricDesign == 'yes':
            if modelSeparately == 'no':
                f.write('\n')
                f.write('FileVersion:' + ' '*7 + '3\n\n')
            else:
                f.write('\n')
                f.write('FileVersion:' + ' '*7 + '2\n\n')
        else:
            f.write('\n')
            f.write('FileVersion:' + ' '*7 + '2\n\n')
        
        blockNames = [x['uniqueCombinedName'][0] for x in blockDataframes]
        uniqueConditionsP = blockNames
        if (modelErrorSeparately.lower() == 'yes') and (groupError.lower() == 'yes') and ('Errors' not in uniqueConditionsP):
            condForPrint = len(blockDataframes) + 1
        else:
            condForPrint = len(blockDataframes)
        condForPrintNoNull = condForPrint
        f.write('ResolutionOfTime:   msec\n\n')
        f.write('Experiment:         ' + experimentName + '\n\n')
        f.write('BackgroundColor:    0 0 0\n')
        f.write('TextColor:          255 255 255\n')
        f.write('TimeCourseColor:    255 255 255\n')
        f.write('TimeCourseThick:    3\n')
        f.write('ReferenceFuncColor: 0 0 80\n')
        f.write('ReferenceFuncThick: 3\n\n')
        if includeNull.lower() == 'yes' and nullCondition.lower() == 'yes':
            f.write('NrOfConditions:     ' + str(condForPrint+addGap) + '\n')
        else:
            f.write('NrOfConditions:     ' + str(condForPrintNoNull+addGap) + '\n')
        
        if gaps == 'yes':
            f.write('\n')
            f.write(gapName + '\n')
            gapPairs = [[0,dataframesGaps[dataindex][gapColumns[1]].dropna(axis=0).unique()[0]-dataframesGaps[dataindex][gapColumns[0]].dropna(axis=0).unique()[0]]]
            for gapIndex,gapCol in enumerate(gapColumns):
                if gapIndex>1 and gapIndex<len(gapColumns)-1:
                    pair = [dataframesGaps[dataindex][gapCol].dropna(axis=0).unique()[0]-dataframesGaps[dataindex][gapColumns[0]].dropna(axis=0).unique()[0],dataframesGaps[dataindex][gapColumns[gapIndex+1]].dropna(axis=0).unique()[0]-dataframesGaps[dataindex][gapColumns[0]].dropna(axis=0).unique()[0]]
                    gapPairs.append(pair)
                    
            f.write(str(len(gapPairs)))
            f.write('\n\n')
            for pair in gapPairs:
                if parametricDesign == 'yes':
                    f.write(str(int(pair[0])) + ' ' + str(int(pair[1])) + ' 3\n')
                else:
                    f.write(str(int(pair[0])) + ' ' + str(int(pair[1])) + '\n')

        if dataindex==0 and not configExist:
            colorset = set()
            colorset.add((255,255,255))
            colorset.add((0,0,0))
            colorset.add((0,0,80))
        
            RGBCollection = {}
            
        for block in blockDataframes:
            uniqueConditions = {cond for cond in block['uniqueCombinedName']}

            uniqueConditionsMaster = uniqueConditionsMaster + list(uniqueConditions)
           
            for cond in uniqueConditions:
                if cond != nullConditionName:
                    tempdf = block.loc[block[conditionColumnName] == cond]
                    tempdf = block.loc[block['uniqueCombinedName'] == cond]
                    
                    if  dataindex==0 and not configExist:
                        R = randint(0,255)
                        G = randint(0,255)
                        B = randint(0,255)
                        RGB = (R,G,B)
                        
                        while RGB in colorset:
                            R = randint(0,255)
                            G = randint(0,255)
                            B = randint(0,255)
                            RGB = (R,G,B)
                        colorset.add(RGB)
                        if 'NoneCorr' not in block['uniqueCombinedName'][0]:
                            RGBCollection[block['uniqueCombinedName'][0]] = RGB
                        else:
                            RGBCollection[block['uniqueCombinedName'][0][0:-11]] = RGB
                    else:
                        try:
                            if 'NoneCorr' not in block['uniqueCombinedName'][0]:
                                RGB = RGBCollection[block['uniqueCombinedName'][0]]
                                R = RGB[0]
                                G = RGB[1]
                                B = RGB[2]
                            else:
                                RGB = RGBCollection[block['uniqueCombinedName'][0][0:-11]]
                                R = RGB[0]
                                G = RGB[1]
                                B = RGB[2]
                        except KeyError:
                            RGB = (randint(0,255),randint(0,255),randint(0,255))
                            while RGB in colorset:
                                R = randint(0,255)
                                G = randint(0,255)
                                B = randint(0,255)
                                RGB = (R,G,B)
                            colorset.add(RGB)
                            if 'NoneCorr' not in block['uniqueCombinedName'][0]:
                                RGBCollection[block['uniqueCombinedName'][0]] = RGB
                            else:
                                RGBCollection[block['uniqueCombinedName'][0][0:-11]] = RGB
                    if 'NoneCorr' not in block['uniqueCombinedName'][0]:
                        f.write('\n' + block['uniqueCombinedName'][0])
                        f.write('\n')
                        f.write(str(len(tempdf.index)))
                        f.write('\n\n')
                    else:
                        f.write('\n' + block['uniqueCombinedName'][0][0:-11])
                        f.write('\n')
                        f.write('0')
                        f.write('\n\n')
                    
                    onsetColumn = [x for x in block.columns if 'OnsetTime' in re.split('\.|\[',x)][0]
                    
                    for index, row in tempdf.iterrows():
                        if 'NoneCorr' not in row['uniqueCombinedName']:
                            outputOnset = int(row[onsetColumn] - baselineTime[dataindex])
                            jitterVal = int(row[jitterColumnName])
                            outputOffset = int(outputOnset + trialDuration[0])

                            if parametricDesign == 'yes' and modelSeparately == 'no':
                                f.write(str(outputOnset) + ' ' + str(outputOffset+jitterVal) + ' ' + stimuliWeights[str(row[stimuliColumnName])] + '\n')
                            else:
                                f.write(str(outputOnset) + ' ' + str(outputOffset+jitterVal) + '\n')
                        else:
                            f.write('\n')
                    f.write('\n' + 'Color: ' + str(R) + ' ' + str(G) + ' ' + str(B) + '\n')
                else:
                    if includeNull == 'yes':
                        f.write('\n' + block['uniqueCombinedName'][0])
                        f.write('\n')
                        f.write(str(len(tempdf.index)))
                        f.write('\n\n')
                        onsetColumn = [x for x in block.columns if 'OnsetTime' in x.split('.')][0]
                        tempdf = block.loc[block[conditionColumnName] == cond]
                        for index, row in tempdf.iterrows():
                            outputOnset = int(row[onsetColumn] - baselineTime[dataindex])
                            outputOffset = int(outputOnset + trialDuration[0])
                            if parametricDesign == 'yes' and modelSeparately == 'no':
                                f.write(str(outputOnset) + ' ' + str(outputOffset+jitterVal) + ' ' + stimuliWeights[row[stimuliColumnName]] + '\n')
                            else:
                                f.write(str(outputOnset) + ' ' + str(outputOffset+jitterVal) + '\n')
                        f.write('\n' + 'Color: ' + str(R) + ' ' + str(G) + ' ' + str(B) + '\n')
        
        if (modelErrorSeparately.lower() == 'yes') and (groupError.lower() == 'yes') and 'Errors' not in uniqueConditionsP:
            if not configExist:
                RGB = (randint(0,255),randint(0,255),randint(0,255))
                while RGB in colorset:
                    R = randint(0,255)
                    G = randint(0,255)
                    B = randint(0,255)
                    RGB = (R,G,B)
                colorset.add(RGB)
                RGBCollection['Errors'] = RGB
                f.write('\nErrors\n')
                f.write('0')
                f.write('\n\n')
                f.write('Color: ' + str(R) + ' ' + str(G) + ' ' + str(B))
                f.write('\n')
            else:
                RGB = RGBCollection['Errors']
                R = RGB[0]
                G = RGB[1]
                B = RGB[2]
                f.write('\nErrors\n')
                f.write('0')
                f.write('\n\n')
                f.write('Color: ' + str(R) + ' ' + str(G) + ' ' + str(B))
                f.write('\n')
                
        currentIter += 1
        ratio = currentIter/totIter * 100
        parent_object.my_prbar.bar_value = ratio
                
        f.close()
    
    if not configExist:
        f = open(loaded_path,'r')
        dataJSON = json.load(f)
        dataJSON['colors_config'] = RGBCollection
        f.close()
        f = open(loaded_path,'w')
        f.write(json.dumps(dataJSON))
        f.close()
        
    parent_object.complete_label.text = 'Done!'
    parent_object.sub_box.ids.closebutton.disabled = False