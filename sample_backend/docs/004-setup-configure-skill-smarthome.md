# Step 4: Configure the Alexa Smart Home Skill
Configure the Alexa Smart Home Skill that will process the Smart Home commands.

#### <span style="color:#aaa">4.1</span> Configure the Smart Home Service Endpoint

<span style="color:#ccc">4.1.1</span> Locate and copy the [SkillLambdaArn] from the `config.txt` file. It will have the following format: 

```
arn:aws:lambda:us-east-1:############:function:SampleSkillAdapter
```

<span style="color:#ccc">4.1.2</span> In the _Sample Smart Home Skill_ **Smart Home** tab and in the _Smart Home service endpoint_ section, paste the [SkillLambdaArn] value in the **Default endpoint** input box. 

<span style="color:#ccc">4.1.3</span> Click the **Save** button to save the configuration.

#### <span style="color:#aaa">4.2</span> Configure Account Linking

<span style="color:#ccc">4.2.1</span> Select the _Account Linking_ tab of the _Sample Smart Home Skill_. 

<span style="color:#ccc">4.2.2</span> In the _Authorization URI_ input box, enter `https://www.amazon.com/ap/oa`. 

<span style="color:#ccc">4.2.3</span> In the _Access Token URI_ input box, enter ``https://api.amazon.com/auth/o2/token``. 

<span style="color:#ccc">4.2.4</span> Set the Client Id value to the [Login with Amazon Client ID] from the `config.txt` file. It will have the following format:

```
amzn1.application-oa2-client.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

<span style="color:#ccc">4.2.5</span> Set the **Client Secret** field to the [Login with Amazon Client Secret] value from the `config.txt` file. It will look like the following example:
```
7ebd0170626aaa2c3df0e263bd3aa15553efe565d53d90bd88b1977387b1159c
```

<span style="color:#ccc">4.2.6</span> For the _Scope_, click the **Add scope** and then add the following scope into the text box `profile:user_id`

> For more details on what customer profile information is used, visit https://developer.amazon.com/docs/login-with-amazon/customer-profile.html

<span style="color:#ccc">4.2.7</span> Click the **Save** button to save the configuration.

#### <span style="color:#aaa">4.3</span> Configure Permissions

<span style="color:#ccc">4.3.1</span> Select the _Permissions_ tab of the _Sample Smart Home Skill_. 

<span style="color:#ccc">4.3.2</span> Enable the **Send Alexa Events** toggle.

> TIP: This value needs to be checked and enables the operation of asynchronous messages and proactive state updates.

<span style="color:#ccc">4.3.3</span> Once sending Alexa events is enabled, click the _Show_ link in the **Alexa Skill Messaging** section to expose the Client Secret and then copy the **Client ID** and **Client Secret** to the [Alexa Skill Messaging Client Id] and [Alexa Skill Messaging Client Secret] sections `config.txt` file. The values to save will be inserted into the following sections:

```
[Alexa Skill Messaging Client Id]
amzn1.application-oa2-client.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

[Alexa Skill Messaging Client Secret]
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### <span style="color:#aaa">4.4</span> Set the Allowed Return URLs
Using your account-specific values from the skill configuration section, collect the Redirect URLs and set them in the _Security Profile Web Settings_ **Allowed Return URLs**.

<span style="color:#ccc">4.4.1</span> Return to the _Account Linking_ tab and locate the Returned Urls section towards the bottom of the page. That section should have values that look like the following format:

```
https://pitangui.amazon.com/api/skill/link/XXXXXXXXXXXXXX
https://layla.amazon.com/api/skill/link/XXXXXXXXXXXXXX
https://alexa.amazon.co.jp/api/skill/link/XXXXXXXXXXXXXX
```
> These values will be copied into the previously Security Profile, so leave this tab open to coy values.

<span style="color:#ccc">4.4.2</span> Open [https://developer.amazon.com/iba-sp/overview.html](https://developer.amazon.com/iba-sp/overview.html) in another browser tab and make sure _APPS & SERVICES_ is selected in the top menu and _Security Profiles_ is selected in the sub menu.

<span style="color:#ccc">4.4.3</span> On the _Security Profile Management_ page, click the **Sample Alexa Smart Home** profile.

<span style="color:#ccc">4.4.4</span> In the details for the _Sample Alexa Smart Home - Security Profile_ click the **Web Settings** top tab menu.

<span style="color:#ccc">4.4.5</span> On the Security Profile Management page for the _Sample Alexa Smart Home_ profile, click the **Edit** button.

<span style="color:#ccc">4.4.6</span> In the _Allowed Return URLs_ section click the **Add Another** link until there are 3 text input fields.

<span style="color:#ccc">4.4.7</span> Copy each of the 3 URLs from the _Account Linking_ configuration page into each of the text fields.

<span style="color:#ccc">4.4.8</span> When all fields are entered, click **Save**.

<span style="color:#ccc">4.4.9</span> Once saved, the _Allowed Return URLs_ section should look something like the following:

![Allowed Return URLs Example](img/2.1.14-lwa-web-settings.png "Allowed Return URLs Example")

<span style="color:#ccc">4.4.10</span> Close the _Security Profile Management_ tab and return to the Alexa skill configuration.


<br>

____
Go to [Step 5: Link the Alexa Smart Home Skill](005-setup-link-skill-smarthome.md).
