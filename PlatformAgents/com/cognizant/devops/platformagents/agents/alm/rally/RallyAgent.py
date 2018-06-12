#-------------------------------------------------------------------------------
# Copyright 2017 Cognizant Technology Solutions
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
#-------------------------------------------------------------------------------
'''
Created on Jul 6, 2017

@author: 463188
'''
# Optimization and Pagination might be required. This is the first cut working agent with incremental fetch

from dateutil import parser
from com.cognizant.devops.platformagents.core.BaseAgent import BaseAgent
import json
import datetime
import time

class RallyAgent(BaseAgent):
    def process(self):
        userid = self.config.get("userid", '')
        passwd = self.config.get("passwd", '')
        baseUrl = self.config.get("baseUrl", '')

        storyMetadata = self.config.get("storyMetadata", '')
        relationMetadata = self.config.get("relationMetadata", '')
        
        startFrom = self.config.get("startFrom", '')
        startFrom = parser.parse(startFrom)
        startFrom = startFrom.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        responseTemplate = self.getResponseTemplate()
        data = []
        injectIterationData = {}
        injectArtifactData = {}
        
        ts = time.time()
        
        trackingDetails = self.tracking.get('LastUpdatedDate', None)
        if trackingDetails is None:
            lastUpdated = startFrom
        else:
            lastUpdated = trackingDetails
        
        
        artifactListUrl = baseUrl+"artifact?query=(LastUpdateDate > "+lastUpdated+")"
        print artifactListUrl
        
        artifactListRes = self.getResponse(artifactListUrl, 'GET', userid, passwd, None)
        artifactListResCount=artifactListRes['QueryResult']['TotalResultCount']
        
        for artifact in range(0,artifactListResCount):
           artifactListData = artifactListRes['QueryResult']['Results'][artifact]
           artifactUrl= artifactListData['_ref']
           artifactType= artifactListData['_type']
           artifactRes = self.getResponse(artifactUrl, 'GET', userid, passwd, None)
           
           if artifactType == "Task":
               injectArtifactData = {}
               artifactTask = artifactRes['Task']
               injectArtifactData['Name']=artifactTask['Name']
               injectArtifactData['Type']=artifactType
               injectArtifactData['Description']=artifactTask['Description']
               injectArtifactData['Date']=artifactTask['CreationDate']
               injectArtifactData['ID']=artifactTask['FormattedID']
               injectArtifactData['LastUpdateDate']=artifactTask['LastUpdateDate']
               if artifactTask['Iteration'] != None:
                injectArtifactData['IterationName']=artifactTask['Iteration']['_refObjectName']
                injectArtifactData['IterationUrl']=artifactTask['Iteration']['_ref']
                iterationRef = injectArtifactData['IterationUrl'].split("/")
                iterationReflen= len(iterationRef)
                iterationID= iterationRef[iterationReflen-1]
                injectArtifactData['IterationID']=int(iterationID)
               else :
                injectArtifactData['IterationID'] = 0
               injectArtifactData['State']=artifactTask['State']
               injectArtifactData['Workspace']=artifactTask['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactTask['Project']['_refObjectName']
               projectUrl=artifactTask['Project']['_ref']
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               injectArtifactData['WorkProduct']=artifactTask['WorkProduct']['_refObjectName']
               if artifactTask['Release'] != None:
                injectArtifactData['ReleaseName']=artifactTask['Release']['_refObjectName']
                ReleaseUrl=artifactTask['Release']['_ref']
                ReleasetRes = self.getResponse(ReleaseUrl, 'GET', userid, passwd, None)
                for Release in ReleasetRes:
                  injectArtifactData['ReleasePlanEstimate']=ReleasetRes['Release']['PlanEstimate']
                  injectArtifactData['ReleasePlannedVelocity']=ReleasetRes['Release']['PlannedVelocity']
                  injectArtifactData['ReleaseDate']=ReleasetRes['Release']['ReleaseDate']
                  injectArtifactData['ReleaseStartDate']=ReleasetRes['Release']['ReleaseStartDate']             
               else :
                 injectArtifactData['Release'] = 0
               data.append(injectArtifactData)

           
           elif artifactType == "TestCase":
               injectArtifactData = {}
               artifactTestCase = artifactRes['TestCase']
               injectArtifactData['Name']=artifactTestCase['Name']
               injectArtifactData['Type']= artifactType
               injectArtifactData['Date']=artifactTestCase['CreationDate']
               injectArtifactData['ID']=artifactTestCase['FormattedID']
               injectArtifactData['Priority']=artifactTestCase['Priority']
               injectArtifactData['Risk']=artifactTestCase['Risk']
               injectArtifactData['TesCaseType']=artifactTestCase['Type']
               injectArtifactData['LastUpdateDate']=artifactTestCase['LastUpdateDate'] 
               injectArtifactData['ResultUrl']=artifactTestCase['Results']['_ref']
               injectArtifactData['Workspace']=artifactTestCase['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactTestCase['Project']['_refObjectName']
               projectUrl=artifactTestCase['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               injectArtifactData['IterationID']= 0
               injectArtifactData['WorkProduct']=artifactTestCase['WorkProduct']['_refObjectName']
               data.append(injectArtifactData)


           elif artifactType == "HierarchicalRequirement":
                
               injectArtifactData = {}
               artifactHierarchyReq = artifactRes['HierarchicalRequirement']
               injectArtifactData['Name']=artifactHierarchyReq['Name']
               injectArtifactData['Type']= "UserStory"
               injectArtifactData['Date']=artifactHierarchyReq['CreationDate']
               injectArtifactData['ID']=artifactHierarchyReq['FormattedID']
               injectArtifactData['FlowStateChangedDate']=artifactHierarchyReq['FlowStateChangedDate']
               injectArtifactData['ScheduleState']=artifactHierarchyReq['ScheduleState']
               injectArtifactData['TestcaseCount']=artifactHierarchyReq['TestCaseCount']
               
               
               if artifactHierarchyReq['Iteration'] != None:
                injectArtifactData['IterationName']=artifactHierarchyReq['Iteration']['_refObjectName']
                injectArtifactData['IterationUrl']=artifactHierarchyReq['Iteration']['_ref']
                iterationRef = injectArtifactData['IterationUrl'].split("/")
                iterationReflen= len(iterationRef)
                iterationID= iterationRef[iterationReflen-1]
                injectArtifactData['IterationID']=int(iterationID)
               else :
                 injectArtifactData['IterationID'] = 0
               
               injectArtifactData['PlanEstimate']=artifactHierarchyReq['PlanEstimate']
               
               if artifactHierarchyReq['Release'] != None:
                injectArtifactData['ReleaseName']=artifactHierarchyReq['Release']['_refObjectName']
                ReleaseUrl=artifactHierarchyReq['Release']['_ref']
                ReleasetRes = self.getResponse(ReleaseUrl, 'GET', userid, passwd, None)
                for Release in ReleasetRes:
                  injectArtifactData['ReleasePlanEstimate']=ReleasetRes['Release']['PlanEstimate']
                  injectArtifactData['ReleasePlannedVelocity']=ReleasetRes['Release']['PlannedVelocity']
                  injectArtifactData['ReleaseDate']=ReleasetRes['Release']['ReleaseDate']
                  injectArtifactData['ReleaseStartDate']=ReleasetRes['Release']['ReleaseStartDate']                 
                
               else :
                 injectArtifactData['Release'] = 0
                            
               
               
               injectArtifactData['TaskActualTotal']=artifactHierarchyReq['TaskActualTotal']
               injectArtifactData['TaskEstimateTotal']=artifactHierarchyReq['TaskEstimateTotal']
               injectArtifactData['TaskRemainingTotal']=artifactHierarchyReq['TaskRemainingTotal']
               injectArtifactData['TaskCount']=artifactHierarchyReq['Tasks']['Count']
               
               injectArtifactData['Workspace']=artifactHierarchyReq['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactHierarchyReq['Project']['_refObjectName']
               projectUrl=artifactHierarchyReq['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               
               data.append(injectArtifactData)
               
           elif artifactType == "Defect":

               injectArtifactData = {}
               artifactDefect = artifactRes['Defect']
               injectArtifactData['Name']=artifactDefect['Name']
               injectArtifactData['Type']= artifactType
               injectArtifactData['CreationDate']=artifactDefect['CreationDate']
               injectArtifactData['ID']=artifactDefect['FormattedID']
               injectArtifactData['FlowStateChangedDate']=artifactDefect['FlowStateChangedDate']
               injectArtifactData['ScheduleState']=artifactDefect['ScheduleState']
               injectArtifactData['TestcaseCount']=artifactDefect['TestCaseCount']
               injectArtifactData['ClosedDate']=artifactDefect['ClosedDate']
               injectArtifactData['Environment']=artifactDefect['Environment']
               injectArtifactData['DefectSuiteCount']=artifactDefect['DefectSuites']['Count']               
               
               if artifactDefect['Iteration'] != None:
                injectArtifactData['IterationName']=artifactDefect['Iteration']['_refObjectName']
                injectArtifactData['IterationUrl']=artifactDefect['Iteration']['_ref']
                iterationRef = injectArtifactData['IterationUrl'].split("/")
                iterationReflen= len(iterationRef)
                iterationID= iterationRef[iterationReflen-1]
                injectArtifactData['IterationID']=int(iterationID)
               else :
                 injectArtifactData['IterationID'] = 0
               injectArtifactData['PlanEstimate']=artifactDefect['PlanEstimate']
               injectArtifactData['Priority']=artifactDefect['Priority']
               injectArtifactData['State']=artifactDefect['State']
               injectArtifactData['SubmittedBy']=artifactDefect['SubmittedBy']['_refObjectName']
               injectArtifactData['TaskActualTotal']=artifactDefect['TaskActualTotal']
               injectArtifactData['TaskEstimateTotal']=artifactDefect['TaskEstimateTotal']
               injectArtifactData['TaskRemainingTotal']=artifactDefect['TaskRemainingTotal']
               injectArtifactData['TaskStatus']=artifactDefect['TaskStatus']
               injectArtifactData['TaskCount']=artifactDefect['Tasks']['Count']
               injectArtifactData['Workspace']=artifactDefect['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactDefect['Project']['_refObjectName']
               projectUrl=artifactDefect['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               
               data.append(injectArtifactData)
               
           elif artifactType == "DefectSuite":
               
               injectArtifactData = {}
               artifactDefectSuite = artifactRes['DefectSuite']
               injectArtifactData['Name']=artifactDefectSuite['Name']
               injectArtifactData['Type']= artifactType
               injectArtifactData['CreationDate']=artifactDefectSuite['CreationDate']
               injectArtifactData['ID']=artifactDefectSuite['FormattedID']
               injectArtifactData['FlowStateChangedDate']=artifactDefectSuite['FlowStateChangedDate']
               injectArtifactData['ScheduleState']=artifactDefectSuite['ScheduleState']
               
                             
               
               if artifactDefectSuite['Iteration'] != None:
                injectArtifactData['IterationName']=artifactDefectSuite['Iteration']['_refObjectName']
                injectArtifactData['IterationUrl']=artifactDefectSuite['Iteration']['_ref']
                iterationRef = injectArtifactData['IterationUrl'].split("/")
                iterationReflen= len(iterationRef)
                iterationID= iterationRef[iterationReflen-1]
                injectArtifactData['IterationID']=int(iterationID)
               else :
                 injectArtifactData['IterationID'] = 0
               injectArtifactData['PlanEstimate']=artifactDefectSuite['PlanEstimate']
               
               
               injectArtifactData['PlanEstimate']=artifactDefectSuite['PlanEstimate']                                               
               injectArtifactData['TaskActualTotal']=artifactDefectSuite['TaskActualTotal']
               injectArtifactData['TaskEstimateTotal']=artifactDefectSuite['TaskEstimateTotal']
               injectArtifactData['TaskRemainingTotal']=artifactDefectSuite['TaskRemainingTotal']
               injectArtifactData['TaskStatus']=artifactDefectSuite['TaskStatus']
               injectArtifactData['TaskCount']=artifactDefectSuite['Tasks']['Count']
               injectArtifactData['Workspace']=artifactDefectSuite['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactDefectSuite['Project']['_refObjectName']
               projectUrl=artifactDefectSuite['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               
               data.append(injectArtifactData)


           elif artifactType == "TestSet":
               
               injectArtifactData = {}
               artifactTestSet = artifactRes['TestSet']
               injectArtifactData['Name']=artifactTestSet['Name']
               injectArtifactData['Type']= artifactType
              
               injectArtifactData['CreationDate']=artifactTestSet['CreationDate']
               injectArtifactData['ID']=artifactTestSet['FormattedID']
               injectArtifactData['FlowStateChangedDate']=artifactTestSet['FlowStateChangedDate']
               injectArtifactData['ScheduleState']=artifactTestSet['ScheduleState']
               injectArtifactData['TestcaseCount']=artifactTestSet['TestCases']['Count']
               if artifactTestSet['Iteration'] != None:
                injectArtifactData['IterationName']=artifactTestSet['Iteration']['_refObjectName']
                injectArtifactData['IterationUrl']=artifactTestSet['Iteration']['_ref']
                iterationRef = injectArtifactData['IterationUrl'].split("/")
                iterationReflen= len(iterationRef)
                iterationID= iterationRef[iterationReflen-1]
                injectArtifactData['IterationID']=int(iterationID)
               else :
                 injectArtifactData['IterationID'] = 0
               
               
               if artifactTestSet['Release'] != None:
                injectArtifactData['ReleaseName']=artifactTestSet['Release']['_refObjectName']
                ReleaseUrl=artifactTestSet['Release']['_ref']
                ReleasetRes = self.getResponse(ReleaseUrl, 'GET', userid, passwd, None)
                for Release in ReleasetRes:
                  injectArtifactData['ReleasePlanEstimate']=ReleasetRes['Release']['PlanEstimate']
                  injectArtifactData['ReleasePlannedVelocity']=ReleasetRes['Release']['PlannedVelocity']
                  injectArtifactData['ReleaseDate']=ReleasetRes['Release']['ReleaseDate']
                  injectArtifactData['ReleaseStartDate']=ReleasetRes['Release']['ReleaseStartDate']                 
                
               else :
                 injectArtifactData['Release'] = 0
               injectArtifactData['PlanEstimate']=artifactTestSet['PlanEstimate']                                               
               injectArtifactData['TaskActualTotal']=artifactTestSet['TaskActualTotal']
               injectArtifactData['TaskEstimateTotal']=artifactTestSet['TaskEstimateTotal']
               injectArtifactData['TaskRemainingTotal']=artifactTestSet['TaskRemainingTotal']
               injectArtifactData['TaskStatus']=artifactTestSet['TaskStatus']
               injectArtifactData['TaskCount']=artifactTestSet['Tasks']['Count']
               injectArtifactData['Workspace']=artifactTestSet['Workspace']['_refObjectName']
               injectArtifactData['ProjectName']=artifactTestSet['Project']['_refObjectName']
               projectUrl=artifactTestSet['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectArtifactData['ProjectID']= int(projectRef[projectReflen-1])
               
               data.append(injectArtifactData)
           else:
               pass

        
        data_iteration = []   
        projectBaseUrl=baseUrl+"projects/"
        projectListRes=self.getResponse(projectBaseUrl, 'GET', userid, passwd, None)
        
        
        for Project in range(0,projectListRes['QueryResult']['TotalResultCount']):
         projectUrl=projectListRes['QueryResult']['Results'][Project]['_ref']
         projectRes=self.getResponse(projectUrl, 'GET', userid, passwd, None)
         iterationCount=projectRes['Project']['Iterations']['Count']
         iterationUrl=projectRes['Project']['Iterations']['_ref']
         iterationRes=self.getResponse(iterationUrl, 'GET', userid, passwd, None)
         
 
         
         for iteration in range(0,iterationCount):
               
               iterationRevisionUrl=iterationRes['QueryResult']['Results'][iteration]['RevisionHistory']['_ref']
               iterationRevisionRes= self.getResponse(iterationRevisionUrl, 'GET', userid, passwd, None)
               iterationRevisionCount=iterationRes['QueryResult']['TotalResultCount']
               iterationWPCount= iterationRes['QueryResult']['Results'][iteration]['WorkProducts']['Count']
               iterationWPUrl= iterationRes['QueryResult']['Results'][iteration]['WorkProducts']['_ref']
               
               injectIterationData = {}
               injectIterationData['IterationWorkspace']=projectRes['Project']['Workspace']['_refObjectName']
               injectIterationData['IterationProjectName']=projectRes['Project']['_refObjectName']
               projectUrl=projectRes['Project']['_ref']
               
               projectRef = projectUrl.split("/")
               projectReflen= len(projectRef)
               injectIterationData['ProjectID']= int(projectRef[projectReflen-1])
               injectIterationData['IterationName']=iterationRes['QueryResult']['Results'][iteration]['Name']
               injectIterationData['IterationUrl']=iterationRes['QueryResult']['Results'][iteration]['_ref']
               iterationRef = injectIterationData['IterationUrl'].split("/")
               iterationReflen= len(iterationRef)
               iterationID= iterationRef[iterationReflen-1]
               injectIterationData['IterationID']=int(iterationID)
               
               injectIterationData['IterationCreationDate']=iterationRes['QueryResult']['Results'][iteration]['CreationDate']
               injectIterationData['IterationEndDate']=iterationRes['QueryResult']['Results'][iteration]['EndDate']
               injectIterationData['IterationPlanEstimate']=iterationRes['QueryResult']['Results'][iteration]['PlanEstimate']
               injectIterationData['IterationPlannedVelocity']=iterationRes['QueryResult']['Results'][iteration]['PlannedVelocity']
               injectIterationData['IterationStartDate']=iterationRes['QueryResult']['Results'][iteration]['StartDate']
               injectIterationData['IterationState']=iterationRes['QueryResult']['Results'][iteration]['TaskActualTotal']
               injectIterationData['IterationTaskEstimateTotal']=iterationRes['QueryResult']['Results'][iteration]['TaskEstimateTotal']
               injectIterationData['IterationTaskRemainingTotal']=iterationRes['QueryResult']['Results'][iteration]['TaskRemainingTotal']
                  
               data_iteration.append(injectIterationData)           
        
        self.publishToolsData(data, storyMetadata)
        self.publishToolsData(data_iteration, relationMetadata)
        self.tracking['LastUpdatedDate'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.updateTrackingJson(self.tracking)
          
if __name__ == "__main__":
    RallyAgent()       
