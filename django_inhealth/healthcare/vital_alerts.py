"""
Vital Signs Alert Notification System
Sends email and SMS alerts based on vital sign status
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from twilio.rest import Client


def get_critical_vitals(vital_sign):
    """
    Analyze all vital signs and return critical ones with their status
    Returns: list of tuples (vital_name, value, color, contact_level)
    """
    critical_vitals = []

    # Check Heart Rate
    hr_status = vital_sign.get_heart_rate_status()
    if hr_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Heart Rate', vital_sign.heart_rate, hr_status[0], hr_status[1]))

    # Check Systolic BP
    sbp_status = vital_sign.get_sbp_status()
    if sbp_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Systolic BP', vital_sign.blood_pressure_systolic, sbp_status[0], sbp_status[1]))

    # Check Diastolic BP
    dbp_status = vital_sign.get_dbp_status()
    if dbp_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Diastolic BP', vital_sign.blood_pressure_diastolic, dbp_status[0], dbp_status[1]))

    # Check Temperature
    temp_status = vital_sign.get_temperature_status()
    if temp_status[0] in ['blue', 'red', 'orange']:
        temp_display = f"{vital_sign.temperature_value}°{vital_sign.temperature_unit}"
        critical_vitals.append(('Temperature', temp_display, temp_status[0], temp_status[1]))

    # Check Respiratory Rate
    rr_status = vital_sign.get_respiratory_rate_status()
    if rr_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Respiratory Rate', vital_sign.respiratory_rate, rr_status[0], rr_status[1]))

    # Check Oxygen Saturation
    o2_status = vital_sign.get_oxygen_saturation_status()
    if o2_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Oxygen Saturation', f"{vital_sign.oxygen_saturation}%", o2_status[0], o2_status[1]))

    # Check Glucose
    glucose_status = vital_sign.get_glucose_status()
    if glucose_status[0] in ['blue', 'red', 'orange']:
        critical_vitals.append(('Blood Glucose', f"{vital_sign.glucose} mg/dL", glucose_status[0], glucose_status[1]))

    return critical_vitals


def send_vital_alert_email(recipient_email, recipient_name, patient_name, critical_vitals, alert_type):
    """
    Send email alert for critical vital signs
    alert_type: 'emergency', 'doctor', or 'nurse'
    """
    if not recipient_email:
        return False

    try:
        subject = f"🚨 Critical Vital Signs Alert - {patient_name}"

        message = render_to_string('healthcare/email/vital_alert_email.html', {
            'recipient_name': recipient_name,
            'patient_name': patient_name,
            'critical_vitals': critical_vitals,
            'alert_type': alert_type,
        })

        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_vital_alert_sms(phone_number, patient_name, critical_vitals, alert_type):
    """
    Send SMS alert for critical vital signs
    """
    if not phone_number or not settings.TWILIO_ACCOUNT_SID:
        return False

    try:
        # Format phone number
        if not phone_number.startswith('+'):
            phone_number = f"+1{phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"

        # Build SMS message
        alert_emoji = "🚨" if alert_type in ['emergency', 'doctor'] else "⚠️"
        message = f"{alert_emoji} InHealth Alert: Critical vitals for {patient_name}. "

        for vital_name, value, color, contact_level in critical_vitals[:3]:  # Limit to 3 vitals for SMS
            message += f"{vital_name}: {value} ({contact_level}). "

        message += "Please check your email for details."

        # Send SMS via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def process_vital_alerts(vital_sign):
    """
    Main function to process vital sign alerts and send notifications
    """
    # Get all critical vitals
    critical_vitals = get_critical_vitals(vital_sign)

    if not critical_vitals:
        return  # No critical vitals, no alerts needed

    # Get patient and doctor info
    patient = vital_sign.encounter.patient
    patient_name = patient.full_name
    doctor = vital_sign.encounter.provider

    # Determine highest alert level
    has_blue = any(v[2] == 'blue' for v in critical_vitals)
    has_red = any(v[2] == 'red' for v in critical_vitals)
    has_orange = any(v[2] == 'orange' for v in critical_vitals)

    # Blue or Red alerts: Notify patient and doctor
    if has_blue or has_red:
        alert_type = 'emergency' if has_blue else 'doctor'

        # Notify Patient
        if patient.email:
            send_vital_alert_email(
                patient.email,
                patient.full_name,
                patient_name,
                critical_vitals,
                alert_type
            )

        if patient.phone:
            send_vital_alert_sms(
                patient.phone,
                patient_name,
                critical_vitals,
                alert_type
            )

        # Notify Doctor
        if doctor:
            doctor_user = doctor.user
            if doctor_user.email:
                send_vital_alert_email(
                    doctor_user.email,
                    f"Dr. {doctor.full_name}",
                    patient_name,
                    critical_vitals,
                    alert_type
                )

            if doctor.phone:
                send_vital_alert_sms(
                    doctor.phone,
                    patient_name,
                    critical_vitals,
                    alert_type
                )

    # Orange alerts: Notify nurse
    elif has_orange:
        # Get the nurse who recorded the vitals or any nurse assigned to the patient
        nurse = vital_sign.recorded_by_nurse

        if nurse:
            nurse_user = nurse.user
            if nurse_user.email:
                send_vital_alert_email(
                    nurse_user.email,
                    nurse.full_name,
                    patient_name,
                    critical_vitals,
                    'nurse'
                )

            if nurse.phone:
                send_vital_alert_sms(
                    nurse.phone,
                    patient_name,
                    critical_vitals,
                    'nurse'
                )
