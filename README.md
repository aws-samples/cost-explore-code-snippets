# ce-code

This solution exports your AWS cost Explorer spend by linked account and emails it to you with your forecasted amount for the month.


## Requirements
You must be able to access the payer account
Have cost Explorer enabled
Enable SES, following the section below



## Pre-Rec
Get started with [SES](https://docs.aws.amazon.com/ses/latest/dg/setting-up.html) by verifying an email address and sending domain so that you can start sending email through SES and request production access for your account by using the SES account set up wizard.

Using the SES account set up wizard to set up your account
Sign in to the AWS Management Console and open the Amazon SES console at https://console.aws.amazon.com/ses/.

Select Get started from the SES console home page and the wizard will walk you through the steps of setting up your SES account.

The SES account set up wizard will only be presented if you have not yet created any identities (email address or domain) in SES.


## Deploy Cloudformation
ce-forecast-cf.yaml  - Deploy in the payer account cloudformation to have access to different linked accounts data

The emails that are parameters must be the ones set up in the prerequisite

## Clean up
To clean up this appointment, delete the cloud formation template in your account

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

