# Step 8: Send an Event
Send an external event into Alexa from the Endpoint Device backend. This simulates an external event on the endpoint that will need to be updated with Alexa.


#### <span style="color:#aaa">8.1</span> Send a Proactive State Update

<span style="color:#ccc">8.1.1</span> In Postman, select the **POST** _/events_ resource from the left menu.

<span style="color:#ccc">8.1.2</span> Select the _Body_ tab and view the raw JSON. It should look like the following:
```
{
  "event": {
    "endpoint": {
    	"userId" : "0",
    	"id": "black_switch",
    	"state": "OFF",
    	"type": "SWITCH"
    }
  }
}
```
<span style="color:#ccc">8.1.3</span> Update the JSON by replacing the `"userId"` "0" value with the [user_id] stored in the `config.txt` file. When edited, it should something like the following:
```
{
  "event": {
    "endpoint": {
    	"userId" : "amzn1.account.XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    	"id": "black_switch",
    	"state": "OFF",
    	"type": "SWITCH"
    }
  }
}
```

<span style="color:#ccc">8.1.1</span> Click **Save** in the top right and then and then click the **Send** button. 

<span style="color:#ccc">8.1.2</span> Return to the [AWS IoT Things console](https://console.aws.amazon.com/iotv2/home?region=us-east-1#/thinghub) and note the _state_ value of the _black_switch_. The state should reflect the _"state"_ value passed in the body. For instance, if set to _"OFF"_, the _black_switch_ attribute _state_ will be set to _OFF_.

<br>

____
Go to [Step 9: Clean Up](009-setup-cleanup.md).