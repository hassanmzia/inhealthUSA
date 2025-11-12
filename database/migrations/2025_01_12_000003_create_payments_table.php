<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payments', function (Blueprint $table) {
            $table->id('payment_id');
            $table->unsignedBigInteger('patient_id');
            $table->unsignedBigInteger('billing_id')->nullable();
            $table->dateTime('payment_date');
            $table->decimal('amount', 10, 2);
            $table->enum('payment_method', ['Cash', 'Credit Card', 'Debit Card', 'Check', 'Bank Transfer', 'Insurance', 'Other'])->default('Cash');
            $table->string('transaction_id')->nullable();
            $table->enum('status', ['Completed', 'Pending', 'Failed', 'Refunded'])->default('Completed');
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->foreign('patient_id')->references('patient_id')->on('patients')->onDelete('cascade');
            $table->foreign('billing_id')->references('billing_id')->on('billings')->onDelete('set null');
            $table->index(['patient_id', 'payment_date']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payments');
    }
};
