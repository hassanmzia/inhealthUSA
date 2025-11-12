<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Message extends Model
{
    use HasFactory;

    protected $primaryKey = 'message_id';

    protected $fillable = [
        'sender_id',
        'sender_type',
        'recipient_id',
        'recipient_type',
        'subject',
        'body',
        'is_read',
        'read_at',
        'parent_message_id',
    ];

    protected $casts = [
        'is_read' => 'boolean',
        'read_at' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the sender (polymorphic relation)
     */
    public function sender()
    {
        return $this->morphTo(__FUNCTION__, 'sender_type', 'sender_id');
    }

    /**
     * Get the recipient (polymorphic relation)
     */
    public function recipient()
    {
        return $this->morphTo(__FUNCTION__, 'recipient_type', 'recipient_id');
    }

    /**
     * Get the parent message (for threading)
     */
    public function parentMessage(): BelongsTo
    {
        return $this->belongsTo(Message::class, 'parent_message_id', 'message_id');
    }

    /**
     * Get replies to this message
     */
    public function replies()
    {
        return $this->hasMany(Message::class, 'parent_message_id', 'message_id');
    }

    /**
     * Mark message as read
     */
    public function markAsRead(): void
    {
        if (!$this->is_read) {
            $this->update([
                'is_read' => true,
                'read_at' => now(),
            ]);
        }
    }

    /**
     * Scope to filter unread messages
     */
    public function scopeUnread($query)
    {
        return $query->where('is_read', false);
    }

    /**
     * Scope to filter read messages
     */
    public function scopeRead($query)
    {
        return $query->where('is_read', true);
    }
}
