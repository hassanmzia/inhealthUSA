<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class Patient extends Model
{
    use HasFactory;

    protected $table = 'patients';
    protected $primaryKey = 'patient_id';

    protected $fillable = [
        'first_name',
        'last_name',
        'middle_name',
        'date_of_birth',
        'age',
        'gender',
        'address_street',
        'address_city',
        'address_state',
        'address_zip',
        'phone_number',
        'email',
        'is_active',
    ];

    protected $casts = [
        'date_of_birth' => 'date',
        'is_active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient's full name
     */
    public function getFullNameAttribute(): string
    {
        return "{$this->first_name} {$this->last_name}";
    }

    /**
     * Get the patient's encounters
     */
    public function encounters(): HasMany
    {
        return $this->hasMany(Encounter::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's emergency contacts
     */
    public function emergencyContacts(): HasMany
    {
        return $this->hasMany(EmergencyContact::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's insurance information
     */
    public function insurance(): HasMany
    {
        return $this->hasMany(InsuranceInformation::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's allergies
     */
    public function allergies(): HasMany
    {
        return $this->hasMany(Allergy::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's prescriptions
     */
    public function prescriptions(): HasMany
    {
        return $this->hasMany(Prescription::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's social history
     */
    public function socialHistory(): HasOne
    {
        return $this->hasOne(SocialHistory::class, 'patient_id', 'patient_id')->latestOfMany('social_history_id');
    }

    /**
     * Get the patient's past medical history
     */
    public function pastMedicalHistory(): HasMany
    {
        return $this->hasMany(PastMedicalHistory::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's surgical history
     */
    public function surgicalHistory(): HasMany
    {
        return $this->hasMany(SurgicalHistory::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's family history
     */
    public function familyHistory(): HasMany
    {
        return $this->hasMany(FamilyHistory::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's billings
     */
    public function billings(): HasMany
    {
        return $this->hasMany(Billing::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's payments
     */
    public function payments(): HasMany
    {
        return $this->hasMany(Payment::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the patient's devices
     */
    public function devices(): HasMany
    {
        return $this->hasMany(Device::class, 'patient_id', 'patient_id');
    }

    /**
     * Get messages sent by the patient
     */
    public function sentMessages(): MorphMany
    {
        return $this->morphMany(Message::class, 'sender');
    }

    /**
     * Get messages received by the patient
     */
    public function receivedMessages(): MorphMany
    {
        return $this->morphMany(Message::class, 'recipient');
    }

    /**
     * Get all messages (sent and received)
     */
    public function messages()
    {
        return Message::where(function($query) {
            $query->where('sender_type', self::class)
                  ->where('sender_id', $this->patient_id);
        })->orWhere(function($query) {
            $query->where('recipient_type', self::class)
                  ->where('recipient_id', $this->patient_id);
        })->orderBy('created_at', 'desc');
    }

    /**
     * Get unread messages count
     */
    public function getUnreadMessagesCountAttribute(): int
    {
        return $this->receivedMessages()->unread()->count();
    }

    /**
     * Scope to get only active patients
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}
