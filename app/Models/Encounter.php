<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Encounter extends Model
{
    use HasFactory;

    protected $table = 'encounters';
    protected $primaryKey = 'encounter_id';

    protected $fillable = [
        'patient_id',
        'provider_id',
        'encounter_date',
        'encounter_type',
        'status',
        'department_id',
    ];

    protected $casts = [
        'encounter_date' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this encounter
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the provider for this encounter
     */
    public function provider(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'provider_id', 'provider_id');
    }

    /**
     * Get the department for this encounter
     */
    public function department(): BelongsTo
    {
        return $this->belongsTo(Department::class, 'department_id', 'department_id');
    }

    /**
     * Get the chief complaints
     */
    public function chiefComplaints(): HasMany
    {
        return $this->hasMany(ChiefComplaint::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the vital signs
     */
    public function vitalSigns(): HasMany
    {
        return $this->hasMany(VitalSign::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the diagnoses
     */
    public function diagnoses(): HasMany
    {
        return $this->hasMany(Diagnosis::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the prescriptions
     */
    public function prescriptions(): HasMany
    {
        return $this->hasMany(Prescription::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the physical examination
     */
    public function physicalExamination(): HasOne
    {
        return $this->hasOne(PhysicalExamination::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the clinical impression
     */
    public function clinicalImpression(): HasOne
    {
        return $this->hasOne(ClinicalImpression::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the treatment plan
     */
    public function treatmentPlan(): HasOne
    {
        return $this->hasOne(TreatmentPlan::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Scope for active encounters
     */
    public function scopeActive($query)
    {
        return $query->whereIn('status', ['Scheduled', 'In Progress']);
    }

    /**
     * Scope for completed encounters
     */
    public function scopeCompleted($query)
    {
        return $query->where('status', 'Completed');
    }
}
