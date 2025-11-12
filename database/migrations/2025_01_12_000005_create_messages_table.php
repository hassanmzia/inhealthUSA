<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('messages', function (Blueprint $table) {
            $table->id('message_id');

            // Polymorphic sender (Patient or Provider)
            $table->unsignedBigInteger('sender_id');
            $table->string('sender_type'); // App\Models\Patient or App\Models\Provider

            // Polymorphic recipient (Patient or Provider)
            $table->unsignedBigInteger('recipient_id');
            $table->string('recipient_type'); // App\Models\Patient or App\Models\Provider

            // Message content
            $table->string('subject');
            $table->text('body');

            // Message status
            $table->boolean('is_read')->default(false);
            $table->timestamp('read_at')->nullable();

            // Threading support
            $table->unsignedBigInteger('parent_message_id')->nullable();

            $table->timestamps();

            // Indexes
            $table->index(['sender_id', 'sender_type']);
            $table->index(['recipient_id', 'recipient_type']);
            $table->index('is_read');
            $table->index('created_at');

            // Foreign key for threading
            $table->foreign('parent_message_id')
                  ->references('message_id')
                  ->on('messages')
                  ->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('messages');
    }
};
