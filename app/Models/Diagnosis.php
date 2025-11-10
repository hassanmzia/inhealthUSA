<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Diagnosis extends Model
{
    use HasFactory;

    protected $table = 'diagnoses';
    protected $primaryKey = 'diagnosis_id';
    public $timestamps = false;

    protected $fillable = [
        'encounter_id',
        'diagnosis_description',
        'icd10_code',
        'icd11_code',
        'diagnosis_type',
        'status',
        'onset_date',
        'resolved_date',
        'notes',
        'diagnosed_by',
    ];

    protected $casts = [
        'onset_date' => 'date',
        'resolved_date' => 'date',
        'diagnosed_at' => 'datetime',
    ];

    /**
     * Get the encounter for this diagnosis
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the provider who made the diagnosis
     */
    public function diagnosingProvider(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'diagnosed_by', 'provider_id');
    }

    /**
     * Scope for active diagnoses
     */
    public function scopeActive($query)
    {
        return $query->where('status', 'Active');
    }

    /**
     * Scope for primary diagnoses
     */
    public function scopePrimary($query)
    {
        return $query->where('diagnosis_type', 'Primary');
    }
}
