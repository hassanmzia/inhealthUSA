<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PhysicalExamination extends Model
{
    use HasFactory;

    protected $table = 'physical_examinations';
    protected $primaryKey = 'exam_id';
    public $timestamps = false;

    protected $fillable = [
        'encounter_id',
        'general_appearance',
        'heent_findings',
        'neck_findings',
        'cardiovascular_findings',
        'respiratory_findings',
        'gastrointestinal_findings',
        'genitourinary_findings',
        'musculoskeletal_findings',
        'neurological_findings',
        'integumentary_findings',
        'psychiatric_findings',
        'performed_by',
    ];

    protected $casts = [
        'performed_at' => 'datetime',
    ];

    /**
     * Get the encounter for this examination
     */
    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    /**
     * Get the provider who performed the examination
     */
    public function performer(): BelongsTo
    {
        return $this->belongsTo(Provider::class, 'performed_by', 'provider_id');
    }
}
