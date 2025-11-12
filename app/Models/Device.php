<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Device extends Model
{
    use HasFactory;

    protected $table = 'devices';
    protected $primaryKey = 'device_id';

    protected $fillable = [
        'patient_id',
        'device_unique_id',
        'device_type',
        'device_name',
        'manufacturer',
        'model_number',
        'firmware_version',
        'capabilities',
        'status',
        'battery_level',
        'last_sync',
        'registration_date',
        'notes',
    ];

    protected $casts = [
        'capabilities' => 'array',
        'battery_level' => 'integer',
        'last_sync' => 'datetime',
        'registration_date' => 'date',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    // Device type constants
    const TYPE_WATCH = 'Watch';
    const TYPE_RING = 'Ring';
    const TYPE_EARCLIP = 'EarClip';
    const TYPE_ADAPTER = 'Adapter';
    const TYPE_PULSE_GLUCOMETER = 'PulseGlucometer';

    // Status constants
    const STATUS_ACTIVE = 'Active';
    const STATUS_INACTIVE = 'Inactive';
    const STATUS_MAINTENANCE = 'Maintenance';
    const STATUS_RETIRED = 'Retired';

    // Capability options
    public static $capabilityOptions = [
        'Pulse',
        'Temperature',
        'SpO2',
        'Blood Pressure',
        'ECG',
        'GPS',
        'Fall Detection',
        'Blood Glucose',
        'Weight',
        'Stethoscope',
        'X-Ray',
        'Sleep Apnea Monitor',
        'Vibration Alert',
    ];

    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }

    /**
     * Get the capabilities as a formatted string
     */
    public function getCapabilitiesStringAttribute(): string
    {
        return is_array($this->capabilities) ? implode(', ', $this->capabilities) : '';
    }

    /**
     * Check if device has a specific capability
     */
    public function hasCapability(string $capability): bool
    {
        return is_array($this->capabilities) && in_array($capability, $this->capabilities);
    }

    /**
     * Get battery status color
     */
    public function getBatteryColorAttribute(): string
    {
        if ($this->battery_level >= 70) return 'green';
        if ($this->battery_level >= 30) return 'yellow';
        return 'red';
    }
}
