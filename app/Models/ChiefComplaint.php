<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ChiefComplaint extends Model
{
    use HasFactory;

    protected $table = 'chief_complaints';
    protected $primaryKey = 'complaint_id';
    public $timestamps = false;

    protected $fillable = [
        'encounter_id',
        'chief_complaint',
    ];

    protected $casts = [
        'recorded_at' => 'datetime',
    ];

    /**
     * Get the encounter for this complaint
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }
}
