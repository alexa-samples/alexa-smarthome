# Step 6: Create the Endpoints
Create endpoints to be discovered during the Alexa Smart Home Skill Discovery.


#### <span style="color:#aaa">6.1</span> Set Up Postman 
Postman is a tool for managing and executing HTTP requests and is very useful for API development and usage.

##### <span style="color:#aaa">6.1.1</span> Install Postman 
<span style="color:#ccc">6.1.1</span> Go to [getpostman.com](getpostman.com) and download and install the correct Postman application for your platform.

<span style="color:#ccc">6.1.2</span> Download the Postman Sample Smart Home Collection from https://raw.githubusercontent.com/alexa/alexa-smarthome/master/sample_backend/lambda/sample_backend.postman_collection.json into the `Alexa-SmartHome-Sample` directory on your Desktop. 

##### <span style="color:#aaa">6.1.2</span> Import the _Alexa Smart Home (sample_backend)_ Postman collection

<span style="color:#ccc">6.1.2.1</span> Open Postman.

<span style="color:#ccc">6.1.2.2</span> In Postman, click **Import** from the main menu and browse to the `sample_backend.postman_collection.json` file or drag it onto the _Import_ dialog. 

##### <span style="color:#aaa">6.1.3</span> Create a Postman environment
To fill out the variable values of the configuration use a Postman environment to store configuration-specific values.

<span style="color:#ccc">6.1.3.1</span> In the top right of Postman, click the gear icon to open the _Environment options_ drop down menu and select **Manage Environments**.

![Postman - Manage Environments](img/6.1.3.1-postman-manage-environments.png "Postman - Manage Environments")

<span style="color:#ccc">6.1.3.2</span> In opened _MANAGE ENVIRONMENTS_ dialog, click the **Add** in the bottom right.

<span style="color:#ccc">6.1.3.3</span> For the _Environment Name_ enter `Alexa Smart Home (sample_backend)`.

<span style="color:#ccc">6.1.3.4</span> Add a **Key** value called  `aws_region` and set its **Value** to `us-east-1`.

<span style="color:#ccc">6.1.3.5</span> Add another **Key** value called  `endpoint_api_id` and set its **Value** to the [EndpointApiId] value from the `config.txt` file.

<span style="color:#ccc">6.1.3.6</span> Click the **Add** button again to save the environment settings.

<span style="color:#ccc">6.1.3.6</span> Close the _MANAGE ENVIRONMENTS_ dialog and in the top right of Postman select the newly created _Alexa Smart Home (sample_backend)_ environment from the  environment drop down menu.

#### <span style="color:#aaa">6.2</span> Create Endpoints 
Use Postman to generate endpoints.

<span style="color:#ccc">6.2.1</span> Browse to the AWS IoT console at https://console.aws.amazon.com/iotv2/home?region=us-east-1#/thinghub and note the existing _Things_, if any.

<span style="color:#ccc">6.2.2</span> In Postman, select the **POST** _/endpoints_ resource from the left menu and then click the **Send** button in the top right.

<span style="color:#ccc">6.2.3</span> Return to the [AWS IoT Things console](https://console.aws.amazon.com/iotv2/home?region=us-east-1#/thinghub) and refresh the page. A new `black_switch` Thing should be available.

<span style="color:#ccc">6.2.4</span> Click on the `black_switch` Thing instance to inspect its attributes. They should look like the following:

![black_switch Thing Inpection - Manage Environments](img/6.2.4-thing-inspection.png "black_switch Thing Inspection")

> Note that the user_id is set to 0. This is a default value useful for development. However, Discovery for the Smart Home Skill would not find this device since it is expecting a user_id in the form of a profile from Login with Amazon.

<span style="color:#ccc">6.2.5</span> Go to https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables:selected=SampleUsers and select the **Items** tab.

<span style="color:#ccc">6.2.6</span> In the list of _SampleUsers_ select the first entry UserId that looks like the following format: 
```
amzn1.account.XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
<span style="color:#ccc">6.2.7</span> Copy the UserId value and save it to the [user_id] section of the `config.txt` file.

<span style="color:#ccc">6.2.8</span> Return to the [AWS IoT Things console](https://console.aws.amazon.com/iotv2/home?region=us-east-1#/thinghub) and select the `black_switch` Thing to view its attributes.

<span style="color:#ccc">6.2.9</span> In the top right of the `black_switch` attributes click **Edit**.

<span style="color:#ccc">6.2.10</span> On the _Edit black_switch_ attributes page, set the value of the _user_id_ **Attribute key** to the [user_id] stored in the `config.txt` file. This associates the `black_switch` thing with that user profile.



<br>

____
Go to [Step 7: Test the Endpoints](007-setup-test-endpoints.md).
