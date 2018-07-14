# Step 5: Link the Alexa Smart Home Skill
Finalize the Lambda configuration and link the Alexa Smart Home Skill to your account.

#### <span style="color:#aaa">5.1</span> Update the Skill Lambda Environment variables
With a completed Alexa Smart Home Skill configuration, the Alexa Skill Client ID and Client Secret will need to be passed to the backend. To accomplish this, you can set the environment variables of the Lambda that is handling the Endpoint interactions.

<span style="color:#ccc">5.1.2</span> Browse to https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/SampleEndpointAdapter?tab=configuration.

<span style="color:#ccc">5.1.3</span> Expand the **Environment variables** section add a Key called `client_id`.

<span style="color:#ccc">5.1.4</span> For the _client\_id_ value enter the value stored in [Alexa Skill Messaging Client Id] from the `config.txt` file.

<span style="color:#ccc">5.1.5</span> In the **Environment variables** section add another Key called `client_secret`.

<span style="color:#ccc">5.1.6</span> For the _client\_secret_ value enter the value stored in [Alexa Messaging Skill Client Secret] from the `config.txt` file.

<span style="color:#ccc">5.1.7</span> When both the _client\_id_ and _client\_secret_ environment variables are added, click **Save** at the top of the page.

#### <span style="color:#aaa">5.2</span> Link the Alexa Smart Home Skill

<span style="color:#ccc">5.2.1</span> Go to https://alexa.amazon.com/ and select **Skills** from the left menu.

> Tip: Replace the skill value at the end of https://alexa.amazon.com/spa/index.html#skills/beta/ALEXA_SKILL_ID to go directly to a skill.
> For example, https://alexa.amazon.com/spa/index.html#skills/beta/amzn1.ask.skill.203e1508-e33b-4b63-8e0e-70b97e45408d


<span style="color:#ccc">5.2.2</span> Click **Your Skills** from the top right of the section.

<span style="color:#ccc">5.2.3</span> Locate your Sample Smart Home Skill in the list of skills in the _DEV SKILLS_ section and click on it.

![Smart Home Skill Example](img/5.2.3-smart-home-skill.png "Smart Home Skill Example")

<span style="color:#ccc">5.2.4</span> On the _Sample Smart Home Skill_ page, click **Enable** in the top right and authenticate with your Amazon account.

<span style="color:#ccc">5.2.5</span> On authentication, verify you are presented with the _Sample Alexa Smart Home_ authentication dialog and authenticate using your Amazon account. The transitional page will look something like the following in a browser:

![Linking Authentication](img/5.2.5-linking-dialog.png "Linking Authentication")

<span style="color:#ccc">5.2.6</span> Click **Allow** to link your Account with the _Sample Alexa Smart Home_ skill.

<span style="color:#ccc">5.2.7</span> On success, you should be presented with a window that instructing you to close the page and return to the _Sample Smart Home Skill_.

<span style="color:#ccc">5.2.8</span> When redirected back to the Skill page, you will be prompted 'Discover Devices'. Click **Cancel**  for now as no new devices from the Sample Smart Home Skill will be returned without additional configuration.

<br>

____
Go to [Step 6: Create the Endpoints](006-setup-create-endpoints.md).
