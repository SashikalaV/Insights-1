/*******************************************************************************
 *  * Copyright 2017 Cognizant Technology Solutions
 *  * 
 *  * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 *  * use this file except in compliance with the License.  You may obtain a copy
 *  * of the License at
 *  * 
 *  *   http://www.apache.org/licenses/LICENSE-2.0
 *  * 
 *  * Unless required by applicable law or agreed to in writing, software
 *  * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *  * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 *  * License for the specific language governing permissions and limitations under
 *  * the License.
 *******************************************************************************/
package com.cognizant.devops.platformservice.customsettings.service;

import org.apache.log4j.Logger;
import org.springframework.stereotype.Service;

import com.cognizant.devops.platformdal.settingsconfig.SettingsConfiguration;
import com.cognizant.devops.platformdal.settingsconfig.SettingsConfigurationDAL;


@Service("settingsConfigurationService")
public class SettingsConfigurationServiceImpl implements SettingsConfigurationService{
	
	private static Logger LOG = Logger.getLogger(SettingsConfigurationServiceImpl.class);

	@Override
	public Boolean saveSettingsConfiguration(String settingsJson,String settingsType,String activeFlag,String lastModifiedByUser) {		
		SettingsConfiguration settingsConfiguration = populateSettingsConfiguration(settingsJson,settingsType, activeFlag, lastModifiedByUser);
		SettingsConfigurationDAL settingsConfigurationDAL = new SettingsConfigurationDAL();		
		return settingsConfigurationDAL.saveSettingsConfiguration(settingsConfiguration);		
	}	

	@Override
	public SettingsConfiguration loadSettingsConfiguration(String settingsType) {
		SettingsConfigurationDAL settingsConfigurationDAL = new SettingsConfigurationDAL();		
		return settingsConfigurationDAL.loadSettingsConfiguration(settingsType);	
	}
	

	private SettingsConfiguration populateSettingsConfiguration(String settingsJson, String settingsType,
			String activeFlag, String lastModifiedByUser) {
		SettingsConfiguration settingsConfiguration = new SettingsConfiguration();
		settingsConfiguration.setSettingsJson(settingsJson);
		settingsConfiguration.setSettingsType(settingsType);
		settingsConfiguration.setActiveFlag(activeFlag);
		settingsConfiguration.setLastModifiedByUser(lastModifiedByUser);
		return settingsConfiguration;
	}	

}