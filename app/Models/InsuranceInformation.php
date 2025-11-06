<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class InsuranceInformation extends Model
{
    use HasFactory;

    protected $table = 'insurance_information';
    protected $primaryKey = 'insurance_id';

    protected $fillable = [
        'patient_id',
        'provider_name',
        'plan_type',
        'policy_number',
        'group_number',
        'subscriber_name',
        'subscriber_relationship',
        'effective_date',
        'termination_date',
        'is_primary',
    ];

    protected $casts = [
        'effective_date' => 'date',
        'termination_date' => 'date',
        'is_primary' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this insurance
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }
}
