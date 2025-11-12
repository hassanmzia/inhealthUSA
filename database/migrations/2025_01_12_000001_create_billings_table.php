<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('billings', function (Blueprint $table) {
            $table->id('billing_id');
            $table->unsignedBigInteger('patient_id');
            $table->unsignedBigInteger('encounter_id')->nullable();
            $table->string('invoice_number')->unique();
            $table->date('billing_date');
            $table->date('due_date');
            $table->decimal('total_amount', 10, 2);
            $table->decimal('amount_paid', 10, 2)->default(0);
            $table->decimal('amount_due', 10, 2);
            $table->enum('status', ['Pending', 'Paid', 'Partial', 'Overdue', 'Cancelled'])->default('Pending');
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->foreign('patient_id')->references('patient_id')->on('patients')->onDelete('cascade');
            $table->foreign('encounter_id')->references('encounter_id')->on('encounters')->onDelete('set null');
            $table->index(['patient_id', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('billings');
    }
};
