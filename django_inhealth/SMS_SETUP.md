# SMS Setup Guide for InHealth EHR

This guide explains how to configure SMS messaging functionality using Twilio.

## Prerequisites

1. A Twilio account (sign up at https://www.twilio.com/)
2. A Twilio phone number

## Setup Steps

### 1. Install Required Package

The Twilio package is already included in `requirements.txt`. If you haven't installed it yet:

```bash
pip install twilio==9.0.4
```

### 2. Get Twilio Credentials

1. Log in to your Twilio account at https://www.twilio.com/console
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Get a Twilio phone number from https://www.twilio.com/console/phone-numbers
   - Or use your existing Twilio number

### 3. Configure Environment Variables

Add the following to your `.env` file (create it from `.env.example` if it doesn't exist):

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Important Notes:**
- Replace `your_account_sid_here` with your actual Twilio Account SID
- Replace `your_auth_token_here` with your actual Twilio Auth Token
- Use your Twilio phone number in E.164 format (e.g., `+1234567890`)
- **Never commit your `.env` file to version control!**

### 4. Test SMS Functionality

1. Ensure doctors and patients have phone numbers in their profiles
2. Compose a message from doctor to patient (or vice versa)
3. Check the "Send SMS notification" checkbox
4. Send the message
5. The recipient should receive an SMS notification

## Phone Number Format

Phone numbers in the database can be in any format:
- `(123) 456-7890`
- `123-456-7890`
- `1234567890`
- `+1234567890`

The system automatically converts them to E.164 format for Twilio.

## Troubleshooting

### "SMS service not configured" error
- Check that all three environment variables are set
- Restart your Django server after adding environment variables

### "Failed to send SMS" error
- Verify your Twilio credentials are correct
- Check that your Twilio account has sufficient balance
- Ensure the recipient's phone number is valid
- Check Twilio console for error logs

### Phone number not in profile
- Doctors: Update phone number in Provider profile
- Patients: Update phone number in Patient profile

## Production Considerations

1. **Security**: Store credentials in environment variables, not in code
2. **Rate Limits**: Be aware of Twilio's rate limits
3. **Costs**: Monitor your Twilio usage and costs
4. **Compliance**: Ensure SMS usage complies with healthcare regulations (HIPAA, etc.)
5. **Opt-in**: Consider implementing SMS opt-in/opt-out functionality

## SMS Message Content

When a message is sent with SMS notification:
- **From Doctor to Patient**: "New message from Dr. [Name]\nSubject: [Subject]\n\nLog in to view your message."
- **From Patient to Doctor**: "New message from patient [Name]\nSubject: [Subject]\n\nLog in to view your message."

## Support

For Twilio support, visit: https://support.twilio.com/
For InHealth EHR support, contact your system administrator.
