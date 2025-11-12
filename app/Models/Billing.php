<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Billing extends Model
{
    use HasFactory;

    protected $table = 'billings';
    protected $primaryKey = 'billing_id';

    protected $fillable = [
        'patient_id',
        'encounter_id',
        'invoice_number',
        'billing_date',
        'due_date',
        'total_amount',
        'amount_paid',
        'amount_due',
        'status',
        'notes',
    ];

    protected $casts = [
        'billing_date' => 'date',
        'due_date' => 'date',
        'total_amount' => 'decimal:2',
        'amount_paid' => 'decimal:2',
        'amount_due' => 'decimal:2',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function patient(): BelongsTo
    {
        return $this->belongsTo(Patient::class, 'patient_id', 'patient_id');
    }

    public function encounter(): BelongsTo
    {
        return $this->belongsTo(Encounter::class, 'encounter_id', 'encounter_id');
    }

    public function billingItems(): HasMany
    {
        return $this->hasMany(BillingItem::class, 'billing_id', 'billing_id');
    }

    public function payments(): HasMany
    {
        return $this->hasMany(Payment::class, 'billing_id', 'billing_id');
    }
}
