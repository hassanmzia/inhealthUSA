<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Provider extends Model
{
    use HasFactory;

    protected $table = 'providers';
    protected $primaryKey = 'provider_id';

    protected $fillable = [
        'first_name',
        'last_name',
        'specialty',
        'license_number',
        'npi_number',
        'phone',
        'email',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the provider's full name
     */
    public function getFullNameAttribute(): string
    {
        return "Dr. {$this->first_name} {$this->last_name}";
    }

    /**
     * Get the provider's encounters
     */
    public function encounters(): HasMany
    {
        return $this->hasMany(Encounter::class, 'provider_id', 'provider_id');
    }

    /**
     * Scope to get only active providers
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}
