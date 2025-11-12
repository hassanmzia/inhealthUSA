<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;

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
     * Get messages sent by the provider
     */
    public function sentMessages(): MorphMany
    {
        return $this->morphMany(Message::class, 'sender');
    }

    /**
     * Get messages received by the provider
     */
    public function receivedMessages(): MorphMany
    {
        return $this->morphMany(Message::class, 'recipient');
    }

    /**
     * Get all messages (sent and received)
     */
    public function messages()
    {
        return Message::where(function($query) {
            $query->where('sender_type', self::class)
                  ->where('sender_id', $this->provider_id);
        })->orWhere(function($query) {
            $query->where('recipient_type', self::class)
                  ->where('recipient_id', $this->provider_id);
        })->orderBy('created_at', 'desc');
    }

    /**
     * Get unread messages count
     */
    public function getUnreadMessagesCountAttribute(): int
    {
        return $this->receivedMessages()->unread()->count();
    }

    /**
     * Scope to get only active providers
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}
