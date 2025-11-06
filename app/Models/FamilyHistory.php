<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class FamilyHistory extends Model
{
    use HasFactory;

    protected $table = 'family_history';
    protected $primaryKey = 'family_history_id';

    protected $fillable = [
        'patient_id',
        'relationship',
        'condition_name',
        'age_of_onset',
        'notes',
    ];

    protected $casts = [
        'age_of_onset' => 'integer',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this family history
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }
}
