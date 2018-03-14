# Step 7: Test the Endpoints
Now that the environment is in place and a test device has been created, test out the endpoints.


#### <span style="color:#aaa">Step 7.1</span> Discover devices via a voice command

<span style="color:#ccc">7.1.1</span> Browse to https://echosim.io and login with your Amazon account.

<span style="color:#ccc">7.1.2</span> Activate echosim.io by clicking and holding the speaker icon and give the command <span style="color:#199">"Discover Devices"</span>. Alexa should respond with <span style="color:blue">"Starting Discovery..."</span> with a description of the discovery process.

<span style="color:#ccc">7.1.3</span> Return to https://alexa.amazon.com/ and select **Smart Home** from the left menu and then select **Devices** in the main window.

<span style="color:#ccc">7.1.4</span> From the list of devices, not the inclusion of a **Sample Black Switch** with a description of _A Sample Black Switch_ in the list of _Devices_.

> Note If you are using an Echo device to issue a "Discover Devices" command, once discovery is complete, Alexa should respond <span style="color:blue">"I found one new switch called sample black switch."</span> or possibly with additional devices discovered.  Note the addition of a _Sample Black Switch_ device to your list of devices.

> Optionally, for device discovery, you can browse to https://alexa.amazon.com/spa/index.html#appliances and click the **Discover** button at the bottom of the page.

#### <span style="color:#aaa">Step 7.2</span> Send at Turn On voice command

<span style="color:#ccc">7.2.1</span> Activate echosim and give the command <span style="color:#199">"Turn on Black Switch"</span>. Alexa should respond with <span style="color:blue">"OK"</span>.

<span style="color:#ccc">7.2.2</span> Return to the [AWS IoT Things console](https://console.aws.amazon.com/iotv2/home?region=us-east-1#/thinghub) and locate the Sample Black Switch Thing instance to inspect its attributes.

<span style="color:#ccc">7.2.3</span> The Sample Black Switch thing attributes should reflect the state of the "ON" or "OFF" power voice command when the Thing is refreshed.

<br>

____
Go to [Step 8: Send an Event](008-setup-send-an-event.md).
