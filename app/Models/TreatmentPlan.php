<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class TreatmentPlan extends Model
{
    use HasFactory;

    protected $table = 'treatment_plans';
    protected $primaryKey = 'plan_id';

    protected $fillable = [
        'encounter_id',
        'plan_description',
        'diagnostic_workup',
        'treatment_details',
        'patient_education',
        'follow_up_instructions',
        'prevention_measures',
        'clingpt_suggestions',
        'created_by',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the encounter for this treatment plan
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the provider who created this plan
     */
    public function creator(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'created_by', 'provider_id');
    }
}
