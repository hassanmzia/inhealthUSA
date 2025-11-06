<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SurgicalHistory extends Model
{
    use HasFactory;

    protected $table = 'surgical_history';
    protected $primaryKey = 'surgery_id';
    public $timestamps = false;

    protected $fillable = [
        'patient_id',
        'procedure_name',
        'surgery_date',
        'surgeon_name',
        'hospital',
        'complications',
        'notes',
    ];

    protected $casts = [
        'surgery_date' => 'date',
        'created_at' => 'datetime',
    ];

    /**
     * Get the patient for this surgical history
     */
    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }
}
