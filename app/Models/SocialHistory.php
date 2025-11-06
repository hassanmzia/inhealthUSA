<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SocialHistory extends Model
{
    use HasFactory;

    protected $table = 'social_history';
    protected $primaryKey = 'social_history_id';

    protected $fillable = [
        'patient_id',
        'tobacco_use',
        'tobacco_frequency',
        'alcohol_use',
        'alcohol_frequency',
        'drug_use',
        'sexual_history',
        'occupation',
        'living_situation',
        'exercise_frequency',
        'diet_habits',
        'sleep_quality',
        'sleep_duration',
        'hobbies',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this social history
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }
}
