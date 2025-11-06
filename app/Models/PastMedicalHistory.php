<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PastMedicalHistory extends Model
{
    use HasFactory;

    protected $table = 'past_medical_history';
    protected $primaryKey = 'pmh_id';

    protected $fillable = [
        'patient_id',
        'condition_name',
        'icd10_code',
        'diagnosis_date',
        'status',
        'notes',
    ];

    protected $casts = [
        'diagnosis_date' => 'date',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this medical history
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }
}
