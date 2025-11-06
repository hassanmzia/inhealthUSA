<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Allergy extends Model
{
    use HasFactory;

    protected $table = 'allergies';
    protected $primaryKey = 'allergy_id';

    protected $fillable = [
        'patient_id',
        'allergen_name',
        'allergy_type',
        'reaction',
        'severity',
        'onset_date',
        'status',
        'notes',
    ];

    protected $casts = [
        'onset_date' => 'date',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the patient for this allergy
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }

    /**
     * Scope for active allergies
     */
    public function scopeActive($query)
    {
        return $query->where('status', 'Active');
    }

    /**
     * Scope for critical allergies
     */
    public function scopeCritical($query)
    {
        return $query->whereIn('severity', ['Severe', 'Life-threatening']);
    }
}
