<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Prescription extends Model
{
    use HasFactory;

    protected $table = 'prescriptions';
    protected $primaryKey = 'prescription_id';

    protected $fillable = [
        'encounter_id',
        'patient_id',
        'provider_id',
        'medication_id',
        'medication_name',
        'dosage',
        'frequency',
        'duration',
        'quantity',
        'refills',
        'route',
        'instructions',
        'pharmacy_name',
        'pharmacy_address',
        'pharmacy_phone',
        'prescribed_date',
        'start_date',
        'end_date',
        'status',
        'notes',
    ];

    protected $casts = [
        'prescribed_date' => 'date',
        'start_date' => 'date',
        'end_date' => 'date',
        'quantity' => 'integer',
        'refills' => 'integer',
    ];

    /**
     * Get the encounter for this prescription
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the patient for this prescription
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the provider who prescribed this
     */
    public function provider(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'provider_id', 'provider_id');
    }

    /**
     * Scope for active prescriptions
     */
    public function scopeActive($query)
    {
        return $query->where('status', 'Active');
    }
}
