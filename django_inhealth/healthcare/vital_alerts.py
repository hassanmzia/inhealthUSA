"""
Vital Signs Alert Notification System
Two-stage intelligent alert system:
1. First asks patient for permission to notify providers
2. Sends alerts to doctor/nurse/EMS only based on patient's response
3. Auto-escalates if patient doesn't respond within timeout
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
import uuid


def get_user_notification_preferences(user):
    """
    Get or create notification preferences for a user
    Returns default preferences if not set
    """
    from .models import NotificationPreferences

    try:
        return NotificationPreferences.objects.get(user=user)
    except NotificationPreferences.DoesNotExist:
        # Create default preferences
        return NotificationPreferences.objects.create(user=user)


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


def send_vital_alert_whatsapp(whatsapp_number, patient_name, critical_vitals, alert_type):
    """
    Send WhatsApp alert for critical vital signs via Twilio WhatsApp API
    """
    if not whatsapp_number or not settings.TWILIO_ACCOUNT_SID:
        return False

    try:
        # Format phone number for WhatsApp
        if not whatsapp_number.startswith('+'):
            whatsapp_number = f"+1{whatsapp_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"

        # Build WhatsApp message (can be longer and more detailed than SMS)
        alert_emoji = "🚨" if alert_type in ['emergency', 'doctor'] else "⚠️"

        if alert_type == 'emergency':
            alert_level = "⚠️ *EMERGENCY ALERT*"
        elif alert_type == 'doctor':
            alert_level = "🔴 *CRITICAL ALERT*"
        else:
            alert_level = "⚠️ *WARNING ALERT*"

        message = f"{alert_level}\n\n"
        message += f"*InHealth EHR - Vital Signs Alert*\n"
        message += f"Patient: *{patient_name}*\n\n"
        message += f"*Critical Vital Signs Detected:*\n"

        for vital_name, value, color, contact_level in critical_vitals:
            # Use emojis for visual impact
            if color == 'blue':
                status_emoji = "🔵"
            elif color == 'red':
                status_emoji = "🔴"
            else:
                status_emoji = "🟠"

            message += f"{status_emoji} {vital_name}: *{value}* ({contact_level})\n"

        message += f"\n📧 Check your email for complete details and recommended actions.\n"

        if alert_type == 'emergency':
            message += f"\n⚠️ *IMMEDIATE ACTION REQUIRED*\n"
            message += f"Please seek medical attention immediately."

        # Send WhatsApp message via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Get WhatsApp sender number from settings or use default format
        whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        if not whatsapp_from:
            # Twilio WhatsApp sandbox format
            whatsapp_from = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"
        elif not whatsapp_from.startswith('whatsapp:'):
            whatsapp_from = f"whatsapp:{whatsapp_from}"

        whatsapp_to = f"whatsapp:{whatsapp_number}"

        client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=whatsapp_to
        )
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message to {whatsapp_number}: {str(e)}")
        return False


def get_active_nurses(patient):
    """
    Get all active nurses who should be notified about patient alerts
    Returns nurses from the patient's hospital/department
    """
    from .models import Nurse

    # Try to get nurses from patient's hospital
    if hasattr(patient, 'hospital') and patient.hospital:
        return Nurse.objects.filter(
            hospital=patient.hospital,
            is_active=True
        )

    # If no hospital, get all active nurses (fallback)
    return Nurse.objects.filter(is_active=True)[:5]  # Limit to 5 nurses


def send_patient_permission_request_email(patient_email, patient_name, critical_vitals, alert_type, response_token):
    """
    Send email to patient asking for permission to notify providers
    Includes interactive buttons/links for patient response
    """
    if not patient_email:
        return False

    try:
        subject = f"🚨 Health Alert - Your Response Needed - {patient_name}"

        # Build response URLs
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        approve_doctor_url = f"{base_url}/vital-alert/respond/{response_token}/approve_doctor/"
        approve_nurse_url = f"{base_url}/vital-alert/respond/{response_token}/approve_nurse/"
        approve_ems_url = f"{base_url}/vital-alert/respond/{response_token}/approve_ems/"
        approve_all_url = f"{base_url}/vital-alert/respond/{response_token}/approve_all/"
        decline_url = f"{base_url}/vital-alert/respond/{response_token}/decline/"

        message = render_to_string('healthcare/email/patient_permission_request.html', {
            'patient_name': patient_name,
            'critical_vitals': critical_vitals,
            'alert_type': alert_type,
            'approve_doctor_url': approve_doctor_url,
            'approve_nurse_url': approve_nurse_url,
            'approve_ems_url': approve_ems_url,
            'approve_all_url': approve_all_url,
            'decline_url': decline_url,
        })

        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [patient_email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send permission request email to {patient_email}: {str(e)}")
        return False


def send_patient_permission_request_sms(phone_number, patient_name, critical_vitals, alert_type, response_token):
    """
    Send SMS to patient asking for permission to notify providers
    Includes response link
    """
    if not phone_number or not settings.TWILIO_ACCOUNT_SID:
        return False

    try:
        # Format phone number
        if not phone_number.startswith('+'):
            phone_number = f"+1{phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"

        # Build response URL (shortened for SMS)
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        response_url = f"{base_url}/vital-alert/respond/{response_token}/"

        # Build SMS message
        alert_emoji = "🚨" if alert_type == 'emergency' else "⚠️"
        critical_count = len(critical_vitals)

        message = f"{alert_emoji} HEALTH ALERT: {critical_count} critical vital sign(s) detected for {patient_name}. "
        message += f"Should we notify your healthcare team? Respond: {response_url}"

        # Send SMS via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Failed to send permission request SMS to {phone_number}: {str(e)}")
        return False


def send_patient_permission_request_whatsapp(whatsapp_number, patient_name, critical_vitals, alert_type, response_token):
    """
    Send WhatsApp message to patient asking for permission to notify providers
    Includes interactive response options
    """
    if not whatsapp_number or not settings.TWILIO_ACCOUNT_SID:
        return False

    try:
        # Format phone number for WhatsApp
        if not whatsapp_number.startswith('+'):
            whatsapp_number = f"+1{whatsapp_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"

        # Build response URLs
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        approve_doctor_url = f"{base_url}/vital-alert/respond/{response_token}/approve_doctor/"
        approve_nurse_url = f"{base_url}/vital-alert/respond/{response_token}/approve_nurse/"
        approve_ems_url = f"{base_url}/vital-alert/respond/{response_token}/approve_ems/"
        approve_all_url = f"{base_url}/vital-alert/respond/{response_token}/approve_all/"
        decline_url = f"{base_url}/vital-alert/respond/{response_token}/decline/"

        # Build WhatsApp message
        if alert_type == 'emergency':
            alert_level = "🚨 *EMERGENCY HEALTH ALERT*"
        elif alert_type == 'doctor':
            alert_level = "🔴 *CRITICAL HEALTH ALERT*"
        else:
            alert_level = "⚠️ *HEALTH WARNING ALERT*"

        message = f"{alert_level}\n\n"
        message += f"*InHealth EHR - Your Response Needed*\n"
        message += f"Patient: *{patient_name}*\n\n"
        message += f"*Critical Vital Signs Detected:*\n"

        for vital_name, value, color, contact_level in critical_vitals:
            # Use emojis for visual impact
            if color == 'blue':
                status_emoji = "🔵"
            elif color == 'red':
                status_emoji = "🔴"
            else:
                status_emoji = "🟠"

            message += f"{status_emoji} {vital_name}: *{value}* ({contact_level})\n"

        message += f"\n*Would you like us to notify your healthcare team?*\n\n"
        message += f"Please choose one of the following options:\n\n"
        message += f"1️⃣ Notify Doctor: {approve_doctor_url}\n\n"
        message += f"2️⃣ Notify Nurse: {approve_nurse_url}\n\n"
        message += f"3️⃣ Call EMS: {approve_ems_url}\n\n"
        message += f"4️⃣ Notify All: {approve_all_url}\n\n"
        message += f"❌ No Action Needed: {decline_url}\n\n"

        if alert_type == 'emergency':
            message += f"⏰ *Please respond within 15 minutes, or we will automatically notify your doctor.*"
        else:
            message += f"⏰ Please respond within 15 minutes."

        # Send WhatsApp message via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Get WhatsApp sender number from settings or use default format
        whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        if not whatsapp_from:
            # Twilio WhatsApp sandbox format
            whatsapp_from = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"
        elif not whatsapp_from.startswith('whatsapp:'):
            whatsapp_from = f"whatsapp:{whatsapp_from}"

        whatsapp_to = f"whatsapp:{whatsapp_number}"

        client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=whatsapp_to
        )
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp permission request to {whatsapp_number}: {str(e)}")
        return False


def send_alert_to_providers(alert_response):
    """
    Send alerts to healthcare providers based on patient's response
    Called by VitalSignAlertResponse model after patient responds or auto-escalation

    Args:
        alert_response: VitalSignAlertResponse instance with patient's decision
    """
    from .models import VitalSignAlertResponse

    vital_sign = alert_response.vital_sign
    patient = alert_response.patient
    patient_name = patient.full_name
    critical_vitals = alert_response.critical_vitals_json
    alert_type = alert_response.alert_type

    # Get doctor and nurses
    doctor = vital_sign.encounter.provider if hasattr(vital_sign, 'encounter') else None
    active_nurses = get_active_nurses(patient)

    # Track who was notified
    doctor_notified = False
    nurses_notified = 0
    ems_notified = False

    # ============================================================================
    # NOTIFY DOCTOR (if patient approved)
    # ============================================================================
    if alert_response.patient_wants_doctor and doctor:
        doctor_email = None
        doctor_user = getattr(doctor, 'user', None)

        if doctor_user and doctor_user.email:
            doctor_email = doctor_user.email
        elif hasattr(doctor, 'email') and doctor.email:
            doctor_email = doctor.email

        # Check notification preferences
        if doctor_user:
            prefs = get_user_notification_preferences(doctor_user)

            # Send email if enabled
            if doctor_email and prefs.should_send_email(alert_type):
                send_vital_alert_email(
                    doctor_email,
                    f"Dr. {doctor.full_name}",
                    patient_name,
                    critical_vitals,
                    alert_type
                )
                doctor_notified = True

            # Send SMS if enabled
            if hasattr(doctor, 'phone') and doctor.phone and prefs.should_send_sms(alert_type):
                send_vital_alert_sms(
                    doctor.phone,
                    patient_name,
                    critical_vitals,
                    alert_type
                )

            # Send WhatsApp if enabled
            doctor_whatsapp = prefs.whatsapp_number if prefs.whatsapp_number else (doctor.phone if hasattr(doctor, 'phone') else None)
            if doctor_whatsapp and prefs.should_send_whatsapp(alert_type):
                send_vital_alert_whatsapp(
                    doctor_whatsapp,
                    patient_name,
                    critical_vitals,
                    alert_type
                )
        else:
            # No user account, send alerts by default
            if doctor_email:
                send_vital_alert_email(
                    doctor_email,
                    f"Dr. {doctor.full_name}",
                    patient_name,
                    critical_vitals,
                    alert_type
                )
                doctor_notified = True

            if hasattr(doctor, 'phone') and doctor.phone:
                send_vital_alert_sms(
                    doctor.phone,
                    patient_name,
                    critical_vitals,
                    alert_type
                )

    # ============================================================================
    # NOTIFY NURSES (if patient approved)
    # ============================================================================
    if alert_response.patient_wants_nurse:
        for nurse in active_nurses:
            nurse_user = getattr(nurse, 'user', None)
            nurse_email = None

            if nurse_user and nurse_user.email:
                nurse_email = nurse_user.email
            elif hasattr(nurse, 'email') and nurse.email:
                nurse_email = nurse.email

            # Check notification preferences
            if nurse_user:
                prefs = get_user_notification_preferences(nurse_user)

                # Send email if enabled
                if nurse_email and prefs.should_send_email(alert_type):
                    send_vital_alert_email(
                        nurse_email,
                        nurse.full_name,
                        patient_name,
                        critical_vitals,
                        alert_type
                    )
                    nurses_notified += 1

                # Send SMS if enabled
                if hasattr(nurse, 'phone') and nurse.phone and prefs.should_send_sms(alert_type):
                    send_vital_alert_sms(
                        nurse.phone,
                        patient_name,
                        critical_vitals,
                        alert_type
                    )

                # Send WhatsApp if enabled
                nurse_whatsapp = prefs.whatsapp_number if prefs.whatsapp_number else (nurse.phone if hasattr(nurse, 'phone') else None)
                if nurse_whatsapp and prefs.should_send_whatsapp(alert_type):
                    send_vital_alert_whatsapp(
                        nurse_whatsapp,
                        patient_name,
                        critical_vitals,
                        alert_type
                    )
            else:
                # No user account, send alerts by default
                if nurse_email:
                    send_vital_alert_email(
                        nurse_email,
                        nurse.full_name,
                        patient_name,
                        critical_vitals,
                        alert_type
                    )
                    nurses_notified += 1

                if hasattr(nurse, 'phone') and nurse.phone:
                    send_vital_alert_sms(
                        nurse.phone,
                        patient_name,
                        critical_vitals,
                        alert_type
                    )

    # ============================================================================
    # NOTIFY EMS (if patient approved)
    # ============================================================================
    if alert_response.patient_wants_ems:
        # Get EMS contact from settings
        ems_email = getattr(settings, 'EMS_CONTACT_EMAIL', None)
        ems_phone = getattr(settings, 'EMS_CONTACT_PHONE', None)

        if ems_email:
            send_vital_alert_email(
                ems_email,
                "EMS Dispatch",
                patient_name,
                critical_vitals,
                'emergency'  # EMS always gets emergency level
            )
            ems_notified = True

        if ems_phone:
            send_vital_alert_sms(
                ems_phone,
                patient_name,
                critical_vitals,
                'emergency'
            )

    # Update the alert response record
    alert_response.doctor_notified = doctor_notified
    alert_response.nurse_notified = (nurses_notified > 0)
    alert_response.ems_notified = ems_notified
    alert_response.notifications_sent_at = timezone.now()
    alert_response.patient_response_status = 'completed'
    alert_response.save()

    # Log the notifications
    print(f"Provider notifications sent for patient {patient_name}")
    print(f"Doctor notified: {doctor_notified}, Nurses notified: {nurses_notified}, EMS notified: {ems_notified}")
    print(f"Based on patient response: {alert_response.get_patient_response_status_display()}")


def process_vital_alerts(vital_sign):
    """
    STAGE 1: Two-stage intelligent alert system
    Creates alert and sends permission request to PATIENT ONLY
    Providers are only notified based on patient's response (Stage 2)
    """
    # Get all critical vitals
    critical_vitals = get_critical_vitals(vital_sign)

    if not critical_vitals:
        return  # No critical vitals, no alerts needed

    from .models import VitalSignAlertResponse

    # Get patient info
    patient = vital_sign.encounter.patient
    patient_name = patient.full_name

    # Determine highest alert level
    has_blue = any(v[2] == 'blue' for v in critical_vitals)
    has_red = any(v[2] == 'red' for v in critical_vitals)

    # Determine alert type based on severity
    if has_blue:
        alert_type = 'emergency'
    elif has_red:
        alert_type = 'critical'
    else:
        alert_type = 'warning'

    # ============================================================================
    # STAGE 1: Create Alert Response Record and Send Permission Request to Patient
    # ============================================================================

    # Generate unique response token
    response_token = str(uuid.uuid4())

    # Convert critical_vitals list to JSON-serializable format
    critical_vitals_json = [
        {
            'vital_name': vital[0],
            'value': str(vital[1]),
            'color': vital[2],
            'contact_level': vital[3]
        }
        for vital in critical_vitals
    ]

    # Create alert response record
    alert_response = VitalSignAlertResponse.objects.create(
        vital_sign=vital_sign,
        patient=patient,
        alert_type=alert_type,
        critical_vitals_json=critical_vitals_json,
        response_token=response_token,
        patient_response_status='pending',
        timeout_minutes=15  # Default 15 minutes before auto-escalation
    )

    # Get patient's user account if exists
    patient_user = getattr(patient, 'user', None)

    # Send permission request to patient
    # This is the ONLY notification sent in Stage 1
    if patient_user:
        prefs = get_user_notification_preferences(patient_user)

        # Send email permission request if enabled
        if patient.email and prefs.should_send_email(alert_type):
            send_patient_permission_request_email(
                patient.email,
                patient.full_name,
                critical_vitals,
                alert_type,
                response_token
            )

        # Send SMS permission request if enabled
        if patient.phone and prefs.should_send_sms(alert_type):
            send_patient_permission_request_sms(
                patient.phone,
                patient_name,
                critical_vitals,
                alert_type,
                response_token
            )

        # Send WhatsApp permission request if enabled
        whatsapp_num = prefs.whatsapp_number or patient.phone
        if whatsapp_num and prefs.should_send_whatsapp(alert_type):
            send_patient_permission_request_whatsapp(
                whatsapp_num,
                patient_name,
                critical_vitals,
                alert_type,
                response_token
            )
    else:
        # No user account, send permission requests by default
        if patient.email:
            send_patient_permission_request_email(
                patient.email,
                patient.full_name,
                critical_vitals,
                alert_type,
                response_token
            )

        if patient.phone:
            send_patient_permission_request_sms(
                patient.phone,
                patient_name,
                critical_vitals,
                alert_type,
                response_token
            )

    # Log the alert creation
    print(f"Two-stage vital sign alert created for patient {patient_name}")
    print(f"Alert ID: {alert_response.alert_id}")
    print(f"Alert type: {alert_type.upper()}")
    print(f"Critical vitals: {len(critical_vitals)}")
    print(f"Permission request sent to patient. Waiting for response...")
    print(f"Auto-escalation in {alert_response.timeout_minutes} minutes if no response")

    # STAGE 2 happens when:
    # 1. Patient responds via link -> VitalSignAlertResponse.process_patient_response() -> send_alert_to_providers()
    # 2. Timeout occurs -> Auto-escalation task -> VitalSignAlertResponse.auto_escalate() -> send_alert_to_providers()
