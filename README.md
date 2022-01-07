[comment]: # "Auto-generated SOAR connector documentation"
# IronNet

Publisher: IronNet  
Connector Version: 1\.0\.2  
Product Vendor: IronNet  
Product Name: IronDefense  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.6\.19142  

This app provides generic actions for interacting with IronDefense


This app integrates with IronNet's IronDefense platform to facilitate investigation, hunt, and alert
triage


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a IronDefense asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base\_url** |  required  | string | The base URL for the IronAPI
**verify\_server\_cert** |  optional  | boolean | Validate the IronAPI certificate
**username** |  required  | string | The username to use for authentication
**password** |  required  | password | The password to use for authentication
**enable\_alert\_notifications** |  optional  | boolean | Ingest IronDefense Alert Notifications into Phantom
**alert\_notification\_actions** |  optional  | string | Alert Notification Actions to include for ingest \(if ingest is enabled\)\.  Enter in CSV format\.
**alert\_categories** |  optional  | string | Alert Categories to exclude from ingest \(if ingest is enabled\)\.  Enter in CSV format\.
**alert\_subcategories** |  optional  | string | Alert SubCategories to exclude from ingest \(if ingest is enabled\)\. Enter in CSV format\.
**alert\_severity\_lower** |  optional  | numeric | Minimum Severity of Alerts to ingest \(if ingest is enabled\)
**alert\_severity\_upper** |  optional  | numeric | Maximum Severity of Alerts to ingest \(if ingest is enabled\)
**alert\_limit** |  optional  | numeric | Limit of Alert Notifications to ingest at a time \(if ingest is enabled\)
**enable\_dome\_notifications** |  optional  | boolean | Ingest IronDefense Dome Notifications into Phantom
**dome\_categories** |  optional  | string | Dome Categories to exclude from ingest \(if ingest is enabled\)\.  Enter in CSV format\.
**dome\_limit** |  optional  | numeric | Limit of Dome Notifications to ingest at a time \(if ingest is enabled\)
**enable\_event\_notifications** |  optional  | boolean | Ingest IronDefense Event Notifications into Phantom
**event\_notification\_actions** |  optional  | string | Event Notification Actions to include for ingest \(if ingest is enabled\)\.  Enter in CSV format\.
**event\_categories** |  optional  | string | Event Categories to exclude from ingest \(if ingest is enabled\)\.  Enter in CSV format\.
**event\_subcategories** |  optional  | string | Event SubCategories to exclude from ingest \(if ingest is enabled\)\. Enter in CSV format\.
**event\_severity\_lower** |  optional  | numeric | Minimum Severity of Events to ingest \(if ingest is enabled\)
**event\_severity\_upper** |  optional  | numeric | Maximum Severity of Events to ingest \(if ingest is enabled\)
**event\_limit** |  optional  | numeric | Limit of Event Notifications to ingest at a time \(if ingest is enabled\)
**store\_event\_notifs\_in\_alert\_containers** |  optional  | boolean | Store Event Notification in Alert Containers\. If selected, Event Notifications will be stored as artifacts in the container of their corresponding Alert \(Note that if this option is selected, any Event Notifications prior to the event being associated with the alert will not be ingested\)\. If left unselected, Event Notifications will be stored as artifacts in their own container\.

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[rate alert](#action-rate-alert) - Provides a rating for an Alert within IronDefense  
[set alert status](#action-set-alert-status) - Sets the status of an Alert within IronDefense  
[comment on alert](#action-comment-on-alert) - Adds a comment to an Alert within IronDefense  
[report bad activity](#action-report-bad-activity) - Reports observed bad activity to IronDefense  
[get community info](#action-get-community-info) - Gets community information related to an IronDefense alert  
[get events](#action-get-events) - Retrieves IronDefense Events for a given Alert ID  
[on poll](#action-on-poll) - Ingests Configured Notifications from IronDefense into Phantom  
[get alerts](#action-get-alerts) - Retrieves Alerts within IronDefense  
[get event](#action-get-event) - Retrieves IronDefense Event for a given Event ID  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'rate alert'
Provides a rating for an Alert within IronDefense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | The ID of the IronDefense alert | string |  `irondefense alert id` 
**analyst\_severity** |  required  | The severity of the alert | string | 
**analyst\_expectation** |  required  | The analyst expectation for the alert | string | 
**comment** |  required  | Text of comment | string | 
**share\_comment\_with\_irondome** |  optional  | Shares the provided comment with IronDome | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.alert\_id | string |  `irondefense alert id` 
action\_result\.parameter\.analyst\_expectation | string | 
action\_result\.parameter\.analyst\_severity | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.share\_comment\_with\_irondome | boolean | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'set alert status'
Sets the status of an Alert within IronDefense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | The ID of the IronDefense alert | string |  `irondefense alert id` 
**alert\_status** |  required  | The status of the alert | string | 
**comment** |  required  | Text of comment | string | 
**share\_comment\_with\_irondome** |  optional  | Shares the provided comment with IronDome | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.alert\_id | string |  `irondefense alert id` 
action\_result\.parameter\.alert\_status | string | 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.share\_comment\_with\_irondome | boolean | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'comment on alert'
Adds a comment to an Alert within IronDefense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | The ID of the IronDefense alert | string |  `irondefense alert id` 
**comment** |  required  | Text of comment | string | 
**share\_comment\_with\_irondome** |  optional  | Shares the provided comment with IronDome | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.alert\_id | string |  `irondefense alert id` 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.share\_comment\_with\_irondome | boolean | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'report bad activity'
Reports observed bad activity to IronDefense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Identifying name of the observed bad activity | string | 
**description** |  optional  | Description of the observed bad activity | string | 
**domain** |  optional  | Domain associated with the observed bad activity | string |  `domain` 
**ip** |  optional  | IP associated with the observed bad activity | string |  `ip` 
**activity\_start\_time** |  required  | Start time of observed bad activity \- in RFC3339 format \(https\://tools\.ietf\.org/html/rfc3339\) | string | 
**activity\_end\_time** |  optional  | End time of observed bad activity \- in RFC3339 format \(https\://tools\.ietf\.org/html/rfc3339\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.activity\_end\_time | string | 
action\_result\.parameter\.activity\_start\_time | string | 
action\_result\.parameter\.description | string | 
action\_result\.parameter\.domain | string |  `domain` 
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.parameter\.name | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get community info'
Gets community information related to an IronDefense alert

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | The ID of the IronDefense alert | string |  `irondefense alert id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.alert\_id | string |  `irondefense alert id` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.cognitive\_system\_score | numeric | 
action\_result\.data\.\*\.community\_comments\.\*\.comment | string | 
action\_result\.data\.\*\.community\_comments\.\*\.self | boolean | 
action\_result\.data\.\*\.community\_comments\.\*\.created | string | 
action\_result\.data\.\*\.community\_comments\.\*\.dome\_tags | string | 
action\_result\.data\.\*\.community\_comments\.\*\.enterprise | boolean | 
action\_result\.data\.\*\.correlations\.\*\.correlations\.\*\.enterprise\_correlations | numeric | 
action\_result\.data\.\*\.correlations\.\*\.correlations\.\*\.ip | string |  `ip` 
action\_result\.data\.\*\.correlations\.\*\.correlations\.\*\.domain | string |  `domain` 
action\_result\.data\.\*\.correlations\.\*\.correlations\.\*\.community\_correlations | numeric | 
action\_result\.data\.\*\.correlations\.\*\.dome\_tag | string | 
action\_result\.data\.\*\.dome\_notifications\.\*\.category | string | 
action\_result\.data\.\*\.dome\_notifications\.\*\.alert\_ids | string | 
action\_result\.data\.\*\.dome\_notifications\.\*\.id | numeric | 
action\_result\.data\.\*\.dome\_notifications\.\*\.dome\_tags | string | 
action\_result\.data\.\*\.dome\_notifications\.\*\.created | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.malicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.benign\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.resource\_owner | boolean | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.activity\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.comments\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.whitelisted\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.suspicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.first\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip\.last\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.malicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.benign\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.resource\_owner | boolean | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.activity\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.comments\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.whitelisted\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.suspicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.first\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain\.last\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.malicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.benign\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.resource\_owner | boolean | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.activity\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.comments\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.whitelisted\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.suspicious\_count | numeric | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.first\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior\.last\_seen | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.domain | string |  `domain` 
action\_result\.data\.\*\.correlation\_participation\.\*\.ip | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.behavior | string | 
action\_result\.data\.\*\.correlation\_participation\.\*\.dome\_tag | string |   

## action: 'get events'
Retrieves IronDefense Events for a given Alert ID

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | The ID of the alert associated with the events to retrieve | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
action\_result\.parameter\.alert\_id | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.events\.\*\.sub\_category | string | 
action\_result\.data\.\*\.events\.\*\.dst\_entity\_attribute\_type | string | 
action\_result\.data\.\*\.events\.\*\.src\_entity\_attribute | string | 
action\_result\.data\.\*\.events\.\*\.alert\_id | string | 
action\_result\.data\.\*\.events\.\*\.total\_bytes | string | 
action\_result\.data\.\*\.events\.\*\.id | string | 
action\_result\.data\.\*\.events\.\*\.src\_entity\_attribute\_type | string | 
action\_result\.data\.\*\.events\.\*\.category | string | 
action\_result\.data\.\*\.events\.\*\.is\_blacklisted | boolean | 
action\_result\.data\.\*\.events\.\*\.confidence | numeric | 
action\_result\.data\.\*\.events\.\*\.raw\_data\_formats | string | 
action\_result\.data\.\*\.events\.\*\.severity | numeric | 
action\_result\.data\.\*\.events\.\*\.bytes\_in | string | 
action\_result\.data\.\*\.events\.\*\.is\_whitelisted | boolean | 
action\_result\.data\.\*\.events\.\*\.src\_ip | string |  `ip` 
action\_result\.data\.\*\.events\.\*\.end\_time | string | 
action\_result\.data\.\*\.events\.\*\.updated | string | 
action\_result\.data\.\*\.events\.\*\.bytes\_out | string | 
action\_result\.data\.\*\.events\.\*\.start\_time | string | 
action\_result\.data\.\*\.events\.\*\.dst\_entity\_attribute | string | 
action\_result\.data\.\*\.events\.\*\.created | string | 
action\_result\.data\.\*\.events\.\*\.url | string |  `url` 
action\_result\.data\.\*\.events\.\*\.secondary\_app\_protocol | string | 
action\_result\.data\.\*\.events\.\*\.primary\_app\_protocol | string |  `protocol` 
action\_result\.data\.\*\.events\.\*\.dst\_port | string |  `port` 
action\_result\.data\.\*\.events\.\*\.iron\_dome\_shared\_time | string | 
action\_result\.data\.\*\.events\.\*\.dst\_ip | string |  `ip` 
action\_result\.data\.\*\.events\.\*\.vue\_url | string | 
action\_result\.data\.\*\.events\.\*\.src\_network\_id | string | 
action\_result\.data\.\*\.events\.\*\.dst\_network\_id | string | 
action\_result\.data\.\*\.constraint\.total | string | 
action\_result\.data\.\*\.constraint\.limit | numeric | 
action\_result\.data\.\*\.constraint\.offset | numeric |   

## action: 'on poll'
Ingests Configured Notifications from IronDefense into Phantom

Type: **ingest**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get alerts'
Retrieves Alerts within IronDefense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  optional  | The IDs of the IronDefense alerts to filter\. Enter in CSV format\. | string | 
**category** |  optional  | The categories of the IronDefense alerts to filter\. Enter in CSV format\. | string | 
**sub\_category** |  optional  | The subcategories of the IronDefense alerts to filter\. Enter in CSV format\. | string | 
**status** |  optional  | The statuses of the IronDefense alerts to filter\. Enter in CSV format\. | string | 
**min\_severity** |  optional  | The minimum severity of IronDefense alerts to filter\. | numeric | 
**max\_severity** |  optional  | The maximum severity of IronDefense alerts to filter\. | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.alert\_id | string | 
action\_result\.parameter\.category | string | 
action\_result\.parameter\.sub\_category | string | 
action\_result\.parameter\.status | string | 
action\_result\.parameter\.min\_severity | numeric | 
action\_result\.parameter\.max\_severity | numeric | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.alerts\.\*\.status | string | 
action\_result\.data\.\*\.alerts\.\*\.category | string | 
action\_result\.data\.\*\.alerts\.\*\.updated | string | 
action\_result\.data\.\*\.alerts\.\*\.raw\_data\_formats | string | 
action\_result\.data\.\*\.alerts\.\*\.severity | numeric | 
action\_result\.data\.\*\.alerts\.\*\.created | string | 
action\_result\.data\.\*\.alerts\.\*\.first\_event\_created | string | 
action\_result\.data\.\*\.alerts\.\*\.aggregation\_criteria | string | 
action\_result\.data\.\*\.alerts\.\*\.event\_count | numeric | 
action\_result\.data\.\*\.alerts\.\*\.analyst\_severity | string | 
action\_result\.data\.\*\.alerts\.\*\.vue\_url | string |  `url` 
action\_result\.data\.\*\.alerts\.\*\.last\_event\_created | string | 
action\_result\.data\.\*\.alerts\.\*\.id | string | 
action\_result\.data\.\*\.alerts\.\*\.analyst\_expectation | string | 
action\_result\.data\.\*\.alerts\.\*\.sub\_category | string | 
action\_result\.data\.\*\.constraint\.total | string | 
action\_result\.data\.\*\.constraint\.limit | numeric | 
action\_result\.data\.\*\.constraint\.offset | numeric | 
action\_result\.parameter\.sort\_field | string | 
action\_result\.parameter\.sort\_order | string |   

## action: 'get event'
Retrieves IronDefense Event for a given Event ID

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**event\_id** |  required  | The ID of the event to retrieve | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
action\_result\.parameter\.event\_id | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.event\.sub\_category | string | 
action\_result\.data\.\*\.event\.dst\_entity\_attribute\_type | string | 
action\_result\.data\.\*\.event\.src\_entity\_attribute | string | 
action\_result\.data\.\*\.event\.alert\_id | string | 
action\_result\.data\.\*\.event\.total\_bytes | string | 
action\_result\.data\.\*\.event\.id | string | 
action\_result\.data\.\*\.event\.src\_entity\_attribute\_type | string | 
action\_result\.data\.\*\.event\.category | string | 
action\_result\.data\.\*\.event\.is\_blacklisted | boolean | 
action\_result\.data\.\*\.event\.confidence | numeric | 
action\_result\.data\.\*\.event\.raw\_data\_formats | string | 
action\_result\.data\.\*\.event\.severity | numeric | 
action\_result\.data\.\*\.event\.bytes\_in | string | 
action\_result\.data\.\*\.event\.is\_whitelisted | boolean | 
action\_result\.data\.\*\.event\.src\_ip | string |  `ip` 
action\_result\.data\.\*\.event\.end\_time | string | 
action\_result\.data\.\*\.event\.app\_domains | string | 
action\_result\.data\.\*\.event\.updated | string | 
action\_result\.data\.\*\.event\.bytes\_out | string | 
action\_result\.data\.\*\.event\.start\_time | string | 
action\_result\.data\.\*\.event\.dst\_entity\_attribute | string | 
action\_result\.data\.\*\.event\.created | string | 
action\_result\.data\.\*\.event\.url | string |  `url` 
action\_result\.data\.\*\.event\.secondary\_app\_protocol | string | 
action\_result\.data\.\*\.event\.primary\_app\_protocol | string |  `protocol` 
action\_result\.data\.\*\.event\.dst\_port | string |  `port` 
action\_result\.data\.\*\.event\.iron\_dome\_shared\_time | string | 
action\_result\.data\.\*\.event\.dst\_ip | string |  `ip` 
action\_result\.data\.\*\.event\.vue\_url | string |  `url` 
action\_result\.data\.\*\.event\.src\_network\_id | string | 
action\_result\.data\.\*\.event\.dst\_network\_id | string | 
action\_result\.data\.\*\.context\.\*\.name | string | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.long\_value | string | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.name | string |  `url` 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.trans\_protocol\_value | string | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.bool\_value | boolean | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.string\_value | string | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.ip\_value | string |  `ip` 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.app\_protocol\_value | string | 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.uuid\_value | string |  `md5` 
action\_result\.data\.\*\.context\.\*\.columns\.\*\.values\.\*\.data\.\*\.double\_value | numeric | 