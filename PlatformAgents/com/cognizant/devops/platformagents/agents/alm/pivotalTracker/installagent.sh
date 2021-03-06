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
# Turn on a case-insensitive matching (-s set nocasematch)
opt=$1
echo "$opt"
case $opt in
        [lL][Ii][nN][uU][Xx])
                echo "PivotalTracker Running on Linux..."
				sudo cp -xp InSightsPivotalTrackerAgent.sh  /etc/init.d/InSightsPivotalTrackerAgent
				sudo chmod +x /etc/init.d/InSightsPivotalTrackerAgent
				sudo chkconfig InSightsPivotalTrackerAgent on
				sudo service  InSightsPivotalTrackerAgent status
				sudo service  InSightsPivotalTrackerAgent stop
				sudo service  InSightsPivotalTrackerAgent status
				sudo service  InSightsPivotalTrackerAgent start
				sudo service  InSightsPivotalTrackerAgent status
				
				echo "Service installaton steps completed"
                ;;
        [uU][bB][uU][nN][tT][uU])
                echo "PivotalTracker Running on Ubuntu..."
				sudo cp -xp InSightsPivotalTrackerAgent.service /etc/systemd/system
				sudo systemctl enable InSightsPivotalTrackerAgent
				sudo systemctl start InSightsPivotalTrackerAgent
				echo "Service installaton steps completed"
                ;;
        centos)
                echo "PivotalTracker Running on centso..."
                ;;
        *)
        	    echo "Please provide correct OS input"
esac
