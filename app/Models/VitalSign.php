<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class VitalSign extends Model
{
    use HasFactory;

    protected $table = 'vital_signs';
    protected $primaryKey = 'vital_signs_id';
    public $timestamps = false;

    protected $fillable = [
        'encounter_id',
        'temperature_value',
        'temperature_unit',
        'blood_pressure_systolic',
        'blood_pressure_diastolic',
        'heart_rate',
        'respiratory_rate',
        'oxygen_saturation',
        'weight_value',
        'weight_unit',
        'height_value',
        'height_unit',
        'bmi',
        'notes',
        'recorded_by',
    ];

    protected $casts = [
        'recorded_at' => 'datetime',
        'temperature_value' => 'decimal:1',
        'oxygen_saturation' => 'decimal:2',
        'weight_value' => 'decimal:2',
        'height_value' => 'decimal:2',
        'bmi' => 'decimal:1',
    ];

    /**
     * Get the encounter for this vital sign
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the provider who recorded this
     */
    public function recorder(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'recorded_by', 'provider_id');
    }

    /**
     * Get formatted blood pressure
     */
    public function getBloodPressureAttribute(): string
    {
        return "{$this->blood_pressure_systolic}/{$this->blood_pressure_diastolic}";
    }
}
