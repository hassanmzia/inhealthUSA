<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ClinicalImpression extends Model
{
    use HasFactory;

    protected $table = 'clinical_impressions';
    protected $primaryKey = 'impression_id';

    protected $fillable = [
        'encounter_id',
        'patient_evaluation_summary',
        'clinical_impression',
        'differential_diagnoses',
        'clinical_considerations',
        'clingpt_suggestions',
        'created_by',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the encounter for this impression
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the provider who created this impression
     */
    public function creator(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'created_by', 'provider_id');
    }
}
