<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('devices', function (Blueprint $table) {
            $table->id('device_id');
            $table->unsignedBigInteger('patient_id');
            $table->string('device_unique_id')->unique();
            $table->enum('device_type', ['Watch', 'Ring', 'EarClip', 'Adapter', 'PulseGlucometer']);
            $table->string('device_name', 200);
            $table->string('manufacturer', 200)->nullable();
            $table->string('model_number', 100)->nullable();
            $table->string('firmware_version', 50)->nullable();
            $table->json('capabilities')->nullable();
            $table->enum('status', ['Active', 'Inactive', 'Maintenance', 'Retired'])->default('Active');
            $table->integer('battery_level')->nullable(); // 0-100 percentage
            $table->timestamp('last_sync')->nullable();
            $table->date('registration_date');
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->foreign('patient_id')->references('patient_id')->on('patients')->onDelete('cascade');
            $table->index(['patient_id', 'status']);
            $table->index('device_unique_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('devices');
    }
};
